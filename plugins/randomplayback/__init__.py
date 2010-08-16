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

#http://api.jamendo.com/get2/id/track/jsonpretty/?n=100&order=ratingweek_desc

import gtk
import gobject
from modules import functions
import os

from modules import clWidgets

from threading import Thread
from time import sleep

from random import random

class NumCombo(gtk.ComboBox):
    def __init__(self, num):
        liststore = gtk.ListStore(gobject.TYPE_STRING)
        gtk.ComboBox.__init__(self, liststore)
        cell = gtk.CellRendererText()

        self.pack_start(cell, True)
        self.add_attribute(cell, 'text', 0)
        
        self.modelist = num
        for mode in self.modelist:
            self.append_text(str(mode))
        self.set_active(0)
        
    def set_item(self, mode):
        self.set_active(self.modelist.index(mode))

class SelectCriteriaDialog(gtk.Dialog):
    def __init__(self, pyjama):
        self.pyjama = pyjama
        gtk.Dialog.__init__(self)

        self.set_modal(True)
        self.set_resizable(False)

        hbox = gtk.HBox()
        self.vbox.pack_start(hbox, False, True)
        hbox.show()

        l = gtk.Label("Get")
        hbox.pack_start(l, False, True)
        l.show()

        self.num = NumCombo([10,20,30,40,50,60,70,80,90])
        self.num.set_tooltip_text(_("Number of songs to add to the playlist"))
        hbox.pack_start(self.num, False, True)
        self.num.show()

        l = gtk.Label("random songs out of")
        hbox.pack_start(l, False, True)
        l.show()

        self.outof = NumCombo([100,200,300,400,500,600,700,800,900,1000])
        self.outof.set_tooltip_text(_("From how many songs do you want to pick these random songs?\nThe higher this value is, the more 'random' is the result."))
        hbox.pack_start(self.outof, False, True)
        self.outof.connect("changed", self.cb_changed)
        self.outof.show()

        l = gtk.Label("songs. ")
        hbox.pack_start(l, False, True)
        l.show()

        hbox = gtk.HBox()
        self.vbox.pack_start(hbox, False, True)
        hbox.show()

        l = gtk.Label("Sort this")
        hbox.pack_start(l, False, True)
        l.show()

        self.lnum = gtk.Label(" 100 ")
        hbox.pack_start(self.lnum, False, True)
        self.lnum.show()

        l = gtk.Label("songs by")
        hbox.pack_start(l, False, True)
        l.show()

        self.order = clWidgets.OrderCombo()
        self.order.set_tooltip_text(_("From which list should the songs be taken?."))
        hbox.pack_start(self.order, False, True)
        self.order.show()

        l = gtk.Label("and the tag")
        hbox.pack_start(l, False, True)
        l.show()

        self.tags = clWidgets.TagsCombo(self.pyjama)
        self.tags.set_tooltip_text(_("Tag you want to select random songs from."))
        hbox.pack_start(self.tags, False, True)
        self.tags.show()

        self.add_button(gtk.STOCK_OK, gtk.RESPONSE_OK)

    def cb_changed(self, widget):
        if widget is self.outof:
            self.lnum.set_markup(" %s " % self.pyjama.window.get_active_text(self.outof))
#        elif widget is self.tags:
#            self.num.set_markup(" %s " % widget.entry.get_text())
class main():
    def __init__(self, pyjama):
        self.pyjama = pyjama

        self.pyjama.Events.connect_event("alldone", self.ev_alldone)
        self.pyjama.Events.connect_event("nowplaying", self.ev_nowplaying)

        self.genre = _("--all--")
        self.num_of_songs_to_add = 10
        self.num_of_songs_to_select_from = 100
        self.order_by = "ratingweek"
        self.direction = "desc"

        self.autofill = False

        self.number_of_songs_to_select_from_database = 10

    def ev_nowplaying(self, track):
        if self.autofill:
            if track.position_in_playlist > -1 and track.position_in_playlist >= len(self.pyjama.player.playlist)-3:
                self.auto_fill_playlist()

    def ev_alldone(self):
        menu = self.pyjama.window.menubar

