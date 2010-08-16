#!/usr/bin/env python
# -*- coding: utf-8 -*-

# ----------------------------------------------------------------------------
# pyjama - python jamendo audioplayer
# Copyright (c) 2009 Daniel Nögel
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, version 3 of the License.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
# ----------------------------------------------------------------------------


# This script was inspired by Chris Brown's gnome-media-keys script for amarok

import gobject
import os, sys

try:
    import dbus
    from dbus import glib
except Exception, inst:
    print "python-dbus and libdbus-glib needed for mmhotkeys"
    raise 

#
# Checks
#

# Check if Gnome Settings Daemon is running:
ret = os.popen("ps -C gnome-settings-daemon|grep settings").read()
if ret == "":
    print "gnome-settings-daemon not running"
    raise(ImportError, "gnome-settings-daemon not running")

# Gnome Version for dbus selection
VERSION = os.popen('LANG=C gnome-about --gnome-version|grep Version|cut -d \" \" -f 2').read()
if VERSION == "": VERSION = "2.18"

class main():
    def __init__(self, pyjama):
        self.pyjama = pyjama

        bus = dbus.SessionBus()
        # Connect to signal:
        if VERSION > "2.20":
            try:
                object = bus.get_object("org.gnome.SettingsDaemon", "/org/gnome/SettingsDaemon/MediaKeys")
                object.connect_to_signal("MediaPlayerKeyPressed", self.ev_key_pressed, dbus_interface='org.gnome.SettingsDaemon.MediaKeys')
            except:
                print "Error connecting to SettingsDaemon."
                raise
        else:
            try:
                object = bus.get_object("org.gnome.SettingsDaemon", "/org/gnome/SettingsDaemon")
                object.connect_to_signal("MediaPlayerKeyPressed", self.ev_key_pressed, dbus_interface="org.gnome.SettingsDaemon")
            except:
                print "Error connecting to SettingsDaemon."
                raise

    def ev_key_pressed(self, *keys):
        for key in keys:
            if key == "Play":
                self.pyjama.window.on_bPlay_clicked(None)
            elif key == "Pause":
                self.pyjama.window.on_bPlay_clicked(None)
            elif key == "Stop":
                self.pyjama.window.on_bStop_clicked(None)
            elif key == "Next":
                self.pyjama.window.on_bNext_clicked(None)
            elif key == "Previous":
                self.pyjama.window.on_bPrev_clicked(None)


