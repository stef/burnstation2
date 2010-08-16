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

# ----------------------------------------------------------------------------
# This is pyjama's main class. It holds allmost every other class, which
# is needed. If you are writing plugins, this main class will be passed
# to you plugin's __init__ function!
# ----------------------------------------------------------------------------

## @package clMain
# Pyjama's main class 'main' will be given
# to any derived class.
# (Almost) any class is referenced here.

from math import floor
from time import strftime, gmtime, time, sleep

import urllib
import hashlib

from threading import Thread

import traceback 
import os
import sys
import re


#
# Pyjama Modules
#
try:
    import clXMLRPC
    XMLRPC_AVAILABLE = True
except:
    XMLRPC_AVAILABLE = False
    print ("Error import clXMLRPC")

try:
    import gnome.ui
    GNOME_UI_AVAILABLE = True
except:
    GNOME_UI_AVAILABLE = False
import functions
import clSettings
import clJamendo
#if os.name == "posix" or "mac" or "OVERRIDE-PLAYER" in sys.argv:
#    import clGstreamer010 as PLAYER
#else:
#    import clPlayerForWin as PLAYER
import clGstreamer010 as PLAYER
#import clDB
import dbthreaded
import clThreadedDownload #clPlayer
from clWidgets import *
import clEntry#, clProgressWindow
import clPlugin, clEvent
import notification
import clBrowserInterface
import download_db
import clLayouts
import clPreferences
from extended_modules import clPlaylists
from extended_modules import clBookmarks
try:
    import download_db as update
except:
    print ("Error importing update module")

## Pyjama's main class which is passed to most modules as pyjama
class main():
    ## The Constructor
    # @param self Object Pointer
    # @param parent The class calling pyjama.
    # In this case this is clWindow. Since 'main'
    # is thought to be the main class, parent is later
    # treated as if it was a child of 'main'
    # @param options  A OptionParser object
    def __init__(self, parent, options):
        ## Holds a bool indicating if pyjama is running verbose
        self.verbose = options.verbose
        ## Holds a bool indicating if pyjama is running in debugging mode
        self.debug = options.debug
        ## Holds a bool indicating if pyjama is running in debugging extreme mode
        self.debug_extreme = options.debug_extreme
#        self.print_tracebacks = options.print_tracebacks
        
        ## Hold pyjama's current version
        self.version = functions.VERSION
        if GNOME_UI_AVAILABLE:
            gnome.init("Pyjama", self.version)
        print "PYJAMA FOUND IN %s" % functions.install_dir()


        ## In some cases to many windows pop up on pyjama's
        # startup. If you want to popup a message on startup
        # please wait until need_attention is False!
        self.need_attention = False

        ## Pyjama's Event class
        self.Events = clEvent.Events()
        # Create some events:
        self.Events.add_event("pluginloaded")
        self.Events.add_event("nowplaying")
        self.Events.add_event("alldone")
        self.Events.add_event("showing_album_page")
        self.Events.add_event("showing_artist_page")
        self.Events.add_event("firstrun")
        self.Events.add_event("error")
        self.Events.add_event("info")
        self.Events.add_event("info")
        self.Events.add_event("layout_changed")
        self.Events.add_event("populate_listmenu")
        self.Events.add_event("populate_playlistmenu")
        self.Events.add_event("scrolled_window_resized")
        self.Events.add_event("playlist_tooltip")
        self.Events.add_event("quit")
        self.Events.add_event("albuminfo_created")
        self.Events.add_event("hide_controls")
        self.Events.add_event("show_controls")


        ## Connect to some events
        self.Events.connect_event("pluginloaded", self.ev_plugin_loaded)
        self.Events.connect_event("error", self.error)
        self.Events.connect_event("info", self.info)
        
        self.home_fkt = self.go_home_fkt

        ## Pyjama's Settings class
        # Use for simple general settings
        # data will be stored in a pyjama.cfg
        self.settings = clSettings.settings(self)

        ## Pyjama's database setting class
        # Use this, if you need to store many
        # values.
        self.settingsdb = dbthreaded.DB_Settings(self)
#        self.settingsdb = clDB.DB_Settings(self)
        ## Database class  clDB.DB
        self.db = dbthreaded.DB(self)
