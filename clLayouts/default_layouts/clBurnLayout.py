#!/usr/bin/env python
# -*- coding: utf-8 -*-

#
# Burn Layout - CD/USB burning layout
#

import gtk
import os

from modules import clWidgets, clThreadedDownload, clEntry, functions

class BurnLayout(gtk.Layout):
    def __init__(self, pyjama):
        self.pyjama = pyjama
        
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

    def cb_target_cd_clicked(self, ev):
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
        # draw the burn-cd dialog
        label = gtk.Label("hello")
        self.put(label, 50, 50)
        self.show_all()

    class ToolBar(gtk.HBox):
        def __init__(self, pyjama):
            gtk.HBox.__init__(self)
            self.pyjama = pyjama
            self.layout = self.pyjama.layouts.layouts['top']
