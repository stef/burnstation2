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

# GUI
import pygtk
pygtk.require('2.0')
import gtk
import gobject

# Glade
import gtk.glade

import os
import sys
#sys.path.insert(0, "/home/barabbas/.pyjama/user_modules/")
if os.name == "posix" or os.name == "mac":
    sys.path.append("/usr/share/apps/pyjama") # linux
else:
    sys.path.append(os.path.join(os.getenv('PROGRAMFILES'), "pyjama")) # windows

# Time formatting
from time import strftime, gmtime, time, sleep

#RegEx
import re
import hashlib

# Needed for my special functions
# like imagepack creation
import shutil
import tarfile

# Object Serialisation for Drag'n'Drop
import pickle

import clMain
from clWidgets import *
import clEntry
import clMenu, clToolbar
import functions
import clLayouts
from clLayouts.default_layouts import clAlbumBrowser, clAlbumLayout, clArtistLayout, clBurnLayout

#~ from threading import Thread
#~ def threaded(f):
    #~ def wrapper(*args, **kwargs):
        #~ t = Thread(target=f, args=args, kwargs=kwargs)
        #~ t.start()
    #~ return wrapper
    #~ 
#~ @threaded
class winGTK(gtk.Window):
    def __init__(self, options, parent=None):
        self.__alldone = False
        self.options = options
        #gtk.rc_parse('/usr/share/themes/Industrial/gtk0.0/gtkrc') #stf
        
        self.main = clMain.main(self, options)
        self.main.settings.set_value("PYJAMA", "crashed", True)

        self.layout = {}

        ### Standard- Hintergrundfarbe:
        self.bgcolor = "#4785C2" #"#75A3D1"#"#4785C2"

        ### Standardfarben- Playlist
        self.CellBGColor = "STANDARD"
        self.CellSize = 8
        self.markupCurPlaying = '<span foreground="blue"><i><b>__ARTIST__</b></i>\n   __NUM__) __TITLE__</span>'
        self.markupNormalEntry ='<span>__ARTIST__\n   __NUM__) __TITLE__</span>'# '__ARTIST__\n\t__TITLE__' 
        
        gtk.Window.__init__(self)
#        try:
#            self.set_screen(parent.get_screen())
#        except AttributeError:
#            self.connect('delete', self.quit)

        self.event_delete = self.connect('delete_event', self.quit)
        self.set_title("Burnstation 2.0 - powered by Python Jamendo Audiocenter")
        self.set_default_size(850, 600)
        self.set_position(gtk.WIN_POS_CENTER)
        self.set_icon_from_file(os.path.join(functions.install_dir(), "images", "hspbp-burnstation.png"))
        self.set_skip_taskbar_hint(not self.main.settings.get_value("PYJAMA", "show_window_in_taskbar", False))

        self.set_border_width(0)
        self.event_window_state = self.connect('window-state-event', self.window_state_event)
        
        self.vbox = gtk.VBox(False, 0)
        self.add(self.vbox)
        self.vbox.set_border_width(0)

        ## Tooltip delay for the tvPlaylist
        # needed 'cause somehow the query-tooltip
        # event is fired on mousemove all the time
        self.tooltip_delay = self.main.settings.get_value("PERFORMANCE", "TOOLTIP_DELAY", 70)

        #
        # Buttonbox -------------
        #
        ##### PLACE FOR MENU
        ###################
        
        # CREATE SIDEBAR
        # Place for Menu and Toobar
        self.vbTop = gtk.VBox()
        self.vbox.pack_start(self.vbTop, False, False)
        # Paned Playlist / Media
        self.hpaned = gtk.HPaned()
        self.vbox.pack_start(self.hpaned, True, True, 0)
        
        # CREATE MAIN VIEW
        # Place for Media / Table
        self.vbMain = gtk.VBox()
        self.vpaned = gtk.VPaned()


        self.hpaned.pack1(self.vbMain, True, False)
        self.vbMedia = gtk.VBox()
        self.vbMain.pack_end(self.vbMedia, True, True)
        self.vbMedia.pack_end(self.vpaned, True, True)

        #################################################################
        # Menu
#        NEW_TOOLBAR_POSITION = self.main.settings.get_value("PYJAMA", "NEW_TOOLBAR_POSITION", False)
        self.menubar = clMenu.Menu(self)
 #       if NEW_TOOLBAR_POSITION is True:
        #self.vbTop.pack_start(self.menubar, False, False)
#        else:
#            self.vbMain.pack_start(self.menubar, False, False)

        #################################################################


        #################################################################
        # TOP NAVBAR
        # NAV BUTTONBOX

        self.toolbar = clToolbar.Toolbar(self)
#        if NEW_TOOLBAR_POSITION is True:
        self.vbTop.pack_start(self.toolbar, False, False)
#        else:
#            self.vbMain.pack_start(self.toolbar, False, False)
        #################################################################



        #################################################################
        # CREATE MEDIA VIEW
#        self.vpaned.pack1(self.vbTop, False, True)
        self.scrolledwindow = gtk.ScrolledWindow()
        self.scrolledwindow.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
        self.scrolledwindow.set_size_request(550, 150) #zwangsgröße
        self.event_scrolled_window_resize = self.scrolledwindow.connect("size-allocate", self.scrolled_window_resize)        

        # This VBox contains all items to be shown in the top vpaned
        self.vbMainLayout = gtk.VBox()
        self.vbMainLayout.pack_end(self.scrolledwindow, True, True)

        # this frame holds vbMainLayout
        self.f = gtk.Frame()
        self.f.set_shadow_type(gtk.SHADOW_IN)
        self.LayoutInfo = InfoLabel(self.main)
        self.f.set_label_widget(self.LayoutInfo)
        self.f.add(self.vbMainLayout)




        self.vpaned.pack1(self.f, True, True)
        

##        self.vbTop.pack_end(self.scrolledwindow, True, True, 0)

        
        #################################################################
      
        ##################################################################
        ## Top- VIEW, Result p Page etc.
        ##
        ## this vbox devides next hbox from infolabel following
#        self.vbTop = gtk.VBox()
#        self.vbMedia.pack_end(self.vbTop, False, True)


        #MUST STAY
        # Info- Widget
        # contains title for currently shown Layout
#        self.lbCaption = gtk.Label("")
#        self.vbMain.pack_end(self.lbCaption, False, True , 10)

#        self.LayoutInfo = InfoLabel(self.main)
#        self.vbMain.pack_end(self.LayoutInfo, False, True , 10)
        #################################################################
        

        #################################################################
        # PLAYLIST
        # CREATE TREEVIEW 

        self.vbSideBar = gtk.VBox(False)
        self.swTreeView = gtk.ScrolledWindow()
        self.swTreeView.set_policy(gtk.POLICY_NEVER, gtk.POLICY_AUTOMATIC)
        # create a liststore with one string column to use as the model
        self.liststore = gtk.ListStore(gobject.TYPE_STRING) # gobject.TYPE_INT
        # create the TreeView using liststore
        self.tvPlaylist = gtk.TreeView(self.liststore)
        self.tvPlaylist.props.has_tooltip = True
        self.tooltip_timestamp = 0 # needed since this signial fired all the time the mouse moves. This var will implement a delay of some ms
        if not "notooltips" in sys.argv and not "no-tooltips" in sys.argv:
            self.tvPlaylist.connect('query-tooltip', self.cb_query_tooltip)

