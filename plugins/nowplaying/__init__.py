#!/usr/bin/env python
# -*- coding: utf-8 -*-

# ----------------------------------------------------------------------------
# pyjama - python jamendo audioplayer
# Copyright (c) 2008 Daniel Nögel
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

import gtk
import os

class main():
    def __init__(self, pyjama):
        self.pyjama = pyjama
        ev = self.pyjama.Events
#        ev.nowplaying += self.notification
        ev.connect_event("nowplaying", self.notification)

        self.pyjama.preferences.register_plugin("Nowplaying", self.register_preferences, self.save_preferences)
        
#    def notification(self, artist, album, track, icon, size = None):
    def notification(self, track):
        icon = self.pyjama.get_album_image(track.album_id)
        size = self.pyjama.settings.get_value("PYJAMA", 'notification_cover_size')

        artist = track.artist_name
        album = track.album_name
        track = track.name

#        if "listenstats" in self.pyjama.plugins.loaded:
#            print "listenstats"

        self.pyjama.icon.show_notification(caption  =_("Now playing"), text = "<b><i>%s</i></b>:\n%s" % (artist, track), img = icon, size = size)

        #
        # Script
        #
        script = self.pyjama.settings.get_value("NOWPLAYING", 'EXECUTE', "")
        if script != "":
            try:
                os.system("%s \"%s\" \"%s\" \"%s\"" % (script, artist.replace("\"", "\\\""), album.replace("\"", "\\\""), track.replace("\"", "\\\"")))
#                print("nowplaying: %s executed" % script)
            except:
                print ("An error occured while executing %s" % script)

    def register_preferences(self):
        script = self.pyjama.settings.get_value("NOWPLAYING", 'EXECUTE', "")
        vbox = gtk.VBox()

        hbox = gtk.HBox()
        self.entry = gtk.Entry()
        self.entry.set_text(script)
        self.entry.show()
        lbl = gtk.Label("Script to execute")
        lbl.show()
        tt = """Pyjama will execute this script any time a new song is played and pass some song infos to it. 
Please make that script executable or enter a command like <b>sh /home/USER/my_script.sh</b>.

Pyjama will pass the artist as first, the album as second and the track as third param to the script.
"""
        lbl.set_tooltip_markup(tt)
        self.entry.set_tooltip_markup(tt)

        hbox.pack_start(lbl, False, True, 10)
        hbox.pack_end(self.entry, True, True, 10)

        vbox.pack_start(hbox, False, True, 10)
        
        vbox.show_all()
        return vbox

    def save_preferences(self):
        self.pyjama.settings.set_value("NOWPLAYING", 'EXECUTE', self.entry.get_text(), str)


        
