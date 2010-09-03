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


## @package clGstreamer010
# Pyjamas player module


import pygtk
pygtk.require('2.0')

import sys, os

import gobject

import pygst
pygst.require('0.10')
import gst
import gst.interfaces
import gtk
import random

# Needed to prevent that the *same*
# object appears to times in the playlist
import copy

# Time formatting
from time import strftime, gmtime, time

import functions

from modules import clDownloader

## Converts a given time from seconds to a more readable string
# @param seconds as int
# @return string
def sec2time(seconds):
    try:
        time_string = strftime("%M:%S", gmtime(seconds))
    except ValueError:
        return "00:00"
    return time_string

## The new track object replaces all those
# track-dicts
class Track:
    def __init__(self):
        self.name = None
        self.duration = None
        self.numalbum = None
        self.id = None
        self.license = None
        self.id3genre = None    

        self.album_id = None
        self.album_name = None

        self.artist_name = None
        self.artist_id = None

        self.stream = None
        self.local = None
        self.uid = None

        self.position_in_playlist = None

    ## This actually wraps my class into a dictionary :)
    # This methode was implemented for compability reasons
    # only and will be deleted some day.
    def __getitem__(self, item):
        print ""
        print "The track object now no longer is a dictionary"
        print "You can easily switch to the new track-object"
        print "by simply replacing track['%s'] through" % str(item)
        print "track.%s." % str(item)
        print ""
        print "Using a track object as a dictionary is deprecated!"
        return self.__dict__[item]


    def print_info(self):
        #return "Track: Artist: %s, Album: %s, Track: %s" % (self.artist_name, self.album_name, self.name)
        ret = ""
        for item in self.__dict__:
            ret += "%s: %s\n" % (item, str(self.__dict__[item]))
        return ret

    __call__ = print_info
    __str__ = print_info

class TrackError(Exception):
    pass

## !!! WORKING !!!
#gst-launch-0.10 uridecodebin uri=http://upload.wikimedia.org/wikipedia/commons/4/48/Frase_de_Neil_Armstrong.ogg ! volume volume=1.0 ! equalizer-10bands band0=12.0 band1=12.0 band2=12.0 ! pulsesink

