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

## @package clXMLRPC
# This module will - perhaps - be used for inter process
# communication later.
# Since I just need this feature in order to connect pyjama
# with jamendo playlists, I will use a more failsafe mechanism
# for the time being. 


from SimpleXMLRPCServer import SimpleXMLRPCServer

import socket
socket.setdefaulttimeout(3)
import xmlrpclib

from threading import Thread
import gtk

class ClientOnlyException(Exception):
    pass

class XmlrpcHandler:
    def __init__(self, pyjama):
        self.pyjama = pyjama

    def test(self, inte):
        return True

    def load_playlist(self, playlist_file):
        print ("Got playlist %s" % playlist_file)
        self.pyjama.playlist_to_load = playlist_file

    def get_curplaying(self):
        return self.pyjama.player.cur_playing

    def get_state(self):
        return self.pyjama.player.status

    def playpause(self):
        gtk.gdk.threads_enter()
        self.pyjama.window.on_bPlay_clicked(None)
        gtk.gdk.threads_leave()

    #~ def pause(self):
        #~ self.pyjama.window.cb_bC

    def next(self):
        gtk.gdk.threads_enter()
        self.pyjama.window.on_bNext_clicked(None)
        gtk.gdk.threads_leave()

    def prev(self):
        gtk.gdk.threads_enter()
        self.pyjama.window.on_bPrev_clicked(None)
        gtk.gdk.threads_leave()

    #~ def print_string(self, string):
        #~ print string

class XMLRPC:
    def __init__(self, pyjama, clientonly=False):
        self.pyjama = pyjama
        self.clientonly = clientonly

        self.connect_or_create()

    def connect_or_create(self):
        self.server = None
        self.role = None
        ## check if a server is running
        # if not, serve
        try:
            self.server = xmlrpclib.ServerProxy("http://localhost:50506", allow_none=True) 
            self.server.test(23)
            self.role = "client"
            print ("Found XMLRPC-Server on localhost:50506")
        except socket.error, inst:
            if self.clientonly:
                raise ClientOnlyException, "No server found"
            thr = Thread(target = self.serve, args = ())
            thr.start()
            self.role = "server"

    def send_playlist(self, playlist_file):
        self.server.load_playlist(playlist_file)

    # run by client
    def test(self):
        if self.role == "client":
            try:
                self.server.test(23)
            except:
                print ("Server no more running")
                self.connect_or_create()
                

    def quit(self):
        if self.role == "server":
            try:
                self.server.shutdown()
            except Exception, inst:
                print ("Error shutting down the XMLRPC-server: %s" % inst)

    def serve(self):
        self.server = SimpleXMLRPCServer(("localhost", 50506), allow_none=True)
        self.server.register_instance(XmlrpcHandler(self.pyjama))
        print ("Running XMLRPC-Server on localhost:50506")
        self.server.serve_forever()
        return self.server
