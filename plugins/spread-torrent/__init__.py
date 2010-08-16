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
import gtk.glade


import gobject
import os
import sys
import time
import shutil

from threading import Thread
try:
    import libtorrent as lt
    lt.fingerprint("PO", 0, 2, 0, 0)
except:
    print ("python-libtorrent needed for this plugin")
    raise

from modules import functions

def threaded(f):
    def wrapper(*args, **kwargs):
        t = Thread(target=f, args=args, kwargs=kwargs)
        t.start()
    return wrapper


def calculate_discusage(dir):
    total_size = 0
    file_number = 0

    if not os.path.exists(dir): return -1

    for root, dirs, files in os.walk(dir):
        for file in files:
            file_path = os.path.join(root, file)
            file_size = os.path.getsize(file_path)
            total_size += file_size
            file_number += 1
    return total_size

MP3 = "http://api.jamendo.com/get2/bittorrent/file/redirect/?album_id=ALBUMID&type=archive&class=mp32"
OGG = "http://api.jamendo.com/get2/bittorrent/file/redirect/?album_id=ALBUMID&type=archive&class=ogg3"

STATE = ['queued', 'checking', 'downloading metadata', \
            'downloading', 'finished', 'seeding', 'allocating']

# Pyjama's Odd Torrent Apportion Tool - odd ey?