#        entry = menu.append_entry(menu.get_rootmenu("Extras"), "---", "jamlists-sep")

        entry = menu.insert_entry(3, menu.get_rootmenu("Extras"), _("Random Playback"), "jamlists")

#        menu.set_item_image(entry, os.path.join(functions.install_dir(), "images", "playlist.png"))

        submenu = gtk.Menu()
        entry.set_submenu(submenu)
        submenu.show()

        ### Random Songs from database
        randdb = gtk.ImageMenuItem(_("Append %i random songs" % self.num_of_songs_to_add))
        randdb.connect("activate", self.cb_menuactivate, "randdb")
        randdb.show()
        submenu.append(randdb)

        ### random songs with certain criteria
        rand = gtk.ImageMenuItem(_("Append %i random songs by criteria" % self.num_of_songs_to_add))
        rand.connect("activate", self.cb_menuactivate, "rand")
        rand.show()
        submenu.append(rand)

        ### auto fill playlist with random songs
        self.autorand = gtk.CheckMenuItem(_("Auto fill playlist"))#self.num_of_songs_to_add))
        self.autorand.connect("activate", self.cb_menuactivate, "autorand")
        self.autorand.show()
        submenu.append(self.autorand)

        self.accel_group = gtk.AccelGroup()
        self.autorand.add_accelerator("activate", self.accel_group, ord("a"), gtk.gdk.MOD1_MASK, gtk.ACCEL_VISIBLE)
        self.pyjama.window.add_accel_group(self.accel_group)

#        ### Top Playlists
#        self.toplists = gtk.ImageMenuItem(_("Best rated Playlists"))
#        self.toplists.show()
#        submenu.append(self.toplists)

#        self.toplists_submenu = gtk.Menu()
#        self.toplists_submenu.show()
#        self.toplists.set_submenu(self.toplists_submenu)

#        ### Playlists powered by Jamendo
#        self.jamlists = gtk.ImageMenuItem(_("Official Jamendo Playlists"))
#        self.jamlists.show()
#        submenu.append(self.jamlists)



