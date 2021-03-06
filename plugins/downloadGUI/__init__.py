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

import gtk, gtk.glade

from urllib import urlopen

import os
import sys
import time
import tarfile

from modules import functions
from modules import dbthreaded #clDB

ASSUMED_NUMBER_OF_ARTISTS = 12000.0

class main():
    def __init__(self, pyjama):
        self.pyjama = pyjama
        self.home = functions.preparedirs()

        self.install_dir = functions.install_dir()

        self.pyjama.dump_tools.download_fkt = self.download
        self.pyjama.set_download_database_fkt(self.auto_download)

        self.pyjama.Events.connect_event("dbtools_message", self.ev_message)
        self.pyjama.Events.connect_event("alldone", self.ev_alldone)

    def create_dialog(self):
        gladefile = os.path.join(self.install_dir, "plugins", "downloadGUI", "downloadGUI.glade")
        try:
            self.wTree = gtk.glade.XML(gladefile)  
        except RuntimeError:
            print "Error loading glade file"
            print "tried to load it from: ", gladefile
            raise

        self.dialog = self.wTree.get_widget("dialog1")
        self.dialog.set_size_request(300,177)
        self.bCancel = self.wTree.get_widget("bCancel")
        self.bStart = self.wTree.get_widget("bStart")
        self.bOK = self.wTree.get_widget("bOK")
        self.progressbar = self.wTree.get_widget("progressbar1")

        self.bCancel.show()
        self.progressbar.show()

        self.dialog.set_title("Downloading Database")

        self.dialog.connect('delete_event', self.quit)
        self.bCancel.connect('clicked', self.ev_bCancel_clicked)
        self.bOK.connect('clicked', self.ev_bOK_clicked)
        self.bStart.connect('clicked', self.ev_bStart_clicked)

        self.dialog.set_icon_from_file(os.path.join(functions.install_dir(), "images", "pyjama.png"))


    ## -2: no hash file
    ## -1: hash values differ
    ## 1: hash values are equal
    def check_hash(self):
        url = "http://xn--ngel-5qa.de/jamendo/last_md5"
        try:
            remote_hash = urlopen(url).read()
        except:
            return

        local_file = os.path.join(self.home, "database_hash")
        if os.path.exists(local_file):
            try:
                fh = open(local_file)
                if fh:
                    local_hash = fh.read()
                    fh.close()
                    if local_hash != remote_hash:
                        return -1
                    else:
                        return 1
                else:
                    return
            except:
                return
        else:
            print ("No local hash file found")
            return -2

        
        

    def auto_download(self, force_jamendo=False):
        self.create_dialog()
        self.dialog.show()
        self.bStart.set_sensitive(False)
        self.bCancel.set_sensitive(False)
        self.pyjama.dump_tools.delete_db()
        self.pyjama.dump_tools.create_tables()
        ret = self.pyjama.dump_tools.create_db(force_jamendo)
        if ret == "nofile":
            self.pyjama.Events.raise_event("error", None, "Error downloading the database dump from jamendo. Please try again later and notify me about this.")
            self.dialog.destroy()
            return
        self.pyjama.dump_tools.finish()
        self.dialog.destroy()

    def ev_show(self, ev):
        self.create_dialog()
        self.dialog.run()

    def ev_alldone(self):
        # Append menu entry
        menu = self.pyjama.window.menubar
        entry = menu.append_entry(menu.get_rootmenu("Extras"), _("Load Database Dump"), "downloadgui")
        entry.connect("activate", self.ev_show)
        menu.set_item_image(entry, gtk.STOCK_NETWORK)

        if self.pyjama.settings.get_value("downloadgui", "autoupdate", False):
            # Auto update
            ret =  self.check_hash()
            if ret == -2:
                self.auto_download()
            elif ret == -1:
                self.auto_download()
            elif ret == 1:
                print ("Your database dump is up to date")
            else:
                print ("Could not check if you dump is up to date - this is no problem at all, just update manually from time to time")

    def ev_message(self, message, info=None):
        if message == "xml":
            self.dialog.set_title(_("Parsing Database"))
            fraction = (info / ASSUMED_NUMBER_OF_ARTISTS) * 1.0
            if fraction > 1: fraction == 1.0
            self.set_bar(fraction, "%i Artists inserted" % info)
        else:
            self.set_bar(None, message)
            if message == "Finished":
                try:
                    artists_old = self.pyjama.db.artists
                    albums_old = self.pyjama.db.albums
                    tracks_old = self.pyjama.db.tracks
                except:
                    artists_old = 0
                    albums_old = 0
                    tracks_old = 0
                print ("Finished, now loading new database")
                self.pyjama.db = dbthreaded.DB(self.pyjama)
                self.pyjama.window.sbStatus.set_text("Counter", _("Artists: %i, Albums: %i, Tracks: %i") % (self.pyjama.db.artists, self.pyjama.db.albums,   self.pyjama.db.tracks))

                self.progressbar.set_fraction(1.0)
                self.bStart.hide()
                self.bOK.show()

                self.pyjama.info("Database downloaded", "Got %i new artists, %i new albums, %i new tracks" % (self.pyjama.db.artists - artists_old, self.pyjama.db.albums - albums_old,   self.pyjama.db.tracks - tracks_old))
                

    def ev_bOK_clicked(self, widget):
        self.dialog.destroy()

    def ev_bStart_clicked(self, ev):
        self.bStart.set_sensitive(False)
        self.bCancel.set_sensitive(False)

        self.pyjama.dump_tools.delete_db()
        self.pyjama.dump_tools.create_tables()
        ret = self.pyjama.dump_tools.create_db()
        if ret == "nofile":
            self.pyjama.Events.raise_event("error", None, "Error downloading the database dump from the mirror.\nPlease try running 'pyjama --update-jamendo' in order to get the database right from jamendo.")
            self.dialog.destroy()
            return
        self.pyjama.dump_tools.finish()