#@threaded
class main():

    #   columns
    (
      COLUMN_STATE,
      COLUMN_PROGRESS,
      COLUMN_DOWNLOADRATE,
      COLUMN_UPLOADRATE,
      COLUMN_SEEDERS,
      COLUMN_LEECHERS,
      COLUMN_SEEN,
      COLUMN_AVAILABLE,
      COLUMN_NAME
    ) = range(9)

    # columns 2
    (
      COLUMN_INFO,
      COLUMN_VALUE
    ) = range(2)

    def __init__(self, pyjama):
        self.pyjama = pyjama

        self.torrents_to_serve = int(self.pyjama.settings.get_value("TORRENT", "number_of_torrents", 10, float))
        self.format = self.pyjama.settings.get_value("TORRENT", "torrent_format", "both") #mp3 both ogg
        self.old_torrents = self.pyjama.settings.get_value("TORRENT", "old_torrents", 1) #0 - 5 (spread, ignore, delete, upload only, download only)

        self.quit = False

        self.window = None

        self.torrentdir = os.path.join(functions.preparedirs(), "torrent")
        if not os.path.exists(self.torrentdir):
            try:
                os.mkdir(self.torrentdir)
            except Exception, inst:
                print ("Could not create %s" % self.torrentdir)
                raise
        self.discusage = calculate_discusage(self.torrentdir)//1024.0**2

        self.torrent = Torrent(path=self.torrentdir)
        self.pyjama.Events.connect_event("alldone", self.ev_alldone)
        self.pyjama.Events.connect_event("quit", self.ev_quit)

    ## Shows the potato main window
    def show_window(self, dummy_event_catcher = None):
        xml = gtk.glade.XML(os.path.join(functions.install_dir(), "plugins", "spread-torrent", "window.glade"))
        
        self.window = xml.get_widget('window1')
        self.notebook = xml.get_widget('notebook1')
        self.treeview_torrents = xml.get_widget('treeview1')
        self.treeview_torrents_iter = {}
        self.treeview_statistics = xml.get_widget('treeview2')
        self.hbuttonbox = xml.get_widget('hbuttonbox1')
        self.scrolledwindow_torrents = xml.get_widget('scrolledwindow3')
        self.hs_timeout = xml.get_widget('hs_timeout')
        #~ self.bClose = xml.get_widget('bClose')
        self.notebook.set_current_page(0)

        btn = gtk.ToggleButton()
        btn.set_use_stock(True)
        self.hbuttonbox.pack_start(btn)
        btn.connect("toggled", self.cb_toggle)
        hbox = gtk.HBox()
        btn.img = gtk.Image()
        btn.img.set_from_stock(gtk.STOCK_MEDIA_PLAY, gtk.ICON_SIZE_BUTTON)
        btn.lbl = gtk.Label("Torrent active")
        hbox.pack_start(btn.img, False, False)
        hbox.pack_start(btn.lbl, False, False)
        hbox.show_all()
        btn.add(hbox)
        btn.show()
        btn.set_active(True)
        btn.set_tooltip_text("Click here to start/pause the torrent client")

        btn = gtk.Button(stock=gtk.STOCK_CLOSE)
        #~ btn.set_use_stock(True)
        #~ btn.set_label()
        self.hbuttonbox.pack_end(btn)
        btn.connect("clicked", self.cb_destroy_window)
        btn.show()
        btn.set_tooltip_text("After closing this window, the client will run in background")

        self.combobox = xml.get_widget("combobox1")
        if self.format == "ogg":
            self.combobox.set_active(0)
        elif self.format == "mp3":
            self.combobox.set_active(1)
        elif self.format == "both":
            self.combobox.set_active(2)

        self.cb_old_torrents = xml.get_widget("combobox2")
        self.cb_old_torrents.set_active(int(self.old_torrents))

        self.spin_torrents = xml.get_widget('spin_torrents')
        self.spin_download_rate = xml.get_widget('spin_download')
        self.spin_upload_rate = xml.get_widget('spin_upload')

        #
        # Load values
        #
        self.spin_torrents.set_value(self.pyjama.settings.get_value("TORRENT", "number_of_torrents", 10, float))
        self.spin_download_rate.set_value(self.pyjama.settings.get_value("TORRENT", "download_rate", 0, float))
        self.spin_upload_rate.set_value(self.pyjama.settings.get_value("TORRENT", "upload_rate", 0, float))


        #
        # Connect
        #
        self.spin_torrents.connect("value-changed", self.cb_spin_changed)
        self.spin_download_rate.connect("value-changed", self.cb_spin_changed)
        self.spin_upload_rate.connect("value-changed", self.cb_spin_changed)
        self.combobox.connect("changed", self.cb_combo_changed)
        self.cb_old_torrents.connect("changed", self.cb_combo_changed)
        self.hs_timeout.connect("value-changed", self.cb_hs_changed)


        #
        # Configure Window
        #
        self.window.set_title("Potato - Pyjama's Odd Torrent Apportion Tool")#(self.__class__.__name__)
        self.window.set_icon_from_file(os.path.join(functions.install_dir(), "plugins", "spread-torrent", "spread-torrent.png"))
        self.window.connect('delete_event', self.cb_destroy_window)
        self.window.set_skip_taskbar_hint(False)
        #~ self.window.move(100, 100)

        #
        # Configure Treeview STATS
        #
        ## Model
        model = gtk.ListStore(
            gobject.TYPE_STRING,
            gobject.TYPE_STRING
       )
        self.treeview_statistics.set_model(model)
        ## Columns
        # Info
        renderer = gtk.CellRendererText()
        renderer.set_data("column", self.COLUMN_INFO)
        column = gtk.TreeViewColumn("Infos", renderer, text=self.COLUMN_INFO)
        self.treeview_statistics.append_column(column)
        #~ column.set_sort_column_id(self.COLUMN_INFO)
        column.set_sizing(gtk.TREE_VIEW_COLUMN_FIXED)
        column.set_resizable(True)
        column.set_fixed_width(160)

        # Value
        renderer = gtk.CellRendererText()
        renderer.set_data("column", self.COLUMN_VALUE)
        column = gtk.TreeViewColumn("Values", renderer, text=self.COLUMN_VALUE)
        self.treeview_statistics.append_column(column)
        #~ column.set_sort_column_id(self.COLUMN_VALUE)
        column.set_sizing(gtk.TREE_VIEW_COLUMN_FIXED)
        column.set_resizable(True)
        column.set_fixed_width(70)


        #
        # Configure Treeview TORRENT
        #
        ## Model
        model = gtk.ListStore(
            gobject.TYPE_STRING,
            gobject.TYPE_STRING,
            gobject.TYPE_STRING,
            gobject.TYPE_STRING,
            gobject.TYPE_INT,
            gobject.TYPE_INT,
            gobject.TYPE_INT,
            gobject.TYPE_STRING,
            gobject.TYPE_STRING
       )
        self.treeview_torrents.set_model(model)
        ## Columns
        # State
        renderer = gtk.CellRendererText()
        renderer.set_data("column", self.COLUMN_PROGRESS)
        column = gtk.TreeViewColumn("Status", renderer, text=self.COLUMN_STATE)
        self.treeview_torrents.append_column(column)
        column.set_sort_column_id(self.COLUMN_PROGRESS)
        column.set_sizing(gtk.TREE_VIEW_COLUMN_FIXED)
        column.set_resizable(True)
        column.set_fixed_width(70)
        
        # Progress
        renderer = gtk.CellRendererText()
        renderer.set_data("column", self.COLUMN_PROGRESS)
        column = gtk.TreeViewColumn("  %  ", renderer, text=self.COLUMN_PROGRESS)
        self.treeview_torrents.append_column(column)
        column.set_sort_column_id(self.COLUMN_PROGRESS)
        column.set_sizing(gtk.TREE_VIEW_COLUMN_FIXED)
        column.set_resizable(True)
        column.set_fixed_width(60)

        # Download Rate
        renderer = gtk.CellRendererText()
        renderer.set_data("column", self.COLUMN_DOWNLOADRATE)
        column = gtk.TreeViewColumn("Down\nkB/s ", renderer, text=self.COLUMN_DOWNLOADRATE)
        self.treeview_torrents.append_column(column)
        column.set_sort_column_id(self.COLUMN_DOWNLOADRATE)
        column.set_sizing(gtk.TREE_VIEW_COLUMN_FIXED)
        column.set_resizable(True)
        column.set_fixed_width(70)

        # Upload Rate
        renderer = gtk.CellRendererText()
        renderer.set_data("column", self.COLUMN_UPLOADRATE)
        column = gtk.TreeViewColumn("Up\nkB/s", renderer, text=self.COLUMN_UPLOADRATE)
        self.treeview_torrents.append_column(column)
        column.set_sort_column_id(self.COLUMN_UPLOADRATE)
        column.set_sizing(gtk.TREE_VIEW_COLUMN_FIXED)
        column.set_resizable(True)
        column.set_fixed_width(60)

        # Seeders
        renderer = gtk.CellRendererText()
        renderer.set_data("column", self.COLUMN_SEEDERS)
        column = gtk.TreeViewColumn("Seeds", renderer, text=self.COLUMN_SEEDERS)
        self.treeview_torrents.append_column(column)
        column.set_sort_column_id(self.COLUMN_SEEDERS)
        column.set_sizing(gtk.TREE_VIEW_COLUMN_FIXED)
        column.set_resizable(True)
        column.set_fixed_width(70)

        # Leechers
        renderer = gtk.CellRendererText()
        renderer.set_data("column", self.COLUMN_LEECHERS)
        column = gtk.TreeViewColumn("Leecher", renderer, text=self.COLUMN_LEECHERS)
        self.treeview_torrents.append_column(column)
        column.set_sort_column_id(self.COLUMN_LEECHERS)
        column.set_sizing(gtk.TREE_VIEW_COLUMN_FIXED)
        column.set_resizable(True)
        column.set_fixed_width(85)

        # Seen
        renderer = gtk.CellRendererText()
        renderer.set_data("column", self.COLUMN_SEEN)
        column = gtk.TreeViewColumn("Peers", renderer, text=self.COLUMN_SEEN)
        self.treeview_torrents.append_column(column)
        column.set_sort_column_id(self.COLUMN_SEEN)
        column.set_sizing(gtk.TREE_VIEW_COLUMN_FIXED)
        column.set_resizable(True)
        column.set_fixed_width(65)

        # Available
        renderer = gtk.CellRendererText()
        renderer.set_data("column", self.COLUMN_AVAILABLE)
        column = gtk.TreeViewColumn("Availbility", renderer, text=self.COLUMN_AVAILABLE)
        self.treeview_torrents.append_column(column)
        column.set_sort_column_id(self.COLUMN_AVAILABLE)
        column.set_sizing(gtk.TREE_VIEW_COLUMN_FIXED)
        column.set_resizable(True)
        column.set_fixed_width(85)

        # Name Column
        renderer = gtk.CellRendererText()
        renderer.set_data("column", self.COLUMN_NAME)
        column = gtk.TreeViewColumn(_("Torrent"), renderer, text=self.COLUMN_NAME)
        self.treeview_torrents.append_column(column)
        column.set_sort_column_id(self.COLUMN_NAME)
        column.set_sizing(gtk.TREE_VIEW_COLUMN_GROW_ONLY)
        column.set_resizable(True)
        column.set_fixed_width(300)

        #~ page = self.notebook.get_nth_page(0)
        #~ self.notebook.set_menu_label_text(page, "asd")

        #
        # Set info tab
        #
        img = xml.get_widget("img_potato")
        img.set_from_file(os.path.join(functions.install_dir(), "plugins", "spread-torrent", "spread-torrent.png"))

        label_desc = xml.get_widget("label_description")
        label_desc.set_markup(
        """<b>Potato</b> is a small torrent client for pyjama that lets you give something back to the community!
        Potato automatically gets torrent files that needs sharing and seeds them.
        Of course you can set how many torrents you'd like to share and reduce bandwith.""".replace("        ", "")
        )

        self.window.show()

        self.timeout = self.pyjama.settings.get_value("TORRENT", "refresh_rate", 1000)
        #~ num = self.torrents_to_serve
        #~ if num < 50:
            #~ timeout = 1000
        #~ elif num >= 50 and num < 100:
            #~ timeout = 2000
        #~ elif num >= 100 and num < 500:
            #~ timeout = 3000
        #~ elif num >= 500:
            #~ timeout = 5000

        self.last_refresh = 0
        #~ self.refresh_window()
        gobject.timeout_add(1000, self.refresh_window)

    ## Sets information for a given torrent to a given iter
    # for self.treeview_torrens
    # @param self OP
    # @param iter Iter to set
    # @param torrent The torrent handler
    # @return a tuple to be passed to model.set(*retval)
    def set_torrent_information(self, iter, torrent):
        status = torrent.status()
        name = torrent.name()
        
        progress = "%06.2f" % (status.progress * 100.0)
        downloadrate = "%.1f" % (status.download_rate/1024.0)
        uploadrate = "%.1f" % (status.upload_rate/1024.0)
        state = STATE[status.state]
        seeds = status.num_seeds
        leecher = status.num_peers - seeds
        seen = status.list_peers

        availbility = "%i|%i|%.1f" % (status.num_complete, status.num_incomplete ,status.distributed_copies)
        
        return (iter,
            self.COLUMN_STATE, state,
            self.COLUMN_PROGRESS, progress,
            self.COLUMN_DOWNLOADRATE, downloadrate,
            self.COLUMN_UPLOADRATE, uploadrate,
            self.COLUMN_SEEDERS, seeds,
            self.COLUMN_LEECHERS, leecher,
            self.COLUMN_SEEN, seen,
            self.COLUMN_AVAILABLE, availbility,
            self.COLUMN_NAME, name
        )        

    ## Refreshes all values shown in this main window - called
    # every second
    def refresh_window(self):
        if self.last_refresh + self.timeout - 1 > time.time():
            return True
        self.last_refresh = time.time()
        print time.time()
        if self.window is None:
            return False
        #~ print self.torrent.session.dht_state()
        
        #~ print self.torrent.session.status().dht_nodes
        #~ print self.torrent.session.status().dht_torrents
        #~ print "-"
        
        #~ # Check alerts
        #~ alert = self.torrent.session.pop_alert()
        #~ i = 0
        #~ if isinstance(alert, lt.state_changed_alert):
            #~ i += 1
            #~ state = alert.state
            #old_state = alert.prev_state
            #~ torrent = alert.handle
            #print "changed", torrent.name()
        #~ else:
            #~ print alert
        #~ print "*"*20, i, "*"*20
        
        #
        # Set the treeview TORRENTS
        #
        model = self.treeview_torrents.get_model()
        #~ model.clear()
        overal_progress = 0
        for torrent in self.torrent.session.get_torrents():
            name = torrent.name()
            status = torrent.status()
            overal_progress += status.progress

            ## If the torrent is in the iter-list, use this iter
            if self.treeview_torrents_iter.has_key(name):
                try:
                    iter = self.treeview_torrents_iter[name]
                    ret = self.set_torrent_information(iter, torrent)
                    model.set(*ret)
                except:
                    ## Ok, there was an error - so we need to get the
                    # correct iter anoter way
                    pass
                else:
                    ## Hey, it worked - so lets continue with the next
                    # torrent
                    continue
            
            ## If the torrent wasn't in the iter-list, we need to 
            # get its iter by enumerating all model's iters
            iter = model.get_iter_first()            
            found = False
            while iter:
                if model.get_value(iter, self.COLUMN_NAME) == name:
                    ret = self.set_torrent_information(iter, torrent)
                    model.set(*ret)
                    found = True
                    break
                iter = model.iter_next(iter)
            ## And finally: If there wasn't any iter for this torrent
            # in the model, we create a new iter
            if not found:
                iter = model.append()
                ret = self.set_torrent_information(iter, torrent)
                model.set(*ret)
            ## Add the iter to the list
            self.treeview_torrents_iter[name] = iter


        ################################################################

        down, up = self.total_transfer()

        ret = self.torrent.overal_infos()
        if ret is not None:
            finished = str(ret['finished'] + ret['seeding'])
            downloading = str(ret['downloading'])
            queued = str(ret['queued'])
        else:
            finished = "n/A"
            downloading = "n/A"
            queued = "n/A"
        
        if self.torrent.session is not None:
            downrate = self.torrent.session.status().download_rate / 1024.0
            uprate = self.torrent.session.status().upload_rate / 1024.0
            session_down = self.torrent.session.status().total_download
            session_up = self.torrent.session.status().total_upload
        else:
            downrate = 0
            uprate = 0
            session_down = 0
            session_up = 0

        #
        # Set treeview STATISTICS
        #
        infos = [
            {
              "info":"Download rate",
              "value":"%.2f kB/s" % downrate
            },
            {
              "info":"Upload rate",
              "value":"%.2f kB/s" % uprate
            },
            {
              "info":"Downloaded this session",
              "value":"%.2f MB" % (session_down/1024.0**2)
            },
            {
              "info":"Uploaded this session",
              "value":"%.2f MB" % (session_up/1024.0**2)
            },
            {
              "info":"Ever downloaded",
              "value":"%.2f MB" % (down/1024.0**2)
            },
            {
              "info":"Ever uploaded",
              "value":"%.2f MB" % (up/1024.0**2)
            },
            {
              "info":"Share ratio",
              "value":"%.3f" % (up/down)
            },
            {
              "info":"Torrents finished",
              "value":finished
            },
            {
              "info":"Torrents loading",
              "value":downloading
            },
            {
              "info":"Torrents queued",
              "value":queued
            },
            {
              "info":"Total progress",
              "value": "%.2f%%" % ((overal_progress / len(self.torrent.session.get_torrents()))*100.0)
            },
            {
              "info":"Disc usage",
              "value":"%.2f" % self.discusage
            },
        ]
        model = self.treeview_statistics.get_model()
        model.clear()
        for item in infos:
            info = item['info']
            value = item['value']
            
            iter = model.append()
            model.set (iter,
                self.COLUMN_INFO, info,
                self.COLUMN_VALUE, value
            )

        #~ self.treeview_torrents.set_model(model)
        #~ self.scrolledwindow_torrents.set_hadjustment(had)
        #~ self.scrolledwindow_torrents.set_vadjustment(vad)
        return True

    ## This timeout is triggered every 5 minutes
    # to save some fast resume data.
    def save_fast_resume(self, exit=False):
        ## Destroy Timeout, if potato is going to be exited
        if exit:
            pass

        if self.torrent is None:
            return

        if self.torrent.session is None:
            return
            
        # Pause the session
        paused_before = False
        if self.torrent.session.is_paused():
            paused_before = True
        else:
            self.torrent.session.pause()
        
        ## Delete Alert stack
        while self.torrent.session.pop_alert():
            pass

        ## Trigger fast resume
        num_resume_data = 0
           
        for torrent in self.torrent.session.get_torrents():
            #~ self.torrent.session.remove_torrent(torrent)
            torrent.save_resume_data()
            num_resume_data += 1

        ## After timeout seconds saving the resume data will be aborted
        timeout = 10
        time_start = time.time()

        ## Fast resume works asynchronously -
        # for this reason we have to get the results
        # with this loop
        resume_ok_counter = 0
        resume_error_counter = 0
        i = 0
        while num_resume_data > 0:
            if time.time() >= time_start + timeout:
                print ("[TORRENT] Aborted saving the resume data due timeout")
                break
            #~ print dir(self.torrent.session.pop_alert())
            ret = self.torrent.session.pop_alert()
            if ret:
                if isinstance(ret, lt.save_resume_data_failed_alert):
                    #~ if "does not have a complete" in ret.message(): #fastresume_rejected_alert
                    #~ print (ret.message())
                    resume_error_counter += 1
                    num_resume_data -= 1
                    pass
                elif isinstance(ret, lt.save_resume_data_alert):
                    resume_data = lt.bencode(ret.resume_data)
                    torrent_handle = ret.handle
                    name_long = torrent_handle.get_torrent_info().name()
                    name_short = "%s[...]" % name_long
                    try:
                        fh = open(os.path.join(self.torrentdir, "%s.resumedata" % name_long), "wb")
                        fh.write(resume_data)
                        fh.close()
                        #~ print ("Saved resume data for '%s'" % name_short)
                        resume_ok_counter += 1
                    except Exception, inst:
                        print ("Error writing resumedata for '%s': %s" % (name_short, inst))
                    num_resume_data -= 1                        
                else:
                    pass

        if not paused_before and not exit:
            self.torrent.session.resume()
        print ("[TORRENT] Resume data for %i/%i torrents written" % (resume_ok_counter, len(self.torrent.session.get_torrents())))
        if resume_error_counter > 0:
            print ("[TORRENT] %i torrents had no valid resume data" % resume_error_counter)
        return True

    ## Timeout callback called every 60 seconds - as the calculation
    # of the directory size might take some time, this is done
    # every minute, only
    def timeout_60_seconds(self):
        ## Calculate discusage of torrent files
        self.discusage = calculate_discusage(self.torrentdir)/1024.0**2

        ## Save session's transfer volume
        if self.torrent.session is None:
            down = 0
            up = 0
        else:
            down = self.torrent.session.status().total_download
            up = self.torrent.session.status().total_upload
        self.pyjama.settings.set_value("TORRENT", "current_session_upload", up)
        self.pyjama.settings.set_value("TORRENT", "current_session_download", down)

        return True

    ## Starts some threads
    def start_threads(self):
        thr = Thread(target = self.get_list, args = ())
        thr.start()

        thr = Thread(target = self.start, args = ())
        thr.start()

        return False

    ## Returns the size of all downloaded data from a specifig
    # .torrent file
    def torrent_size(self, torrent):
        if not os.path.exists(torrent):
            return -1

        try:
            content = open(torrent, "rb").read()
        except:
            return -2

        try:
            ret = lt.bdecode(content)
        except:
            return -3

        try:
            name = ret['info']['name']
            return calculate_discusage(os.path.join(self.torrentdir, name))
        except:
            return -4

    ## Returns the size a torrent has, when it has been successfully
    # downloaded (pieces*piece_length)
    def theoretical_torrent_size(self, torrent):
        if not os.path.exists(torrent):
            return -1

        try:
            content = open(torrent, "rb").read()
        except:
            return -2

        try:
            ret = lt.bdecode(content)
        except Exception, inst:
            print inst
            return -3

        try:
            plength = int(ret['info']['piece length'])
            pieces = len(ret['info']['pieces']) / 20
            size = int(plength * pieces)
            return size
        except Exception, inst:
            return -4

    ## Delete all torrent related data from a give .torrent file
    def delete_torrent(self, torrent):
        if not os.path.exists(torrent):
            return -1

        try:
            content = open(torrent, "rb").read()
        except:
            return -2

        try:
            ret = lt.bdecode(content)
        except:
            return -3

        try:
            name = ret['info']['name']
            shutil.rmtree(os.path.join(self.torrentdir, name))
            os.remove(torrent)
            return True
        except:
            return False
        
    def get_torrent_name(self, torrent):
        if not os.path.exists(torrent):
            return -1

        try:
            content = open(torrent, "rb").read()
        except:
            return -2

        try:
            ret = lt.bdecode(content)
        except:
            return -3

        try:
            name = ret['info']['name']
            return name
        except:
            return -4

    ## Gets a list of needseeding-torrents and seeds them
    # also manages old torrents
    def get_list(self):
        self.pyjama.jamendo.last_query_hack()
        needseeding_list = self.pyjama.jamendo.query("id/album/json/?order=needseeding_desc&n=1000", caching_time=60*60*24*300,  raise_query_event=False)
        if needseeding_list:
            torrents = []
            ## Actually we need to loops here: If the user has defined
            # to share MP3 as well as OGG and set to spread 100 torrents,
            # we do not need the first 100 torrents from the list but
            # the first 50 torrents from the list (mp3+ogg).
            # So simply iterating the list would be more complicated
            # at the end.
            for ALBUMID in needseeding_list:
                if self.format == "mp3" or self.format == "both":
                    torrents.append((ALBUMID, MP3.replace("ALBUMID", str(ALBUMID))))
                if self.format == "ogg" or self.format == "both":
                    torrents.append((ALBUMID, OGG.replace("ALBUMID", str(ALBUMID))))
            
            counter = 0
