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
from threading import Thread

from modules import functions
#from modules import clDB
from modules.clGstreamer010 import Track

class MyMenuItem(gtk.MenuItem):
    def __init__(self, rating):
        gtk.MenuItem.__init__(self)

#        # get and remove label
#        lbl = self.get_children()[0]
#        self.remove(lbl)

        img = gtk.Image()
        pix = gtk.gdk.pixbuf_new_from_file_at_size(os.path.join(functions.install_dir(), "plugins", "rating", "star%s.png" % rating), 16*rating, 16)
        img.set_from_pixbuf(pix)
        img.show()
        self.add(img)
        self.show_all()

class LabelImageMenuItem(gtk.MenuItem):
    def __init__(self, rating, track):
        gtk.MenuItem.__init__(self)

        hbox= gtk.HBox()
        hbox.show()

        lbl = gtk.Label()
        lbl.set_text("%s: %s" % (track.artist_name,track.name))
        lbl.show()

        img = gtk.Image()
        pix = gtk.gdk.pixbuf_new_from_file_at_size(os.path.join(functions.install_dir(), "plugins", "rating", "star%s.png" % rating), 16*rating, 16)
        img.set_from_pixbuf(pix)
        img.show()


        hbox.pack_start(img, False, True)
        hbox.pack_start(lbl, False, True)

        self.add(hbox)
        self.show_all()

class main():
    def __init__(self, pyjama):
        self.pyjama = pyjama

        self.pyjama.preferences.register_plugin("Rating", self.create_preferences, self.save_preferences)

        self.pyjama.Events.connect_event("alldone", self.ev_alldone)

        self.pyjama.Events.connect_event("populate_playlistmenu", self.ev_populate_playlistmenu)
        self.pyjama.Events.connect_event("populate_listmenu", self.ev_populate_listmenu)

        self.pyjama.Events.connect_event("playlist_tooltip",  self.ev_playlist_tooltip)

    def ev_playlist_tooltip(self, x, y, tooltip_boxes):
        vbox1, vbox2 = tooltip_boxes
        path = self.pyjama.window.tvPlaylist.get_path_at_pos(int(x), int(y))

        if path:
            track = self.pyjama.player.playlist[path[0][0]]

            rating = self.pyjama.settingsdb.get_value("rating_track", track.id, None)
            if rating is not None:
                label = gtk.Label()
                label.set_markup(_("<i>Rating:</i>"))
#                label.set_justify(gtk.JUSTIFY_LEFT)
                label.show()
                vbox1.pack_start(label, False, True)

                pix = gtk.gdk.pixbuf_new_from_file_at_size(os.path.join(functions.install_dir(), "plugins", "rating", "star%s.png" % rating), 16*rating, 16)

                img = gtk.Image()
                img.set_from_pixbuf(pix)
                img.show()
                vbox2.pack_start(img, False, True)


    def ev_populate_listmenu(self, rootmenu):
        selection = self.pyjama.window.tvList.get_selection()
        model, tmpIter = selection.get_selected()
        if tmpIter is None: return
        track = Track()
        path =  model.get_path(tmpIter)
        ret = self.pyjama.window.tvList.get_item(path)
        
        track.id = ret[self.pyjama.window.tvList.COLUMN_TRACKID]
        if track.id < 0: return


        mnu = gtk.ImageMenuItem(_("Rate track"))
        rootmenu.append(mnu)

        try:
            img = gtk.Image()
            pix = gtk.gdk.pixbuf_new_from_file_at_size(os.path.join(functions.install_dir(), "plugins", "rating", "rating.png"), 16, 16)
            img.set_from_pixbuf(pix)
            mnu.set_image(img)
        except:
            print ("Star image not found or corrupt")



        submenu = gtk.Menu()

        for rating in range(5,0,-1):
            tmp = MyMenuItem(rating)
            tmp.connect("activate", self.cb_rating, rating, track)
            submenu.append(tmp)
            tmp.show()

        mnu.set_submenu(submenu)
        submenu.show()
        mnu.show()

    def ev_populate_playlistmenu(self, rootmenu):
        model, tmpIter = self.pyjama.window.tvSelection.get_selected()
        if tmpIter is None: return
        path =  model.get_path(tmpIter)
        track = self.pyjama.player.playlist[path[0]]

        mnu = gtk.ImageMenuItem(_("Rate track"))
        rootmenu.append(mnu)

        try:
            img = gtk.Image()
            pix = gtk.gdk.pixbuf_new_from_file_at_size(os.path.join(functions.install_dir(), "plugins", "rating", "rating.png"), 16, 16)
            img.set_from_pixbuf(pix)
            mnu.set_image(img)
        except:
            print ("Star image not found or corrupt")



        submenu = gtk.Menu()

        for rating in range(5,0,-1):
            tmp = MyMenuItem(rating)
            tmp.connect("activate", self.cb_rating, rating, track)
            submenu.append(tmp)
            tmp.show()

        mnu.set_submenu(submenu)
        submenu.show()
        mnu.show()

    def cb_rating(self, widget, rating, track):
        self.pyjama.settingsdb.set_value("rating_track", track.id, rating)
        if self.pyjama.verbose:
            print ("rated track %i with %i stars" % (track.id,rating), track.name)


    def ev_alldone(self):
        menubar = self.pyjama.window.menubar

        entry = menubar.insert_entry(4, menubar.get_rootmenu("Extras"), _("Favorite Tracks"), "Favorite Tracks")
        menubar.set_item_image(entry, os.path.join(functions.install_dir(), "images", "star.png"))