#        self.db = clDB.DB(self)

        ## Some database-dump tools
        self.dump_tools = download_db.dump_tools(self)
        ## The clWindow.gtkWIN reference 
        self.window = parent
        ## The notification TrayIcon class notification.TrayIcon
        self.icon = notification.TrayIcon(self)
        ## The Audio class clGstreamer010.Player
        self.player = PLAYER.Player(self, sink=self.__get_audio_interface())
        ## Pyjama's class for jamendo's get2 api clJamendo.Jamendo
        self.jamendo = clJamendo.Jamendo(self)
        ## The browser class clBrowserInterfacce.Browser for handling
        # different browser calls
        self.browser = clBrowserInterface.Browser(self)
        ## Pyjama's clLayouts.Layouts is referenced here
        # it is most important for anything to show up in the
        # main paned field
        self.layouts = clLayouts.Layouts(self)
        ## Preferences
        self.preferences = clPreferences.Preferences(self)

        if XMLRPC_AVAILABLE:
            self.xmlrpc = clXMLRPC.XMLRPC(self)
        
            for item in sys.argv:
                if item.endswith(".m3u"):
                    if self.xmlrpc.role == "client":
                        try:
                            self.xmlrpc.server.test("test123")
                        except Exception, inst:
                            print ("Could not connect to server: %s" % inst)
                            break

        ## A bool indicating if theming is used or not
        self.nocolor = options.theme != None or options.nocolor
        ## Switches every 200 ms to rearrange widgets if the
        # window size changed
        # \todo Improve since this is really ugly!
        self.allow_rearrange = True

        ## Pyjama's home directory
        self.home = functions.preparedirs()
        ## Stores the currently marked item 
        self.tvMarkedItem = None

        ## If one sets this attrib to a string
        # which is an file's uri, pyjama will
        # load that file as a playlist and set
        # this attrib to None again
        self.playlist_to_load = None
        
        # Tracks currently shown in draw_albumdetail
        # This was replaced through StockBotton- Tags!
        #self.tracks = {}
        
        # Is the Timer running?
#        self.timer = False

        ## Function to call when a database should be downloaded
        self.download_database = self.simple_database_downloader

        ## Bool - is the progressbar pulsing?
        self.pulsing = False
        
        ## List storing history_back items
        self.historyBack = []
        ## List storing history_forward items
        self.historyForward = []
        ## Dictionary stroing the currently shown page
        self.historyCurrent = {}

        #
        # Load additional modules
        #
        # Some modules have been plugins before that were moved
        # here in order not to bloat the plugin interace to much.
        # I think it is a good decision to not implement extended
        # functionality in the main source.
        print ("Loading modules")
        self.playlists = clPlaylists.main(self)
        self.bookmarks = clBookmarks.main(self)

        ## If a playlist was given:
        if len(sys.argv)>1:
            if os.path.exists(sys.argv[1]):
                if self.check_another_instance_running() is True:
                    
                    try:
                        self.xmlrpc.send_playlist(sys.argv[1])
                        sys.exit(0)
                    except Exception, inst:
                        print ("Error passing the playlist to the running instance - will no play it in this instance: %s" % inst)
                        #self.playlists.open_playlist_from_file(sys.argv[1])
                        self.playlist_to_load = sys.argv[1]
                else:
                    # if no other instance was found, this instance
                    # will play the playlist
                    #~ self.playlists.open_playlist_from_file(sys.argv[1])
                    self.playlist_to_load = sys.argv[1]

        ## clPlugin.Plugins class referenced here.
        # Loaded last to have any other class loaded
        # for the plugins
        self.plugins = clPlugin.Plugins(self)
        if self.settings.get_value("PYJAMA", "FIRST_RUN", True) == True:
            self.Events.raise_event("firstrun")
            self.settings.set_value("PYJAMA", "FIRST_RUN", "False")

#        self.Events.raise_event("error", None, "test1")
#        self.Events.raise_event("error", None, "test2")

        # decided to let the timer run all the time
        self.start_timer()
    