#            delete_list = []
            for ALBUMID, uri in torrents:
#                if counter >= self.torrents_to_serve:
#                    # Delete?
#                    #~ if len(os.listdir(self.torrentdir)) > int(self.torrents_to_serve)*2:
#                    dest = os.path.join(self.torrentdir, "%i_%s" % (ALBUMID, format))
#                    if os.path.exists(dest):
#                        delete_list.append(dest)
#                        #~ print ("%s can be deleted" % dest)

#                else:
                if counter < self.torrents_to_serve:
                    # Download and add
                    counter += 1
                    
                    if "class=mp3" in uri:
                        format = "mp3"
                    else:
                        format = "ogg"
                    
                    dest = os.path.join(self.torrentdir, "%i_%s" % (ALBUMID, format))
                    source = uri
                    
                    if not os.path.exists(dest):
                        torrent = self.pyjama.download(source, dest)
                    if os.path.exists(dest):
                        if self.pyjama.verbose:
                            print ("Downloaded torrent for album %i" % ALBUMID)
                        th = self.torrent.load_torrent(dest)
                        #~ if not isinstance(th, type(1)):
                            #~ self.torrent.print_data(th)
                    else:
                        #~ if self.pyjama.verbose:
                        print ("Download of album %i failed" % ALBUMID)

        size = 0
        count = 0
        for filename in os.listdir(self.torrentdir):
            path = os.path.join(self.torrentdir, filename)
            if not os.path.isdir(path) and filename.endswith("_mp3") or filename.endswith("_ogg"):
                pos = filename.find("_")
                format = filename[pos+1:]
                album_id = int(filename[:pos])

                if album_id in needseeding_list:
                    if self.format == "both":
                        ## As both formats are spread, any album
                        # id can be found twice in the list.
                        # So the actual number of album_ids
                        # is only half of the total number
                        # of torrents to seed.
                        if needseeding_list.index(album_id) < self.torrents_to_serve/2.0:
                            continue
                    elif self.format == format:
                        ## If only one format is going to be seeded
                        # and this torrent matches this format
                        # it needs to be found in the first X
                        # album_ids of needseeding_list
                        if needseeding_list.index(album_id) < self.torrents_to_serve:
                            continue
                count += 1
                ## Ok, we've got a torrent file which is not under the
                # top X needseeding torrents.
                # What does the user want us to do with it?
                if self.old_torrents == 0:      # Spread
                    th = self.torrent.load_torrent(path)
                elif self.old_torrents == 1:    # Ignore
                    pass
                elif self.old_torrents == 2:    # Delete
                    print("Deleting: %s" % path)
                    self.delete_torrent(path)
                    #~ self.delete_torrent(path)
                elif self.old_torrents == 3:    # Upload only
                    th = self.torrent.load_torrent(dest)
                    th.auto_managed(False)
                    th.set_download_limit(1)
                elif self.old_torrents == 4:    # Download only
                    th = self.torrent.load_torrent(dest)
                    th.auto_managed(False)
                    th.set_upload_limit(1)
        
                ret = self.torrent_size(path)
                if ret > 0:
                    size += ret
        modes = ["Spread", "Ignore", "Delete", "Upload only", "Download only"]
        print "%i MB found in %i old torrents. Current mode: %s" % (size //  1024**2, count, modes[self.old_torrents])

    ## Starts libtorrent.session()
    def start(self):
        self.torrent.start_session()

        dl = self.pyjama.settings.get_value("TORRENT", "download_rate", 0, float)*1024
        ul = self.pyjama.settings.get_value("TORRENT", "upload_rate", 0, float)*1024
        
        self.torrent.set_download_limit(int(dl))
        self.torrent.set_upload_limit(int(ul))
        #~ self.torrent.set_download_limit(1000)

        #~ while not self.quit:
            #~ torrents =  self.torrent.get_torrents()
#~ 
            #~ if torrents is not None and torrents != []:
                #~ for torrent in torrents:
                    #~ self.torrent.print_data(torrent)
#~ 
            #~ down, up = self.total_transfer()
            #~ print ("Downloaded: %.02f | Uploaded: %.02f" %  (down/1024.0**2, up/1024.0**2))
            #~ time.sleep(5)
        #~ return True
        
    ## At the end of a session the whole transfer volume is written
    # to config
    def write_total_session_transfer(self):
        down, up = self.total_transfer()

        last_up = self.pyjama.settings.get_value("TORRENT", "current_session_upload", 0, float)
        last_down = self.pyjama.settings.get_value("TORRENT", "current_session_download", 0, float)
        down += last_down
        up += last_up

        self.pyjama.settings.set_value("TORRENT", "upload", up)
        self.pyjama.settings.set_value("TORRENT", "download", down)

        self.pyjama.settings.set_value("TORRENT", "current_session_upload", 0)
        self.pyjama.settings.set_value("TORRENT", "current_session_download", 0)

    ## Returns a tuple (down, up) showing how man bytes have been
    # transfered over the whole time (ever)
    def total_transfer(self):
        if self.torrent.session is None:
            down = 0
            up = 0
        else:
            down = self.torrent.session.status().total_download
            up = self.torrent.session.status().total_upload

        if down < 0: down = 0
        if up < 0: up = 0

        up_old = self.pyjama.settings.get_value("TORRENT", "upload", 0, float)
        down_old = self.pyjama.settings.get_value("TORRENT", "download", 0, float)

        down_new = down_old + down
        up_new = up_old + up

        return (down_new, up_new)

    #
    # Callbacks 
    #
    def cb_hs_changed(self, widget):
        self.timeout = int(widget.get_value())
        self.pyjama.settings.set_value("TORRENT", "refresh_rate", self.timeout)
    
    def cb_toggle(self, widget):
        if widget.get_active():
            widget.img.set_from_stock(gtk.STOCK_MEDIA_PLAY, gtk.ICON_SIZE_BUTTON)
            widget.lbl.set_text("Torrent active")
            if self.torrent.session is not None:
                self.torrent.session.resume()
        else:
            widget.img.set_from_stock(gtk.STOCK_MEDIA_PAUSE, gtk.ICON_SIZE_BUTTON)
            widget.lbl.set_text("Torrent paused")
            if self.torrent.session is not None:
                self.torrent.session.pause()

    def cb_combo_changed(self, widget):
        if widget == self.combobox:
            self.pyjama.settings.set_value("TORRENT", "torrent_format", self.combobox.get_active_text().lower())
            self.format = self.pyjama.settings.get_value("TORRENT", "torrent_format", "ogg")
        elif widget == self.cb_old_torrents:
            self.pyjama.settings.set_value("TORRENT", "old_torrents", self.cb_old_torrents.get_active(), int)
            self.old_torrents = int(self.cb_old_torrents.get_active())



    def cb_spin_changed(self, widget):
        if widget == self.spin_torrents:
            self.pyjama.settings.set_value("TORRENT", "number_of_torrents", widget.get_value())
            self.torrents_to_serve = int(widget.get_value())
        elif widget == self.spin_download_rate:
            self.pyjama.settings.set_value("TORRENT", "download_rate", widget.get_value())
            self.torrent.set_download_limit(int(widget.get_value()*1024))
        elif widget == self.spin_upload_rate:
            self.pyjama.settings.set_value("TORRENT", "upload_rate", widget.get_value())
            self.torrent.set_download_limit(int(widget.get_value()*1024))
        

    def cb_destroy_window(self, widget, event=None):
        if self.window is not None:
            self.window.destroy()
            self.window = None

    #
    # Events
    #

    ## Called when pyjama is closed
    # Write some fast resume data
    def ev_quit(self):
        self.quit = True
        
        if self.window is not None:
            self.window.destroy()
            
        self.write_total_session_transfer()
                
        self.save_fast_resume(exit=True)


    def ev_alldone(self):
        if self.pyjama.xmlrpc.role == "client":
            self.pyjama.Events.raise_event("error", None, "Another instance of pyjama is running - won't start spread-torrent")
            return

        ## If the previous session wasn't closed regulary,
        # this will write its stats to config file
        self.write_total_session_transfer()

        menu = self.pyjama.window.menubar
        entry = menu.append_entry(menu.get_rootmenu("Extras"), _("Spread Torrents"), "potato")
        entry.connect("activate", self.show_window)
        menu.set_item_image(entry, os.path.join(functions.install_dir(), "plugins", "spread-torrent", "spread-torrent.png"))

        gobject.timeout_add(3000, self.start_threads)
        gobject.timeout_add(60000, self.timeout_60_seconds)
        gobject.timeout_add(60000*5, self.save_fast_resume)


            
#~ @threaded
#~ class Torrent(Thread):
class Torrent():
    def __init__(self, path="./", begin=6881, end=6891):
        self.path = path
        self.begin = begin
        self.end = end

        #~ self.stop = False
        #~ Thread.__init__(self)   

        self.session = None
        #~ self.torrents = []

    def set_upload_limit(self, bytes=0):
        self.session.set_upload_rate_limit(bytes)

    def set_download_limit(self, bytes=0):
        self.session.set_download_rate_limit(bytes)

    def get_upload_limit(self):
        return self.session.upload_rate_limit()

    def get_download_limit(self):
        return self.session.download_rate_limit()

    def end_session(self):
        # no idea what to do here - have a look at main.ev_quit()
        pass

    def start_session(self):
        self.session = lt.session()
        ret = self.session.listen_on(self.begin, self.end)
        self.session.set_alert_mask(lt.alert.category_t.storage_notification+lt.alert.category_t.status_notification)
        
        #~ self.session.start_upnp()
        self.session.start_dht(self.session.dht_state())
        
        if not ret:
            print ("Error opening a session")
            return -1

    def get_torrents(self):
        return self.session.get_torrents()

    def load_torrent(self, filename):
        while self.session is None:
            time.sleep(1)

        resume_data = "None"

        try:
            content = lt.bdecode(open(filename, "rb").read())
        except Exception, inst:
            print ("Error opening torrent file '%s': %s" % (filename, inst))
            return -1

        if content is None:
            return -2

        folder = os.path.dirname(filename)
        name = content['info']['name']
        resume_file = os.path.join(folder, "%s.resumedata" % name)
        if os.path.exists(resume_file):
            try:
                resume_data = lt.bdecode(open(resume_file, "rb").read())
                print ("Loaded resumefile for '%s'" % name[:30])
            except Exception, inst:
                resume_data = "None"
                print ("Error opening resumefile '%s': %s" % (resume_file, inst))

        try:
            info = lt.torrent_info(content)
        except Exception, inst:
            print ("Error parsing torrent '%s': %s" % (filename, inst))
            return -3
        try:
            th = self.session.add_torrent(info, self.path, resume_data, lt.storage_mode_t.storage_mode_sparse, True)
            #~ th = self.session.add_torrent({"torrent_info":info,
            #~ "save_path":self.path,
            #~ "resume_data":"None",
            #~ "storage_mode_t":lt.storage_mode_t.storage_mode_sparse,
            #~ "paused":True
            #~ })
            #~ th.pause()
            th.auto_managed(True)

        except Exception, inst:
            print ("Error adding the torrent '%s': %s" % (filename, inst))
            return -4

        #~ self.torrents.append(th)
        return th

    def overal_infos(self):
        if self.session is None:
            return None
        
        total = len(self.session.get_torrents())

        dict = {}
        dict['queued'] = 0
        dict['checking'] = 0
        dict['downloading metadata'] = 0
        dict['downloading'] = 0
        dict['finished'] = 0
        dict['seeding'] = 0
        dict['allocating'] = 0

        dict['unfinished'] = 0

        for torrent in self.session.get_torrents():
            state = STATE[torrent.status().state]
            dict[state] += 1
            if state != "finished" and state != "seeding":
                dict['unfinished'] += 1

        return dict
        

    def print_data(self, th):
        info = th.get_torrent_info()

        print th.name()
        status = th.status()
#            print dir(status)
        #~ print "%s | Done: %d%% | Up: %i | Down: %i | Peers: %i | Seeds: %i | Total PCs in Network: %i" % (STATE[status.state], status.progress*100.0, status.download_rate, status.upload_rate, status.num_peers, status.num_seeds, status.list_peers)
        print status.num_pieces, "/", info.num_pieces()
        ret = self.overal_infos()
        print  ("Finished: %i, Unfinished: %i, Queued: %i" % (ret['finished']+ret['seeding'], ret['unfinished'], ret['queued']))
        
        down = self.session.status().download_rate // 1024.0
        up = self.session.status().upload_rate // 1024.0
        print ("%.02f kB/s down, %.02f kB/s up" % (down, up))
        print 20*"-"
        #~ pieces = ""
        #~ for piece in status.pieces:
            #~ if piece:
                #~ pieces += "+"
            #~ else:
                #~ pieces += "-"
        #~ print pieces

            #print status.num_complete, "/", status.num_incomplete #vollständige versionen im netz
