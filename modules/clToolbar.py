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

import gtk, gtk.glade
import os
import time

import functions

from modules.clWidgets import EqualizerBox
from modules.clGstreamer010 import Track

## @package clToolbar
# Holds Pyjama's Toolbar Class


## A gtk.Toolbar with an additional method
# for setting images
class Toolbar(gtk.Toolbar):
    ## The Constructor
    # @param self Object Pointer
    # @param window Reference to pyjama's window class
    def __init__(self, window):
        ## Reference to pyjama
        self.pyjama = window.main

        gtk.Toolbar.__init__(self)
        show_toolbar_text = self.pyjama.settings.get_value("PYJAMA", "SHOW_TOOLBAR_TEXT", True)
#        if show_toolbar_text == None:
#            self.pyjama.settings.set_value("PYJAMA", "SHOW_TOOLBAR_TEXT", True)
        if show_toolbar_text:
            self.set_style(gtk.TOOLBAR_BOTH)
        else:
            self.set_style(gtk.TOOLBAR_ICONS)
        self.set_icon_size(gtk.ICON_SIZE_LARGE_TOOLBAR)# (gtk.ICON_SIZE_DIALOG) # large_toolbar
        self.set_show_arrow(True)
#        self.set_border_width(5)


        #
        # ToolButtons
        #
        ## Back Button
        self.bHistoryBack = gtk.ToolButton(_("Back"))
        self.bHistoryBack.set_stock_id(gtk.STOCK_GO_BACK)
        self.bHistoryBack.set_sensitive(False)
        self.bHistoryBack.set_label(_("Back"))
        self.bHistoryBack.set_tooltip_text(_("Show previous page in history"))
        self.bHistoryBack.connect("clicked", self.on_bHistoryBack_clicked)
        self.insert(self.bHistoryBack, -1)

        ## Home Button
        self.bHome = gtk.ToolButton(_("Home"))
        self.bHome.set_stock_id(gtk.STOCK_HOME)
        self.bHome.set_label(_("Home"))
        self.bHome.set_tooltip_text(_("Show start-page"))
        self.bHome.connect("clicked", self.on_bHome_clicked)
        self.insert(self.bHome, -1)

        ## Forward Button
        self.bHistoryForward = gtk.ToolButton(_("Forward"))
        self.bHistoryForward.set_stock_id(gtk.STOCK_GO_FORWARD)
        self.bHistoryForward.set_sensitive(False)
        self.bHistoryForward.set_label(_("Forward"))
        self.bHistoryForward.set_tooltip_text(_("Show next page in history"))
        self.bHistoryForward.connect("clicked", self.on_bHistoryForward_clicked)
        self.insert(self.bHistoryForward, -1)

        ## Burn Button
        self.bBurn = gtk.ToolButton(_("Burn"))
        self.bBurn.set_stock_id(gtk.STOCK_CDROM)
        self.bBurn.set_label(_("Burn"))
        self.bBurn.set_tooltip_text(_("Burn selected playlist"))
        self.bBurn.connect("clicked", self.on_bBurn_clicked)
        self.insert(self.bBurn, -1)

        ## Seperator
        self.Separator1 = gtk.SeparatorToolItem()
        self.insert(self.Separator1, -1)

        # ADD ALBUM TO PLAYLIST
        self.lbAppendAlbum = gtk.ToolButton(label=_("Append"))
        self.lbAppendAlbum.set_stock_id(gtk.STOCK_ADD)
        self.lbAppendAlbum.set_tooltip_text(_("Append this album on playlist"))
        self.lbAppendAlbum.connect("clicked", self.on_lbAppendAlbum_clicked)
        self.insert(self.lbAppendAlbum, -1)
        # GET MORE ALBUMS FROM THIS PLAYLIST
        self.lbArtistsAlbumsToPlaylist = gtk.ToolButton(label=_("Append"))
        self.lbArtistsAlbumsToPlaylist.set_stock_id(gtk.STOCK_ADD)
        self.lbArtistsAlbumsToPlaylist.set_tooltip_text(_("Append artists albums to playlist"))
        self.lbArtistsAlbumsToPlaylist.connect("clicked", self.on_lbAppendArtistsAlbums_clicked)
        self.insert(self.lbArtistsAlbumsToPlaylist, -1)
        # GET MORE ALBUMS FROM THIS PLAYLIST
        self.lbMoreAlbumsFromThisArtist2 = gtk.ToolButton(label=_("Artist"))
        self.set_image(self.lbMoreAlbumsFromThisArtist2, os.path.join(functions.install_dir(), "images", "personal.png"))
        self.lbMoreAlbumsFromThisArtist2.set_tooltip_text(_("Get more music from this artist"))
        self.lbMoreAlbumsFromThisArtist2.connect("clicked", self.on_lbMoreAlbumsFromThisArtist_clicked)
        self.insert(self.lbMoreAlbumsFromThisArtist2, -1)

        ## Seperator
        self.Separator2 = gtk.SeparatorToolItem()
        self.insert(self.Separator2, -1)

        ## Expander
        self.space_fs = gtk.ToolItem()
        self.space_fs.set_expand(True)
        self.insert(self.space_fs, -1)

        self.bPref = gtk.ToolButton("Preferences")
        #self.bPref.set_stock_id(gtk.STOCK_PREFERENCES)
        #self.bPref.set_tooltip_text(_("Show Preferences"))
        self.bPref.connect("clicked", self.pyjama.show_preferences)
        #self.insert(self.bPref, -1)
        #self.bPref.show()
        

        #
        # Accelerators
        #
        self.accel_group = gtk.AccelGroup()
        self.bHistoryBack.add_accelerator("clicked", self.accel_group, 65361, gtk.gdk.MOD1_MASK, gtk.ACCEL_VISIBLE)
        self.bHome.add_accelerator("clicked", self.accel_group, ord("h"), gtk.gdk.CONTROL_MASK, gtk.ACCEL_VISIBLE)
        self.bHistoryForward.add_accelerator("clicked", self.accel_group, 65363, gtk.gdk.MOD1_MASK, gtk.ACCEL_VISIBLE)
        self.bBurn.add_accelerator("clicked", self.accel_group, ord("b"), gtk.gdk.CONTROL_MASK, gtk.ACCEL_VISIBLE)
        self.bPref.add_accelerator("clicked", self.accel_group, ord("p"), gtk.gdk.CONTROL_MASK, gtk.ACCEL_VISIBLE)
        self.pyjama.window.add_accel_group(self.accel_group)

        self.show_all()

    ## Set Image for a Button
    # @param self Object Pointer
    # @param widget Widget to set image for
    # @param uri URI to the image to be set
    # @return None
    def set_image(self, widget, uri):
        w, h = gtk.icon_size_lookup(self.get_icon_size())
        if not os.path.exists(uri):
            if os.path.exists(os.path.join(functions.install_dir(), "images", uri)):
                uri = os.path.join(functions.install_dir(), "images", uri)
        pixbuf = gtk.gdk.pixbuf_new_from_file_at_size(uri, w, h)
        img = gtk.Image()
        img.set_from_pixbuf(pixbuf)
        img.show()
        widget.set_icon_widget(img)

    ######################################################################
    #                                                                    #
    #                               Events                               #
    #                                                                    #
    ######################################################################

    def on_bHistoryForward_clicked(self, ev):
        if len(self.pyjama.historyForward) >= self.pyjama.settings.get_value("PERFORMANCE", "HISTORY_SIZE"):
            self.pyjama.historyForward.pop(0)
        if len(self.pyjama.historyForward) > 0:
            self.pyjama.historyBack.append(self.pyjama.historyCurrent)
            ret = self.pyjama.historyForward.pop()
            layout = ret['layout']
            data1 = ret['data1']
            data2 = ret['data2']
            data3 = ret['data3']
            data4 = ret['data4']
            self.pyjama.layouts.show_layout(layout, data1, data2, data3, data4, fromhistory=True, who_called = "on_bHistoryForward_clicked")

    def on_bHome_clicked(self, ev):
        #~ print self.pyjama.check_another_instance_running()
        self.pyjama.go_home()

    def on_bHistoryBack_clicked(self, ev):
        if len(self.pyjama.historyBack) >= self.pyjama.settings.get_value("PERFORMANCE", "HISTORY_SIZE"):
            self.pyjama.historyBack.pop(0)
        if len(self.pyjama.historyBack) > 0:
            self.pyjama.historyForward.append(self.pyjama.historyCurrent)
            ret = self.pyjama.historyBack.pop()
            layout = ret['layout']
            data1 = ret['data1']
            data2 = ret['data2']
            data3 = ret['data3']
            data4 = ret['data4']
            self.pyjama.layouts.show_layout(layout, data1, data2, data3, data4, fromhistory=True, who_called = "on_bHistoryBack_clicked")
        
    def on_bBurn_clicked(self, ev):
        self.pyjama.layouts.show_layout("burn")

    def on_bAbout_clicked(self, ev):
        self.pyjama.window.show_about()

    def cb_show_equalizer(self, ev=None):
        eq = EqualizerBox(self.pyjama)
        eq.dialog()

    def on_lbMoreAlbumsFromThisArtist_clicked(self, ev):
        # query db for artist informations and more albums
        self.pyjama.start_pulsing(text = _("Requesting local database"))
        ret = self.pyjama.db.artistinfos(self.lbMoreAlbumsFromThisArtist2.tag, time.time())        
        self.pyjama.stop_pulsing()
        self.pyjama.layouts.show_layout("artist", ret, who_called = "on_lbMoreAlbumsFromThisArtist_clicked")

    def on_lbAppendAlbum_clicked(self, ev):
        tracks = self.lbAppendAlbum.tag
        for track in tracks: # for track in self.main.tracks:
            track.uid = "%f%s" % (time.time(), track.id)
            self.pyjama.add2playlist(track)
        status = self.pyjama.player.status
        if status == "Error" or status == "End" or status == None:
            self.pyjama.window.on_bPlay_clicked(None)

    def on_lbAppendArtistsAlbums_clicked(self, ev):
        for track in self.pyjama.db.artisttracks(self.lbMoreAlbumsFromThisArtist2.tag):
            track.uid = "%f%s" % (time.time(), track.id)
            self.pyjama.add2playlist(track)
        status = self.pyjama.player.status
        if status == "Error" or status == "End" or status == None:
            self.pyjama.window.on_bPlay_clicked(None)
