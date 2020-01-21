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

import optparse
import sys

from locale import gettext as _

from sgtlauncher import SgtLauncher

from sgtlauncher_lib import set_up_logging, get_version


def parse_options():
    """Support for command line options"""
    parser = optparse.OptionParser(version="%%prog %s" % get_version())
    parser.add_option(
        "-v", "--verbose", action="count", dest="verbose",
        help=_("Show debug messages"))
    (options, args) = parser.parse_args()

    set_up_logging(options)


def main():
    """Main application for SGT Puzzles Collection"""
    parse_options()

    # Run the application.
    app = SgtLauncher.MyApplication()
    try:
        exit_status = app.run(None)
    except KeyboardInterrupt:
        exit_status = 130
    sys.exit(exit_status)