#        entry.connect("enter-notify-event", self.cb_enter_notify_event)

        self.submenu = gtk.Menu()
        self.submenu.show()

        entry.set_submenu(self.submenu)

        menubar.append_entry(menubar.get_rootmenu("Extras"), "---", "favtracks_sep")

        self.load_data()
#        thr = Thread(target = self.load_data, args = ())
#        thr.start()

    def load_data(self):
        # only needed for threading
#        temp_db_settings_ressource = clDB.DB_Settings(self.pyjama)
#        temp_db_ressource = clDB.DB(self.pyjama)
        temp_db_settings_ressource = self.pyjama.settingsdb
        temp_db_ressource = self.pyjama.db

        sql = "SELECT option, value FROM settings WHERE section='rating_track' ORDER BY value DESC LIMIT %i" % int(self.pyjama.settings.get_value("rating", "tracks_to_show", 10))
        ret = temp_db_settings_ressource.query(sql)
#        temp_db_settings_ressource.close()
        if ret == [] or ret is None or ret == "": return

        tracklist = []
        ratinglist = []

        for item, rating in ret:
            tracklist.append( item )
            ratinglist.append( rating )

        ret = self.pyjama.db.get_multiple_trackinfos(tracklist)

        for child in self.submenu.get_children():
            self.submenu.remove(child)

        for track_id in tracklist:
            for track in ret:
                if track_id == track.id:
                    try:
                        pos = tracklist.index(track_id)
                        mnu = LabelImageMenuItem(ratinglist[pos], track)
                        self.submenu.append(mnu)
                        mnu.connect("activate", self.cb_mnu_activate, track)
                    except:
                        print ("Error - rated track wasn't found in the database")


    def cb_mnu_activate(self, widget, track):
        self.pyjama.add2playlist(track)

    def create_preferences(self):
        vbox = gtk.VBox()

        hbox = gtk.HBox()
        vbox.pack_start(hbox, False, True, 10)
        hbox.show()

        hbox2 = gtk.HBox()
        vbox.pack_start(hbox2, False, True, 10)
        hbox2.show()

        ## Tracks to show
        lblTracks = gtk.Label()
        lblTracks.set_markup(_("Number of Tracks to show"))
        lblTracks.set_line_wrap(True)
        lblTracks.set_single_line_mode(False)
        lblTracks.show()
        hbox.pack_start(lblTracks, False, True, 10)

        self.spin1 = gtk.SpinButton()
        self.spin1.set_range(0,100)
        self.spin1.set_increments(1,10)
        self.spin1.set_value(self.pyjama.settings.get_value("rating", "tracks_to_show", 10, float))
        hbox.pack_end(self.spin1, False, True)
        
        
        vbox.show_all()
        return vbox

    def save_preferences(self):
        self.pyjama.settings.set_value("rating", "tracks_to_show", self.spin1.get_value(), int)
        self.load_data()
