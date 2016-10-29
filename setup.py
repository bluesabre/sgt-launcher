#!/usr/bin/python

import os
import sys
import site

from setuptools import setup, find_packages
from setuptools.command.install import install as _install

from gi.repository import GLib


print(str(sys.argv))


def get_installation_prefix(install_dir):
    py_version = '%s.%s' % (sys.version_info[0], sys.version_info[1])
    if '--user' in sys.argv:
        path = site.getusersitepackages()
        prefix = path.split("/lib/python%s/site-packages" % py_version)[0]
        if (os.path.exists(prefix)):
            return prefix
    else:
        for directory in ["dist-packages", "site-packages"]:
            py_dir = "/lib/python%s/%s" % (py_version, directory)
            if py_dir in install_dir:
                prefix = install_dir.split(py_dir)[0]
                if os.path.exists(prefix):
                    return prefix
    return ""


def _post_install(install_dir):
    prefix = get_installation_prefix(install_dir)
    print("compiling schemas")
    os.system('glib-compile-schemas %s/share/glib-2.0/schemas' % prefix)
    print("updating icon cache")
    os.system('gtk-update-icon-cache -f -t %s/share/icons/hicolor/' % prefix)


def get_translations():
    appname = "sgt-launcher"
    files = []
    for filename in os.listdir("po"):
        if filename.endswith(".po"):
            lang = filename[:-3]

            build_dir = os.path.join("po", "build", lang)
            install_dir = "share/locale/%s/LC_MESSAGES/" % lang
            po_filename = os.path.join("po", filename)
            mo_filename = os.path.join(build_dir, "%s.mo" % appname)

            if not os.path.exists(build_dir):
                os.makedirs(build_dir)

            os.system("msgfmt -o %s %s" % (mo_filename, po_filename))
            files.append((install_dir, [mo_filename]))

    # Convert desktop file
    desktop_in = "sgt-launcher.desktop.in"
    desktop_out = "sgt-launcher.desktop"
    os.system("intltool-merge -d po %s %s" % (desktop_in, desktop_out))

    return files


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
            'galaxies',
            'guess',
            'inertia',
            'keen',
            'lightup',
            'loopy',
            'magnets',
            'map',
            'mines',
            'net',
            'netslide',
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


def get_data_files():
    translations = get_translations()
    build_launchers()

    my_data_files = [
        ('share/icons/hicolor/scalable/apps/',
            ['sgtlauncher/data/icons/scalable/sgt-launcher.svg']),
        ('share/applications/',
            ['sgt-launcher.desktop']),
        ('share/glib-2.0/schemas/',
            ['sgt-launcher.gschema.xml']),
        ] + translations
    return my_data_files


class install(_install):
    def run(self):
        _install.run(self)
        self.execute(_post_install, (self.install_lib,),
                     msg="Running post install task")


setup(
    name="sgtlauncher",
    version="0.1",
    author="Sean Davis",
    author_email="bluesabre@ubuntu.com",
    description="Launcher for Simon Tatham's Portable Puzzle Collection",
    license="GPL3",
    keywords="game,puzzle,gtk,gnome",
    url="launchpad.net",
    cmdclass={'install': install},
    scripts=['sgtlauncher/sgt-launcher'],
    data_files=get_data_files(),
    packages=find_packages(),
)