## Pyjama's Player class based on gstreamer0.10
class Player:
    def __init__(self, parent, sink="alsasink"): #pulsesink
        print ("Will use %s" % sink)
    
        parent.Events.add_event("player-status")
        parent.Events.add_event('end_of_playlist')

        ## Boolean - is the player playing?
        self.playing = False

        ## current buffer
        self.buffer = 0

        BIN_TO_USE = "new"
        if "oldbin" in sys.argv: BIN_TO_USE = "old"

        self.equalizer_available = False
        self.equalizer_bands = 10

        ## The gstreamer player object
        if BIN_TO_USE == "new":
            self.player = gst.element_factory_make("playbin", "player")

            #equalizer-nbands num-bands=15 band5
            pipe = "audioresample ! audioamplify amplification=1.0 ! equalizer-10bands ! %s" % sink
            pipe = pipe.split(" ")
            #~ pipe = "audioresample ! equalizer-10bands band0=12.0 band1=12.0 band2=12.0 ! pulsesink".split(" ")
            
            self.bin = gst.Bin('my-bin')
            audioconvert = gst.element_factory_make('audioconvert')
            self.bin.add(audioconvert)
            pad = audioconvert.get_pad("sink")
            ghostpad = gst.GhostPad("sink", pad)
            self.bin.add_pad(ghostpad)
            
            
            next_is_pipe_element=True
            pipeel=None
            els=[audioconvert]
            i=0
            while len(pipe)>i:
                el=pipe[i]
                i+=1
                if el.strip()!="":
                    if el=="!":
                        next_is_pipe_element=True
                    else:
                        if next_is_pipe_element:
                            if parent.debug:
                                print ("pipe element: %s"%el)
                            if el.startswith('equalizer'):
                                pipeel = gst.element_factory_make(el)
                                self.eq=pipeel
                                self.bin.add(pipeel)
                                els.append(pipeel)
                            elif el.startswith('audioamplify'):
                                pipeel = gst.element_factory_make(el)
                                self.amp=pipeel
                                self.bin.add(pipeel)
                                els.append(pipeel)
                            elif el.startswith('audioresample'):
                                pipeel = gst.element_factory_make(el)
                                self.resample=pipeel
                                self.bin.add(pipeel)
                                els.append(pipeel)
                            elif el.startswith('audio/x-raw-int'):
                                caps = gst.Caps(el)
                                filter = gst.element_factory_make("capsfilter", "filter")
                                self.bin.add(filter)
                                filter.set_property("caps", caps)
                                els.append(filter)
                            else:
                                try:
                                    pipeel = gst.element_factory_make(el)
                                except gst.ElementNotFoundError:
                                    if el == "pulsesink":
                                        print ("Could not load pulseaudio interface.\nWill try ALSA now.")
                                        try:
                                            pipeel = gst.element_factory_make("alsasink")
                                        except:
                                            print ("ALSA also did not work")
                                            raise
                                    elif el == "alsasink":
                                        print ("Could not load ALSA interface.\nWill try pulseaudio now.")
                                        try:
                                            pipeel = gst.element_factory_make("pulseaudio")
                                        except:
                                            print("Pulseaudio also did not work")
                                            raise
                                    else:
                                        raise
                                self.bin.add(pipeel)
                                els.append(pipeel)

                            next_is_pipe_element=False
                        else:
                            data=el.split("=")
                            if parent.debug:
                                print ("\tproperty %s = %s"%(data[0],data[1]))
                            try:
                                if data[1].isdigit():
                                    val=int(data[1])
                                else:
                                    val=float(data[1])
                            except:
                                val=data[1]
                            pipeel.set_property(data[0],val)
                            
            
                    
            
            gst.element_link_many(*els)
            fakesink = gst.element_factory_make('fakesink', "my-fakesink")
            #self.player.set_property("video-sink", fakesink)
            self.player.set_property("audio-sink", self.bin)
            
            
            #~ bus = self.player.get_bus()
            #~ bus.add_signal_watch()
            #~ bus.connect('message', self.on_message)
            #~ self.player.set_state(gst.STATE_PLAYING)

            self.src = self.player
            self.volume = self.player

            self.equalizer_available = True
            
        elif BIN_TO_USE == "old":
            self.player = gst.element_factory_make("playbin", "player") # old playbin
            self.src = self.player
            self.volume = self.player
        else: ## not working pipe
            self.player = gst.Pipeline("pyjama_player")
            
            self.src = gst.element_factory_make("uridecodebin", "src")
            self.player.add(self.src)

            self.volume_bin = gst.element_factory_make("volume", "volume")
            self.player.add(self.volume_bin)

            self.equalizer_bin = gst.element_factory_make("equalizer-10bands", "equalizer")
            self.player.add(self.equalizer_bin)

            self.pulse_bin = gst.element_factory_make("pulsesink", "pulse") # alsasink
            self.player.add(self.pulse_bin)

        

        #
        # The following lines of code were meant to replace the playbin
        # for some reasons this didn't work for me
        #

        #        #gst-launch-0.10 souphttpsrc location=http://upload.wikimedia.org/wikipedia/commons/4/48/Frase_de_Neil_Armstrong.ogg ! decodebin ! audioconvert ! alsasink

        #        self.player = gst.Pipeline("pyjama_player")

        #        self.src = gst.element_factory_make("souphttpsrc", "src")
        #        self.player.add(self.src)
        #        self.decoder = gst.element_factory_make("decodebin", "decoder")
        #        self.player.add(self.decoder)
        #        self.converter = gst.element_factory_make("audioconvert", "convert")
        #        self.player.add(self.converter)
        #        self.sink = gst.element_factory_make("alsasink", "sink")
        #        self.player.add(self.sink)


        ## End of stream
        self.EOS = False

        bus = self.player.get_bus()
        bus.enable_sync_message_emission()
        bus.add_signal_watch()
        bus.connect('sync-message::element', self.on_sync_message)
        bus.connect('message', self.on_message)

