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

__all__ = [
    'project_path_not_found',
    'get_data_file',
    'get_data_path',
]

# Where your project will look for your data (for instance, images and ui
# files). By default, this is ../data, relative your trunk layout
__sgtlauncher_data_directory__ = '../data/'
__license__ = 'GPL-3+'
__version__ = '0.2.3'

import os


class project_path_not_found(Exception):
    """Raised when we can't find the project directory."""


def get_data_file(*path_segments):
    """Get the full path to a data file.

    Returns the path to a file underneath the data directory (as defined by
    `get_data_path`). Equivalent to os.path.join(get_data_path(),
    *path_segments).
    """
    return os.path.join(get_data_path(), *path_segments)


def get_data_path():
    """Retrieve sgt-launcher data path

    This path is by default <sgtlauncher_lib_path>/../data/ in trunk
    and /usr/share/sgtlauncher in an installed version but this path
    is specified at installation time.
    """
    if __sgtlauncher_data_directory__ == '../data/':
        path = os.path.join(
            os.path.dirname(__file__), __sgtlauncher_data_directory__)
        abs_data_path = os.path.abspath(path)
    else:
        abs_data_path = os.path.abspath(__sgtlauncher_data_directory__)
    if not os.path.exists(abs_data_path):
        print(abs_data_path)
        raise project_path_not_found

    return abs_data_path


def get_version():
    """Retrieve the program version."""
    return __version__
