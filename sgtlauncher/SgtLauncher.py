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
import subprocess
import gi

from locale import gettext as _

gi.require_version('Gtk', '3.0')
gi.require_version('Gdk', '3.0')

from gi.repository import Gdk  # noqa: E402
from gi.repository import GdkPixbuf  # noqa: E402
from gi.repository import Gtk  # noqa: E402
from gi.repository import Gio  # noqa: E402
from gi.repository import GLib  # noqa: E402
from gi.repository import Pango  # noqa: E402

from . import SgtSocketLauncher  # noqa: E402
import sgtlauncher_lib  # noqa: E402


class MyWindow(Gtk.ApplicationWindow):
    def __init__(self, app, appname, launchers):
        self.appname = appname
        self.title = _("SGT Puzzles Collection")

        Gtk.Window.__init__(self, title=self.title, application=app)
        self.set_title(self.title)
        self.set_role(self.title)
        self.set_startup_id("sgt-launcher")
        self.set_default_icon_name(appname)
        self.set_default_size(800, 600)
        self.set_position(Gtk.WindowPosition.CENTER)

        self.launcher = SgtSocketLauncher.SgtSocketLauncher()

        self.game_process = None

        self.socket = Gtk.Socket.new()
        self.socket.set_can_focus(True)
        self.socket.set_focus_on_click(True)
        self.socket.set_receives_default(True)
        self.socket.connect("plug_removed", self.socket_disconnect)
        self.socket.connect("plug_added", self.socket_connect)

        display = Gdk.Display.get_default()
        seat = display.get_default_seat()
        self.keyboard = seat.get_keyboard()

        self.setup_ui(launchers)

    def setup_ui(self, launchers):
        """Initialize the headerbar, actions, and individual views"""
        self.hb = Gtk.HeaderBar()
        self.hb.props.show_close_button = True
        self.hb.props.title = self.title
        self.set_titlebar(self.hb)

        self.set_wmclass("sgt-launcher", _("SGT Puzzles Collection"))

        self.stack = Gtk.Stack.new()
        self.add(self.stack)

        self.setup_action_buttons()
        self.setup_launcher_view(launchers)
        self.setup_loading_view()
        self.setup_game_view()

    def setup_action_buttons(self):
        """Initialize the in-game action buttons"""
        # Button definitions
        buttons = {
            "new-game": (_("New Game"), "document-new-symbolic", 57,
                         Gdk.KEY_n),
            "undo": (_("Undo"), "edit-undo-symbolic", 30, Gdk.KEY_u),
            "redo": (_("Redo"), "edit-redo-symbolic", 27, Gdk.KEY_r)
        }

        # Setup Action buttons
        self.action_buttons = {}
        for key in list(buttons.keys()):
            # Create the button
            self.action_buttons[key] = Gtk.Button.new_from_icon_name(
                buttons[key][1], Gtk.IconSize.LARGE_TOOLBAR)
            # Add a tooltip
            self.action_buttons[key].set_tooltip_text(buttons[key][0])
            # Enable hiding
            self.action_buttons[key].set_no_show_all(True)
            # Connect the clicked event
            self.action_buttons[key].connect("clicked",
                                             self.on_keyboard_button_click,
                                             buttons[key][2], buttons[key][3])

        # Add the buttons
        self.hb.pack_start(self.action_buttons["new-game"])

        buttonbox = Gtk.Box.new(Gtk.Orientation.HORIZONTAL, 0)
        ctx = buttonbox.get_style_context()
        ctx.add_class("linked")

        buttonbox.pack_start(self.action_buttons["undo"], False, False, 0)
        buttonbox.pack_start(self.action_buttons["redo"], False, False, 0)
        self.hb.pack_start(buttonbox)

    def setup_launcher_view(self, launchers):
        """Initialize the launcher view with the games"""
        # Populate the model (name, comment, icon_name, exe)
        listmodel = Gtk.ListStore(str, str, str, str)
        for launcher in launchers:
            listmodel.append(launcher)

        # Initialize the treeview
        view = Gtk.TreeView(model=listmodel)
        view.set_headers_visible(False)

        # Create and pack the custom column
        col = Gtk.TreeViewColumn.new()

        # Pixbuf: icon renderer
        pixbuf = Gtk.CellRendererPixbuf()
        pixbuf.props.stock_size = Gtk.IconSize.DIALOG
        col.pack_start(pixbuf, False)
        col.add_attribute(pixbuf, "icon-name", 2)

        # Text: label renderer
        text = Gtk.CellRendererText()
        text.props.wrap_mode = Pango.WrapMode.WORD
        col.pack_start(text, True)
        col.add_attribute(text, "text", 0)

        # Draw custom cell
        col.set_cell_data_func(text, self.treeview_cell_text_func, None)
        col.set_cell_data_func(pixbuf, self.treeview_cell_pixbuf_func, None)

        # Add the column and enable typeahead
        view.append_column(col)
        view.set_search_column(0)

        view.connect("row-activated", self.on_activated)

        # Add the treeview to a scrolled window
        scrolled = Gtk.ScrolledWindow.new()
        scrolled.add(view)

        self.stack.add_named(scrolled, "launcher")

    def setup_loading_view(self):
        """Initialize the loading view used to correctly embed the window"""
        parent_box = Gtk.Box.new(Gtk.Orientation.VERTICAL, 0)
        child_box = Gtk.Box.new(Gtk.Orientation.VERTICAL, 6)

        self.launching_image = Gtk.Image.new()
        self.launching_title = Gtk.Label.new()
        self.launching_label = Gtk.Label.new(_("Please wait..."))

        spinner = Gtk.Spinner.new()
        spinner.start()

        child_box.pack_start(self.launching_image, False, False, 0)
        child_box.pack_start(self.launching_title, False, False, 0)
        child_box.pack_start(self.launching_label, False, False, 0)
        child_box.pack_start(spinner, False, False, 0)

        parent_box.set_center_widget(child_box)

        self.stack.add_named(parent_box, "loading")

    def setup_game_view(self):
        """Initialize the game view where the game is embedded"""
        self.stack.add_named(self.socket, "game")

    # Callables
    def hide_actions(self):
        """Hide the in-game action buttons"""
        for key in list(self.action_buttons.keys()):
            self.action_buttons[key].hide()

    def show_actions(self):
        """Show the in-game action buttons"""
        for key in list(self.action_buttons.keys()):
            self.action_buttons[key].show()

    def set_subtitle(self, title):
        """Set the window subtitle"""
        self.hb.set_subtitle(title)

    def launch(self, title, icon_name, path):
        """Launch the specified application"""
        if self.launcher.embeddable:
            self.embedded_launch(title, icon_name, path)
        else:
            self.unembedded_launch(title, icon_name, path)

    def embedded_launch(self, title, icon_name, path):
        # Toggle GTK_CSD=0 to guarantee embedding
        csd_env = os.environ.copy()
        csd_env["GTK_CSD"] = "0"

        self.game_process = subprocess.Popen([path], env=csd_env)

        subtitle = _("Loading %s") % title

        if os.path.isfile(icon_name):
            self.launching_image.set_from_file(icon_name)
        else:
            self.launching_image.set_from_icon_name(icon_name,
                                                    Gtk.IconSize.DIALOG)
        self.launching_title.set_markup("<b>%s</b>" % title)
        self.set_view("loading", icon_name, subtitle)

        def on_success():
            self.set_view("game", icon_name, title)

        def on_error():
            return self.back_to_launcher()

        self.launcher.launch(self.socket, self.game_process,
                             on_success, on_error)

    def unembedded_launch(self, title, icon_name, path):
        subtitle = _("Loading %s") % title

        if os.path.isfile(icon_name):
            self.launching_image.set_from_file(icon_name)
        else:
            self.launching_image.set_from_icon_name(icon_name,
                                                    Gtk.IconSize.DIALOG)
        self.launching_title.set_markup("<b>%s</b>" % title)
        self.set_view("loading", icon_name, subtitle)

        def poll_process():
            res = GLib.SOURCE_CONTINUE
            if self.game_process is None:
                res = GLib.SOURCE_REMOVE
            if self.game_process.poll() is not None:
                res = GLib.SOURCE_REMOVE
            if res == GLib.SOURCE_REMOVE:
                self.back_to_launcher()
            return res

        def launch_game():
            self.game_process = subprocess.Popen([path])
            self.hide()
            GLib.timeout_add(200, poll_process)
            return GLib.SOURCE_REMOVE

        GLib.timeout_add(500, launch_game)

    def back_to_launcher(self):
        if not self.launcher.embeddable:
            self.show()
        if self.game_process is not None:
            self.game_process.terminate()
            self.game_process = None
        self.set_view("launcher")

    def set_view(self, name, icon_name=None, subtitle=None):
        """Change the view, setting the icon name and subtitle"""
        if name == "launcher":
            self.stack.set_transition_type(Gtk.StackTransitionType.OVER_RIGHT)
            self.hide_actions()
        if name == "loading":
            self.stack.set_transition_type(Gtk.StackTransitionType.OVER_LEFT)
            self.hide_actions()
        if name == "game":
            self.stack.set_transition_type(Gtk.StackTransitionType.OVER_LEFT)
            self.show_actions()

        title = self.title
        if icon_name is None:
            icon_name = self.appname
        if subtitle is None:
            subtitle = ""
        else:
            title = "%s - %s" % (title, subtitle)

        if name != "launcher" and os.path.isfile(icon_name):
            self.set_default_icon_from_file(icon_name)
        else:
            self.set_default_icon_name(icon_name)

        self.set_subtitle(subtitle)
        self.stack.set_visible_child_name(name)

        self.get_window().set_title(title)

        if name == "game":
            self.socket.grab_focus()
        else:
            self.grab_focus()

    # Events
    def socket_connect(self, socket):
        """Embedded window connected"""
        return True

    def socket_disconnect(self, socket):
        """Embedded window disconnected"""
        self.back_to_launcher()
        return True

    def on_keyboard_button_click(self, button, keycode, keyval):
        """Send keypress to embedded window on button click"""
        self.socket.grab_focus()
        event = Gdk.Event.new(Gdk.EventType.KEY_PRESS)
        event.keyval = keyval
        event.hardware_keycode = keycode
        event.window = self.get_window()
        event.set_device(self.keyboard)
        event.put()

    def treeview_cell_text_func(self, col, renderer, model, treeiter, data):
        """Render the treeview row"""
        name, comment, icon_name, exe = model[treeiter][:]
        markup = "<b>%s</b>\n%s" % (name, comment)
        renderer.set_property('markup', markup)
        return

    def treeview_cell_pixbuf_func(self, col, renderer, model, treeiter, data):
        """Render the treeview row"""
        name, comment, icon_name, exe = model[treeiter][:]
        if os.path.isfile(icon_name):
            pixbuf = GdkPixbuf.Pixbuf.new_from_file_at_size(icon_name, 48, 48)
            renderer.set_property("pixbuf", pixbuf)
        return

    def on_activated(self, widget, treeiter, col):
        """Launch the selected application"""
        model = widget.get_model()
        name, comment, icon_name, exe = model[treeiter][:]
        self.launch(name, icon_name, exe)