#        self.download("http://xn--ngel-5qa.de/jamendo/download.php")
    
    def set_bar(self, fraction=None, text=""):
        if fraction:
            self.progressbar.set_fraction(fraction)
        else:
            pass
#            self.progressbar.pulse()
        self.progressbar.set_text(text)
        self.pyjama.window.do_events()
        return True


    def extract(self, archive, dest):
        th = tarfile.open(name=archive, mode='r:*')
        try:
            th.extractall(dest)
        except Exception, inst:
            self.pyjama.Events.raise_event("error", inst, "Error extracting the archive")
            return

    def download(self, url, local_filename):

        try:
            local_file = open(os.path.join(self.home, local_filename), "wb")
            stream, length = self.create_download(url, proxy=None)

            if not length:
                length = "unknown"
            else:
                length = int(length)
#            print "Lade %s (%s bytes).." % (url, length)
            curbyte = 0.0

            content = stream.read(1024)
            local_file.write(content)
            curbyte += len(content)

            milli= time.time()*1000

            while content:
                content = stream.read(1024)
                curbyte += len(content)

                if length != "unknown":
                    if time.time()*1000 > milli + 200: 
                        milli = time.time() *1000
                        self.progress = 100*curbyte/length
                        self.set_bar(self.progress/100, "%d%%"% self.progress)
#                        print self.progress
#                    print "%s: %.02f/%.02f kb (%d%%)" % ( local_filename, curbyte/1024.0, length/1024.0, 100*curbyte/length)
                local_file.write(content)
                
            stream.close()
            local_file.close()
            self.set_bar(1.0, "Done")
        except Exception, inst:
            self.dialog.destroy()
            print "Fehler beim Laden von %s: %s" % (url, inst)
            self.pyjama.Events.raise_event("error", inst, "Fehler beim Laden von %s" % url)


    def create_download(self, url, proxy = None):
        stream = urlopen(url, None, proxy)

        filename=stream.info().getheader("Content-Length")
        if not filename:
            filename = "temp"

        return (stream, filename)

    def ev_bCancel_clicked(self, ev):
        self.dialog.destroy()

    def quit(self, widget, ev):
        return True



