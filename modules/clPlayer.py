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

######################################################################
#                                                                    #
#                THIS INTERFACE IS DEPRECATED                        #
#                                                                    #
######################################################################

######################################################################
#
# This is pyjama's old MOC interface. It was just used for testing 
# resons while i've been looking for a proper replacement which
# has been found in gstreamer0.10
#

import os#, sys

# Time formatting
from time import strftime, gmtime, time

# Pipes
import subprocess

from constants import *
import functions

# Gettext - Übersetzung
functions.translation_gettext()
#def notrans((string):
#    return string

def notrans(txt):
    return txt

###################################################################
#
# converts seconds into a more readable string
# RETURNS: string
#
def sec2time(seconds):
    time_string = strftime("%M:%S", gmtime(seconds))
    return time_string

class Player:
    def __init_notrans((self, parent):
        self.main = parent
        self.cur_playing = None
        self.last_played = None
        self.connection_tries = 0

        self.artist_counter = {}
        self.album_counter = {}
        self.track_counter = {}

        self.playlist = {}
        self.playlist_track_uids = []
        
        self.percentage = None
        self.text = None
        self.status = None 
        self.cursec = None
        self.duration = None
        self.togo = None
        self.artist_name  = None
        self.track_name = None
        self.numalbum = None

    ###################################################################
    #
    # adds a track-object to the playlist
    # RETURNS: n/A
    #
    def add2playlist(self, track):
        count = len(self.playlist)
        self.playlist[count] = track
        self.playlist_track_uids.append(track['uid'])

    ###################################################################
    #
    # guess what: clear playlist 
    # RETURNS: n/A
    #
    def clearplaylist(self):
        self.cur_playing = None
        self.last_played = None
        self.playlist = {}
        self.playlist_track_uids = []

    ###################################################################
    #
    # checks status of mocp
    # RETURNS: None if not playing, otherwise mocp status-infos
    #
    def check_status(self):
        if self.status == "End":
            return None
        if self.cur_playing == None: 
            self.status =  "End"
        else:
            ret = self.__pipe("mocp -i")
            if self.main.debug_extreme:
                print ret
            if ret == None: #Fehler
                self.status = "Error"
            elif ret[0].strip() == "State: STOP":
                self.connection_tries +=1
                if self.connection_tries >= CONNECTION_TRIES:
                    # SINCE JAMENDO DOES NOT HAVE
                    # SONGLENGTHS FOR EVERY TRACK
                    # WE JUST PLAY THE NEXT TRACK
                    # AFTER 5 RETRIES
                    self.next()
                    #self.cur_playing = None
                    #self.main.stop_timer()
                    #self.status = "Stop"
                else:
                    #self.main.start_timer()
                    self.status = "Buffering %s" % (self.connection_tries*".")
            else:
                self.status = "Playing"
                self.cursec =  int(ret[7].replace("CurrentSec: ", "").strip())
                self.duration = int(self.cur_playing['duration'])
                self.percentage =  (1.0 / self.duration) * self.cursec
                self.togo = self.cursec - self.duration
                self.artist_name = self.cur_playing['artist_name']
                self.track_name = self.cur_playing['name']
                self.numalbum = self.cur_playing['numalbum']
                self.text = "%s:%s: %s / %s - %s" % (self.cur_playing['artist_name'] ,self.cur_playing['name'], sec2time(self.cursec), sec2time(self.duration), sec2time(self.togo*-1))
                if self.togo == -1:
                    uid = self.cur_playing['uid']
                    if uid in self.playlist_track_uids:
                        pos = self.playlist_track_uids.index(uid)
                        if len(self.playlist)> pos+1:
                            self.play(self.playlist[pos+1], pos+1)

    ###################################################################
    #
    # a tiny little pipe
    # RETURNS: string
    #
    def __pipe(self, command):
        p = subprocess.Popen(command, bufsize=0, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
        return p.stdout.readlines()

    ###################################################################
    #
    # set volume via mocp
    # RETURNS: n/A
    #
    def set_volume(self, volume):
        mocp = "mocp -v %s" % volume
        os.system(mocp)

    ###################################################################
    #
    # remove a track from playlist
    # RETURNS: n/A
    #
    def remove(self, items):
        for item in items:
            del self.playlist[item]
            self.playlist_track_uids = []
        pl = {}
        counter = 0
        for x in self.playlist:
            pl[counter] = self.playlist[x]
            self.playlist_track_uids.append(self.playlist[x]['uid'])
            counter += 1
        self.playlist = pl
            
        
    ###################################################################
    #
    # play next track in playlist
    # RETURNS: n/A
    #
    def next(self):
        uid = self.cur_playing['uid']
        if uid in self.playlist_track_uids:
            pos = self.playlist_track_uids.index(uid)
            if len(self.playlist)> pos+1:
                self.play(self.playlist[pos+1], pos+1)
            else:
                self.status = "End"

    ###################################################################
    #
    # play previous track in playlist
    # RETURNS: n/A
    #                
    def prev(self):
        uid = self.cur_playing['uid']
        if uid in self.playlist_track_uids:
            pos = self.playlist_track_uids.index(uid)
            if pos-1 >= 0:
                self.play(self.playlist[pos-1], pos-1)

    ###################################################################
    #
    # ???
    # RETURNS: n/A
    #
    def test(self, array, key):
        if array.has_key(key):
            array[key] += 1
        else:
            array[key] = 1
#        print array[key]

    ###################################################################
    #
    # play a track
    # RETURNS: n/A
    #            
    def play(self, track, activate_item=None):
        self.test(self.artist_counter, track['artist_id'])
        self.test(self.album_counter, track['album_id'])
        self.test(self.track_counter, track['id'])
        if track['stream'] == "query":
            track['stream'] = self.main.jamendo.stream(track['id'])
        if track['duration'] == 0:
            #GET FROM JAMENDO
            track['duration'] = -1
        x = "mocp -l " +  track['stream']
        ret = os.system(x)
        if ret <> 0:
            print notrans(("Error running moc")
            print notrans(("Sometimes deleting '~/.moc' helpes")
        self.connection_tries = 0
        self.last_played = self.cur_playing
        self.cur_playing = track
        self.status = "Starting"
        #self.main.start_timer()
        img = self.main.get_album_image(self.cur_playing['album_id'])
        self.main.notification(notrans(("Now playing"), "<b><i>%s</i></b>:\n%s" % (track['artist_name'], track['name']), icon = img, size = NOTIFICATION_COVER_SIZE)
        if activate_item != None:
            self.main.setplaylist(activate_item)

    ###################################################################
    #
    # stop playing
    # RETURNS: n/A
    #        
    def stop(self):
        self.percentage = None
        self.text = None
        self.cursec = None
        self.duration = None
        self.togo = None
        self.artist_name  = None
        self.track_name = None
        self.numalbum = None
        self.status = "End"
        x = "mocp -s"
        os.system(x)