#        self.plugins.loaded['test2'].test()

        if os.name != "posix" and os.name != "mac" and not "OVERRIDE-PLAYER" in sys.argv:
            self.Events.raise_event("info", text="You are running pyjama on windows. As far as I tested it, it worked fine except from the player support.\nFor this reason for windows the module <i>clPlayerForWin</i> was loaded for playback. This is only a hack for testing reasons, if you want to try out <i>clGstreamer010</i>, run pyjama with '<b>pyjama OVERRIDE-PLAYER</b>'")

    ## Navigate to pyjama's default page
    # shown at startup
    # @param self The Object Pointer
    def go_home(self):
        self.jamendo.last_query_hack()
        self.home_fkt()

    ## Pyjama's default home-function showing
    # 10 best rated albums of this week
    # @param self The Object Pointer
    def go_home_fkt(self):
        self.layouts.show_layout("top", 10, "ratingweek", 1, "all", who_called = "on_bHome_clicked")

    ## Set a new function to call when go_home() is called
    # @param self The Object Pointer
    # @param fkt The function to call when go_home() is called
    def set_home_fkt(self, fkt):
        self.home_fkt = fkt

    
    def __get_audio_interface(self):
        audio = self.settings.get_value("SOUND", "audiointerface", "alsa")
        if audio == "alsa":
            return "alsasink"
        else:
            return "pulsesink"

    ## Read a jamendo m3u playlist file and populates the playlist with that
    # @param playlist The playlist's uri
    # @return List with track ids
    def read_playlist(self, playlist):
            if self.debug:
                print "Loading Playlist %s" % playlist
            fh = file(playlist, "r")
            if fh:
                lines = fh.readlines()
                fh.close()
            else:
                print ("Error reading %s") % playlist
                return

            for line in lines:
                if "xspf.org" in line:
                    lines = functions.read_xspf_playlist(playlist)
                    if lines is None:
                        print ("Error parsing '%s' as xspf playlist" % playlist)
                        return
                    break

            if True:#dialog.get_filter() == filter1: #M3U
                track_ids = []
                tracks = []
                rg1 = re.compile('.*?\\d+.*?(\\d+)',re.IGNORECASE|re.DOTALL)
                rg2 = re.compile('.*?(\/)(stream)(\/)(\d+)',re.IGNORECASE|re.DOTALL)
                for line in lines:
                    if "jamendo.com/get2/stream/track/redirect/?id=" in line:
                        m = rg1.search(line.strip())
                        if m:
                            track_id=m.group(1)
                            track_ids.append(int(track_id))
                    elif "jamendo.com/stream/" in line:
                        m = rg2.search(line.strip())
                        if m:
                            track_id=m.group(4)
                            track_ids.append(int(track_id))
                    elif line.startswith("#"):
                        pass
                    else:
                        print ("This is not a Jamendo track or not readable with pyjama: %s") % line.strip()
                return track_ids

    ## Downloads the database from jamendo and 
    # prints all messages to console
    # @param self Object Pointer
    # @param force_jamendo If set to True the database 
    # will be downloaded directly from jamendo,
    # if set to False, the database will be downloaded
    # from a mirror
    def simple_database_downloader(self, force_jamendo=False):
        dia = gtk.MessageDialog(self.window, gtk.DIALOG_MODAL, gtk.MESSAGE_INFO, 0, _("Downloading database dump from Jamendo right now. Please be patient.\n\nFor more information please run Pyjama from console.\n\nThis might take up to a minute"))
        dia.show()
        self.window.do_events()
        dump = update.dump_tools()
        dump.delete_db()
        dump.create_tables()
        ret = dump.create_db(force_jamendo)
        if ret == "nofile":
            if force_jamendo:
                 self.Events.raise_event("error", None, "Error downloading the database dump from jamendo. Please try again later and notify me about this.")
            else:
                self.Events.raise_event("error", None, "Error downloading the database dump from the mirror.\nPlease try running 'pyjama --update-jamendo' in order to get the database right from jamendo.")
            dia.destroy()
            return
        dump.finish()
        dia.destroy()

        self.db = dbthreaded.DB(self)
        self.window.sbStatus.set_text("Counter", _("Artists: %i, Albums: %i, Tracks: %i") % (self.db.artists, self.db.albums, self.db.tracks))

    ## Sets a download function for jamendo's database
    # @param self Object Pointer
    # @param fkt The function to run
    def set_download_database_fkt(self, fkt):
        self.download_database = fkt

    ## Show the plugin dialog
    # @param self Object Pointer
    # @param event Dummy param for callbacks
    # @return None
    def show_plugins(self, event=None):
        clPlugin.ShowPluginsDialog(self)

    ##  Show the preferences dialog
    # @param self OP
    # @param widget Dummy param for callbacks
    # @param name Set this for a module's / plugin's
    # name in order to show its page on start
    def show_preferences(self, widget=None, name=None):
        self.preferences.show_preferences(name)

    ## This function can only tell if another  instance is
    # running but not, if NO other instance is running
    # @return True if another instance is running, None if undecideable(?)
    def check_another_instance_running(self):
        if XMLRPC_AVAILABLE:
            self.xmlrpc.test()
            if self.xmlrpc.role == "client":
                return True
            else:
                return None
        else:
            return None

    ## Quit some running processes
    # usually called by window.really_quit()
    def quit(self):
        print ("Quitting...")
        print ("... settings database,")
        self.settingsdb.quit()
        print ("... main database,")
        self.db.quit()

        print ("... sending 'quit' signal,")
        self.Events.raise_event("quit")
        
        print ("... marking shutdown as clean,")
        self.settings.set_value("PYJAMA", "crashed", False)

        print ("... shutting down XMLRPC Server.")
        self.xmlrpc.quit()
        print ("Done.")

    ## Reloads the current layout page
    # @param self Object Pointer
    # @param event Dummy param for callbacks
    # @param ignore_cache Bool indicating if reload should be cached or not.
    # Set it to True if you want pyjama to reload this query from Jamendo
    # @return None
    def reload_current_page(self, ev=None, ignore_cache=False):
        # save scroll position for scrolledwindow
        adjustment = self.window.scrolledwindow.get_vadjustment()
        self.window.scrolledwindow.hide()

        if ignore_cache is True:
            self.jamendo.set_ignore_cache(True)

        # reloading page
        data = self.historyCurrent
        self.layouts.show_layout(data['layout'], data['data1'], data['data2'], data['data3'], data['data4'], fromhistory=True, who_called='reload_current_page')

        self.jamendo.set_ignore_cache(False)

        # load scroll position
        self.window.scrolledwindow.set_vadjustment(adjustment)
        self.window.scrolledwindow.show()

    ## shows an info dialog
    def info(self, title="Information", text=""):
        dialog = MyDialog(title,self.window, \
            gtk.DIALOG_MODAL | gtk.DIALOG_DESTROY_WITH_PARENT, \
            (gtk.STOCK_OK, gtk.RESPONSE_ACCEPT), gtk.STOCK_DIALOG_INFO, text)
        dialog.set_icon_from_file(os.path.join(functions.install_dir(), "images", "pyjama.png"))
        dialog.run()
        dialog.destroy()


    ## Called whenever pyjama.Events.raise_event("error", *args) is fired.
    # Will print an error and its traceback to console
    # @param self Object Pointer
    # @param error_inst A short error message
    # @param desc Optional description of that error
    # @return None
    def error(self, error_inst, desc=False, details=None, threadsafe=False):
        print "An error occured: %s" % error_inst
        tb =  traceback.format_exc()
        print "-"*60
        print tb
        print "-"*60
        if details is not None:
            print details
            print "-"*60
        if not desc: 
            desc = error_inst
        print desc
        self.window.show_error_message(desc, tb, details, threadsafe=threadsafe)


    ## Called whenever pyjama.Events.raise_event("pluginloaded", *args) is fired.
    # Prints some infos for the loaded plugin to console
    # @param self Object Pointer
    # @param name The plugin's full name
    # @param version The plugin's version
    # @param order Plugin's order value (see clPlugin documentation)
    # @param mod_name Plugin's file name
    # @return None
    def ev_plugin_loaded(self, name, version, order, mod_name):# plugin_name, module_name):