#        # After an update to python2.6 the old-school set_custom() method
#        # for tooltips didn't work any more for me.
#        # For this reason, I use the set_tooltip_window method
#        ttwin = gtk.Window(gtk.WINDOW_POPUP)
#        hbox = gtk.HBox()
#        ttwin.add(hbox)
#        self.tvPlaylist.set_tooltip_window(ttwin)

        self.tvPlaylist.connect("row_activated", self.on_tvPlaylist_row_activated)
        self.tvPlaylist.connect("cursor-changed", self.on_tvPlaylist_cursor_changed)
        self.tvPlaylist.connect("motion-notify-event", self.on_tvPlaylist_motion_notify)
        self.tvPlaylist.connect("enter-notify-event", self.on_tvPlaylist_enter_notify)
        self.tvPlaylist.connect("leave-notify-event", self.on_tvPlaylist_leave_notify)
        self.tvPlaylist.connect("button-press-event", self.on_tvPlaylist_button_press)
        self.tvPlaylist.connect("key-press-event",self.on_tvPlaylist_key_press)
        #self.tvPlaylist.set_hover_selection(True)
        # TreeSelection:
        self.tvPlaylistSelection = self.tvPlaylist.get_selection()
        self.tvPlaylistSelection.set_mode(gtk.SELECTION_SINGLE)
        # CELLRENDERER FOR TEXT
        self.cell = gtk.CellRendererText()
        # CREATE COLUMN 
        # create the TreeViewColumns to display the data
        self.tvColumn = gtk.TreeViewColumn('Playlist', self.cell, markup=0)#text=0)
        # ADD COLUMN TO TV
        self.tvPlaylist.append_column(self.tvColumn)
        # DRAG&DROP
        self.tvPlaylist.enable_model_drag_source(gtk.gdk.BUTTON1_MASK, [('text/plain', gtk.TARGET_SAME_APP, 0)], gtk.gdk.ACTION_MOVE)
        self.tvPlaylist.connect("drag-data-get", self.on_tvPlaylist_DragDataGet)

        self.tvPlaylist.enable_model_drag_dest([('text/plain', 0, 0)], gtk.gdk.ACTION_MOVE)
        self.tvPlaylist.connect("drag-data-received", self.on_tvPlaylist_DragDataReceived)

        self.tvPlaylist.connect("drag_data_delete", self.on_tvPlaylist_DragDataEnd)

#        self.tvPlaylist.connect("drag_data_get", self.drag_data_get_data)
#        self.tvPlaylist.connect("drag_data_received",self.drag_data_received_data)
        # Pack TV INTO SCROLLED WINDOW
        self.swTreeView.add(self.tvPlaylist)
        self.swTreeView.set_size_request(150, 100)

        # PROGRESSBAR
        self.pbSong = gtk.ProgressBar()
        self.pbSong.set_orientation(gtk.PROGRESS_LEFT_TO_RIGHT)
        self.pbSong.set_pulse_step(0.05)   
        self.pbSong.set_tooltip_text("Left click: Seek the stream\nRight click: Switch time display")     
        self.ebProgressbar = gtk.EventBox()
        self.ebProgressbar.add(self.pbSong)
        self.ebProgressbar.set_above_child(False)
        self.ebProgressbar.add_events (gtk.gdk.BUTTON_RELEASE)
        self.ebProgressbar.connect("button_release_event", self.on_pbSong_clicked)
        self.pbSong.ShowRemainingTime = False
        self.pbSong.counter = 0
        
        # HSCALE AS VOLUME CONTROL
        hsAdjustment = gtk.Adjustment(value=self.main.settings.get_value("SOUND", "default_vol"), lower=0, upper=self.main.settings.get_value("SOUND", "vol_max"), step_incr=10, page_incr=2, page_size=10)
        self.hsVolume = gtk.VolumeButton()#gtk.HScale(hsAdjustment)
        self.hsVolume.set_value(self.main.settings.get_value("SOUND", "default_vol"))
        self.hsVolume.set_adjustment(hsAdjustment)
        self.hsVolume.connect("value-changed", self.on_sbVolume_Change)
        #self.hsVolume.set_draw_value(False)      
            #self.hsVolume.set_digits(0)
        #################################################################        

        #################################################################
        #
        # TABLE FOR PLAYER- CONTROL
        #
        #self.bbControls = gtk.HButtonBox()
        #self.bbControls.set_spacing(gtk.BUTTONBOX_SPREAD)
        self.tbControls = gtk.Table(1, 4, True)
        
        # POSSIBLE SIZES FOR STOCKBUTTON
        # gtk.ICON_SIZE_INVALID gtk.ICON_SIZE_MENU gtk.ICON_SIZE_SMALL_TOOLBAR gtk.ICON_SIZE_LARGE_TOOLBAR   
        # gtk.ICON_SIZE_BUTTON gtk.ICON_SIZE_DND gtk.ICON_SIZE_DIALOG
        # DEFAULT IS gtk.ICON_SIZE_MENU
        # PREV- Button
        self.bPrev = StockButton(gtk.STOCK_MEDIA_PREVIOUS)
        #self.bbControls.add(self.bPrev False, True, 0)
        self.bPrev.connect("clicked", self.on_bPrev_clicked)
        self.bPrev.set_tooltip_text(_("Play previous"))
        self.tbControls.attach(self.bPrev, 0, 1, 0, 1)
        # Play- Button       
        self.bPlay = StockButton(gtk.STOCK_MEDIA_PLAY)
        #self.bbControls.pack_start(self.bPlay, False, True, 0)
        self.bPlay.connect("clicked", self.on_bPlay_clicked)
        self.bPlay.connect("button_press_event", self.on_bPlay_pressed)




#        self.__accel_group = gtk.AccelGroup()
#        self.bPlay.add_accelerator("clicked", self.__accel_group, gtk.keysyms.space, 0, gtk.ACCEL_VISIBLE)
#        self.add_accel_group(self.__accel_group)


        
        self.bPlay.set_tooltip_text("%s\n%s" % (_("Play/pause"), _("Right click for stop")))

        self.tbControls.attach(self.bPlay, 1, 2, 0, 1)