#        gobject.timeout_add(500, self.update)


        ## Reference to pyjama
        self.pyjama = parent
        ## Song being played
        self.cur_playing = None
        ## Song played before
        self.last_played = None
        ## Obsolete
        self.connection_tries = 0

        ## Dictionary - Number each artist was played
        self.artist_counter = {}
        ## Dictionary - Number each album was played
        self.album_counter = {}
        ## Dictionary - Number each track was played
        self.track_counter = {}

        ## List of Tracks
        self.playlist = []#{}
        ## List of ids of the tracks in the playlist
        self.playlist_track_uids = []

        ## Playback position in %
        self.percentage = None
        self.text = None
        ## Status of the player
        self.status = None 
        ## Current position of song in s
        self.cursec = None
        ## Duration of the song being played in s
        self.duration = None
        ## Seconds to go
        self.togo = None
        ## Name of the artist being played
        self.artist_name  = None
        ## Name of the track being played
        self.track_name = None
        ## Number of the track being played
        self.numalbum = None

        ## Load equalizer settings:
        if self.equalizer_available:
            bands = []
            for i in range(self.equalizer_bands):
                val = self.pyjama.settings.get_value("SOUND", "band%i" % i, 0.0, float)
                bands.append(val)
            self.set_equalizer(bands)

    ## Set pyjama's equalizer
    # @param self OP
    # @param bands A list with values between -24.0 and +12.0
    def set_equalizer(self, bands):
        i = 0
        for band in bands:
            self.eq.set_property("band%i" % i, float(band))
            i += 1

    ###################################################################
    #
    # adds a track-object to the playlist
    # RETURNS: n/A
    #
    def add2playlist(self, track):
        if isinstance(track, Track):
            for pl_track in self.playlist:
                if track is pl_track:
                    if self.pyjama.verbose:
                        print ("Track #%i in playlist and the track you added are identical. Will now create a copy." % pl_track.position_in_playlist)
                    track = copy.deepcopy(track)
            count = len(self.playlist)
            # self.playlist[count] = track
            track.uid = random.random()
            track.position_in_playlist = count
            self.playlist.append(track)
            self.playlist_track_uids.append(track.uid)
        else:
            print "No valid track object was given"
            raise TrackError

    ###################################################################
    #
    # moves a track-object inside the playlist
    # RETURNS: n/A
    #
    def move_item(self, source, dest, before):
#        print source, dest
#      #  if source == dest or (dest == source-1 and not before) or (dest == source+1 and before): return
#        if dest == 0 and before: dest = 1
#        if dest == len(self.playlist) and not before: dest = len(self.playlist) 
        if dest > source:
            if before: 
                before = -1
            else:
                before = 0
        else:
            if before: 
                before = 0
            else:
                before = 1
        dest = dest + before

        old = self.playlist.pop(source)
        self.playlist.insert(dest, old)
        old.position_in_playlist = dest
        print ("new pos in playlist:", dest)

        old = self.playlist_track_uids.pop(source)
        self.playlist_track_uids.insert(dest, old)

        if self.pyjama.debug_extreme:
            for track in self.playlist:
                print track.id

    ###################################################################
    #
    # remove a track from playlist
    # RETURNS: n/A
    #
    def remove(self, items):
        for item in items:
            track = self.playlist.pop(item)
            self.playlist_track_uids.remove(track.uid)