#        if self.verbose:
        print ("Plugin '%s' V%s (%s) loaded") % (name, version, mod_name)

    ## Setting self.allow_rearrange.
    # This function is called by an gobject Timeout and allways return False
    # @param self Object Pointer
    # @return False
    def set_allow_rearrange(self):
        self.allow_rearrange=True
        return False


#    def check_next_possible(self, page=None, rpp=None):
#        if page == None: page = self.cur_page
#        if rpp == None: rpp = self.results_per_page
#        if page >= floor(self.db.albums / rpp) - 2:
#            self.window.sbNextPage.set_sensitive(False)
#        else:
#            self.window.sbNextPage.set_sensitive(True)

#    def check_prev_possible(self, page=None):
#        if page == None: page = self.cur_page
#        if page == 1:
#            self.window.sbPrevPage.set_sensitive(False)
#        else:
#            self.window.sbPrevPage.set_sensitive(True)
            

    ## Add a given list of track objects to playlist
    # @param self Object Pointer
    # @param tracks List of Tracks
    # @param play Optional bool. If this is set True 
    # pyjama will start playing the first track of the given list
    # @return None
    def appendtracks(self, tracks, play = False):
        cur = len(self.player.playlist)
        for track in tracks:
            track.uid = "%f%s" % (time(), track.uid)
            self.add2playlist(track)
            status = self.player.status
        if play:
            self.window.on_bStop_clicked(None)
            self.setplaylist(cur)
            self.window.on_bPlay_clicked(None)        

    ## Removes an item from the playlist
    # @param self Object Pointer
    # @param item Integer
    # @return None
    def remove_item_from_playlist(self, item):
        if item < self.tvMarkedItem:
            self.tvMarkedItem -= 1
        elif item == self.tvMarkedItem:
            self.tvMarkedItem = None
        self.player.remove(item)

    ## Moves an item in the playlist
    # @param self Object Pointer
    # @param s Source path of item moved
    # @param d Destination path of the item moved
    # @param before Indicates of the item is dropped after or before the destination
    # @return None
    def move_playlist_item(self, s, d, before): # sourcepath, destpath
        c = self.tvMarkedItem
        if d > s:
            if before: 
                bf = -1
            else:
                bf = 0
        else:
            if before: 
                bf = 0
            else:
                bf = 1
        dest = d + bf


        self.tvMarkedItem = dest
        self.player.move_item(s, d, before)


    ## Adds a single track to the playlist
    # @param self Object Pointer
    # @param track a Track
    # @return None
    def add2playlist(self, track):
        self.player.add2playlist(track)

        artist_name = track.artist_name
        track_name = track.name
        track_numalbum = track.numalbum