#        # Stop- Button
#        self.bStop = StockButton(gtk.STOCK_MEDIA_STOP)
#        #self.bbControls.pack_start(self.bStop, False, True, 0)
#        self.bStop.connect("clicked", self.on_bStop_clicked)
#        self.bStop.set_tooltip_text(_("Stop"))
#        self.tbControls.attach(self.bStop, 2, 3, 0, 1)
        # Next- Button
        self.bNext = StockButton(gtk.STOCK_MEDIA_NEXT)
        #self.bbControls.pack_start(self.bNext, False, True, 0)
        self.bNext.connect("clicked", self.on_bNext_clicked)
        self.bNext.set_tooltip_text(_("Play next"))
        self.tbControls.attach(self.bNext, 2, 3, 0, 1)

        self.tbControls.attach(self.hsVolume, 3, 4, 0, 1)
        #################################################################
        
        #################################################################
        #
        # TABLE FOR PLAYLIST- CONTROL
        #
        self.tbPlaylist = gtk.Table(1, 2, True)
        # DELETE- Button
        self.bDelete = StockButton(gtk.STOCK_REMOVE)#STOCK_DELETE
        self.bDelete.connect("clicked", self.on_bDelete_clicked)
        self.bDelete.set_tooltip_text(_("Remove selected song from playlist"))
        self.tbPlaylist.attach(self.bDelete, 0, 1, 0, 1)
        # CLEAR- Button
        self.bClear = StockButton(gtk.STOCK_CLEAR)#CLEAR
        self.bClear.connect("clicked", self.on_bClear_clicked)
        self.bClear.set_tooltip_text(_("Clear playlist"))
        self.tbPlaylist.attach(self.bClear, 1, 2, 0, 1)
        #################################################################

        #################################################################
        #
        # ADD TO SIDEBAR
        #
        # ADD VPaned TO HPANED
        SideBarFrame = gtk.Frame(_("Playlist"))
        SideBarFrame.set_shadow_type(gtk.SHADOW_IN)
        SideBarFrame.add(self.vbSideBar)
        SideBarFrame.set_size_request(430, -1) #stf
        self.hpaned.pack2(SideBarFrame, False, True) #swTreeView
        self.hpaned.set_position(700)
        
        # COVER VIEW
        self.vbCover = gtk.VBox()
        self.vbSideBar.pack_start(self.vbCover, False, True, 5)
        self.lbCoverArtist = gtk.Label("")
        self.lbCoverAlbum = gtk.Label("")
        self.imgCover = gtk.Image()
        self.imgCover.set_size_request(100,100)
        sep = gtk.HSeparator()
        self.vbCover.pack_start(self.imgCover, False, True)
        self.vbCover.pack_start(self.lbCoverArtist, False, True)
        self.vbCover.pack_start(self.lbCoverAlbum, False, True)
        self.vbCover.pack_end(sep, False, False, 5)

        if True:
            self.imgCover.set_from_file(os.path.join(functions.install_dir(), "images", "hspbp-burnstation.png"))
        else:
            animation = gtk.gdk.PixbufAnimation(os.path.join(functions.install_dir(), "images", "pyjama_anim.gif"))
            self.imgCover.set_from_animation(animation)
        self.lbCoverArtist.set_text('Burnstation 2.0')
        self.lbCoverAlbum.set_text('powered by Python Jamendo Audio')
        
        # ADD SCROLLBAR TO VBOX
        #self.vbSideBar.pack_start(self.hsVolume, False, True)
        # ADD PROGRESSBAR's EVENTBOX TO VBOX
#        self.hbox_scroll_volume = gtk.HBox()
#        self.hbox_scroll_volume.pack_end(self.ebProgressbar, True, True)
#        self.hbox_scroll_volume.show_all()
#        self.hbox_scroll_volume.set_size_request(-1, 28)
#        self.vbSideBar.pack_start(self.hbox_scroll_volume, False, True)



        # ADD TV TO VPANED
        # ADD BUTTONBOX CONTROLS TO VBOX
        # ADD BUTTONBOX CONTROLS PLAYLIST TO VBOX

        self.vbSideBar.pack_start(self.tbControls, False, True)
        self.vbSideBar.pack_start(self.ebProgressbar, False, True)

        self.vbSideBar.pack_start(self.swTreeView, True, True)

        self.vbSideBar.pack_start(self.tbPlaylist, False, True)



        self.tvSelection = self.tvPlaylist.get_selection()
        #################################################################        

        #################################################################
        # USER WIDGET STATUSBAR
        self.sbStatus = StatusBar("Counter", "Info", "VarInfo", "Player")
        self.sbStatus.statusbars["Player"]['statusbar'].set_size_request(100,-1)
        self.sbStatus.set_text("Counter", _("Artists: %i, Albums: %i, Tracks: %i") % (self.main.db.artists, self.main.db.albums, self.main.db.tracks))

        self.sbStatus.show()
        self.vbox.pack_start(self.sbStatus, False, True, 0)
        
        self.pbWait = gtk.ProgressBar()
        self.vbox.pack_start(self.pbWait, False, True, 0)
        self.pbWait.set_pulse_step(0.02)        
        self.pbWait.show()
        #################################################################
        
#       model, iter = treeselection.get_selected()

#        REMOVE SELECTED
#        selection = self.tvPlaylist.get_selection()
#        model, iter = selection.get_selected()

#        if iter:
#            path = self.liststore.get_path(iter)[0]
#            self.liststore.remove(iter)
#            print path
#            del articles[ path ]

        #################################################################
        ### BACKGROUND COLORS
        if self.CellBGColor != "STANDARD":
            self.cell.set_property('cell-background', self.CellBGColor)
        self.cell.set_property('size-points', self.CellSize)
        #################################################################
        
        #################################################################
        # BOTTOM LIST SHOWING TRACKS
        # TreeView
        # CREATE TREEVIEW 
        self.swTVList = gtk.ScrolledWindow()
        self.swTVList.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
        self.tvList = TreeViewList()
        self.tvList.connect("row_activated", self.on_tvList_row_activated)
        self.tvList.connect("button-press-event", self.on_tvList_button_press)
        self.swTVList.add(self.tvList)

#        self.tvList.enable_model_drag_source(gtk.gdk.BUTTON1_MASK, [('text/plain', gtk.TARGET_SAME_APP, 0)], gtk.gdk.ACTION_MOVE)
#        self.tvList.connect("drag-data-get", self.on_tvList_DragDataGet)

#        self.vpaned.pack2(self.swTVList, True, True)
        self.vpaned2 = gtk.VPaned()  # containing tracklist and mozilla?
        self.vpaned.pack2(self.vpaned2, True, True) # containing media view and vpaned2        

        ## Frame vor swTVList
        self.TVListFrame = gtk.Frame(_("Tracklist"))
        self.TVListFrame.set_size_request(-1, 130 ) #stf
        self.TVListFrame.add(self.swTVList)

        self.vpaned2.pack1(self.TVListFrame, True, True)
        #################################################################

        #self.connect("configure-event", self.test2)

        self.show_all()
        self.toolbar.lbMoreAlbumsFromThisArtist2.hide()
        self.toolbar.lbAppendAlbum.hide()
        self.toolbar.lbArtistsAlbumsToPlaylist.hide()
        self.toolbar.Separator2.hide()

        # Insert a Menu item for showing / hiding vbCover
        #stf
        #chkCover = gtk.CheckMenuItem(_("Show Cover Image"))
        #chkCover.set_active(self.main.settings.get_value("PYJAMA", "SHOW_COVER", True))
        #view = self.menubar.get_rootmenu("View").get_submenu()
        #view.insert(chkCover, 0)
        #chkCover.connect("activate", self.switch_show_cover)
        #chkCover.show()
        #self.switch_show_cover(chkCover)
        #sep = gtk.SeparatorMenuItem()
        #view.insert(sep, 1)
        #sep.show()