#        for item in items:
#            del self.playlist[item]
#            self.playlist_track_uids = []
#        pl = {}
#        counter = 0
#        for x in self.playlist:
#            pl[counter] = self.playlist[x]
#            self.playlist_track_uids.append(self.playlist[x]['uid'])
#            counter += 1
#        self.playlist = pl        

    ###################################################################
    #
    # guess what: clear playlist 
    # RETURNS: n/A
    #
    def clearplaylist(self):
        self.cur_playing = None
        self.last_played = None
        self.playlist = []#{}
        self.playlist_track_uids = []
        
    ###################################################################
    #
    # set volume via mocp
    # RETURNS: n/A
    #
    def set_volume(self, volume):
        #print volume
        volume = volume / 100.0
        #print volume
        self.volume.set_property('volume', volume)


    ###################################################################
    #
    # checks status of mocp
    # RETURNS: None if not playing, otherwise mocp status-infos
    #
    def check_status(self):
        if self.status == "paused":
            self.pyjama.Events.raise_event("player-status", "paused")
            return "paused"
        if self.status == "End":
            self.pyjama.Events.raise_event("player-status", "end")
            return None
        if self.cur_playing == None: 
            self.pyjama.Events.raise_event("player-status", "end")
            self.status =  "End"
        else:
            ret = self.get_state
#            if self.pyjama.debug_extreme:
#                print ret
#            else:
            self.status = "Playing"
            position, duration = self.query_position() 
            self.cursec = position // (10**9)
            self.duration = int(self.cur_playing.duration)
            self.percentage =  (1.0 / self.duration) * self.cursec
            if self.percentage > 1: self.percentage = 0
            self.togo = self.cursec - self.duration
            self.artist_name = self.cur_playing.artist_name
            self.track_name = self.cur_playing.name
            self.numalbum = self.cur_playing.numalbum
            self.text = "%s:%s: %s / %s - %s" % (self.cur_playing.artist_name ,self.cur_playing.name, sec2time(self.cursec), sec2time(self.duration), sec2time(self.togo*-1))
            self.pyjama.Events.raise_event("player-status", "playing", self.cursec, self.duration)

#                print self.togo
#                if self.togo <= 0:
#                    uid = self.cur_playing['uid']
#                    if uid in self.playlist_track_uids:
#                        pos = self.playlist_track_uids.index(uid)
#                        if len(self.playlist)> pos+1:
#                            self.play(self.playlist[pos+1], pos+1)        
        

    def on_eos(self):
        self.EOS = False
        #print "END OF STREAM"
        #self.playing = False        
        self.next()
        #self.player.seek(0L)
        #self.play_toggled()
        
    def on_sync_message(self, bus, message):
        if message.structure is None:
            return
        if message.structure.get_name() == 'prepare-xwindow-id':
            self.videowidget.set_sink(message.src)
            message.src.set_property('force-aspect-ratio', True)
            
    def on_message(self, bus, message):
        t = message.type
        if t == gst.MESSAGE_ERROR:
            err, debug = message.parse_error()
            #~ print "GstError: %s" % err, debug
            uri = self.src.get_property('uri')
            #~ print self.cur_playing.stream
            #self.pyjama.Events.raise_event("error", err, "<b>Playback Error</b>: %s\n\nIn most cases this means that jamendo is not available for pyjama.\n\nPlease report this error to me, if it persists." % err, "%s\n\n%s" % (debug, uri))
            print "<b>Playback Error</b>: %s\n\nIn most cases this means that jamendo is not available for pyjama.\n\nPlease report this error to me, if it persists." % err, "%s\n\n%s" % (debug, uri)
            self.stop()
            self.next()
            return
            if self.EOS:
                self.on_eos()
            else:
                self.next()
        elif t == gst.MESSAGE_EOS:
            self.EOS = True
            self.on_eos()
        elif t == gst.MESSAGE_BUFFERING:
            percentage = message.parse_buffering()
            self.buffer = percentage

    def set_location(self, location):
        #~ self.player.set_property('uri', location)
        self.src.set_property('uri', location)

    def query_position(self):
        "Returns a (position, duration) tuple"
        try:
            position, format = self.src.query_position(gst.FORMAT_TIME)
        except:
            #~ print ("nopos")
            position = gst.CLOCK_TIME_NONE

        try:
            duration, format = self.src.query_duration(gst.FORMAT_TIME)
        except:
            #~ print ("nodur")
            duration = gst.CLOCK_TIME_NONE

        return (position, duration)


    ## Seek inside a track
    # @param self Object Pointer
    # @param location Position to seek to in ns
    # @return 
    # - True if seeking was succesfull
    # - False if seeking failed
    def seek(self, location):
        gst.debug("seeking to %r" % location)
        event = gst.event_new_seek(1.0, gst.FORMAT_TIME,
            gst.SEEK_FLAG_FLUSH | gst.SEEK_FLAG_ACCURATE,
            gst.SEEK_TYPE_SET, location,
            gst.SEEK_TYPE_NONE, 0)

        res = self.src.send_event(event)
        if res:
            gst.info("setting new stream time to 0")
            self.src.set_new_stream_time(0L)
            return True
        else:
            gst.error("seek to %r failed" % location)
            return False


    def pause(self):
        gst.info("pausing player")
        self.status = "paused"
        self.src.set_state(gst.STATE_PAUSED)
        self.playing = False

    ###################################################################
    #
    # ???
    # RETURNS: n/A
    #
    def increment_counter(self, array, key):
        if key in array:
            array[key] += 1
        else:
            array[key] = 1