#        gtk.gdk.threads_enter()
        markup = self.window.markupNormalEntry.replace("__ARTIST__", artist_name).replace("__TITLE__", track_name).replace("__NUM__", str(track_numalbum))
        tmpIter = self.window.liststore.append([markup]) #, track.id
        path = self.window.liststore.get_path(tmpIter)
#        gtk.gdk.threads_leave()
#        tt = gtk.Tooltip()
#        tt.set_text("")
#        self.window.tvPlaylist.set_tooltip_row(tt, path)


    ## Set the Cover image and some other informations.
    # This methode is called whenever the mouse moves over
    # the playlist.
    # @param self Object Pointer
    # @param path Optional path of the playlist item to set cover for.
    # If this value is None, the currently selected item will be shown.
    # @return None
    def showInfo(self, path=None):
        if path == None:
            if self.tvMarkedItem != None and self.tvMarkedItem < len(self.player.playlist):
                path = self.tvMarkedItem
            else:
                return None
#        if path == None:
#            ret = self.window.tvPlaylistSelection.get_selected()
#            if ret != None:
#                model, retIter = ret
#                if retIter != None:
#                    path = model.get_path(retIter)[0]
#                else:
#                    return None
#            else:
#                return None
            
        track = self.player.playlist[path]
        #Covers = simplejson.loads(track['album_Covers'])

        self.window.lbCoverArtist.set_text(track.artist_name)
        self.window.lbCoverAlbum.set_text(track.album_name)

        # set image via thread
        thr = Thread(target = self.__get_image_for_showInfo, args = ([track]))
        thr.start()


    def __get_image_for_showInfo(self, track):
        img = self.get_album_image(track.album_id)
        if not img: 
            self.window.imgCover.set_from_stock(gtk.STOCK_MISSING_IMAGE, gtk.ICON_SIZE_DND)
        else:
            self.window.imgCover.set_from_file(img)

    ## Mark the currently played item and unmark the last played item
    # @param self Object Pointer
    # @param activate_item Path of the item to mark
    # @return None
    def setplaylist(self, activate_item):
        self.window.pbSong.set_fraction(0)
        self.window.pbSong.set_text("")

        model = self.window.tvPlaylist.get_model()
        retIter = model.get_iter(activate_item)
        self.showInfo(activate_item)

        # Unmark last played Item
        if self.tvMarkedItem != None and self.player.last_played != None and self.tvMarkedItem < len(self.player.playlist):
            track = self.player.last_played
            artist_name = track.artist_name
            track.name = track.name
            track.numalbum = str(track.numalbum)
            markup = self.window.markupNormalEntry.replace("__ARTIST__", artist_name).replace("__TITLE__", track.name).replace("__NUM__", track.numalbum)
            self.window.liststore.set(model.get_iter(self.tvMarkedItem), 0, markup)

        # Mark cur. played item
        
        self.window.tvSelection.select_iter(retIter)
        track = self.player.playlist[activate_item] #self.player.cur_playing
        artist_name = track.artist_name
        track.name = track.name
        track.numalbum = str(track.numalbum)
        markup = self.window.markupCurPlaying.replace("__ARTIST__", artist_name).replace("__TITLE__", track.name).replace("__NUM__", track.numalbum)
        self.window.liststore.set(retIter, 0, markup)
        # remember, which item is marked
        self.tvMarkedItem = activate_item

    ## Empty function
    # @param self Object Pointer
    # @return None
    def stop_timer(self):
        pass

    ## Start the gobject timer.
    # This will call timer_event every 200ms
    # @param self Object Pointer
    # @return None
    def start_timer(self):
        gobject.timeout_add(200, self.timer_event)