#        chkToolbarPos = gtk.CheckMenuItem(_("new toolbar position"))
#        chkToolbarPos.set_active(NEW_TOOLBAR_POSITION)
#        view.insert(chkToolbarPos, 1)
#        sep = sep = gtk.SeparatorMenuItem()
#        view.insert(sep, 2)
#        chkToolbarPos.connect("activate", self.switch_new_toolbar_position)
#        chkToolbarPos.show()
#        sep.show()

        self.pbWait.hide()     

#        import gtkmozembed as gtkmoz #gtkmoz
#        self.mozillaWidget = gtkmoz.MozEmbed()
#        self.mozillaWidget.set_size_request(400,300)
#        self.vpaned2.pack2(self.mozillaWidget, True, True)
#        self.vpaned2.show()
#        self.mozillaWidget.show()

        # Register Layouts:
        self.main.layouts.register_layout("top", clAlbumBrowser.AlbumBrowser(self.main))
        self.main.layouts.register_layout("album", clAlbumLayout.AlbumLayout(self.main))
        self.main.layouts.register_layout("artist", clArtistLayout.ArtistLayout(self.main))
        self.main.layouts.register_layout("burn", clBurnLayout.BurnLayout(self.main))
        self.main.layouts.register_layout("burn_cd", clBurnLayout.BurnCDLayout(self.main))
        self.main.layouts.register_layout("burn_usb", clBurnLayout.BurnUSBLayout(self.main))

        # Menu Entry
        #menu = self.menubar
        #entry = menu.append_entry(menu.get_rootmenu("Browse"), _("Albums"), "top")
        #entry.connect("activate", self.cb_show_album_browser)
        #menu.set_item_image(entry, os.path.join(functions.install_dir(), "images", "star.png"))
        #menu.show()

        # Show starting- window
#        self.main.layouts.show_layout("top", 10, "ratingweek", 1, "all", who_called = "window.__init__") 
        #self.main.draw_topoftheweek()

        #
        # Check Database
        #
#        if options.update or not os.path.exists(os.path.join(self.main.home, "pyjama.db")):
        if options.update or not self.main.db.database_ok:
            self.main.download_database()
        if options.update_jamendo:
            self.main.download_database(force_jamendo=True)

        # Raise "alldone" event --this is now called in pyjama.py
        self.__alldone = True
        ev = self.main.Events
        ev.raise_event("alldone")

        # Add preferences menu to the menubar
        # add menu entry
        menu = self.menubar
        root = menu.get_rootmenu("Extras")
        if root:
            menu.append_entry(root, "---", "prefsep")
            mnu = menu.append_entry(root, _("Preferences"), "preferences")
            menu.set_item_image(mnu, gtk.STOCK_PREFERENCES)
            mnu.connect("activate", self.main.show_preferences)
        
        self.main.go_home()

        # for startup time checks:
        if "check-time" in sys.argv:
            sys.exit()

        self.__special_checks()

        if self.main.plugins.blacklisted_browser:
            self.main.need_attention = True
            self.main.info("Blacklisted browser", "Pyjama probably crashed last time.\nIn most cases <b>mozplug</b> or <b>webkit-plugin</b> a responsible for that.\n\nThe browser-plugins where disabled for this reason")
            self.main.need_attention = False

        if not "noexp" in sys.argv:
            self.main.need_attention = True
            self.main.info("Experimental!", "You are using an <b>experimental version</b> of pyjama. It was released to let you review some new features of my program.\nPlease: Report any bugs via \n\n<u>bugs.launchpad.net/pyjama</u>.\n\nThanks!")
            self.main.need_attention = False

        #~ if "hang-up" in sys.argv:
            #~ while 1:
                #~ pass

        #~ if self.main.xmlrpc.role == "client":
            #~ self.main.xmlrpc.server.check()


#        while gtk.events_pending(): gtk.main_iteration()

    ## This event is raised when a tooltip
    # in the playlist is going to be shown.
    # Please connect to pyjama's event
    # 'playlist_tooltip'. It will pass:
    # - the x coords of the mouse pointer
    # - the y coords of the mouse pointer
    # - a tuple holding two vboxes
    # Add the description of the info you want
    # to add to the first vbox and the info
    # itself to the second vbox.
    # /todo: Make this whole event more intuitiv
    def cb_query_tooltip(self, widget, x, y, keyboard_tip, tooltip):
#        tooltip.set_markup("test")
#        print 99*99**9
#        return True
#        CONTAINER="BOX"
#        lbl = gtk.Label("Bin ich krass wunderschönes Tooltip")
#        lbl.show()
#        b = gtk.Button("tst2")
#        b.show()

#        if CONTAINER == "BOX":
#            hbox = gtk.VBox()
#            hbox.show()
#            hbox.pack_start(lbl)
#            hbox.pack_start(b)

#            try:
#                tooltip.set_custom(hbox)
#            except Exception, inst:
#                inst
#        return True



#        return True

#        widget.props.has_tooltip = True
#        print tooltip

#        hbox = gtk.HBox()
#        l = gtk.Label("asd")
#        l.show()
#        hbox.pack_start(l)
#        hbox.show()

#        tooltip.set_custom(hbox)

#        return True

#        settings = gtk.settings_get_default() 
#        print settings.props.gtk_tooltip_timeout

        if self.tooltip_timestamp + self.tooltip_delay > time()*1000:
            return False
        self.tooltip_timestamp = time()*1000

        y = y - 27
        # One can add widgets to this vbox in order
        # to show them in the tooltip
        hbox = gtk.HBox()
        vbox1 = gtk.VBox(True)
        vbox2 = gtk.VBox(True)
        hbox.pack_start(vbox1, False, True)
        hbox.pack_start(vbox2, False, True)

        hbox.set_spacing (10)
        vbox1.set_spacing (10)
        vbox2.set_spacing (10)

    

        l = gtk.Label()
        path = self.tvPlaylist.get_path_at_pos(int(x), int(y))
        if path:
            # Some basic infos
            track = self.main.player.playlist[path[0][0]]
            img_uri = self.main.get_album_image(track.album_id)
            if img_uri:
                img = gtk.Image()
                try:
                    pix = gtk.gdk.pixbuf_new_from_file_at_size(img_uri, 50, 50)
                    img.set_from_pixbuf(pix)
                except:
                    img.set_from_stock(gtk.STOCK_MISSING_IMAGE, gtk.ICON_SIZE_BUTTON)
                img.show()
                vbox1.pack_start(img, False, True)

            l.set_markup("<b>%s</b>\n%s\n%s" % (track.artist_name[:30], track.album_name[:30], track.name[:30]))
            l.show()
            vbox2.pack_start(l, False, True)

#            vbox.pack_start(hbox, False, True)
        else:
            return False


        hbox.show_all()
        
        # Call other functions that might
        # add widgets to the hbox
        self.main.Events.raise_event("playlist_tooltip", x, y, (vbox1, vbox2))


        

#        win = widget.get_tooltip_window()
#        win.show()
#        try:
#            win.remove(win.get_child())
#        except:
#            pass
#        win.move(x, y)
#        win.add(hbox)

        # set the vbox as tooltip custom widget
        tooltip.set_custom(hbox)
        return True

    def cb_show_album_browser(self, widget):
        self.main.layouts.show_layout("top", 10, "ratingweek", 1, "all", who_called = "window.__init__")