#        # Get top playlists in a new thread
#        thr = Thread(target = self.load_playlists, args = ())
#        thr.start()

    def cb_menuactivate(self, widget, user_param, id=None):
        if user_param == "rand":
            dia = SelectCriteriaDialog(self.pyjama)
            dia.set_title("Add random songs")
            result = dia.run()
            dia.destroy()

            if result != gtk.RESPONSE_OK:
                return None

            outof = self.pyjama.window.get_active_text(dia.outof)
            num = self.pyjama.window.get_active_text(dia.num)
            order = self.pyjama.window.get_active_text(dia.order)
            tag = dia.tags.entry.get_text()

            self.genre = tag
            self.num_of_songs_to_add = int(num)
            self.num_of_songs_to_select_from = int(outof)
            self.order_by = order

            if self.genre == _("--all--"):
                query = "id/track/json/?nshuffle=%i&order=%s_%s" % (self.num_of_songs_to_select_from, self.order_by, self.direction)
                if self.pyjama.verbose:
                    print("Getting %i tracks ordered by %s_%s - genre is %s." % (self.num_of_songs_to_select_from, self.order_by, self.direction, self.genre))
            else:
                query = "id/track/json/?nshuffle=%i&order=%s_%s&tag_idstr=%s" % (self.num_of_songs_to_select_from, self.order_by, self.direction, self.genre)
                if self.pyjama.verbose:
                    print("Getting %i tracks ordered by %s_%s - genre is %s." % (self.num_of_songs_to_select_from, self.order_by, self.direction, self.genre))
            self.pyjama.jamendo.set_ignore_cache(True)
            ret = self.pyjama.jamendo.query(query, self.pyjama.settings.get_value("JAMENDO", "CACHING_TIME_SHORT"), raise_query_event=False)
            self.pyjama.jamendo.set_ignore_cache(False)
            if self.pyjama.jamendo.check(ret):
                random_list = self.shuffle_list(ret)
                random_list = random_list[0:self.num_of_songs_to_add]
                retdb = self.pyjama.db.get_multiple_trackinfos(random_list)
                if retdb is not None and retdb != []:
                    retdb = self.shuffle_list(retdb)
                    for track in retdb:
                        self.pyjama.add2playlist(track)
            else:
                print ("There was an error creating the random playlist")
        elif user_param == "randdb":
            retdb = self.get_random_tracks \
                (self.number_of_songs_to_select_from_database)
            if retdb is not None and retdb != []:
                for track in retdb:
                    self.pyjama.add2playlist(track)
        elif user_param == "autorand":
            if widget.get_active():
                self.autofill = True
                dia = SelectCriteriaDialog(self.pyjama)
                dia.set_title("Configure random autofill")
                dia.outof.set_item(1000)
                result = dia.run()
                dia.destroy()

                if result != gtk.RESPONSE_OK:
                    return None


                outof = self.pyjama.window.get_active_text(dia.outof)
                num = self.pyjama.window.get_active_text(dia.num)
                order = self.pyjama.window.get_active_text(dia.order)
                tag = dia.tags.entry.get_text()

                self.genre = tag
                self.num_of_songs_to_add = int(num)
                self.num_of_songs_to_select_from = int(outof)
                self.order_by = order

                self.auto_fill_playlist()
                self.pyjama.notification("Random autofill on", "Now will fill the playlist automatically with random songs when it runs out of songs.")
            else:
                self.autofill = False
                self.pyjama.notification("Random autofill off", "Will no longer fill the playlist with random songs")

    def auto_fill_playlist(self):
        if self.genre == _("--all--"):
            query = "id/track/json/?nshuffle=%i&order=%s_%s" % (self.num_of_songs_to_select_from, self.order_by, self.direction)
            if self.pyjama.verbose:
                print("Getting %i tracks ordered by %s_%s - genre is %s." % (self.num_of_songs_to_select_from, self.order_by, self.direction, self.genre))
        else:
            query = "id/track/json/?nshuffle=%i&order=%s_%s&tag_idstr=%s" % (self.num_of_songs_to_select_from, self.order_by, self.direction, self.genre)
            if self.pyjama.verbose:
                print("Getting %i tracks ordered by %s_%s - genre is %s." % (self.num_of_songs_to_select_from, self.order_by, self.direction, self.genre))
        self.pyjama.jamendo.set_ignore_cache(True)
        ret = self.pyjama.jamendo.query(query, self.pyjama.settings.get_value("JAMENDO", "CACHING_TIME_SHORT"), raise_query_event=False)
        self.pyjama.jamendo.set_ignore_cache(False)
        if self.pyjama.jamendo.check(ret):
            random_list = self.shuffle_list(ret)
            random_list = random_list[0:self.num_of_songs_to_add]
            retdb = self.pyjama.db.get_multiple_trackinfos(random_list)
            if retdb is not None and retdb != []:
                retdb = self.shuffle_list(retdb)
                for track in retdb:
                    self.pyjama.add2playlist(track)
        else:
            print ("There was an error filling the playlist with random songs")

#    def shuffle_track_dict(self, trackdict):
#        shuffle = {}
#        for i in range(0,len(trackdict)):
#            pos = int(random()*len(trackdict))
#            shuffle[i]=trackdict[pos]
#            i+=1
#        return shuffle

    def shuffle_list(self, list2shuffle):
        return list2shuffle

        shuffle = []
        while len(list2shuffle):
            pos = int(random()*len(list2shuffle))
            shuffle.append(list2shuffle[pos])
            list2shuffle[pos] = list2shuffle[-1]
            list2shuffle.pop()



        return shuffle

    ## Get trackinfos for random tracks
    # @return dictionary
    # @param self The Object pointer
    # @param num Number of tracks to get
    def get_random_tracks(self, num):
        sql = """
            SELECT
                tracks.id
            FROM
                tracks
            ORDER BY Random()
            LIMIT %i
            """  % num
        ret = self.pyjama.db.query(sql)
        return self.pyjama.db.get_multiple_trackinfos(ret)

        