#        self.timer = True

    ## Start pulsing the progressbar
    # @param self Object Pointer
    # @param text Optional string. Will be set as text for the progressbar.
    # Will set "" if no value is given.
    # @return None
    def start_pulsing(self, text = ""):
        gobject.timeout_add(50, self.pulse)
        self.window.pbWait.set_fraction(0)        
        self.window.pbWait.set_text(text)
        self.window.pbWait.show()
        

    ## Will pulse the progressbar a step
    # @param self Object Pointer
    # @return 
    # - True if the progressbar is in pulsing mode
    # - False if the progressbar is in normal mode
    def pulse(self):
        self.window.pbWait.pulse()
        if self.pulsing:
            return True
        else:
            return False
    
    ## Stops pulsing
    # @param self Object Pointer
    # @return None
    def stop_pulsing(self):
        self.pulsing = False
        self.window.pbWait.hide()

    ## This event is called ever 200ms by start_timer().
    # This methods interacts with the player class and gets the current
    # track position and some other data. It sets the current status and
    # pulses the progressbar with pulse().
    # @param self Object Pointer
    # @return True to keep the gobject timer running.
    def timer_event(self):
#        ## check if a playlist file was copied to ~/.pyjama/jamendo-playlist.m3u
#        dest = os.path.join(self.home, "jamendo-playlist.m3u")
#        if os.path.exists(dest):
#            print "found file"
            
        # Populate the playlist if self.playlist_to_load
        # it not None
        if self.playlist_to_load is not None:
            if os.path.exists(self.playlist_to_load):
                self.playlists.open_playlist_from_file(self.playlist_to_load)
            self.playlist_to_load = None


        #self.window.pbWait.pulse()
        self.player.check_status()
        status = self.player.status
        trans_stat = _(status)
        fehler = ["Error", "Stop", "End", None]
        self.setStatus( trans_stat )
        if status == "paused":
            self.window.bPlay.setimage(gtk.STOCK_MEDIA_PLAY)
            self.window.bPlay.tag = "play"
            if self.window.pbSong.counter > 2:
                if self.window.pbSong.get_text() == _("paused"):
                    if self.window.pbSong.ShowRemainingTime:
                        txt =  "-%s" % functions.sec2time(self.player.togo*-1)
                    else:
                        txt = "%s/%s" % (functions.sec2time(self.player.cursec), functions.sec2time(self.player.duration))
                else:
                    txt = _("paused")
                if "00:00:00" in txt or txt == "-00:00": txt = "buffering... %i%%" % self.player.buffer
                if self.window.pbSong.get_text() != txt:
                    self.window.pbSong.set_text(txt)
                self.window.pbSong.counter = 0
            self.window.pbSong.counter +=1
            return True
        elif not status in fehler and self.player.percentage != None:
            if self.window.bPlay.tag != "pause":
                self.window.bPlay.setimage(gtk.STOCK_MEDIA_PAUSE)
                self.window.bPlay.tag = "pause"
            #print self.player.text
            if self.player.duration > 0 and self.player.duration < 59*60:
                if self.window.pbSong.get_fraction() != self.player.percentage:
                    self.window.pbSong.set_fraction(self.player.percentage)            
                if self.window.pbSong.ShowRemainingTime:
                    txt =  "-%s" % functions.sec2time(self.player.togo*-1)
                else:
                    txt = "%s/%s" % (functions.sec2time(self.player.cursec), functions.sec2time(self.player.duration))
            else:
                self.window.pbSong.pulse()
                txt = "%s" % functions.sec2time(self.player.cursec)
            if "00:00:00" in txt or txt == "-00:00": txt = "buffering... %i%%" % self.player.buffer
            if self.window.pbSong.get_text() != txt:
                self.window.pbSong.set_text(txt)
            return True
        elif status == "Stop" or status == "End": # and not self.pulsing:
            #self.window.bPlay.setimage(gtk.STOCK_MEDIA_PLAY)
            self.window.bPlay.tag = "play"
            if self.icon.menu.play_button_status != "play":
                self.icon.menu.switch_play_button("play")
            if self.window.pbSong.get_fraction() != 0:
                self.window.pbSong.set_fraction(0)
            if self.window.pbSong.get_text()!= "":
                self.window.pbSong.set_text("")