#    def switch_new_toolbar_position(self, widget):
#        new = widget.get_active()
#        if new is True:
#            container =  self.toolbar.get_parent()
#            container.remove(self.toolbar)
#            container.remove(self.menubar)
#            self.vbTop.pack_start(self.menubar, False, False)
#            self.vbTop.reorder_child(self.menubar, 0)
#            self.vbTop.pack_start(self.toolbar, False, False)
#            self.vbTop.reorder_child(self.toolbar, 1)
#            self.main.settings.set_value("PYJAMA", "NEW_TOOLBAR_POSITION", "True")
#        else:
#            container =  self.toolbar.get_parent()
#            container.remove(self.toolbar)
#            container.remove(self.menubar)
#            self.vbMain.pack_start(self.menubar, False, False)
#            self.vbMain.reorder_child(self.menubar, 0)
#            self.vbMain.pack_start(self.toolbar, False, False)
#            self.vbMain.reorder_child(self.toolbar, 1)
#            self.main.settings.set_value("PYJAMA", "NEW_TOOLBAR_POSITION", "False")

    def switch_show_cover(self, widget):
        show = widget.get_active()
        if show is True:
            self.vbCover.show()
            self.main.settings.set_value("PYJAMA", "SHOW_COVER", "True")
        else:
            self.main.settings.set_value("PYJAMA", "SHOW_COVER", "False")
            self.vbCover.hide()

    def window_state_event(self, widget, event):
        if event.new_window_state & gtk.gdk.WINDOW_STATE_ICONIFIED:
            self.window.visible = False

    def show_window(self,ev):
        self.present()
        #~ self.window.set_skip_taskbar_hint(False)
        
    def on_tvPlaylist_key_press(self, widget, event):
        if event.keyval == 32:
            self.on_bPlay_clicked(None)
            return True

    def on_tvPlaylist_row_activated(self, treeview, path, view_column):
        if path:
            self.on_bStop_clicked(None)
            self.on_bPlay_clicked(path[0])

    def on_tvPlaylist_enter_notify(self, treeview, event):
        pass
#        if not self.menubar.bolFullScreen:
#            self.popup.show_all()
#            self.popup.move(-500,-500)

    def on_tvPlaylist_leave_notify(self, treeview, event):
#        self.popup.hide()
        self.main.showInfo()

    def on_tvPlaylist_motion_notify(self, treeview, event):
        ret = treeview.get_path_at_pos(int(event.x), int(event.y))

        if ret != None:
            current_path, current_column = ret[:2]
            self.main.showInfo(current_path[0])

#            self.popup.move(int(event.x_root-100), int(event.y_root+20))
#            track = self.main.player.playlist[current_path[0]]

#            self.popup.lbl_artist.set_markup("<b>%s</b>" % track.artist_name)
#            self.popup.lbl_album.set_markup( track.album_name )
#            self.popup.lbl_track.set_markup( track.name)

#            self.main.Events.raise_event("playlist_tooltip_move", event, current_path)

#            #print current_column.get_title()
#            renderer = current_column.get_cell_renderers()
#            if renderer != None:
#                renderer = renderer[0]
#                current_position = current_column.cell_get_position(renderer)
#                if current_position:
#                    current_position = current_position[0]
#                    print current_position
#            else:
#                return None
    def on_tvPlaylist_cursor_changed(self, treeview):
            self.main.showInfo()

    def on_pbSong_clicked(self, widget, event):
        if event.button == 3:
            self.pbSong.ShowRemainingTime = not self.pbSong.ShowRemainingTime
            self.main.timer_event()
        elif event.button == 1 and self.main.player.status == "Playing" or self.main.player.status == "paused":
            # get width of this widget
            allocation = widget.get_allocation()
            width = allocation[2]
            # pointer
            pointer = widget.get_pointer()
            x = pointer[0]

            # Calculate Position in percent
            percentage = x * 100 / width

            # seek
            real = long(percentage * self.main.player.duration* (10**7)) # in ns
            self.main.player.seek(real)


    def on_tvList_DragDataGet(self, widget, drag_context, selection, info, timestamp):
        tvListSelection = widget.get_selection()
        model, iter = tvListSelection.get_selected()
        data = model.get_value(iter, 0)
        path =  model.get_path(iter)

        # Will have to replace this with a
        # TYPE_PYOBJECT !!

        data= pickle.dumps({'source':'list','data':data,'path':path})
        print {'source':'list','data':data,'path':path}
        selection.set(selection.target, 8, data)
        return

    def on_tvPlaylist_DragDataGet(self, widget, drag_context, selection, info, timestamp):
        tvPlaylistSelection = self.tvPlaylist.get_selection()
        model, iter = tvPlaylistSelection.get_selected()
        data = model.get_value(iter, 0)
        path =  model.get_path(iter)

        data= pickle.dumps({'source':'playlist','data':data,'path':path})

        selection.set(selection.target, 8, data)
        return


    def on_tvPlaylist_DragDataReceived(self, widget, context, x, y, selection, info, timestamp):
        model = widget.get_model()
        data = selection.data
        data = pickle.loads(data)
        source = data['source']
        if source == "playlist":
            data = [data]
        drop_info = widget.get_dest_row_at_pos(x, y)
        for datum in data:
            if drop_info:
                destpath, position = drop_info
                iter = model.get_iter(destpath)

                destpath = destpath[0]
                sourcepath = datum['path'][0]

                datum = datum['data']
                if self.main.debug_extreme:
                    print "!", sourcepath, destpath, "!"
                if (position == gtk.TREE_VIEW_DROP_BEFORE or position == gtk.TREE_VIEW_DROP_INTO_OR_BEFORE):
                    if self.main.debug_extreme:
                        print "into intoorbefore"
                    model.insert_before(iter, [datum])  
                    self.main.move_playlist_item(sourcepath, destpath, before=True)
                else:
                    if self.main.debug_extreme:
                        print "else"
                    self.main.move_playlist_item(sourcepath, destpath, before=False)
                    model.insert_after(iter, [datum])
            else:
                return
        if context.action == gtk.gdk.ACTION_MOVE:
            context.finish(True, True, timestamp)
        return

    def on_tvPlaylist_DragDataEnd(widget, context, data):
        pass

    def on_tvPlaylist_button_press(self, widget, event):
        if event.button == 3:
#            ret = self.tvPlaylist.get_path_at_pos(int(event.x), int(event.y))
#            selection = self.tvPlaylist.get_selection()
#            model, retIter = selection.get_selected()
#            if retIter is None: retIter = model.get_iter(ret[0])
#            selection.select_iter(retIter)

            mnu = PlaylistMenu(self.main)
            mnu.popup(None, None, None, event.button, event.time)
            if mnu.get_children() == []:
                mnu.destroy()

    def on_tvList_row_activated(self, treeview, path, view_column):
        # ==> view_column ==> geklickte Spalte!
        ret = self.tvList.get_item(path)
        tracknum = ret[self.tvList.COLUMN_TRACKNUM]
        trackid = ret[self.tvList.COLUMN_TRACKID]
        albumid = ret[self.tvList.COLUMN_ALBUMID]
        artistid = ret[self.tvList.COLUMN_ARTISTID]
        if trackid > -1:
            track = self.main.db.get_trackinfos2(trackid)
        #    track.uid = "%f%s" % (time(), trackid)
            self.main.add2playlist(track)
        elif albumid > -1:
            print albumid
            albumdetails = self.main.jamendo.albuminfos(albumid)
            if albumdetails == None:
                tofast(self.window)
                return None
            elif albumdetails == -1:
                return None    
            self.main.layouts.show_layout("album", albumdetails, who_called = "on_tvList_row_activated")
        elif artistid > -1:
            artist = self.main.db.artistinfos(artistid)
            self.main.layouts.show_layout("artist", artist, who_called = "on_tvList_row_activated")

    def on_tvList_button_press(self, widget, event):
        if event.button == 3:
#            ret = self.tvList.get_path_at_pos(int(event.x), int(event.y))
#            selection = self.tvList.get_selection()
#            model, retIter = selection.get_selected()
#            if retIter is None: retIter = model.get_iter(ret[0])
#            selection.select_iter(retIter)

#            ret = self.tvList.get_item(ret[0])
#            print ret

            mnu = ListMenu(self.main)
            mnu.popup(None, None, None, event.button, event.time)
            if mnu.get_children() == []:
                mnu.destroy()

    def on_bDelete_clicked(self, ev):
        liststore, markedIter = self.tvPlaylistSelection.get_selected()
        if markedIter:
            model = self.tvPlaylist.get_model()
            self.main.remove_item_from_playlist(model.get_path(markedIter))
            liststore.remove(markedIter)

    def on_bClear_clicked(self, ev):
        self.main.player.clearplaylist()
        model = self.tvPlaylist.get_model()
        model.clear()

    def on_bNext_clicked(self, ev):
        self.on_bStop_clicked(None)
        self.main.player.next()
        self.main.icon.menu.switch_play_button("pause")
        
    def on_bPrev_clicked(self, ev):
        self.on_bStop_clicked(None)    
        self.main.player.prev()
        self.main.icon.menu.switch_play_button("pause")

    def cb_export_playlist(self, widget):
        m3u = ""
        xspf = '''<?xml version="1.0" encoding="UTF-8"?>
<playlist version="1" xmlns="http://xspf.org/ns/0/">
    <tracklist>
'''
        playlist = self.main.player.playlist
        for track in playlist:
            m3u += track.stream+"\n"
            xspf += "    <track>\n      <title>%s</title>\n       <creator>%s</creator>\n       <location>%s</location>\n    </track>\n" % (track.name, track.artist_name, track.stream)
        m3u = m3u[0:-1]
        xspf += '''\n    <tracklist>
</playlist>'''

        buttons = (gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL, gtk.STOCK_SAVE,   gtk.RESPONSE_OK)
        dialog = gtk.FileChooserDialog(_("Save Playlist"), None, action=gtk.FILE_CHOOSER_ACTION_SAVE, buttons=buttons, backend=None)
        filter1 = gtk.FileFilter()
        filter1.set_name("M3U Playlist Format")
        filter1.add_pattern("*.m3u")
        dialog.add_filter(filter1)
        filter2 = gtk.FileFilter()
        filter2.set_name("XSPF Playlist Format")
        filter2.add_pattern("*.xspf")
        dialog.add_filter(filter2)

        dialog.set_default_response(gtk.RESPONSE_OK)
        dialog.set_current_folder(os.getenv("HOME"))
        dialog.set_current_name("pyjama-playlist")

        response = dialog.run()
        dialog.hide()
        if response == gtk.RESPONSE_OK:
            filename = dialog.get_filename()
            if dialog.get_filter() == filter1: #IF M3U
                content = m3u
                if filename[-4:] != ".m3u":
                    filename += ".m3u"
            else: #XSPF
                content = xspf
                if filename[-5:] != ".xspf":
                    filename += ".xspf"
            if self.main.debug:
                print "Writing to %s" % filename
            fh = open(filename, "w")
            if fh:
                fh.write(content)
                fh.close()
            else:
                print ("Error writing %s") % filename

    def set_play(self):
        status = self.bPlay.tag
        if status == "play" or not status:
            status = "play"
        
        if status == "pause" and self.main.player.is_playing:
            self.main.player.pause()
            self.bPlay.setimage(gtk.STOCK_MEDIA_PLAY)
            self.main.icon.menu.switch_play_button("play")
            self.bPlay.tag = "play"
            return "paused"
        elif status == "play" and self.main.player.status == "paused":
            self.main.player.play()
            self.bPlay.setimage(gtk.STOCK_MEDIA_PAUSE)
            self.main.icon.menu.switch_play_button("pause")
            self.bPlay.tag = "pause"
            return "continued"
        elif status == "play":
            self.bPlay.setimage(gtk.STOCK_MEDIA_PAUSE)
            self.main.icon.menu.switch_play_button("pause")
            self.bPlay.tag = "pause"            
            return "play"
            

    def on_bPlay_pressed(self, widget, event):
        if event.button == 3:
            self.on_bStop_clicked(None)
        
    def on_bPlay_clicked(self, ev):
        stat =  self.set_play()
        if stat == "paused":
            return
        elif stat == "continued":
            return
        model, tmpIter = self.tvSelection.get_selected()
        if tmpIter != None:
            path = self.liststore.get_path(tmpIter)[0]
            self.main.player.play(self.main.player.playlist[path], path)
            self.main.timer_event()
#            if not self.main.timer:
#                self.main.start_timer()
        else:
            model = self.tvPlaylist.get_model()
            # improve this
            try:
                tmpIter = model.get_iter(0)
            except ValueError:
                return None
            path = self.liststore.get_path(tmpIter)[0]
            self.main.player.play(self.main.player.playlist[path], path)
            self.main.timer_event()
#            if not self.main.timer:
#                self.main.start_timer()

                
    def on_bStop_clicked(self, ev):
        self.main.icon.menu.switch_play_button("play")
        self.bPlay.setimage(gtk.STOCK_MEDIA_PLAY)
        self.bPlay.tag = "play"
        listview, markedIter = self.tvPlaylistSelection.get_selected()
        
        # Unmark last played Item
        if markedIter != None and self.main.player.cur_playing != None:
            track = self.main.player.cur_playing
            artist_name = track.artist_name
            track_name = track.name
            track_numalbum = track.numalbum
            markup = self.markupNormalEntry.replace("__ARTIST__", artist_name).replace("__TITLE__", track_name).replace("__NUM__", str(track_numalbum))
            self.liststore.set(markedIter, 0, markup)

        self.main.player.stop()

    def scrolled_window_resize(self, obj, gdkrect):
        self.scrolledwindow_width = gdkrect[2]
        self.scrolledwindow_height = gdkrect[3]
        if self.main.allow_rearrange:
            self.main.allow_rearrange = False
            self.main.Events.raise_event("scrolled_window_resized")
            gobject.timeout_add(200, self.main.set_allow_rearrange)

        
        #if self.main.allow_rearrange and self.main.layout_mode=="top":
            #self.main.allow_rearrange = False
            #self.main.arrange_topoftheweek()
            #gobject.timeout_add(200, self.main.set_allow_rearrange)
        #elif self.main.allow_rearrange and self.main.layout_mode=="artist":
            #self.main.allow_rearrange = False
            #self.main.arrange_artistdetail()
            #gobject.timeout_add(200, self.main.set_allow_rearrange)

    def show_about(self, widget=None):
        xml = gtk.glade.XML(os.path.join(functions.install_dir(), "about.glade"))
        about = xml.get_widget('About')

        img = None

        for child in about.vbox.get_children():
            if isinstance(child, gtk.VBox):
                for sub_child in child.get_children():
                    if isinstance(sub_child, gtk.Image):
                        img = sub_child
                        break
        if img is not None:
            animation = gtk.gdk.PixbufAnimation(os.path.join(functions.install_dir(), "images", "pyjama_anim.gif"))
