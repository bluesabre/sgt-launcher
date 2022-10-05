#!/usr/bin/python3
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
import sys
import subprocess

from gi.repository import GLib

try:
    import DistUtilsExtra.auto
except ImportError:
    sys.stderr.write("To build sgt-launcher you need "
                     "https://launchpad.net/python-distutils-extra\n")
    sys.exit(1)
assert DistUtilsExtra.auto.__version__ >= '2.18', \
    'needs DistUtilsExtra.auto >= 2.18'


def build_launchers():
    applications_dir = "build/applications/"
    if not os.path.exists(applications_dir):
        os.makedirs(applications_dir)

    if '--build-launchers' in sys.argv:
        print("building launchers")
        games = [
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
        flags = GLib.KeyFileFlags.KEEP_TRANSLATIONS
        for game in games:
            for prefix in ["sgt", "puzzle"]:
                desktop = "%s-%s.desktop" % (prefix, game)
                launcher = "applications/%s" % desktop
                keyfile = GLib.KeyFile.new()
                try:
                    if (keyfile.load_from_data_dirs(launcher, flags)):
                        keyfile.set_value("Desktop Entry", "NoDisplay", "true")
                        keyfile.save_to_file("%s%s" % (applications_dir,
                                                       desktop))
                    break
                except GLib.Error:
                    pass

        sys.argv.remove("--build-launchers")


def update_config(libdir, values={}):
    """Update the configuration file at installation time."""
    filename = os.path.join(libdir, 'sgtlauncher_lib', 'sgtlauncherconfig.py')
    oldvalues = {}
    try:
        fin = open(filename, 'r', encoding='utf-8')
        fout = open(filename + '.new', 'w', encoding='utf-8')

        for line in fin:
            fields = line.split(' = ')  # Separate variable from value
            if fields[0] in values:
                oldvalues[fields[0]] = fields[1].strip()
                line = "%s = %s\n" % (fields[0], values[fields[0]])
            fout.write(line)

        fout.flush()
        fout.close()
        fin.close()
        os.rename(fout.name, fin.name)
    except (OSError, IOError):
        print(("ERROR: Can't find %s" % filename))
        sys.exit(1)
    return oldvalues


def move_icon_file(root, target_data, prefix):
    """Move the icon files to their installation prefix."""
    old_icon_path = os.path.normpath(
        os.path.join(root, target_data, 'share', 'sgt-launcher', 'media'))
    for icon_size in ['scalable', 'pixmap']:
        # Install sgt-launcher.png to share/pixmaps
        if icon_size == 'pixmap':
            old_icon_file = os.path.join(old_icon_path, 'sgt-launcher.png')
            icon_path = os.path.normpath(
                os.path.join(root, target_data, 'share', 'pixmaps'))
            icon_file = os.path.join(icon_path, 'sgt-launcher.png')
        # Install everything else to share/icons/hicolor
        else:
            old_icon_file = os.path.join(old_icon_path, 'sgt-launcher.svg')
            icon_path = os.path.normpath(
                os.path.join(root, target_data, 'share', 'icons',
                             'hicolor', icon_size, 'apps'))
            icon_file = os.path.join(icon_path, 'sgt-launcher.svg')

        # Get the real paths.
        old_icon_file = os.path.realpath(old_icon_file)
        icon_file = os.path.realpath(icon_file)

        if not os.path.exists(old_icon_file):
            print(("ERROR: Can't find", old_icon_file))
            sys.exit(1)
        if not os.path.exists(icon_path):
            os.makedirs(icon_path)
        if old_icon_file != icon_file:
            print(("Moving icon file: %s -> %s" % (old_icon_file, icon_file)))
            os.rename(old_icon_file, icon_file)

    # Media is now empty
    if len(os.listdir(old_icon_path)) == 0:
        print(("Removing empty directory: %s" % old_icon_path))
        os.rmdir(old_icon_path)

    return icon_file


def get_desktop_file(root, target_data, prefix):
    """Move the desktop file to its installation prefix."""
    desktop_path = os.path.realpath(
        os.path.join(root, target_data, 'share', 'applications'))
    desktop_file = os.path.join(
        desktop_path, 'org.bluesabre.SgtLauncher.desktop')
    return desktop_file


def update_desktop_file(filename, script_path):
    """Update the desktop file with prefixed paths."""
    try:
        fin = open(filename, 'r', encoding='utf-8')
        fout = open(filename + '.new', 'w', encoding='utf-8')

        for line in fin:
            if 'Exec=' in line:
                cmd = line.split("=")[1].split(None, 1)
                line = "Exec=%s" % os.path.join(script_path, 'sgt-launcher')
                if len(cmd) > 1:
                    line += " %s" % cmd[1].strip()  # Add script arguments back
                line += "\n"
            fout.write(line)
        fout.flush()
        fout.close()
        fin.close()
        os.rename(fout.name, fin.name)
    except (OSError, IOError):
        print(("ERROR: Can't find %s" % filename))
        sys.exit(1)


def write_metainfo_file(filename_in):
    filename_out = filename_in.rstrip('.in')
    cmd = ["intltool-merge", "-x", "-d", "po", filename_in, filename_out]
    print(" ".join(cmd))
    subprocess.call(cmd, shell=False)


def remove_metainfo_in(root, target_data):
    metainfo_directory = os.path.normpath(
        os.path.join(root, target_data, 'share', 'sgt-launcher',
                     'metainfo'))
    if not os.path.exists(metainfo_directory):
        return

    metainfo_in = os.path.join(metainfo_directory,
                               "sgt-launcher.appdata.xml.in")
    if os.path.exists(metainfo_in):
        os.remove(metainfo_in)

    if len(os.listdir(metainfo_directory)) == 0:
        print(("Removing empty directory: %s" % metainfo_directory))
        os.rmdir(metainfo_directory)


# Update AppData with latest translations first.
write_metainfo_file("data/metainfo/sgt-launcher.appdata.xml.in")

# Build the replacement launchers
build_launchers()


class InstallAndUpdateDataDirectory(DistUtilsExtra.auto.install_auto):
    """Command Class to install and update the directory."""

    def run(self):
        """Run the setup commands."""
        DistUtilsExtra.auto.install_auto.run(self)

        print(("=== Installing %s, version %s ===" %
               (self.distribution.get_name(),
                self.distribution.get_version())))

        if not self.prefix:
            self.prefix = ''

        if self.root:
            target_data = os.path.relpath(self.install_data, self.root) + \
                os.sep
            target_pkgdata = os.path.join(target_data, 'share', 'sgt-launcher',
                                          '')
            target_scripts = os.path.join(target_data, 'games')

            data_dir = os.path.join(self.prefix, 'share', 'sgt-launcher', '')
            script_path = os.path.join(self.prefix, 'games')
        else:
            # --user install
            self.root = ''
            target_data = os.path.relpath(self.install_data) + os.sep
            target_pkgdata = os.path.join(target_data, 'share', 'sgt-launcher',
                                          '')
            target_scripts = os.path.join(target_data, 'games')

            # Use absolute paths
            target_data = os.path.realpath(target_data)
            target_pkgdata = os.path.realpath(target_pkgdata)
            target_scripts = os.path.realpath(target_scripts)

            data_dir = target_pkgdata
            script_path = target_scripts

        print(("Root: %s" % self.root))
        print(("Prefix: %s\n" % self.prefix))

        print(("Target Data:    %s" % target_data))
        print(("Target PkgData: %s" % target_pkgdata))
        print(("Target Scripts: %s\n" % target_scripts))
        print(("Data Directory: %s" % data_dir))

        values = {'__sgtlauncher_data_directory__': "'%s'" % (data_dir),
                  '__version__': "'%s'" % self.distribution.get_version()}
        update_config(self.install_lib, values)

        desktop_file = get_desktop_file(self.root, target_data, self.prefix)
        print(("Desktop File: %s\n" % desktop_file))
        move_icon_file(self.root, target_data, self.prefix)
        update_desktop_file(desktop_file, script_path)
        remove_metainfo_in(self.root, target_data)


DistUtilsExtra.auto.setup(
    name='sgt-launcher',
    version='0.2.8',
    license='GPL-3+',
    author='Sean Davis',
    author_email='sean@bluesabre.org',
    description='Launcher for Simon Tatham\'s Portable Puzzle Collection',
    long_description='A collection of logic games written by Simon Tatham. '
                     'This application wraps the games into an all-in-one '
                     'launcher and game suite.',
    url='https://github.com/bluesabre/sgt-launcher',
    data_files=[
        ('games', ['bin/sgt-launcher']),
        ('share/doc/sgt-launcher', ['CHANGELOG.md']),
        ('share/man/man1', ['sgt-launcher.1']),
        ('share/metainfo', ['data/metainfo/sgt-launcher.appdata.xml'])
    ],
    cmdclass={'install': InstallAndUpdateDataDirectory}
)