#            self.timer = False
            return True
        else:
            self.window.bPlay.tag = "play"
            return True

    ## Sets the "Info" column of the statusbar to text
    # @param self Object Pointer
    # @param text The text to set
    # @return None
    def setInfo(self, text):
        self.window.sbStatus.set_text("VarInfo", text)

    ## Sets the "Player" column of the statusbar to text
    # @param self Object Pointer
    # @param text The text to set
    # @return None
    def setStatus(self, text):
        self.window.sbStatus.set_text("Player", text)



    ## Shows a notification
    # @param self Object Pointer
    # @param caption The notification's caption as string
    # @param text The notification's text as stirng
    # @param icon The notification's icon as URI string
    # @param size The notification's icon size as int
    # @return None
    def notification(self, caption, text, icon="pyjama", size = 100):
        self.icon.show_notification(caption, text, icon, size)

    ## Iconifies the window to taskbar if its shown and shows the window
    # when its hidden.
    # @param self Object Pointer
    # @param ev1 Dummy param for callbacks
    # @return None
    def switch_window_state(self, ev1=None):
        if self.window.window.get_state() & gtk.gdk.WINDOW_STATE_ICONIFIED:
            self.window.deiconify()
            self.window.set_skip_taskbar_hint(False)
        else:
            self.window.set_skip_taskbar_hint(True)
            self.window.iconify()


    ## Downloads and caches an album's image from jamendo
    # @param self Object Pointer
    # @param album_id The album's id
    # @param size Optional size as int - default is 100
    # @return
    # - None if an error occures
    # - The file's URI as string if downloading was succesfull
    def get_album_image(self, album_id, size = 100):
        #~ print album_id
        download_from = "http://imgjam.com/albums/s%s/%s/covers/1.%i.jpg"  % (str(album_id)[0:2], album_id, size)
        name = "http://api.jamendo.com/get2/image/album/redirect/?id=%s&imagesize=%i" % (album_id, size)
        md5hash = hashlib.md5(name).hexdigest()
        fh = os.path.join(self.home, "images", md5hash)
        if not os.path.exists(fh):
            try:
                print("Downloading '%s'" % download_from)
                urllib.urlretrieve(download_from, fh)
            except IOError:
                print ("Could not load image")
                return None
        return fh

    def download(self, source, dest):
        try:
            urllib.urlretrieve(source, dest)
        except IOError, inst:
            print ("Could not load %s: %s" % (source, inst))
            return -1