#            img = gtk.Image()
            img.set_from_animation(animation)
#            img.show()
#            while gtk.events_pending():
#                 gtk.main_iteration()
#            about.vbox.pack_start(img, False, True)
        else:
            pixbuf = gtk.gdk.pixbuf_new_from_file(os.path.join(functions.install_dir(), "images", "pyjama.png"))
            about.set_logo(pixbuf)
        about.run()
        about.destroy()

    def get_active_text(self, combobox):
        model = combobox.get_model()
        active = combobox.get_active()
        if active < 0:
            return None
        return model[active][0]
        ## => active = combobox.get_active()

    def setStatus(self, text=""):
        self.message_id = self.sbStatus.push(self.context_id, text)

    def quit(self, widget, event ):
        #~ self.set_skip_taskbar_hint(True)
        self.do_events()
        self.iconify()
        return True
#        return None

    def really_quit(self, ev=None):
        if self.main.verbose:
            print "##########################################################"
            print ("Query Session Statistics:")
            print ("Cached Queries: %i") % self.main.jamendo.cache_counter
            print ("Jamendo Queries: %i") % self.main.jamendo.jamendo_counter
            print ("Database Queries: %i") % self.main.db.query_counter
            print ("Settings Database Queries: %i") % self.main.settingsdb.query_counter
            print "##########################################################"
            print ("Total Cache Statistics:")
            os.system("du -h %s" % os.path.join(functions.preparedirs(), "cache")) 
            print "##########################################################"
            print ("Cached Queries Total:")
            os.system("du -a %s|wc -l" % os.path.join(functions.preparedirs(), "cache")) 
            print "##########################################################"
            print ("Stored Images:")
            os.system("du -a %s|wc -l" % os.path.join(functions.preparedirs(), "images")) 
            print "##########################################################"
            print ("Stored Images Size:")
            os.system("du -h %s|cut -f 1" % os.path.join(functions.preparedirs(), "images")) 
            print "##########################################################"

        self.main.quit()
        #self.do_events()
        sys.exit(0)

        #~ gtk.main_quit()


    #def on_sbVolume_Change(self, range, scroll, value):
    def on_sbVolume_Change(self, widget, value):
        value = int(value)
        if value > self.main.settings.get_value("SOUND", "vol_max"): value = self.main.settings.get_value("SOUND", "vol_max")
        if value < 0: value = 0
        self.main.player.set_volume(value)

    def show_error_message(self, desc, tb, details=None, threadsafe=True):
        more_infos = None
        
        dia = gtk.Dialog()
        dia.set_size_request(400,-1)
        dia.set_icon_from_file(os.path.join(functions.install_dir(), "images", "pyjama.png"))

        lbl = gtk.Label()
        lbl.show()
        lbl.set_markup(str(desc))
        lbl.set_line_wrap(True)
        lbl.set_single_line_mode(False)
        dia.vbox.pack_start(lbl, True, True, 10)

        if tb.strip() != "None":
            more_infos == tb.strip()
        elif details is not None:
            more_infos = details

        if more_infos is not None:
            expander = gtk.Expander("Show/hide details")
            expander.show()
            sw = gtk.ScrolledWindow()
            sw.show()
            expander.add(sw)
            dia.vbox.pack_start(expander, True, True, 10)

            textview = gtk.TextView()
            textview.show()
            sw.add(textview)
            textbuffer = gtk.TextBuffer()
            textview.set_buffer(textbuffer)
            textbuffer.set_text(more_infos)


        dia.set_title("An Error occured")
        dia.add_button(gtk.STOCK_OK, -1)
        if threadsafe:
            gtk.gdk.threads_enter()
        dia.run()
        dia.destroy()
        if threadsafe:
            gtk.gdk.threads_leave()

    def check_alldone(self):
        return self.__alldone

    def do_events(self):
        i = 0
        try:
            max = self.main.settings.get_value("PERFORMANCE", "max_iterations_while_events_pending", 50)
        except:
            max = 50

        while gtk.events_pending():
            if i > max:
                print ("To much interations, breaking events_pending() loop")
                break
            gtk.main_iteration()
#            i += 1

    def setcolor(self, widget):
        if self.main.nocolor:
            return None 
        style = widget.get_style()
        color = widget.get_colormap()
        bg = color.alloc_color(self.bgcolor)#(20000,20000,65000,0)
        fg = color.alloc_color(0, 0, 0, 0)
        style.bg[gtk.STATE_NORMAL] = bg
        style.fg[gtk.STATE_NORMAL] = fg
        widget.set_style(style)



###########################################################
#                                                         #
#                                                         #
#         Special functions for creating imagepacks       #
#                                                         #
#                                                         #
###########################################################
    ## I use this functions to create imagepacks. You can 
    # download them using the imagepack-plugin. You should
    # not actually run this code.
    def __special_checks(self):
        # The following lines download all album-covers
        # from jamendo which aren't on disc, yet.
        # It was only used once to generate an image-pack.
        # Notice: The md5 hash is generated from the get2
        # query ('image_name'). The image itself is downloaded
        # directly from jamendo's server in order not to 
        # overun the get2-interface.
        if "create-imagepack" in sys.argv:
            ID = 0
            LICENSE = 1
            ARTIST = 2
            ALBUM = 3
            ARTIST_URL = 4
            sql = "SELECT albums.id, albums.license_artwork, artists.name, albums.name, artists.url FROM albums, artists WHERE albums.artist_id=artists.id"
            print ("Now querying the database - this will take a while")
            ret = self.main.db.query(sql)
            print ("Done - will now create the imagepack")

            images = ""
            last_percentage = 0.0
            total = len(ret)*1.0
            counter = 1

            txt = "<html><body>\nPyjama's imagepacks contains cover-images of albums that are free available @ jamendo.com<br />\n"
            txt += "Each image is property of it's author and comes with a own license.<br />\n"
            txt += "In the following table you can look up informations for each image by its name in the imagepack.<br /></br>\n"
            txt += "<table><tr><td>MD5 Hash</td><td>Artist</td><td>Album</td><td>License</td></tr>\n"


            download_counter = 0
            for item in ret:
                album_id = item[ID]
                image_name = "http://api.jamendo.com/get2/image/album/redirect/?id=%s&imagesize=100" % album_id
                image_url = "http://imgjam.com/albums/%i/covers/1.100.jpg" % album_id
