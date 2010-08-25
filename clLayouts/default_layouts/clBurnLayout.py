#!/usr/bin/env python
# -*- coding: utf-8 -*-

#
# Burn Layout - CD/USB burning layout
#

import gtk, os, threading, time
from modules import clWidgets, clThreadedDownload, clEntry, functions, burn, mp3info

class BgJob(threading.Thread):
    def __init__(self,widget,fn):
        threading.Thread.__init__(self)
        self.widget = widget
        self.fn     = fn
        self.result = None

    def run(self):
        self.result=self.fn()
        if self.widget:
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
        self.pyjama.window.tvList.clear()
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
        self.pyjama.layouts.show_layout("burn_usb", 0, 0)

    def bgJob(self,msg,fn):
        dialog = clWidgets.MyDialog(msg,
                                    self.pyjama.window,
                                    gtk.DIALOG_MODAL,
                                    None,
                                    gtk.STOCK_DIALOG_WARNING,
                                    msg,
                                    sep=False)
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
            msg=_("Please insert a writable CD/DVD!")
            dialog = clWidgets.MyDialog(msg,
                                        self.pyjama.window,
                                        gtk.DIALOG_MODAL,
                                        buttons,
                                        gtk.STOCK_DIALOG_WARNING,
                                        msg)
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

        self.pyjama.window.liststore.connect('row-changed', self.cb_playlist_changed)
        self.pyjama.window.liststore.connect('row-deleted', self.cb_playlist_changed)
        self.pyjama.window.liststore.connect('row-inserted', self.cb_playlist_changed)

    def cb_playlist_changed(self, _tm, _iter, _x=None):
        if not 'mediaSize' in dir(self.pyjama): return
        files=['/home/stef/music/Beastie_Boys-The_Mix_Up-Advance-2007-FTD/01-beastie_boys-b_for_my_name-ftd.mp3',
                '/home/stef/music/Beastie_Boys-The_Mix_Up-Advance-2007-FTD/02-beastie_boys-14th_st._break-ftd.mp3']
        size=0
        length=0
        self.tracks=[]
        for track in files:
            size+=os.path.getsize(track)
            file = open(track, "rb")
            mpeg3info = mp3info.MP3Info(file)
            file.close()
            length+= mpeg3info.mpeg.length
            self.tracks.append((track,length,size))
        mediaLength = (self.pyjama.mediaSize*2352*8) / 1411200 # bit/s
        #print mediaLength, length
        #print self.pyjama.mediaSize*2048, size
        if length<mediaLength:
            #print "can write as AUDIO"
            self.bAudio.set_sensitive(True)
            self.lWarning.hide()
        else:
            self.bAudio.set_sensitive(False)
        if size<=self.pyjama.mediaSize*2048:
            # write data
            #print "can write as DATA"
            self.bData.set_sensitive(True)
            self.lWarning.hide()
        else:
            self.bData.set_sensitive(False)
            # remove items from list in order to proceed.
            # and press the refresh button
            #print "music overload"
            self.lWarning.show()

    def updateStatus(self):
        while not self.burner.Finished:
            status=self.burner.GetStatus()
            if status:
                gtk.gdk.threads_enter()
                self.status.set_label(status)
                gtk.gdk.threads_leave()
            time.sleep(0.2)

    def burn(self):
        self.burner.BurnCD([x[0] for x in self.tracks], self.format)

    def burnCd(self):
        self.burner = burn.Burner()
        title=("Burning %s disc" % self.format)
        dialog = gtk.Dialog(title,
                            self.pyjama.window,
                            gtk.DIALOG_MODAL)
        dialog.set_has_separator(False)
        title = gtk.Label(title)
        dialog.vbox.pack_start(title, False, False)
        title.show()
        self.status = gtk.Label("")
        dialog.vbox.pack_start(self.status, False, False)
        self.status.show()
        # start job in bg thread
        job=BgJob(dialog, self.burn)
        job.start()
        progress=BgJob(None, self.updateStatus)
        progress.start()
        dialog.run()
        res=job.result
        dialog.destroy()

        msg=_("Thank you!\n\nIf you like this music, please consider\ngoing to jamendo.com and donating to\nthe Artist, so that you can enjoy their\nmusic also in the future.")
        dialog = clWidgets.MyDialog(msg,
                                    self.pyjama.window,
                                    gtk.DIALOG_MODAL,
                                    (gtk.STOCK_OK, gtk.RESPONSE_ACCEPT),
                                    gtk.STOCK_DIALOG_WARNING,
                                    msg)
        dialog.run() # gtk.RESPONSE_NONE,
        dialog.destroy()
        self.pyjama.layouts.show_layout("burn", 0, 0)

    def on_bData_activated(self, ev):
        #print "Burning data CD"
        self.format='DATA'
        self.burnCd()

    def on_bAudio_activated(self, ev):
        #print "Burning audio CD"
        self.format='AUDIO'
        self.burnCd()

    def draw(self, a, b, c, d):
        self.mVbox = gtk.VBox(True)
        self.title = gtk.Label(_("Burning Music"))
        self.mVbox.pack_start(self.title, True, True, 0)

        self.lWarning = gtk.Label()
        self.lWarning.set_markup(_("<b>Rock'n'Roll overload</b>\nToo many tracks on playlist, please remove some to continue burning."))
        self.mVbox.pack_end(self.lWarning, True, True, 0)

        self.mHbox = gtk.HBox(True)
        self.mVbox.pack_start(self.mHbox)

        self.bData = gtk.Button(label="",stock=gtk.STOCK_FILE)
        self.bData.set_tooltip_text(_("Burn as Data - MP3"))
        self.bData.connect("clicked", self.on_bData_activated)
        self.bData.connect("button_press_event", self.on_bData_activated)
        self.mHbox.pack_start(self.bData, True, True, 0)

        self.bAudio = gtk.Button(label="",stock=gtk.STOCK_CDROM)
        self.bAudio.set_tooltip_text(_("Burn as Audio"))
        self.bAudio.connect("clicked", self.on_bAudio_activated)
        self.bAudio.connect("button_press_event", self.on_bAudio_activated)
        self.mHbox.pack_start(self.bAudio, True, True, 0)

        self.put(self.mVbox, 0, 0)
        self.show_all()

        self.cb_playlist_changed(0,0,0)

    class ToolBar(gtk.HBox):
        def __init__(self, pyjama):
            gtk.HBox.__init__(self)
            self.pyjama = pyjama
            self.layout = self.pyjama.layouts.layouts['top']

class BurnUSBLayout(gtk.Layout):
    def __init__(self, pyjama):
        self.pyjama = pyjama
        
        gtk.Layout.__init__(self)
        self.set_size(700,300)                

        # might be obsolet
        self.pyjama.window.setcolor(self)

    def draw(self, a, b, c, d):
        # draw the burn-cd dialog

        if(!check_usb()):
            pass
        else:

               
        self.show_all()

    class ToolBar(gtk.HBox):
        def __init__(self, pyjama):
            gtk.HBox.__init__(self)
            self.pyjama = pyjama
            self.layout = self.pyjama.layouts.layouts['top']