class MyAboutDialog(Gtk.AboutDialog):
    def __init__(self, appname, title, parent):
        Gtk.AboutDialog.__init__(self, use_header_bar=True)
        self.set_program_name(title)
        self.set_transient_for(parent)
        self.set_logo_icon_name(appname)
        self.set_modal(True)

        self.set_authors([
            "Sean Davis (sgt-launcher)",
            "Simon Tatham (Simon Tatham's Portable Puzzle Collection)"
        ])
        self.set_copyright(
            "SGT Puzzles Collection (sgt-launcher)\n"
            "© 2016-2020 Sean Davis\n"
            "\n"
            "Simon Tatham's Portable Puzzle Collection\n"
            "© 2004-2012 Simon Tatham"
        )
        self.set_artists([
            "Pasi Lallinaho"
        ])
        self.set_website("https://github.com/bluesabre/sgt-launcher")
        self.set_license_type(Gtk.License.GPL_3_0)
        self.set_version(sgtlauncher_lib.get_version())

        # Cleanup duplicate buttons
        hbar = self.get_header_bar()
        for child in hbar.get_children():
            if type(child) in [Gtk.Button, Gtk.ToggleButton]:
                child.destroy()

        self.connect("response", self.on_response)

    def on_response(self, dialog, response):
        self.hide()
        self.destroy()