#                images += "%s\n" % image
                md5hash = hashlib.md5(image_name).hexdigest()

                album_name = item[ALBUM]
                if len(item[ALBUM]) > 20:
                    album_name = "%s[...]%s" % (item[ALBUM][:17], item[ALBUM][-3:])
                artist_name = item[ARTIST]
                if len(item[ARTIST]) > 20:
                    artist_name = "%s[...]%s" % (item[ARTIST][:17], item[ARTIST][-3:])

                txt += "<tr><td><a href = 'http://imgjam.com/albums/%i/covers/1.100.jpg'>%s</a></td><td><a href = '%s'>%s</a></td><td><a href='http://www.jamendo.com/album/%i'>%s</a></td><td><a href = '%s'>LICENSE</a></td></tr>\n" % (item[ID], md5hash, item[ARTIST_URL], artist_name, item[ID], album_name, item[LICENSE])

                fh = os.path.join(self.main.home, "images", md5hash)
                perc = float(counter/total*100.0)
                if not os.path.exists(fh):
                    try:
                        download_counter += 1
                        print ("Dowload #%i, Album %i - %f%%" %  (download_counter, album_id, perc))
                        urllib.urlretrieve(image_url, fh)
                        sleep(4)
                    except IOError:
                        print ("Could not load image")
                        #return None
                else:
                    if perc >= last_percentage + 0.3:
                        print ("Album %i already downloaded - (%f%%)" % (album_id, perc))
                        last_percentage = perc
                counter += 1
            print ("%i images downloaded" % download_counter)
            print ("Creating archive")
            tf = tarfile.open("imagepack.tar.gz", "w:gz")
            tf.add(os.path.join(self.main.home, "images"), arcname="images", recursive=True)
            filename = self.__info_file("create")
            if filename is not None:
                tf.add(filename, arcname="README.TXT")
                self.__info_file("delete")
            tf.close()

            print ("Now writing license informations")
            txt += "</table></body></html>"
            fh = open("imagepack-license-infos.htm", "w")
            if fh:
                fh.write(txt)
                fh.close()

            print ("Done")
            sys.exit(0)

            #fh = open("imagelist", "w")
            #if fh:
                #fh.write(images)
                #fh.close()

        # These lines create an "smart" image pack
        # with covers of popular albums
        if "create-smart-imagepack" in sys.argv:
            path = os.path.join(self.main.home, "smart_image_pack")
            if not os.path.exists(path):
                os.mkdir(path)
            query1 = "id/album/json/?n=100&order=ratingmonth_desc"
            query2 = "id/album/json/?n=100&order=rating_desc"
            query3 = "id/album/json/?n=100&order=ratingweek_desc"
            query4 = "id/album/json/?n=100&order=downloaded_desc"
            query5 = "id/album/json/?n=100&order=listened_desc"
            query6 = "id/album/json/?n=100&order=stared_desc"
            for query in [query1, query2, query3, query4, query5, query6]:
                ret = self.main.jamendo.query(query)
                images = ""
                total = len(ret)*1.0
                counter = 1
                for item in ret:
                    album_id = item
                    image_name = "http://api.jamendo.com/get2/image/album/redirect/?id=%s&imagesize=100" % album_id
                    image_url = "http://imgjam.com/albums/%i/covers/1.100.jpg" % album_id
    #                images += "%s\n" % image
                    md5hash = hashlib.md5(image_name).hexdigest()
                    fh = os.path.join(self.main.home, "smart_image_pack", md5hash)
                    test_image = os.path.join(self.main.home, "images", md5hash)
                    perc = float(counter/total*100.0)
                    if os.path.exists(fh):
                        print ("%s alrady exists" % fh)
                    elif os.path.exists(test_image):
                        print ("copied %s from %s" % (fh, test_image))
                        shutil.copy(test_image, fh)
                    else:
                        try:
                            print ("Downloading", album_id, " (%f)" % perc)
                            urllib.urlretrieve(image_url, fh)
                            sleep(1)
                        except IOError:
                            print ("Could not load image")
                            return None
    #                else:
    #                    print (album_id, " already downloaded", " (%f)" % perc)
                    counter += 1
                sleep(1)
            print ("Creating archive")
            tf = tarfile.open("smart-imagepack.tar.gz", "w:gz")
            tf.add(path, arcname="images", recursive=True)
            filename = self.__info_file("create")
            if filename is not None:
                tf.add(filename, arcname="README.TXT")
                self.__info_file("delete")
            tf.close()
            print ("Done")
            sys.exit(0)

        #
        # Find images which were downloaded from the
        # url http://imgjam.com/albums/%i/covers/1.100.jpg
        #
        if "find-wrong-image-uris" in sys.argv:
            sql = "SELECT id FROM albums WHERE 1"
            ret = self.main.db.query(sql)
            filelist = os.listdir(os.path.join(self.main.home, "images"))

            delete_counter = 0
            total = len(ret) * len(filelist)
            counter = 1.0
            for fl in filelist:
                print float(counter/total*100.0)
                for item in ret:
                    counter += 1.0
                    album_id = item[0]
                    image_name = "http://imgjam.com/albums/%i/covers/1.100.jpg" % album_id
                    md5hash = hashlib.md5(image_name).hexdigest()
                    if fl == md5hash:
                        if "delete-those" in sys.argv:
                            f = os.path.join(self.main.home, "images", fl)
                            try:
                                os.remove(f)
                                delete_counter +=1
                                print("%i: Deleted %s" % (delete_counter, f))
                            except:
                                print("Error deleting %s" % f)
                        else:
                            print fl, image_name

        #
        # Print every image that is not a regular album image
        # Warning: This prints also album images and album covers
        # with a size > 100px
        #
        if "print-none-album-covers" in sys.argv:
            sql = "SELECT id FROM albums WHERE 1"
            ret = self.main.db.query(sql)
            filelist = os.listdir(os.path.join(self.main.home, "images"))
            for fl in filelist:
                ok = False
                for item in ret:
                    counter +=1
                    album_id = item[0]
                    image_name = "http://api.jamendo.com/get2/image/album/redirect/?id=%s&imagesize=100" % album_id
                    md5hash = hashlib.md5(image_name).hexdigest()
                    if fl == md5hash:
                        ok = True
                if not ok:
                    print ("Not ok: %s" % fl)

        if "country-check" in sys.argv:
            sql = "SELECT country FROM artists WHERE 1"
            ret = self.main.db.query(sql)
            cts = {}
            for item in ret:
                country = item[0]
                try:
                    cts[country] +=1
                except:
                    cts[country] = 1
            for x in cts:
                if cts[x] > 0:
                    print x, cts[x]
            print ("Total num of countries: %s" % len(cts))
            sys.exit(1)

    def __info_file(self, mode="delete"):
        filename = "5987635.txt"
        if mode != "delete":
            fh = open(filename, "w")
            if fh:
                fh.write("The covers in this archive belong to albums which are available for free at www.jamendo.com.\nThey are property of their artist who released them under certain licenses.\nYou can find out which cover is released under which license by calling\n\n http://xn--ngel-5qa.de/pyjama/release/imagepack-license-infos.htm\n\n On this page every cover of the imagepack is listed.")
                fh.close()
                return filename
        else:
            if os.path.exists(filename):
                os.remove(filename)
