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

import struct
import subprocess
import sys
import time

import xcffib
import xcffib.xproto

from gi.repository import Gtk


class SgtSocketLauncher:

    def __init__(self):
        self.socket = Gtk.Socket.new()
        self.socket.set_can_focus(True)
        self.socket.set_focus_on_click(True)
        self.socket.set_receives_default(True)

    def get_socket(self):
        return self.socket

    def launch(self, path, wm_class=None):
        if wm_class is None:
            wm_class = path

        retry_count = 10
        retry_timer = 0.05

        proc = subprocess.Popen([path])

        count = 0
        window_id = 0
        while window_id == 0:
            proc.poll()
            if proc.returncode is not None:
                return False

            window_id = get_window_id("_NET_WM_PID", proc.pid)
            if window_id == 0:
                window_id = get_window_id("WM_CLASS", wm_class)
            if window_id == 0:
                count += 1
                if count == retry_count:
                    return False
                time.sleep(retry_timer)

        count = 0
        while True:
            proc.poll()
            if proc.returncode is not None:
                return False

            plug_count = 0
            while self.socket.get_plug_window() is None:
                self.socket.add_id(window_id)
                if self.socket.get_plug_window() is None:
                    plug_count += 1
                    if plug_count == retry_count:
                        return False
                    time.sleep(retry_timer)

            if self.socket.get_plug_window().get_xid() == window_id:
                proc.poll()
                if proc.returncode is not None:
                    return

                return True

            count += 1
            if count == retry_count:
                return False
            time.sleep(retry_timer)

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