#        print array[key]

    ###################################################################
    #
    # play a track
    # RETURNS: n/A
    #            
    def play(self, track=None, activate_item=-1):
#        self.player.set_state(gst.STATE_NULL)
#        gst.info("stopped player")
        if self.status == "paused" and track == None:
            track = self.cur_playing
        self.increment_counter(self.artist_counter, track.artist_id)
        self.increment_counter(self.album_counter, track.album_id)
        self.increment_counter(self.track_counter, track.id)
        if track.stream == "query":
            track.stream = self.pyjama.jamendo.stream(track.id)
        if track.duration == 0:
            #GET FROM JAMENDO
            track.duration = 60*59

        self.last_played = self.cur_playing
        self.cur_playing = track
        
        if self.status != "paused":
            self.stop()

        try:
            if track.local != None:
                self.set_location(track.local)
            else:
                self.pyjama.downloader.queue_push(track)
                self.set_location(track.stream)
        except Exception, inst:
            print ("error: %s" % inst)
        gst.info("playing player")
        self.src.set_state(gst.STATE_PLAYING)
        self.playing = True
        self.status = "Playing"

        if activate_item > -1:
            track.position_in_playlist = activate_item

        ev = self.pyjama.Events
        ev.raise_event('nowplaying', track)
#        ev.raise_event('nowplaying', artist = track['artist_name'], album = track['album_name'], track = track['name'], icon = img)
        #self.pyjama.notification(_("Now playing"), "<b><i>%s</i></b>:\n%s" % (track['artist_name'], track['name']), icon = img, size =)

        if activate_item > -1:
            self.pyjama.setplaylist(activate_item)

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
        self.src.set_state(gst.STATE_NULL)
        gst.info("stopped player")
                


    ###################################################################
    #
    # play next track in playlist
    # RETURNS: n/A
    #
    def next(self):
        if self.cur_playing is not None:
            uid = self.cur_playing.uid
            if uid in self.playlist_track_uids:
                pos = self.playlist_track_uids.index(uid)
                if len(self.playlist)> pos+1:
                    self.play(self.playlist[pos+1], pos+1)
                else:
                    self.status = "End"
                    self.pyjama.Events.raise_event('end_of_playlist')
                
    ###################################################################
    #
    # play previous track in playlist
    # RETURNS: n/A
    #                
    def prev(self):
        if self.cur_playing is not None:
            uid = self.cur_playing.uid
            if uid in self.playlist_track_uids:
                pos = self.playlist_track_uids.index(uid)
                if pos-1 >= 0:
                    self.play(self.playlist[pos-1], pos-1)                

    def get_state(self, timeout=1):
        print "getstate"
        return self.src.get_state(timeout=timeout)

    def is_playing(self):
        return self.playing
