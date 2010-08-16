#!/usr/bin/env python
# -*- coding: utf-8 -*-

# ----------------------------------------------------------------------------
# pyjama - python jamendo audioplayer
# Copyright (c) 2008 Daniel Nögel
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
# ----------------------------------------------------------------------------

from pytorrent import TorrentClient
from pytorrent.connection import TransmissionException

import time
import sys
import os


class main():
    def __init__(self, pyjama):
        pass


 
#torrent_file = "./torrent"
#if not os.path.exists(torrent_file):
#    print "Nicht vorhanden"
#    sys.exit(1)
# 
## spawn a transmission daemon
try:
    client = TorrentClient()
except:
    print(60*"#")
    print("You need to have the transmission torrent daemon installed")
    print("Look out for the package 'transmission-cli' or 'transmission'")
    print(60*"#")
    raise
# 
## add our torrent file and start it
#try:
#    torrent = client.add_torrent(torrent_file)
#    for i, file in enumerate(torrent.files):
#        if i != 1: 
#            file.wanted = False
#        else:
#            print "\t"+str(i)+")", file.name+":", file.size, "Bytes"
#    torrent.start() 
#except TransmissionException:
#    print "Torrent already in queue"
#    for t in client.torrents:
#        for i, file in enumerate(t.files):
#            if i == 1:
#                file.wanted = True
#        torrent = t
## print some initial information
#print "Downloading:", torrent.name

## as long as the torrent is not finished print out some download status
#while not torrent.finished:
#    sizes = str(torrent.downloaded_size)+"/"+str(torrent.size)
#    print sizes, "Bytes", "@", torrent.download_rate, "B/s"
#    time.sleep(1)
## thats it. the file has been downloaded
#print "file download finished."
