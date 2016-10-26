#!/usr/bin/python

import os
import sys
import site

from setuptools import setup, find_packages
from setuptools.command.install import install as _install


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


def get_data_files():
    translations = get_translations()

    my_data_files = [
        ('share/icons/hicolor/scalable/apps/',
            ['sgtlauncher/data/icons/scalable/sgt-launcher.svg']),
        ('share/icons/hicolor/16x16/apps/',
            ['sgtlauncher/data/icons/16x16/sgt-launcher.png']),
        ('share/icons/hicolor/24x24/apps/',
            ['sgtlauncher/data/icons/24x24/sgt-launcher.png']),
        ('share/icons/hicolor/32x32/apps/',
            ['sgtlauncher/data/icons/32x32/sgt-launcher.png']),
        ('share/icons/hicolor/48x48/apps/',
            ['sgtlauncher/data/icons/48x48/sgt-launcher.png']),
        ('share/icons/hicolor/64x64/apps/',
            ['sgtlauncher/data/icons/64x64/sgt-launcher.png']),
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