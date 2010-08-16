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

from modules import functions
from modules.clGstreamer010 import Track

class main():
    def __init__(self, pyjama):
        self.pyjama = pyjama

        self.pyjama.Events.connect_event("populate_playlistmenu", self.ev_populate_playlistmenu)
        self.pyjama.Events.connect_event("populate_listmenu", self.ev_populate_listmenu)

        self.pyjama.Events.connect_event("alldone", self.ev_alldone)

    def ev_alldone(self):
        self.pyjama.layouts.register_layout("lyrics", LyricsLayout(self.pyjama))

    def ev_populate_listmenu(self, rootmenu):
        selection = self.pyjama.window.tvList.get_selection()
        model, tmpIter = selection.get_selected()
        if tmpIter is None: return

        path =  model.get_path(tmpIter)
        ret = self.pyjama.window.tvList.get_item(path)
        track = Track()
        track.id = ret[self.pyjama.window.tvList.COLUMN_TRACKID]
        if track.id < 0: return

        url = "track/id/track/data/json/%s?tri=lyrics_text" % track.id
        ret = self.pyjama.jamendo.queryold( url, raise_query_event=False )
        txt = ret[0]['lyrics_text']
        if txt is None: txt = ""

        mnu = gtk.ImageMenuItem(_("Show Lyrics"))
        rootmenu.append(mnu)

        try:
            img = gtk.Image()
            pix = gtk.gdk.pixbuf_new_from_file_at_size(os.path.join(functions.install_dir(), "plugins", "lyrics", "lyrics.png"), 16, 16)
            img.set_from_pixbuf(pix)
            mnu.set_image(img)
        except:
            print ("Image not found or corrupt")

        mnu.show()
        mnu.connect("activate", self.cb_show_lyrics_activate, txt, track.id)
        if len(txt) < 10: mnu.set_sensitive(False)


    def ev_populate_playlistmenu(self, rootmenu):
        model, tmpIter = self.pyjama.window.tvSelection.get_selected()
        if tmpIter is None: return
        path =  model.get_path(tmpIter)
        track = self.pyjama.player.playlist[path[0]]

        url = "track/id/track/data/json/%s?tri=lyrics_text" % track.id
        ret = self.pyjama.jamendo.queryold( url, raise_query_event=False )
        if ret is None: 
            txt = ""
            ex = False
        else:    
            txt = ret[0]['lyrics_text']
            if txt is None: txt = ""
            ex = ret[0]['lyrics_exists']

        mnu = gtk.ImageMenuItem(_("Show Lyrics"))
        rootmenu.append(mnu)

        try:
            img = gtk.Image()
            pix = gtk.gdk.pixbuf_new_from_file_at_size(os.path.join(functions.install_dir(), "plugins", "lyrics", "lyrics.png"), 16, 16)
            img.set_from_pixbuf(pix)
            mnu.set_image(img)
        except:
            print ("Image not found or corrupt")

        mnu.show()
        mnu.connect("activate", self.cb_show_lyrics_activate, txt, track.id)
        if len(txt) < 10: mnu.set_sensitive(False)

    def cb_show_lyrics_activate(self, widget, lyrics, track):
        self.pyjama.layouts.show_layout("lyrics", lyrics, track)

class LyricsLayout(gtk.Layout):
    def __init__(self, pyjama):
        self.pyjama = pyjama
        
        gtk.Layout.__init__(self)
        self.set_size(700,300)

#        sw = gtk.ScrolledWindow()
#        sw.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
#        tv = gtk.TextView()
#        sw.add(tv)
#        sw.show()
#        tv.show()
#        tv.set_size_request(700,300)
#        tv.set_wrap_mode(gtk.WRAP_WORD)
#        self.buffer = tv.get_buffer()
#        self.put(sw, 10, 10)

        self.lbl = gtk.Label()
        self.lbl.set_line_wrap(True)
        self.put(self.lbl, 10, 5)
        self.lbl.show()

#        try:
#            img = gtk.Image()
#            pix = gtk.gdk.pixbuf_new_from_file_at_size(os.path.join(functions.install_dir(), "plugins", "lyrics", "lyrics.png"), 100, 40)
#            img.set_from_pixbuf(pix)
#            self.put(img, 5, 5)
#            img.show()
#        except:
#            print ("Image not found or corrupt")
    

        self.pyjama.window.setcolor(self)


    def draw(self, lyrics, track_id, *args):
        track = self.pyjama.db.get_trackinfos2(track_id)
 #       markup = self.pyjama.window.markuplbCaption.replace("TEXT", _("Showing Lyrics of '%s' by %s" % (track.name, track.artist_name)))
        txt = _("Showing Lyrics of '%s' by %s" % (track.name, track.artist_name))
#        self.pyjama.window.lbCaption.set_markup(markup)
        self.pyjama.window.LayoutInfo.set_text(txt)
        self.pyjama.window.LayoutInfo.set_image(os.path.join(functions.install_dir(), "plugins", "lyrics", "lyrics.png"))
        self.show()

#        self.buffer.set_text(lyrics)
        self.lbl.set_text(lyrics)
        n = lyrics.count("\n")
        self.set_size(700, 300+10*n)

    #
    # Actually this toolbar is just a hbox...
    #
    class ToolBar(gtk.HBox):
        def __init__(self, pyjama):
            gtk.HBox.__init__(self)
            self.hide()
