#!/usr/bin/env python
# -*- coding: utf-8 -*-

#
# Burn Layout - CD/USB burning layout
#

import gtk
import os
import threading
from modules import clWidgets, clThreadedDownload, clEntry, functions, burn, mp3info

class BgJob(threading.Thread):
    def __init__(self,widget,fn):
        threading.Thread.__init__(self)
        self.widget = widget
        self.fn     = fn
        self.result = None

    def run(self):
        self.result=self.fn()
        gtk.gdk.threads_enter()
        self.widget.response(0)
        gtk.gdk.threads_leave()

class BurnLayout(gtk.Layout):
    def __init__(self, pyjama):
        self.pyjama = pyjama
        self.burner = burn.Burner()

        gtk.Layout.__init__(self)
        self.set_size(700,300)

        # might be obsolet
        self.pyjama.window.setcolor(self)

        self.pyjama.downloader.priorize_burn(self.pyjama.player.playlist)

    def draw(self, a, b, c, d):
        self.table = gtk.HBox(True)
        self.table.set_size_request(800, 400)
        self.table.set_border_width(50)
        self.table.set_spacing(100)

        self.put(self.table, 0, 0)

        self.target_usb = gtk.Button()
        self.img_usb = gtk.Image()
        self.target_cd  = gtk.Button()
        self.img_cd = gtk.Image()

        self.img_usb.set_from_file(os.path.join(functions.install_dir(), "images", "burn_usb.png"))
        self.img_cd.set_from_file(os.path.join(functions.install_dir(), "images", "burn_cd.png"))
        self.target_usb.set_size_request(256,256)
        self.target_cd.set_size_request(256,256)
        self.img_usb.set_size_request(256,256)
        self.img_cd.set_size_request(256,256)

        self.target_usb.connect('clicked', self.cb_target_usb_clicked)
        self.target_cd.connect('clicked', self.cb_target_cd_clicked)

        self.target_usb.set_image(self.img_usb)
        self.target_cd.set_image(self.img_cd)

        self.table.pack_start(self.target_usb)
        self.table.pack_end(self.target_cd)

        self.show_all()

    def cb_target_usb_clicked(self, ev):
        pass

    def bgJob(self,msg,fn):
        dialog = gtk.Dialog(msg,
                            self.pyjama.window,
                            gtk.DIALOG_MODAL)
        dialog.set_has_separator(False)
        message = gtk.Label(msg)
        dialog.vbox.pack_start(message, False, False)
        message.show()
        # start job in bg thread
        job=BgJob(dialog, fn)
        job.start()
        dialog.run()
        res=job.result
        dialog.destroy()
        return res

    def cdStatus(self):
        return self.bgJob(_("Checking disc status"),self.burner.cdIsWritable)

    def blankCD(self):
        return self.bgJob(_("Blanking disc"),self.burner.BlankCD)

    def cb_target_cd_clicked(self, ev):
        (isWritable,msg)=self.cdStatus()
        while not isWritable:
            buttons=None
            if msg == "** closed ** CD-RW":
                buttons=(gtk.STOCK_CANCEL, gtk.RESPONSE_REJECT,
                         _("Blank CD"), gtk.RESPONSE_APPLY,
                         gtk.STOCK_OK, gtk.RESPONSE_ACCEPT)
            else:
                buttons=(gtk.STOCK_CANCEL, gtk.RESPONSE_REJECT,
                         gtk.STOCK_OK, gtk.RESPONSE_ACCEPT)
            dialog = gtk.Dialog(_("Please insert a writable CD/DVD!"),
                                self.pyjama.window,
                                gtk.DIALOG_MODAL,
                                buttons)
            message = gtk.Label("Please insert a writable CD/DVD!\n%s" % msg)
            dialog.vbox.pack_start(message, False, True)
            message.show()
            response=dialog.run() # gtk.RESPONSE_NONE,
            dialog.destroy()
            if response in [-2,-4]:
                return
            if response == -10:
                self.blankCD()
            (isWritable,msg)=self.cdStatus()
        self.pyjama.mediaSize=msg
        self.pyjama.layouts.show_layout("burn_cd", 0, 0)

    class ToolBar(gtk.HBox):
        def __init__(self, pyjama):
            gtk.HBox.__init__(self)
            self.pyjama = pyjama
            self.layout = self.pyjama.layouts.layouts['top']

class BurnCDLayout(gtk.Layout):
    def __init__(self, pyjama):
        self.pyjama = pyjama

        gtk.Layout.__init__(self)
        self.set_size(700,300)

        # might be obsolet
        self.pyjama.window.setcolor(self)

    def draw(self, a, b, c, d):
        files=['/home/stef/music/Beastie_Boys-The_Mix_Up-Advance-2007-FTD/01-beastie_boys-b_for_my_name-ftd.mp3',
                '/home/stef/music/Beastie_Boys-The_Mix_Up-Advance-2007-FTD/02-beastie_boys-14th_st._break-ftd.mp3']
        size=0
        length=0
        tracks=[]
        for track in files:
            size+=os.path.getsize(track)
            file = open(track, "rb")
            mpeg3info = mp3info.MP3Info(file)
            file.close()
            length+= mpeg3info.mpeg.length
            tracks.append((track,length,size))
        mediaLength = (self.pyjama.mediaSize*2352*8) / 1411200 # bit/s
        print mediaLength
        if length<mediaLength:
            print "can write as AUDIO"
        if size<=self.pyjama.mediaSize*2048:
            # write data
            print "can write as DATA"
        else:
            # remove items from list in order to proceed.
            # and press the refresh button
            print "music overload"

        self.mVbox = gtk.VBox(True)
        self.title = gtk.Label(_("Burning Music"))
        self.mVbox.pack_start(self.title)
        self.put(self.mVbox, 0, 0)
        self.show_all()

    class ToolBar(gtk.HBox):
        def __init__(self, pyjama):
            gtk.HBox.__init__(self)
            self.pyjama = pyjama
            self.layout = self.pyjama.layouts.layouts['top']
