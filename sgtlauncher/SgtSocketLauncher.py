# -*- Mode: Python; coding: utf-8; indent-tabs-mode: nil; tab-width: 4 -*-
#
#   This program is free software: you can redistribute it and/or modify it
#   under the terms of the GNU General Public License as published by the
#   Free Software Foundation, either version 3 of the License, or
#   (at your option) any later version.
#
#   This program is distributed in the hope that it will be useful, but
#   WITHOUT ANY WARRANTY; without even the implied warranties of
#   MERCHANTABILITY, SATISFACTORY QUALITY, or FITNESS FOR A PARTICULAR
#   PURPOSE.  See the GNU General Public License for more details.
#
#   You should have received a copy of the GNU General Public License along
#   with this program.  If not, see <http://www.gnu.org/licenses/>.

import os
import struct
import time
import typing

import xcffib
import xcffib.xproto

from gi.repository import GdkX11
from gi.repository import GLib

if typing.TYPE_CHECKING:
    import subprocess
    from gi.repository import Gtk


class SgtSocketLauncher:
    def __init__(self):
        self.retry_count = 10
        self.retry_timer = 0.05
        self.process = None
        self.window_id = None
        self.embeddable = self.get_embeddable()

    def get_embeddable(self):
        override = os.environ.get("SGT_ENABLE_EMBED")
        if override is not None:
            return override == "1"

        # Windows are not socketable under Wayland
        wayland = os.environ.get("WAYLAND_DISPLAY")
        if wayland is not None:
            return False

        # Flatpak seems to block embedding (sgt-launcher#8)
        container = os.environ.get("container")
        if container is not None:
            if container == "flatpak":
                return False

        # GNOME doesn't allow for embedded window focus (sgt-launcher#7)
        desktop = os.environ.get("XDG_CURRENT_DESKTOP")
        if desktop is not None:
            if "gnome" in desktop.lower():
                return False

        return True

    def launch(self, socket: "Gtk.Socket", process: "subprocess.Popen",
               on_success: typing.Callable[[], None],
               on_failure: typing.Callable[[], None]) -> None:
        self.process = process

        self.window_id = self.try_to_get_window_id()
        if self.window_id is None:
            on_failure()
            return

        # https://tronche.com/gui/x/icccm/sec-4.html#s-4.1.4
        self.withdraw_window()

        def callback() -> None:
            withdrawn = self.wait_for_window_withdraw()
            if not withdrawn:
                on_failure()
                return

            embedded = self.try_to_embed_window(socket)
            if not embedded:
                on_failure()
                return

            on_success()

        # continue executing after handling current event and withdraw event
        GLib.timeout_add(1000, callback)

    def try_to_get_window_id(self) -> typing.Optional[int]:
        for count in range(self.retry_count):
            self.process.poll()
            if self.process.returncode is not None:
                return None
            window_id = get_window_id("_NET_WM_PID", self.process.pid)
            if window_id != 0:
                return window_id
            time.sleep(self.retry_timer)
        return None

    def withdraw_window(self) -> None:
        gdk_display = GdkX11.X11Display.get_default()
        gdk_window = GdkX11.X11Window.foreign_new_for_display(
            gdk_display, self.window_id)
        gdk_window.withdraw()

    def wait_for_window_withdraw(self) -> bool:
        for count in range(self.retry_count):
            self.process.poll()
            if self.process.returncode is not None:
                return False
            withdrawn = is_withdrawn(self.window_id)
            if withdrawn:
                return True
            time.sleep(self.retry_timer)
        return False

    def try_to_embed_window(self, socket: "Gtk.Socket") -> bool:
        for count in range(self.retry_count):
            self.process.poll()
            if self.process.returncode is not None:
                return False
            socket.add_id(self.window_id)
            if socket.get_plug_window() is not None and \
               socket.get_plug_window().get_xid() == self.window_id:
                return True
            time.sleep(self.retry_timer)
        return False


def get_window_id(prop, value):
    window_id = 0

    c = xcffib.connect()
    root = c.get_setup().roots[0].root

    _NET_CLIENT_LIST = c.core.InternAtom(True, len('_NET_CLIENT_LIST'),
                                         '_NET_CLIENT_LIST').reply().atom

    raw_clientlist = c.core.GetProperty(False, root, _NET_CLIENT_LIST,
                                        xcffib.xproto.GetPropertyType.Any,
                                        0, 2 ** 32 - 1).reply()
    clientlist = get_property_value(raw_clientlist)

    cookies = {}
    for ident in clientlist:
        if prop in dir(xcffib.xproto.Atom):
            atom = getattr(xcffib.xproto.Atom, prop)
        else:
            atom = c.core.InternAtom(True, len(prop), prop).reply().atom
        cookies[ident] = c.core.GetProperty(False, ident, atom,
                                            xcffib.xproto.GetPropertyType.Any,
                                            0, 2 ** 32 - 1)

    for ident in cookies:
        winclass = get_property_value(cookies[ident].reply())
        if isinstance(winclass, list):
            if value in winclass:
                window_id = ident
                break

    c.disconnect()
    return window_id


def get_property_value(property_reply):
    assert isinstance(property_reply, xcffib.xproto.GetPropertyReply)

    if property_reply.format == 8:
        if 0 in property_reply.value:
            ret = []
            s = ''
            for o in property_reply.value:
                if o == 0:
                    ret.append(s)
                    s = ''
                else:
                    s += chr(o)
        else:
            ret = str(property_reply.value.buf().replace(b'\x00', b'\t'),
                      "utf-8")
            ret = ret.split("\t")

        return ret
    elif property_reply.format in (16, 32):
        return list(struct.unpack('I' * property_reply.value_len,
                                  property_reply.value.buf()))

    return None


def is_withdrawn(window_id: int) -> bool:
    c = xcffib.connect()

    atom = c.core.InternAtom(True, len('WM_STATE'), 'WM_STATE').reply().atom
    property_reply = c.core.GetProperty(False, window_id, atom,
                                        xcffib.xproto.GetPropertyType.Any,
                                        0, 2 ** 32 - 1).reply()
    property_value = get_property_value(property_reply)
    c.disconnect()
    withdrawn = not property_value or property_value[0] == 0
    return withdrawn