class MyApplication(Gtk.Application):
    APPNAME = "sgt-launcher"
    TITLE = _("SGT Puzzles Collection")
    GAMES = [
        'blackbox',
        'bridges',
        'cube',
        'dominosa',
        'fifteen',
        'filling',
        'flip',
        'flood',
        'galaxies',
        'guess',
        'inertia',
        'keen',
        'lightup',
        'loopy',
        'magnets',
        'map',
        'mines',
        'mosaic',
        'net',
        'netslide',
        'palisade',
        'pattern',
        'pearl',
        'pegs',
        'range',
        'rect',
        'samegame',
        'signpost',
        'singles',
        'sixteen',
        'slant',
        'solo',
        'tents',
        'towers',
        'tracks',
        'twiddle',
        'undead',
        'unequal',
        'unruly',
        'untangle'
    ]

    def __init__(self):
        Gtk.Application.__init__(self)

    def do_activate(self):
        launchers = self.get_launchers()
        self.win = MyWindow(self, self.APPNAME, launchers)
        self.win.show_all()

    def do_startup(self):
        Gtk.Application.do_startup(self)

        menu = Gio.Menu()
        menu.append(_("About"), "app.about")
        menu.append(_("Report a Bug..."), "app.bugreport")
        menu.append(_("Quit"), "app.quit")
        self.set_app_menu(menu)

        about_action = Gio.SimpleAction.new("about", None)
        about_action.connect("activate", self.about_cb)
        self.add_action(about_action)

        bug_action = Gio.SimpleAction.new("bugreport", None)
        bug_action.connect("activate", self.bugreport_cb)
        self.add_action(bug_action)

        quit_action = Gio.SimpleAction.new("quit", None)
        quit_action.connect("activate", self.quit_cb)
        self.add_action(quit_action)

    def about_cb(self, action, parameter):
        """Show the about dialog"""
        about = MyAboutDialog(self.APPNAME, self.TITLE, self.win)
        about.run()

    def bugreport_cb(self, action, parameter):
        """Take the user to the bug reporting platform"""
        uri = "https://github.com/bluesabre/sgt-launcher/issues"
        Gtk.show_uri_on_window(self.win, uri, Gdk.CURRENT_TIME)

    def quit_cb(self, action, parameter):
        """Exit application"""
        self.quit()

    def exists_in_path(self, binary):
        realpath = os.path.realpath(binary)
        if os.path.exists(realpath):
            return True
        paths = (os.environ.get("PATH")).split(":")
        paths.reverse()
        for path in paths:
            fullpath = os.path.join(path, binary)
            if (os.path.exists(fullpath)):
                return True
        return False

    def get_launchers(self):
        """Get localized launcher contents"""
        flags = GLib.KeyFileFlags.NONE
        prefixed = {}
        for game in self.GAMES:
            for prefix in ["sgt-", "puzzle-", ""]:
                if prefix not in prefixed.keys():
                    prefixed[prefix] = []
                launcher = "applications/%s%s.desktop" % (prefix, game)
                keyfile = GLib.KeyFile.new()
                try:
                    if (keyfile.load_from_data_dirs(launcher, flags)):
                        data = [
                            keyfile.get_value("Desktop Entry", "Name"),
                            keyfile.get_value("Desktop Entry", "Comment"),
                            keyfile.get_value("Desktop Entry", "Icon"),
                            keyfile.get_value("Desktop Entry", "Exec"),
                        ]
                        if self.exists_in_path(data[3]):
                            prefixed[prefix].append(data)
                    break
                except GLib.Error:
                    pass
        launchers = []
        for items in prefixed.values():
            if len(items) > len(launchers):
                launchers = items
        launchers.sort()
        return launchers
