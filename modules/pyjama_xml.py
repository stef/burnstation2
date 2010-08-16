#!/usr/bin/env python
# -*- coding: utf-8 -*-

# ----------------------------------------------------------------------------
# pyjama_xml - xml parser for the new jamendo database dumps
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

########################################################
#                                                      #
# this script is based on Dale Jefferson's 'pyjamendo' #
# thanks for that, it really helped me with my jamendo #
# player                                               #
#                                                      #
########################################################


from xml.sax import make_parser
from xml.sax.handler import ContentHandler



def parse_xml(xml, parent):
        parser = make_parser()
        Handler = Magnatune_handler(parent)
        parser.setContentHandler(Handler)
        parser.parse(open(xml))
        parent.insert_artists(Handler.artists)
        parent.insert_albums(Handler.albums)
        parent.insert_tracks(Handler.tracks)
        parent.insert_tags(Handler.tags)
        print "%i Artists, %i Albums and %i Tracks and %i Tags computed." % (Handler.total_artists, Handler.total_albums, Handler.total_tracks, Handler.total_tags)
        return #artists, albums, tracks, tags


class Magnatune_handler(ContentHandler):
    # initing vars
    def __init__(self, parent):
        self.parent = parent
        self.artists = []
        self.albums = []
        self.tracks = []
        self.tags = []


        self.in_artist = False
        self.in_artist_id = False
        self.in_artist_name = False
        self.in_artist_url = False
        self.in_artist_image = False
        self.in_artist_mbgid = False
        self.in_artist_country = False
        self.in_artist_state = False
        self.in_artist_city = False
        self.in_artist_latitude = False
        self.in_artist_longitude = False

        self.in_album = False
        self.in_album_id = False
        self.in_album_name = False
        self.in_album_url = False
        self.in_album_releasedate = False
        self.in_album_filename = False
        self.in_album_id3genre = False
        self.in_album_mbgid = False
        self.in_album_license_artwork = False

        self.in_track = False
        self.in_track_id = False
        self.in_track_name = False
        self.in_track_duration = False
        self.in_track_numalbum = False
        self.in_track_filename = False
        self.in_track_mbgid = False
        self.in_track_id3genre = False
        self.in_track_license = False

        self.in_track_tag = False
        self.in_track_tag_idstr = False
        self.in_track_tag_weight = False

        self.total_artists = 0
        self.last_artists1 = 0
        self.last_artists2 = 0
        self.total_albums = 0
        self.total_tracks = 0
        self.total_tags = 0
	
        self.trackcount = 0
        self.albumcount = 0
        self.lastid = 0

        self.set_artist_vars()
        self.set_album_vars()
        self.set_track_vars()

        self.track_tags = None
    
    ###################################################################
    #
    # sets_*_vars ints all vars belonging to albums / tracks / artists and sets them to ''
    # RETURNS: n/A
    #
    def set_artist_vars(self):
        self.artist_id, self.artist_name, self.artist_url, self.artist_image, self.artist_mbgid, self.artist_country, self.artist_state, self.artist_city, self.artist_latitude, self.artist_longitude = '','','','','','','','','', ''
    def set_album_vars(self):
        self.album_id, self.album_name, self.album_url, self.album_releasedate, self.album_filename, self.album_id3genre, self.album_mbgid, self.album_license_artwork = '','','','','','','',''
    def set_track_vars(self):
        self.track_id, self.track_name, self.track_duration, self.track_numalbum, self.track_filename, self.track_mbgid, self.track_id3genre, self.track_license, self.track_tag_weight, self.track_tag_idstr = '','','','','','','','', '', ''

    ###################################################################
    #
    # called when a new element is opened
    # RETURNS: n/A
    # 
    def startElement(self, name, attrs):
        # ARIST
        if not self.in_album and not self.in_track:
            if name == "artist":
                self.in_artist = True
            elif name == "id" and self.in_artist:
                self.in_artist_id = True
            elif name == "name" and self.in_artist:
                self.in_artist_name = True
            elif name == "url" and self.in_artist:
                self.in_artist_url = True
            elif name == "image" and self.in_artist:
                self.in_artist_image = True
            elif name == "mbgid" and self.in_artist:
                self.in_artist_mbgid = True
            elif name == "country" and self.in_artist:
                self.in_artist_country = True
            elif name == "state" and self.in_artist:
                self.in_artist_state = True
            elif name == "city" and self.in_artist:
                self.in_artist_city = True
            elif name == "latitude" and self.in_artist:
                self.in_artist_latitude = True
            elif name == "longitude" and self.in_artist:
                self.in_artist_longitude = True
            elif name == "album":
                self.in_album = True
                self.albumcount += 1

        # ALBUM
        if not self.in_track:
            if name == "id" and self.in_album:
                self.in_album_id = True
            elif name == "name" and self.in_album:
                self.in_album_name = True
            elif name == "url" and self.in_album:
                self.in_album_url = True
            elif name == "releasedate" and self.in_album:
                self.in_album_releasedate = True
            elif name == "filename" and self.in_album:
                self.in_album_filename = True
            elif name == "id3genre" and self.in_album:
                self.in_album_id3genre = True
            elif name == "mbgid" and self.in_album:
                self.in_album_mbgid = True
            elif name == "license_artwork" and self.in_album:
                self.in_album_license_artwork = True

        # TRACK

        if name == "track":
            self.in_track = True
            self.trackcount += 1
        elif name == "id" and self.in_track:
            self.in_track_id = True
        elif name == "name" and self.in_track:
            self.in_track_name = True
        elif name == "duration" and self.in_track:
            self.in_track_duration = True
        elif name == "numalbum" and self.in_track:
            self.in_track_numalbum = True
        elif name == "filename" and self.in_track:
            self.in_track_filename = True
        elif name == "mbgid" and self.in_track:
            self.in_track_mbgid = True
        elif name == "id3genre" and self.in_track:
            self.in_track_id3genre = True
        elif name == "license" and self.in_track:
            self.in_track_license = True
        elif name == "tag" and self.in_track:
            self.in_track_tag = True
            self.track_tags = []
        elif name == "idstr" and self.in_track:
            self.in_track_tag_idstr = True
        elif name == "weight" and self.in_track:
            self.in_track_tag_weight = True

    ###################################################################
    #
    # called for the chars between an opening and closing element
    # RETURNS: n/A
    #     
    def characters (self, ch):
        # ARTIST
        if self.in_artist_id:
            self.artist_id = ch
        elif self.in_artist_name:
            self.artist_name = ch
        elif self.in_artist_url:
            self.artist_url = ch
        elif self.in_artist_image:
            self.artist_image = ch
        elif self.in_artist_mbgid :
            self.artist_mbgid = ch
        elif self.in_artist_country:
            self.artist_country = ch
        elif self.in_artist_state:
            self.artist_state = ch
        elif self.in_artist_city:
            self.artist_city = ch
        elif self.in_artist_latitude:
            self.artist_latitude = ch
        elif self.in_artist_longitude:
            self.artist_longitude = ch

        # ALBUM
        if self.in_album_id :
            self.album_id = ch
        elif self.in_album_name:
            self.album_name = ch
        elif self.in_album_url:
            self.album_url = ch
        elif self.in_album_releasedate:
            self.album_releasedate = ch
        elif self.in_album_filename:
            self.album_filename = ch
        elif self.in_album_id3genre:
            self.album_id3genre = ch
        elif self.in_album_mbgid:
            self.album_mbgid = ch
        elif self.in_album_license_artwork:
            self.album_license_artwork = ch

        # TRACK
        if self.in_track_id:
            self.track_id = ch
        elif self.in_track_name:
            self.track_name = ch
        elif self.in_track_duration:
            self.track_duration = ch
        elif self.in_track_numalbum:
            self.track_numalbum = ch
        elif self.in_track_filename:
            self.track_filename = ch
        elif self.in_track_mbgid:
            self.track_mbgid = ch
        elif self.in_track_id3genre:
            self.track_id3genre = ch
        elif self.in_track_license:
            self.track_license = ch
        elif self.in_track_tag_weight:
            self.track_tag_weight = ch
        elif self.in_track_tag_idstr:
            self.track_tag_idstr = ch


    ###################################################################
    #
    # called whenever an element is closed
    # RETURNS: n/A
    #    
    def endElement(self,name):
        # ARTIST
        if not self.in_album and not self.in_track:
            if name == "artist":
                self.in_artist = False
                artist = {}
                artist['id'] = self.artist_id
                artist['name'] = self.artist_name
                artist['url'] = self.artist_url
                artist['image'] = self.artist_image
                artist['mbgid'] = self.artist_mbgid
                artist['country'] = self.artist_country
                artist['state'] = self.artist_state
                artist['city'] = self.artist_city
                artist['latitude'] = self.artist_latitude
                artist['longitude'] = self.artist_longitude
                artist['albumcount'] = self.albumcount
                self.artists.append(artist)

                self.total_artists += 1
                if self.total_artists > self.last_artists1 + 10:
                    if self.parent.pyjama:
                        self.parent.pyjama.Events.raise_event("dbtools_message", "xml", self.total_artists)
                    else:
                        print "%i Artists, %i Albums and %i Tracks and %i Tags computed." % (self.total_artists, self.total_albums, self.total_tracks, self.total_tags)
                    self.last_artists1 = self.total_artists
                if self.total_artists > self.last_artists2 + 500:
                    if not self.parent.pyjama: print "... writing to database"
                    self.parent.insert_artists(self.artists)
                    self.parent.insert_albums(self.albums)
                    self.parent.insert_tracks(self.tracks)
                    self.parent.insert_tags(self.tags)
                    self.artists = []
                    self.albums = []
                    self.tracks = []
                    self.tags = []
                    self.last_artists2 = self.total_artists
		
                self.albumcount = 0
                self.set_artist_vars()
            elif name == "id" and self.in_artist:
                self.in_artist_id = False
            elif name == "name" and self.in_artist:
                self.in_artist_name = False
            elif name == "url" and self.in_artist:
                self.in_artist_url = False
            elif name == "image" and self.in_artist:
                self.in_artist_image = False
            elif name == "mbgid" and self.in_artist:
                self.in_artist_mbgid = False
            elif name == "country" and self.in_artist:
                self.in_artist_country = False
            elif name == "state" and self.in_artist:
                self.in_artist_state = False
            elif name == "city" and self.in_artist:
                self.in_artist_city = False
            elif name == "latitude" and self.in_artist:
                self.in_artist_latitude = False
            elif name == "longitude" and self.in_artist:
                self.in_artist_longitude = False

        # ALBUM
        if not self.in_track:
            if name == "album":
                self.in_album = False
                album = {}
                album['id'] = self.album_id
                album['name'] = self.album_name
                album['url'] = self.album_url
                album['releasedate'] = self.album_releasedate
                album['filename'] = self.album_filename
                album['id3genre'] = self.album_id3genre
                album['mbgid'] = self.album_mbgid
                album['license_artwork'] = self.album_license_artwork
                album['trackcount'] = self.trackcount
                album['artist_id'] = self.artist_id
                self.albums.append(album)

                self.total_albums += 1
                self.trackcount = 0


            elif name == "id" and self.in_album:
                self.in_album_id = False
            elif name == "name" and self.in_album:
                self.in_album_name = False
            elif name == "url" and self.in_album:
                self.in_album_url = False
            elif name == "releasedate" and self.in_album:
                self.in_album_releasedate = False
            elif name == "filename" and self.in_album:
                self.in_album_filename = False
            elif name == "id3genre" and self.in_album:
                self.in_album_id3genre = False
            elif name == "mbgid" and self.in_album:
                self.in_album_mbgid = False
            elif name == "license_artwork" and self.in_album:
                self.in_album_license_artwork = False

        if self.in_track:
            if name == "idstr": self.in_track_tag_idstr = False
            if name == "weight": self.in_track_tag_weight = False
            if name == "tag":
                self.in_track_tag = False
                self.total_tags += 1

                tag = {"artist_id":self.artist_id, "album_id":self.album_id,"track_id":self.track_id, "idstr": self.track_tag_idstr, "weight":self.track_tag_weight}
                self.tags.append(tag)

                self.track_tags = []

        # TRACK
        if name == "track":
            self.in_track = False
            track = {}
            track['id'] = self.track_id
            track['name'] = self.track_name
            track['duration'] = self.track_duration
            track['numalbum'] = self.track_numalbum
            track['filename'] = self.track_filename
            track['mbgid'] = self.track_mbgid
            track['id3genre'] = self.track_id3genre
            track['license'] = self.track_license
            track['album_id'] = self.album_id
            track['artist_id'] = self.artist_id
            self.tracks.append(track)
            self.total_tracks += 1
        elif name == "id" and self.in_track:
            self.in_track_id = False
        elif name == "name" and self.in_track:
            self.in_track_name = False
        elif name == "duration" and self.in_track:
            self.in_track_duration = False
        elif name == "numalbum" and self.in_track:
            self.in_track_numalbum = False
        elif name == "filename" and self.in_track:
            self.in_track_filename = False
        elif name == "mbgid" and self.in_track:
            self.in_track_mbgid = False
        elif name == "id3genre" and self.in_track:
            self.in_track_id3genre = False
        elif name == "license" and self.in_track:
            self.in_track_license = False

