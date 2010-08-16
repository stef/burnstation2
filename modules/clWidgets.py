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


## @package clWidgets
# This module holds a lot of widgets
# which which are used more often.


# GUI
import pygtk
pygtk.require('2.0')
import gtk
import gobject

# Time formatting
from time import gmtime, time, sleep

# math
from math import ceil
import copy
import os
import sys

import urllib

# Benutzerklassen
import functions

from threading import Thread

# Gettext - Übersetzung
functions.translation_gettext()
#def _(string):
#    return string

## shows an error when user makes to much jamendo queries
def tofast(window):
    dia = MyDialog(_('to fast'),
                              window.get_toplevel(),
                              gtk.DIALOG_MODAL | gtk.DIALOG_DESTROY_WITH_PARENT, 
                                (gtk.STOCK_OK, gtk.RESPONSE_ACCEPT),        gtk.STOCK_DIALOG_WARNING, _('Some requests may only be send once a second\nin order not to slow down jamendo\'s database'))
    dia.run()
    dia.destroy()
    window.toolbar.on_bHistoryBack_clicked(None)

## removes some special characters from strings to be shown 
# in albumwidgets
def clear(string):
    if string == None: return string
    string = string.replace("\r", "")
    string = string.replace("\t", "")
    string = string.replace(",", "")
    string = string.replace("&", "&amp;")
#    string = string.replace("«", "")
#    string = string.replace("»", "")
#    string = functions.decode_htmlentities(string)
    return string.strip()
    
def threaded(f):
    def wrapper(*args, **kwargs):
        t = Thread(target=f, args=args, kwargs=kwargs)
        t.start()
    return wrapper
#~ @threaded
#~ class PulsingBar(gtk.ProgressBar):
    #~ def __init__(self):
        #~ self.__pulsing = False
        #~ 
        #~ gtk.ProgressBar.__init__(self)
#~ 
    #~ @threaded
    #~ def pulsing(self):
        #~ gtk.gdk.threads_enter()
        #~ self.pulse()
        #~ while gtk.events_pending(): gtk.main_iteration()
        #~ gtk.gdk.threads_leave()
        #~ return self.__pulsing
        #~ 
    #~ @threaded
    #~ def start(self):
        #~ self.__pulsing = True
        #~ gobject.timeout_add(10, self.pulsing)
#~ 
    #~ @threaded
    #~ def stop(self):
        #~ self.__pulsing = False

    

class InfoLabel(gtk.HBox):
    def __init__(self, pyjama):
        self.pyjama = pyjama
        self.markuplbCaption = "<span size=\"medium\">TEXT</span>"

        gtk.HBox.__init__(self, False)

        self.icon_size = self.pyjama.settings.get_value("PYJAMA", "info_label_icon_size", 24)

        self.lbl = gtk.Label()
        self.lbl.show()

        self.img = gtk.Image()
        self.img.show()

        self.pack_start(self.img, False, True)
        self.pack_start(self.lbl, True, True)

        size = gtk.icon_size_register("usersize1", self.icon_size, self.icon_size)

    def set_text(self, text):
#        self.pyjama.window.f.set_label(text)
        self.lbl.set_markup(self.markuplbCaption.replace("TEXT", text))

    def set_image(self, image=None, size=None):
        if image == None:
            self.img.clear()
            return

        if size is None:
            size = gtk.icon_size_from_name("usersize1")

        if image in gtk.stock_list_ids():
            self.img.set_from_stock(image, size)
            return

        if not os.path.exists(image):
            # try to find the image in pyjama's
            # image folder:
            if not os.path.exists(os.path.join(functions.install_dir(), "images", image)):
                print ("Could not find '%s'" % image)
                return -1
            else:
                image = os.path.join(functions.install_dir(), "images", image)

        try:
            pixbuf = gtk.gdk.pixbuf_new_from_file_at_size(image, self.icon_size, self.icon_size)
            self.img.set_from_pixbuf(pixbuf)
        except ValueError:
            print ("Error loading the image")
            return -2

## Context menu for TreeViewList
# When creating a ListMenu the event
# 'populate_listmenu' will be raised
class ListMenu(gtk.Menu):
    ## The Constructor
    # @param self Object Pointer
    # @param pyjama Pyjama Reference
    def __init__(self, pyjama):
        self.pyjama = pyjama
        gtk.Menu.__init__(self)

#        # Add remove button if an entry is selected:
#        model, tmpIter = pyjama.window.tvList.get_selection().get_selected()
#        if tmpIter != None:
#            #path = pyjama.window.liststore.get_path(tmpIter)[0]
#            mnu = gtk.ImageMenuItem("Remove from List")
#            self.append(mnu)
#            mnu.show()
#            mnu.connect("activate", self.cb_mnu_remove_clicked)

#            img = gtk.Image()
#            img.set_from_stock(gtk.STOCK_REMOVE, gtk.ICON_SIZE_MENU)
#            mnu.set_image(img)


        pyjama.Events.raise_event("populate_listmenu", self)

        self.show()

    def cb_mnu_remove_clicked(self, widget):
        self.pyjama.window.on_bDelete_clicked(None)


## Context menu for the playlist
# When creating a PlaylistMenu the event
# 'populate_playlistmenu' will be raised
class PlaylistMenu(gtk.Menu):
    ## The Constructor
    # @param self Object Pointer
    # @param pyjama Pyjama Reference
    def __init__(self, pyjama):
        self.pyjama = pyjama
        gtk.Menu.__init__(self)

        # Add remove button if an entry is selected:
        model, tmpIter = pyjama.window.tvPlaylist.get_selection().get_selected()
        if tmpIter != None:
            #path = pyjama.window.liststore.get_path(tmpIter)[0]

            ## Show Artist Menu
            mnu = gtk.ImageMenuItem(_("Show artist's page"))
            self.append(mnu)
            mnu.show()
            mnu.connect("activate", self.cb_mnu_artist_clicked)
            img = gtk.Image()
            pb = gtk.gdk.pixbuf_new_from_file_at_size(os.path.join(functions.install_dir(), "images", "personal.png"), 16, 16)
            img.set_from_pixbuf(pb)
            mnu.set_image(img)

            ## Show Album Menu
            mnu = gtk.ImageMenuItem(_("Show album's page"))
            self.append(mnu)
            mnu.show()
            mnu.connect("activate", self.cb_mnu_album_clicked)
            img = gtk.Image()
            pb = gtk.gdk.pixbuf_new_from_file_at_size(os.path.join(functions.install_dir(), "images", "cd.png"), 16, 16)
            img.set_from_pixbuf(pb)
            mnu.set_image(img)

            x = gtk.SeparatorMenuItem()
            x.show()
            self.append(x)


            pyjama.Events.raise_event("populate_playlistmenu", self)


            x = gtk.SeparatorMenuItem()
            x.show()
            self.append(x)

            ## Remove Menu
            mnu = gtk.ImageMenuItem(_("Remove from Playlist"))
            self.append(mnu)
            mnu.show()
            mnu.connect("activate", self.cb_mnu_remove_clicked)
            img = gtk.Image()
            img.set_from_stock(gtk.STOCK_REMOVE, gtk.ICON_SIZE_MENU)
            mnu.set_image(img)


        self.show()

    def cb_mnu_artist_clicked(self, widget):
        model, tmpIter = self.pyjama.window.tvPlaylist.get_selection().get_selected()
        if tmpIter != None:
            path = model.get_path(tmpIter)
            if path != (): path = path[0]

            track = self.pyjama.player.playlist[path]

            artistdetails = self.pyjama.db.artistinfos(track.artist_id)
            self.pyjama.layouts.show_layout("artist", artistdetails)

    def cb_mnu_album_clicked(self, widget):
        model, tmpIter = self.pyjama.window.tvPlaylist.get_selection().get_selected()
        if tmpIter != None:
            path = model.get_path(tmpIter)
            if path != (): path = path[0]
            track = self.pyjama.player.playlist[path]

            albumdetails = self.pyjama.jamendo.albuminfos(track.album_id)
            if not albumdetails: return
            self.pyjama.layouts.show_layout("album", albumdetails)

    def cb_mnu_remove_clicked(self, widget):
        self.pyjama.window.on_bDelete_clicked(None)

## Dialog Class
class MyDialog(gtk.Dialog):
    def __init__(self, caption, toplevel, flags, buttons, image, desc, sep=True, allow_resize=False):
            gtk.Dialog.__init__(self, caption, toplevel, flags, buttons)
            img = gtk.Image()
            img.set_from_stock(image, gtk.ICON_SIZE_DIALOG)
            hbox = gtk.HBox()
            self.vbox.pack_start(hbox)
            hbox.pack_start(img)
            label = gtk.Label()
            label.set_single_line_mode(False)
            label.set_line_wrap(True)
            label.set_markup(desc)
            hbox.pack_start(label)

            self.set_has_separator(sep)
            self.set_resizable(allow_resize)

            self.show_all()

## Process Dialog
# This dialog can be used to show a dialog
# with a progressbar in it
class ProcessDialog(gtk.Dialog):
    def __init__(self, pyjama, caption):
        gtk.Dialog.__init__(self, caption)

        self.set_modal(True)
#        self.set_size_request(400, 300)

        self.progressbar = gtk.ProgressBar()
        self.label = gtk.Label()
        self.label.set_line_wrap(True)
        self.label.set_single_line_mode(False)

        self.vbox.pack_start(self.label, False, True)
        self.vbox.pack_start(self.progressbar, False, True)

        self.show_all()

    def set_status(self, percentage=None, text=None):
        if percentage is not None:
            self.progressbar.set_fraction(percentage/100)
        if text is not None:
            self.progressbar.set_text(text)

    def set_description(self, desc):
        self.label.set_markup(desc)

## Treeview on the bottom with artist-album-tracks fields
class TreeViewList(gtk.TreeView):

    #   columns
    (
      COLUMN_ARTIST,
      COLUMN_ALBUM,
      COLUMN_TRACKNUM,
      COLUMN_TRACK,
      COLUMN_LICENSE,
      COLUMN_ARTISTID,
      COLUMN_ALBUMID,
      COLUMN_TRACKID,
      COLUMN_LICENSEURL
    ) = range(9)

    def __init__(self):
        # create model
        model = self.__create_model()

        # create tree view
        gtk.TreeView.__init__(self, model)
        self.set_rules_hint(True)
        self.set_rubber_banding(True)
        self.set_show_expanders(True)
        #self.set_reorderable(True)
        self.get_selection().set_mode(gtk.SELECTION_SINGLE)#gtk.SELECTION_MULTIPLE
        self.__add_columns(self)

        self.show()

    def get_item(self, path):
        model = self.get_model()
        retIter = model.get_iter(path)
        ret = model.get(retIter, 0, 1, 2, 3, 4, 5, 6, 7, 8)
        return ret
        

    def clear(self):
        model = self.get_model()
        model.clear()


    def add_item(self, item):
        model = self.get_model()
        #articles.append(new_item)
        if item[self.COLUMN_TRACKNUM] != "":
            item[self.COLUMN_TRACKNUM] = "%02d" % int(item[self.COLUMN_TRACKNUM])

        iter = model.append()
        model.set (iter,
            self.COLUMN_ARTIST, item[self.COLUMN_ARTIST],
            self.COLUMN_ALBUM, item[self.COLUMN_ALBUM],
            self.COLUMN_TRACKNUM, item[self.COLUMN_TRACKNUM],
            self.COLUMN_TRACK, item[self.COLUMN_TRACK],
            self.COLUMN_LICENSE, "",
            self.COLUMN_ARTISTID, item[self.COLUMN_ARTISTID],
            self.COLUMN_ALBUMID, item[self.COLUMN_ALBUMID],
            self.COLUMN_TRACKID, item[self.COLUMN_TRACKID],
            self.COLUMN_LICENSEURL, item[self.COLUMN_LICENSE]
       )

    def __create_model(self):

        # create list store
        model = gtk.ListStore(
            gobject.TYPE_STRING,
            gobject.TYPE_STRING,
            gobject.TYPE_STRING,
            gobject.TYPE_STRING,
            gobject.TYPE_STRING,
            gobject.TYPE_INT,
            gobject.TYPE_INT,
            gobject.TYPE_INT,
            gobject.TYPE_STRING
       )
       
#        # add items
#        for item in articles:
#            iter = model.append()

#            model.set (iter,
#                  COLUMN_ARTIST, item[COLUMN_ARTIST],
#                  COLUMN_ALBUM, item[COLUMN_ALBUM],
#                  COLUMN_TRACK, item[COLUMN_TRACK]
#           )
        return model


    def __add_columns(self, treeview):

        model = treeview.get_model()

        # artist column
        renderer = gtk.CellRendererText()
        renderer.set_data("column", self.COLUMN_ARTIST)

        column = gtk.TreeViewColumn(_("Artist"), renderer, text=self.COLUMN_ARTIST)
        treeview.append_column(column)
        column.set_sort_column_id(0)
        column.set_sizing(gtk.TREE_VIEW_COLUMN_AUTOSIZE)
        column.set_resizable(True)
        column.set_fixed_width(250)



        # album column
        renderer = gtk.CellRendererText()
        renderer.set_data("column", self.COLUMN_ALBUM)

        column = gtk.TreeViewColumn(_("Album"), renderer, text=self.COLUMN_ALBUM)
        treeview.append_column(column)
        column.set_sort_column_id(1)
        column.set_sizing(gtk.TREE_VIEW_COLUMN_AUTOSIZE)
        column.set_resizable(True)
        column.set_fixed_width(250)

        # tracknum column
        renderer = gtk.CellRendererText()
        renderer.set_data("column", self.COLUMN_TRACKNUM)

        column = gtk.TreeViewColumn("#", renderer, text=self.COLUMN_TRACKNUM)
        treeview.append_column(column)
        column.set_sort_column_id(2)
        column.set_sizing(gtk.TREE_VIEW_COLUMN_FIXED)
        column.set_resizable(True)
        column.set_fixed_width(40)

        # track column
        renderer = gtk.CellRendererText()
        renderer.set_data("column", self.COLUMN_TRACK)

        column = gtk.TreeViewColumn(_("Track"), renderer, text=self.COLUMN_TRACK)
        treeview.append_column(column)
        column.set_sort_column_id(3)
        column.set_sizing(gtk.TREE_VIEW_COLUMN_AUTOSIZE)
        column.set_resizable(True)
        column.set_fixed_width(150)
        
#        # license column
#        renderer = gtk.CellRendererText()
#        renderer.set_data("column", self.COLUMN_LICENSE)

#        column = gtk.TreeViewColumn(_("Licence"), renderer, text=self.COLUMN_LICENSE)
#        treeview.append_column(column)
#        column.set_sort_column_id(4)
#        column.set_sizing(gtk.TREE_VIEW_COLUMN_FIXED)
#        column.set_resizable(True)
#        column.set_fixed_width(100)

        # license column
        renderer = gtk.CellRendererPixbuf()
        renderer.set_data("column", self.COLUMN_LICENSE)
#        renderer.set_property('cell-background', 'yellow')

        column = gtk.TreeViewColumn(_("Licence"), renderer)
        treeview.append_column(column)
#        column.set_sort_column_id(4)
        column.set_cell_data_func(renderer, self.make_pb)
        column.set_sizing(gtk.TREE_VIEW_COLUMN_FIXED)
        column.set_resizable(True)
        column.set_fixed_width(100)

        column = gtk.TreeViewColumn(_(" "))
        treeview.append_column(column)
        column.set_sizing(gtk.TREE_VIEW_COLUMN_FIXED)
        column.set_resizable(True)
        column.set_fixed_width(1)

    def make_pb(self, tvcolumn, cell, model, iter):
        url = model.get_value(iter, self.COLUMN_LICENSEURL)
        if url is None or url == "":
#            pb = gtk.gdk.pixbuf_new_from_file_at_size(img_file, -1, 20)
            cell.set_property('pixbuf', None)
            return

        if "creativecommons" in url:
            try:
                attribution = url.split("/")[4]
                img_file = os.path.join(functions.install_dir(), "images", "license_images", "cc_small", "%s.png" % attribution)
                if os.path.exists(img_file):
                    pb = gtk.gdk.pixbuf_new_from_file_at_size(img_file, -1, 20)
    #            pb = self.render_icon(stock, gtk.ICON_SIZE_MENU, None)
                    cell.set_property('pixbuf', pb)
                else:
                    return
            except:
                return
        elif "nolicense" in url:
            img_file = os.path.join(functions.install_dir(), "images", "license_images", "pd.png")
            if os.path.exists(img_file):
                pb = gtk.gdk.pixbuf_new_from_file_at_size(img_file, -1, 20)
                cell.set_property('pixbuf', pb)
        elif "artlibre" in url:
            img_file = os.path.join(functions.install_dir(), "images", "license_images",
 "artlibre.png")
            if os.path.exists(img_file):
                pb = gtk.gdk.pixbuf_new_from_file_at_size(img_file, -1, 20)
                cell.set_property('pixbuf', pb)

## widget showing stars as raiting for an album
class Rating(gtk.HBox):
    def __init__(self):
        gtk.HBox.__init__(self)
        self.img=[]
        for img in range(0, 10):
            self.img.append(gtk.Image())
            pixbuf = gtk.gdk.pixbuf_new_from_file_at_size(os.path.join(functions.install_dir(), "images", "star.png"), 16, 16)
            #pixbuf = self.img[img].render_icon(gtk.STOCK_ABOUT, gtk.ICON_SIZE_MENU, detail=None)
            self.img[img].set_from_pixbuf(pixbuf)
            self.pack_start(self.img[img], True, True, 0)
            self.img[img].show()
            
    def set_rating(self, rating):
        for img in self.img:
            img.hide()
            
        rating = int(ceil(float(rating)))
        
        for img in range(0, rating):
            self.img[img].show()

## my statusbar widget
class StatusBar(gtk.HBox):
    def __init__(self, *argv):
        self.statusbars = {}

        gtk.HBox.__init__(self, False)
        
        for item in argv:
            self.statusbars[item] = {'statusbar':gtk.Statusbar()} 
            self.statusbars[item]['conid'] = self.statusbars[item]['statusbar'].get_context_id("Status")
            self.statusbars[item]['msgid'] = self.statusbars[item]['statusbar'].push(self.statusbars[item]['conid'], "")
            self.statusbars[item]['curtext'] =  None
            if item != argv[len(argv)-1]:
                self.statusbars[item]['statusbar'].set_has_resize_grip(False)
                self.statusbars[item]['sep'] = gtk.VSeparator()
                self.pack_start(self.statusbars[item]['statusbar'], True, True, 0)
                self.pack_start(self.statusbars[item]['sep'], False, False, 0)
                self.statusbars[item]['statusbar'].show()
                self.statusbars[item]['sep'].show()
            else:
                self.statusbars[item]['statusbar'].set_has_resize_grip(True)
                self.pack_start(self.statusbars[item]['statusbar'], False, True, 0)
                self.statusbars[item]['statusbar'].show()
#                self.progressBar = gtk.ProgressBar()
#                self.progressBar.set_size_request(30,5)
#                self.progressBar.hide()
#                self.statusbars[item]['statusbar'].add(self.progressBar)

    def set_text(self, statusbar, text):
        if self.statusbars[statusbar]['curtext'] != text:
            self.statusbars[statusbar]['msgid'] = self.statusbars[statusbar]['statusbar'].push(self.statusbars[statusbar]['conid'], text)
            self.statusbars[statusbar]['statusbar'].set_tooltip_text(text)
            self.statusbars[statusbar]['curtext'] = text

## ComboBox for setting results per page
class ResultsPerPageCombo(gtk.ComboBox):
    def __init__(self):
        liststore = gtk.ListStore(gobject.TYPE_STRING)
        gtk.ComboBox.__init__(self,liststore)
        cell = gtk.CellRendererText()

        ## Used to tell apart user generated
        # and auto computed changes of the
        # active item
        self.auto_setting_item = False

        self.pack_start(cell, True)
        self.add_attribute(cell, 'text', 0)
        self.set_tooltip_text(_("How many results should be shown?"))

        self.cbResultsPerPage = gtk.combo_box_new_text()

        self.modelist = ["10", "20", "30", "40", "50", "60", "70", "80", "90", "100"]
        for mode in self.modelist:
            self.append_text(mode)
        self.set_active(0)

    def set_item(self, mode):
        self.auto_setting_item = True
        self.set_property("active", self.modelist.index(str(mode)))
        self.auto_setting_item = False

## holds some basic jamendo order keywords
class OrderCombo(gtk.ComboBox):
    def __init__(self):
        liststore = gtk.ListStore(gobject.TYPE_STRING)
        gtk.ComboBox.__init__(self, liststore)
        cell = gtk.CellRendererText()

        ## Used to tell apart user generated
        # and auto computed changes of the
        # active item
        self.auto_setting_item = False

        self.pack_start(cell, True)
        self.add_attribute(cell, 'text', 0)
        self.set_tooltip_text(_("Select how to order results"))
        
        self.modelist = ["rating", "ratingweek", "ratingmonth", "date", "downloaded", "listened", "starred", "playlisted"]
        for mode in self.modelist:
            self.append_text(mode)
        self.set_active(1)
        
    def set_item(self, mode):
        self.auto_setting_item = True
        self.set_active(self.modelist.index(mode))
        self.auto_setting_item = False

## holds some pre-selected tags
class TagsCombo(gtk.ComboBoxEntry): #Entry
    def __init__(self, pyjama):
        liststore = gtk.ListStore(gobject.TYPE_STRING)
        gtk.ComboBoxEntry.__init__(self, liststore, ) #Entry

        ## Used to tell apart user generated
        # and auto computed changes of the
        # active item
        self.auto_setting_item = False

        cell = gtk.CellRendererText()
        self.pack_start(cell, False)
        self.set_wrap_width(4)
        self.set_tooltip_text(_("Select tags to show"))

        self.set_model(liststore)
#        self.add_attribute(cell, 'text', 0)     

        self.entry = self.child


        default = "ambient experimental instrumental electro alternativ hiphop guitar metal pop punk rock techno triphop world trance progressive gothic hardcore minimal funk dance psychedelic 8bit"
        lst = default.split(" ")
        lst.sort()
        default = " ".join(lst)
        #~ if pyjama.settings.config.has_option("JAMENDO", "TAGs") == False:
        tags = pyjama.settings.get_value("JAMENDO", "newtags", default)
            #~ pyjama.settings.set_value("JAMENDO", "TAGs", default)
        #~ else:
            #~ tags = pyjama.settings.get_value("JAMENDO", "TAGs", default)
#        if not ("--all--") in tags: tags = ("--all-- %s") % tags
        if not _("--all--") in tags: tags = "%s %s" % (_("--all--") , tags)
#        if not _("--custom--") in tags: tags = _("%s --custom--") % tags
        tags = tags.split(" ")
        while "" in tags: tags.remove("")
        self.modelist = tags


        for mode in self.modelist:
            #self.append_text(mode)
            liststore.append([mode])

        self.set_active(0)    
        
    def set_item(self, mode):
        self.auto_setting_item = True
        try:
            self.set_active(self.modelist.index(mode))
        except ValueError:
            # This should not happen at all - but it did once ;)
            self.set_active(0)

        self.auto_setting_item = False

## A label sensible to mouse movements
class MouseLabel(gtk.Label):
    def __init__(self,t):
        gtk.Label.__init__(self, t)

        eventbox = gtk.EventBox()
        eventbox.add(self)
        eventbox.add_events (gtk.gdk.BUTTON_RELEASE)
        boat = gtk.gdk.Cursor(gtk.gdk.WATCH)
        eventbox.window.set_cursor(boat)
        eventbox.connect("realize", self.on_realize)

    def on_realize(self, widget):
        print "asd"
    #     self.set_cursor(watch)

## A button with a StockItem on it
class StockButton(gtk.Button):
    def __init__(self, stock, size=gtk.ICON_SIZE_MENU, text=None):
        gtk.Button.__init__(self, text)

        pixbuf = self.render_icon(stock, size, detail=None)
        self.img = gtk.Image()
        self.img.set_from_pixbuf(pixbuf)
        #set_from_stock(stock_id, size)
        self.set_image(self.img)
        
       
        self.tag = None
        
    def setimage(self, stock, size=gtk.ICON_SIZE_MENU):
        pixbuf = self.render_icon(stock, size, detail=None)
        #self.img = gtk.Image()
        self.img.set_from_pixbuf(pixbuf)
        self.set_image(self.img)


## A Button with an image from a file
class ImageButton(gtk.Button):
    def __init__(self, sFile, w, h=None, text=None):
        gtk.Button.__init__(self, text)
        self.img = gtk.Image()

        # if h is None, assume w being a stock size
        # convert stock size to pixel
        if h is None:
            w, h = gtk.icon_size_lookup(w)
        self.setimage(sFile, w, h)

    def setimage(self, sFile, w, h):
        if not os.path.exists(sFile):
            if os.path.exists(os.path.join(functions.install_dir(), "images", sFile)):
                sFile = os.path.join(functions.install_dir(), "images", sFile)
        pixbuf = gtk.gdk.pixbuf_new_from_file_at_size(sFile, w, h)
        self.img.set_from_pixbuf(pixbuf)
        #set_from_stock(stock_id, size)
        self.set_image(self.img)

    def setstock(self, stock, size=gtk.ICON_SIZE_MENU):
        pixbuf = self.render_icon(stock, size, detail=None)
        self.img.set_from_pixbuf(pixbuf)
        self.set_image(self.img)

## A simple stock/image button
class ImageButton_new(gtk.Button):
    ## Constructor
    # @param self OP
    # @param content A local image-file or a stock-button
    # @param size Depending on 'content' this should be a tuple holding
    # the image's desired size - e.g. (50, 50) - or a gtk.STOCK_SIZE
    def __init__(self, content, size=None):
        gtk.Button.__init__(self)
        
        ## check if image is stock image or path
        if gtk.stock_lookup(content):
            self.set_from_stock(content, size)
        else:
            pass
            #IMAGE!

    ## Set the button's image from stock
    def set_from_stock(self, stock, size=None):
        if not size:
            size = gtk.ICON_SIZE_SMALL_TOOLBAR
        image = gtk.image_new_from_stock(stock, size)
        self.set_image(image)
        

    ## Set the button's image from a file
    # @todo implement
    def set_from_file(self, file, size):
        pass

class MyLinkButton(gtk.Button):
    def __init__(self, uri, text="", small=False):
        gtk.Button.__init__(self)
        self.lbl = gtk.Label()
        self.lbl.show()
        self.add(self.lbl)
        if small:
            self.lbl.set_markup("<u><span foreground='blue' size='small'>%s</span></u>" % text)
        else:
            self.lbl.set_markup("<u><span foreground='blue'>%s</span></u>" % text)
        self.text = text
        self.uri = uri
        self.set_relief(gtk.RELIEF_NONE)

    def set_label(self, text):
        self.lbl.set_markup("<u><span foreground='blue'>%s</span></u>" % text)
        self.text = text

    def get_text(self):
        return self.text

class MyLinkButton_new(gtk.Button):
    def __init__(self, text=None, small=False):
        gtk.Button.__init__(self)
        self.small = small

        hbox = gtk.HBox()
        self.add(hbox)
        
        self.image = gtk.Image()
        self.image.show()

        hbox.pack_start(self.image, False, False)
        
        self.lbl = gtk.Label()
        hbox.pack_start(self.lbl, False, True)
        self.lbl.show()

        self.set_relief(gtk.RELIEF_NONE)

        if text:
            self.__set_text(text)
        

    def set_label(self, text):
        self.lbl.set_markup("<u><span foreground='blue'>%s</span></u>" % text)
        self.text = text

    def set_text(self, text):
        text = clear(text)
        self.set_tooltip_text(text)
        if self.small:
            #~ self.lbl.set_markup("<u><span foreground='blue' size='small'>%s</span></u>" % text)
            self.lbl.set_markup("<span size='small'>%s</span>" % text)
        else:
            self.lbl.set_markup("<u><span foreground='blue'>%s</span></u>" % text)
        self.text = text

    def get_text(self):
        return self.text

    def set_image(self, imgpath, w, h):
        try:
            pb = gtk.gdk.pixbuf_new_from_file_at_size(imgpath, w, h)
            self.image.set_from_pixbuf(pb)
        except Exception as inst:
            print("ERROR: Could not create image: %s" % inst)

# Don't know how to solve this another way
exmaple_layout = gtk.Layout()        
HOVER_COMPACT = 1
HOVER_DETAILED = 2
## This AlbumInfo widget was backported from
# Pyjama2.
class AlbumInfo(gtk.Frame):
    ## Constructor
    # @param Pyjama reference
    # @param album_id If of the album to show
    def __init__(self, pyjama, album, small=False):
        if small:
            hover_type = HOVER_COMPACT
        else:
            hover_type = HOVER_DETAILED

        self.album = album

        if "compact" in sys.argv: hover_type = HOVER_COMPACT
        
        self.__calculate_size(hover_type)
            
        self.pyjama = pyjama

        gtk.Frame.__init__(self)
        if self.pyjama.settings.get_value("PYJAMA", "show_albuminfo_frames", True):
            self.set_shadow_type(gtk.SHADOW_ETCHED_IN)
        else:
            self.set_shadow_type(gtk.SHADOW_NONE)
            
        #~ self.set_shadow_type(gtk.SHADOW_NONE) # SHADOW_NONE SHADOW_ETCHED_IN

        self.eventbox = gtk.EventBox()
        self.eventbox.set_above_child(False)
        self.eventbox.add_events(gtk.gdk.ENTER_NOTIFY and gtk.gdk.LEAVE_NOTIFY)
        self.eventbox.connect("enter-notify-event", self.enter_notify_cb)
        self.eventbox.connect("leave-notify-event", self.leave_notify_cb)
        self.eventbox.connect("realize", self.eventbox_realize_cb)
        self.eventbox.connect("button_release_event", self.button_release_cb)

        self.add(self.eventbox)

        self.layout = gtk.Layout()
        self.eventbox.add(self.layout)

        #~ style = self.layout.get_style()
        #~ self.inverted = str(style.bg[gtk.STATE_NORMAL])

        self.image = gtk.Image()
        self.layout.put(self.image, 5, 5)
        self.layout.set_size_request(self.width, self.height)

        imagepath = self.pyjama.get_album_image(album['album_id'],100)
        try:
            pb = gtk.gdk.pixbuf_new_from_file_at_size(imagepath, 100, 100)
            self.image.set_from_pixbuf(pb)
        except:
            print("Could not read %s" % imagepath)
            self.image.set_from_stock(gtk.STOCK_MISSING_IMAGE, gtk.ICON_SIZE_DIALOG)
        self.image.show()

        self.lbArtist = MyLinkButton_new(small=True)
        self.layout.put(self.lbArtist, 0, 0)
        self.lbArtist.set_image( \
        os.path.join(functions.install_dir(), "images", "personal.png"),
            self.icon_width,
            self.icon_height)

        self.lbAlbum = MyLinkButton_new(small=True)
        self.layout.put(self.lbAlbum, self.album_link_position[0], self.album_link_position[1])
        self.lbAlbum.set_image( \
        os.path.join(functions.install_dir(), "images", "cd.png"),
            self.icon_width,
            self.icon_height)
        self.lbArtist.connect("clicked", self.__cb_linkbutton_clicked)
        self.lbAlbum.connect("clicked", self.__cb_linkbutton_clicked)

        self.show_all()
        self.lbAlbum.hide() #stf

        self.widgets_list = []

        self.buttons = []

        self.bPlay = ImageButton_new(gtk.STOCK_MEDIA_PLAY)
        self.layout.put(self.bPlay, 0, 0)
        self.buttons.append(self.bPlay)
        self.bPlay.connect("clicked", self.cb_bControlPlay)

        self.bAppend = ImageButton_new(gtk.STOCK_ADD)
        self.layout.put(self.bAppend, 0, 0)
        self.buttons.append(self.bAppend)
        self.bAppend.connect("clicked", self.cb_bControlAdd)
        
        self.widgets_list.append(self.bPlay)
        self.widgets_list.append(self.bAppend)
        self.pyjama.Events.raise_event("albuminfo_created", self)

        self.__arrange_widgets()
        
        self.set(album['album_id'], album['album_name'], album['artist_name'], hover_type)
        

    def __calculate_size(self, hover_type):
        self.hover_type = hover_type
        if self.hover_type == HOVER_DETAILED:
            self.height = 130
            self.width = 110
            self.icon_width = self.icon_height = 20

            self.artist_link_position = (0, 100)
            self.album_link_position = (0, 120)

            self.button_slots = [(75,8), (75,43), (75,78), (40, 78), (5, 78)]
            #~ self.COVER_WIDTH = self.COVER_HEIGHT = 100
        else:
            self.height = 110
            self.width = 110
            self.icon_width = self.icon_height = 20
            
            self.artist_link_position = (0, 55)
            self.album_link_position = (0, 80)

            self.button_slots = [(8,8), (43,8), (78,8), (8,43), (43, 43)]
            #~ self.COVER_WIDTH = self.COVER_HEIGHT = 75


    def __arrange_widgets(self):            
        self.layout.set_size_request(self.width, self.height)
        
        self.layout.move(self.lbArtist, self.artist_link_position[0], self.artist_link_position[1])
        self.layout.move(self.lbAlbum, self.album_link_position[0], self.album_link_position[1])

        self.lbArtist.set_size_request(self.width, self.icon_height+10 )
        self.lbAlbum.set_size_request(self.width, self.icon_height+10 )

        counter = 0
        for item in self.widgets_list:
            self.layout.move(item, self.button_slots[counter][0], self.button_slots[counter][1])
            counter += 1
            
        #~ self.layout.move(self.bPlay, self.button_slots[0][0], self.button_slots[0][1])
        #~ self.layout.move(self.bAppend, self.button_slots[1][0], self.button_slots[1][1])

        #~ self.set_size_request(self.width, self.height)


    def set(self, album_id, album_name, artist_name, hover_type=None):
        if hover_type and hover_type != self.hover_type:
            self.__calculate_size(hover_type)
            self.__arrange_widgets()

        self.album_id = album_id

        self.layout.move(self.image, 5, 5)

        self.lbArtist.set_text(artist_name)
        self.lbArtist.set_tooltip_markup(_("<b>Artist</b>: %s") % self.lbArtist.get_tooltip_text())

        self.lbAlbum.set_text(album_name)
        self.lbAlbum.set_tooltip_markup(_("<b>Album</b>: %s") % self.lbAlbum.get_tooltip_text())
        
        if self.hover_type == HOVER_COMPACT:
            self.lbArtist.hide()
            self.lbAlbum.hide()
        
       
    def show_buttons(self):
        color = gtk.gdk.color_parse("orange")

        self.set_image_alpha(self.image, 75)

        if self.hover_type == HOVER_COMPACT:
            #~ self.image.hide()
            self.lbArtist.show()
            #stf self.lbAlbum.show()
        self.layout.modify_bg(gtk.STATE_NORMAL, color)

        for item in self.widgets_list: item.show()
        self.lbAlbum.hide() #stf

    def hide_buttons(self):
        if self.hover_type == HOVER_COMPACT:
            #~ self.image.show()
            self.lbArtist.hide()
            self.lbAlbum.hide()
        self.layout.modify_style(exmaple_layout.get_modifier_style())

        self.set_image_alpha(self.image, 255)
            
        for item in self.widgets_list: item.hide()

    def set_image_alpha(self, image, alpha):
        try:
            pb = image.get_pixbuf()
        except ValueError as inst:
            print("Image does not contain a Pixbuf")
            return
        if not pb: return
        
        pb = pb.add_alpha(False, 1,1,1)
        pixel_array = pb.get_pixels_array()
        pixel_array[:,:,3] = alpha
        image.set_from_pixbuf(pb)

    def set_error_image(self):
        self.image.set_from_stock(gtk.STOCK_MISSING_IMAGE, gtk.ICON_SIZE_DIALOG)

        # Set no-image-available-stock

    def set_cover(self, path):
        try:
            pb = gtk.gdk.pixbuf_new_from_file(path)
            #~ col = pb.get_colorspace()
            #~ ch = pb.get_n_channels()
        
            

            #~ pixbuf = pb
            #~ pixbuf = pixbuf.add_alpha(False, 1, 1, 1)
            #~ pixmap, mask = pb.render_pixmap_and_mask(10)
            #~ gc = pixmap.new_gc()
            #~ pixbuf = pixbuf.get_from_drawable(pixmap, pixmap.get_colormap(), 0, 0, 0, 0, -1, -1)
            #~ print pixbuf.get_has_alpha()
            #~ self.image.set_from_pixbuf(pixbuf)

            #~ pb = pb.add_alpha(False, 1, 1, 1)
            #~ pixmap, mask = pb.render_pixmap_and_mask(10)
            #~ pb = pb.render_threshold_alpha(pixmap, 0, 0, 0, 0, -1, -1, 200)
            #~ print pb.get_has_alpha()
            
            self.image.set_from_pixbuf(pb)
        except Exception, inst:
            self.pyjama.errorhandler()
            print("ERROR: %s" % inst)
            self.set_error_image()

    def __cb_image_clicked(self, ev, ev2, ev3):
        #~ x,y = self.cover.get_pointer()
        #~ if x > 0 and x < 100 and y > 0 and y < 100:
            #~ #print self.album
            #~ #self.par.layout['top'].hide()
            #~ #print self.par.jamendo.albuminfos(self.album['album_id'])
        self.__cb_linkbutton_clicked(self.lbAlbum, None)


    def cb_bControlPlay(self, widget, event=None):
        tracks = self.pyjama.db.albumtracks(self.album['album_id'])
        track_count = len(tracks)

        if track_count == 0:
            print ("Album not in database, yet.")
            #print album['public_date']
            dia = MyDialog(_('Album non existant.'),
                              self.pyjama.window.get_toplevel(),
                              gtk.DIALOG_MODAL | gtk.DIALOG_DESTROY_WITH_PARENT, 
                                (gtk.STOCK_OK, gtk.RESPONSE_ACCEPT), gtk.STOCK_DIALOG_WARNING, _('This album is not in the database.\nPerhaps Jamendo did not unloack that album, yet\n or you are using a old local database.'))
            dia.run()
            dia.destroy()
            return None
        self.pyjama.appendtracks(tracks, play=True)
        
    def cb_bControlAdd(self, widget, event=None):
        tracks = self.pyjama.db.albumtracks(self.album['album_id'])
        track_count = len(tracks)

        if track_count == 0:
            print ("Album not in database, yet.")
            #print album['public_date']
            dia = MyDialog(_('Album non existant.'),
                              self.pyjama.window.get_toplevel(),
                              gtk.DIALOG_MODAL | gtk.DIALOG_DESTROY_WITH_PARENT, 
                                (gtk.STOCK_OK, gtk.RESPONSE_ACCEPT), gtk.STOCK_DIALOG_WARNING, _('This album is not in the database.\nPerhaps Jamendo did not unloack that album, yet\n or you are using a old local database.'))
            dia.run()
            dia.destroy()
            return None

        self.pyjama.appendtracks(tracks)
   
    #
    # Callbacks
    #
    def __cb_linkbutton_clicked(self, widget, event=None):
        if widget == self.lbArtist:
            artistdetails = self.pyjama.db.artistinfos(self.album['artist_id'])
            self.pyjama.layouts.show_layout("artist", artistdetails)
        elif widget == self.lbAlbum:
            albumdetails = self.pyjama.jamendo.albuminfos(self.album['album_id'])
            if not albumdetails: return
            self.pyjama.layouts.show_layout("album", albumdetails)
           
    def button_release_cb(self, widget, event):
        self.__cb_image_clicked(None, None, None)
        #~ self.pyjama.ui.show_page("album-details", album=self.album_id)
    
    def eventbox_realize_cb(self, widget):
        widget.get_window().set_cursor(gtk.gdk.Cursor(gtk.gdk.HAND2))

    def button_clicked_cb(self, widget, button):
        if button == "play":
            print("Play")
            st = "http://api.jamendo.com/get2/stream/track/m3u/?album_id=!!ID!!&order=numalbum_asc&n=all".replace("!!ID!!", str(self.album_id))
            os.system("totem %s &" % st)
        elif button == "append":
            os.system("totem --next")
            print("Append")

    def enter_notify_cb(self, widget, event):
        self.show_buttons()


    def leave_notify_cb(self, widget, event):
        self.hide_buttons()

    def image_download_cb(self, query):
        if not query.error:
            self.set_cover(query.path)
        else:
            print("Image not available")
            self.set_error_image()

## Widget showing cover, artist name and album name from an album id
# also having a hover-menu
target = [
    ('STRING', 0, 0),
    ('text/plain', 0, 0),
    ('application/x-rootwin-drop', 0, 1)
]

class AlbumInfo_old(gtk.Frame):
    def __init__(self, pyjama, album, small=False):
        self.pyjama = pyjama
        self.small = small

        if small:
            self.WIDTH, self.HEIGHT = 100, 110
            self.ICON_HEIGHT = self.ICON_WIDTH = 20
            self.COVER_WIDTH = self.COVER_HEIGHT = 75
            self.COVER_POS_X, self.COVER_POS_Y = (self.WIDTH - self.COVER_WIDTH) // 2 - 5, 0
        else:
            self.WIDTH, self.HEIGHT = 150, 160
            self.ICON_HEIGHT = self.ICON_WIDTH = 20
            self.COVER_WIDTH = self.COVER_HEIGHT = 100
            self.COVER_POS_X, self.COVER_POS_Y = (self.WIDTH - self.COVER_WIDTH) // 2 - 7, 0 


        self.album = album

        gtk.Frame.__init__(self, "")
        #~ self.set_label_align(0.5, 0.5)
        if self.pyjama.settings.get_value("PYJAMA", "show_albuminfo_frames", True):
            self.set_shadow_type(gtk.SHADOW_ETCHED_IN)
        else:
            self.set_shadow_type(gtk.SHADOW_NONE)

        if small:
            self.set_size_request(self.WIDTH, self.HEIGHT)
        else:
            self.set_size_request(self.WIDTH, self.HEIGHT)

        ## Eventbox
        # for mouse events over the whole layout
        self.eventbox = gtk.EventBox()
        self.eventbox.set_above_child(False) # ???
        self.eventbox.add_events (gtk.gdk.ENTER_NOTIFY_MASK)
        self.eventbox.add_events (gtk.gdk.LEAVE_NOTIFY_MASK)
        self.eventbox.connect("enter-notify-event", self.__cb_enter_box)
        self.eventbox.connect("leave-notify-event", self.__cb_leave_box)
        self.eventbox.connect("button-press-event", self.__cb_image_clicked, album)
        self.add(self.eventbox)

        ## Cover Image
        # Get image at 100x100 always and resize it after that
        # in order to not download an image for each size
        imagepath = self.pyjama.get_album_image(album['album_id'],100)
        self.cover = gtk.Image()
        try:
            pb = gtk.gdk.pixbuf_new_from_file_at_size(imagepath, self.COVER_WIDTH, self.COVER_HEIGHT)
            self.cover.set_from_pixbuf(pb)
        except:
            self.cover.set_from_stock(gtk.STOCK_MISSING_IMAGE, gtk.ICON_SIZE_DIALOG)
        self.cover.connect("button-press-event", self.__cb_image_clicked, album)

        self.eventbox_cover = gtk.EventBox()
        #~ self.eventbox_cover.set_above_child(False) # ???
        self.eventbox.connect("enter-notify-event", self.__cb_enter_box)
        self.eventbox.connect("leave-notify-event", self.__cb_leave_box)
        #~ self.eventbox_cover.connect("button-press-event", self.__cb_image_clicked, album)
        self.eventbox_cover.add(self.cover)
        self.eventbox_cover.connect("realize", self.__cb_realize)

        ## Artist Link
        artist_name = album['artist_name']
        self.lArtist = MyLinkButton(artist_name, clear(artist_name)[:20], small=True)
        self.lArtist.set_tooltip_text(artist_name)
        self.lArtist.connect("clicked", self.__cb_linkbutton_clicked)

        ## Album Link
        album_name = album['album_name']
        self.lAlbum = MyLinkButton(album_name, clear(album_name)[:20], small=True)
        self.lAlbum.set_tooltip_text(album_name)
        self.lAlbum.connect("clicked", self.__cb_linkbutton_clicked)


        ## Icons
        i1 = self.__create_image("personal.png", self.ICON_WIDTH, self.ICON_HEIGHT)
        i2 = self.__create_image("cd.png", self.ICON_WIDTH, self.ICON_HEIGHT)

        ## Controls
        # Play
        self.bControlPlay = StockButton(gtk.STOCK_MEDIA_PLAY)
        self.bControlPlay.set_tooltip_text(_("Append this album on playlist and play it"))
        self.bControlPlay.connect("clicked", self.cb_bControlPlay)
        # Add
        self.bControlAdd = StockButton(gtk.STOCK_ADD)
        self.bControlAdd.set_tooltip_text(_("Append this album on playlist"))
        self.bControlAdd.connect("clicked", self.cb_bControlAdd)

        ## Layout
        self.layout = gtk.Layout()
        if small:
            self.layout.set_size(self.WIDTH - 10, self.HEIGHT)
        else:
            self.layout.set_size(self.WIDTH - 10, self.HEIGHT)
        self.eventbox.add(self.layout)
        #~ self.add(self.layout)
        # Put everything to the layout
        self.layout.put(self.eventbox_cover, self.COVER_POS_X, self.COVER_POS_Y) #COVER
        
        self.layout.put(i1, 5, self.COVER_POS_Y + self.COVER_HEIGHT - 5)
        self.layout.put(i2, 5, self.COVER_POS_Y + self.COVER_HEIGHT + 15)
        self.layout.put(self.lArtist, 5 + 15 , self.COVER_POS_Y + self.COVER_HEIGHT - 5)
        self.layout.put(self.lAlbum, 5 + 15, self.COVER_POS_Y + self.COVER_HEIGHT + 15)

        self.layout.put(self.bControlPlay, self.COVER_POS_X + self.COVER_WIDTH - 0, self.COVER_POS_Y + 5)
        self.layout.put(self.bControlAdd, self.COVER_POS_X + self.COVER_WIDTH - 0, self.COVER_POS_Y + 35)
        
        if self.pyjama.debug_extreme:
            print ("Created AlbumInfo for %s[...]") % str(album['album_name'][:20])

        self.pyjama.Events.raise_event("albuminfo_created", self)

        ## Show
        self.eventbox_cover.show()
        self.eventbox.show()
        self.layout.show()
        self.cover.show()
        self.lArtist.show()
        self.lAlbum.show()
        self.show()

        self.__setcolor(self.eventbox_cover)
        self.__setcolor(self.eventbox)
        self.__setcolor(self.layout)

    #
    # Callbacks
    #
    def __cb_realize(self, widget):
        widget.get_window().set_cursor(gtk.gdk.Cursor(gtk.gdk.HAND2))
    
    def __cb_leave_box(self, widget, event):
        x, y = event.x, event.y
        if x + 7 > self.WIDTH or y + 30 > self.HEIGHT or x <= 1 or y <= 1:
            self.pyjama.Events.raise_event("hide_controls", self)
            self.bControlPlay.hide()
            self.bControlAdd.hide()

    def __cb_enter_box(self, widget, event):
        self.pyjama.Events.raise_event("show_controls", self)
        self.bControlPlay.show()
        self.bControlAdd.show()

    def __cb_linkbutton_clicked(self, widget, event=None):
        if widget == self.lArtist:
            artistdetails = self.pyjama.db.artistinfos(self.album['artist_id'])
            self.pyjama.layouts.show_layout("artist", artistdetails)
        elif widget == self.lAlbum:
            albumdetails = self.pyjama.jamendo.albuminfos(self.album['album_id'])
            if not albumdetails: return
            self.pyjama.layouts.show_layout("album", albumdetails)
    #~ def source_drag_data_get(self, btn, context, selection_data, info, time):
        #~ print "start dragging"
        #~ if info == 1:
            #~ print 'I was dropped on the rootwin'
        #~ else:
            #~ selection_data.set(selection_data.target, 8, "I'm Data!")
#~ 
    #~ def source_drag_data_delete(self, btn, context, data):
        #~ print 'Delete the data!'

    def __cb_image_clicked(self, ev, ev2, ev3):
        #~ x,y = self.cover.get_pointer()
        #~ if x > 0 and x < 100 and y > 0 and y < 100:
            #~ #print self.album
            #~ #self.par.layout['top'].hide()
            #~ #print self.par.jamendo.albuminfos(self.album['album_id'])
        self.__cb_linkbutton_clicked(self.lAlbum, None)


    def cb_bControlPlay(self, widget, event=None):
        tracks = self.pyjama.db.albumtracks(self.album['album_id'])
        track_count = len(tracks)

        if track_count == 0:
            print ("Album not in database, yet.")
            #print album['public_date']
            dia = MyDialog(_('Album non existant.'),
                              self.pyjama.window.get_toplevel(),
                              gtk.DIALOG_MODAL | gtk.DIALOG_DESTROY_WITH_PARENT, 
                                (gtk.STOCK_OK, gtk.RESPONSE_ACCEPT), gtk.STOCK_DIALOG_WARNING, _('This album is not in the database.\nPerhaps Jamendo did not unloack that album, yet\n or you are using a old local database.'))
            dia.run()
            dia.destroy()
            return None
        self.pyjama.appendtracks(tracks, play=True)
        
    def cb_bControlAdd(self, widget, event=None):
        tracks = self.pyjama.db.albumtracks(self.album['album_id'])
        track_count = len(tracks)

        if track_count == 0:
            print ("Album not in database, yet.")
            #print album['public_date']
            dia = MyDialog(_('Album non existant.'),
                              self.pyjama.window.get_toplevel(),
                              gtk.DIALOG_MODAL | gtk.DIALOG_DESTROY_WITH_PARENT, 
                                (gtk.STOCK_OK, gtk.RESPONSE_ACCEPT), gtk.STOCK_DIALOG_WARNING, _('This album is not in the database.\nPerhaps Jamendo did not unloack that album, yet\n or you are using a old local database.'))
            dia.run()
            dia.destroy()
            return None

        self.pyjama.appendtracks(tracks)

    #
    # Methodes
    #
    def __create_image(self, fl, w, h):
        imgpath = os.path.join(functions.install_dir(), "images", fl)
        img = gtk.Image()
        
        if os.path.exists(imgpath):
            pb = gtk.gdk.pixbuf_new_from_file_at_size(imgpath, w, h)
            img.set_from_pixbuf(pb)
            
        img.show()
        return img

    def __setcolor(self, widget):
        if self.pyjama.nocolor:
            return None 
        style = widget.get_style()
        color = widget.get_colormap()
        bg = color.alloc_color(self.pyjama.window.bgcolor)
        fg = color.alloc_color(0, 0, 0, 0)
        style.bg[gtk.STATE_NORMAL] = bg
        style.fg[gtk.STATE_NORMAL] = fg
        widget.set_style(style)

## holds some pre-selected tags
class PresetsCombo(gtk.ComboBox): #Entry
    def __init__(self, presets, pyjama=None):
        #~ liststore = gtk.ListStore(gobject.TYPE_STRING, gobject.TYPE_BOOLEAN)
        liststore = gtk.ListStore(gobject.TYPE_STRING)
        gtk.ComboBox.__init__(self, liststore)
        cell = gtk.CellRendererText()
        #~ bol = gtk.CellRendererText()

        ## Used to tell apart user generated
        # and auto computed changes of the
        # active item
        self.auto_setting_item = False

        self.pack_start(cell, True)
        #~ self.pack_end(bol, False)
        
        self.add_attribute(cell, 'text', 0)
        #~ self.add_attribute(bol, 'sensitive', 1)
        self.set_tooltip_text(_("Select a preset"))

        self.modelist = presets
        for mode in self.modelist:
            self.append_text(mode)
        self.set_active(0)

        #~ print self.get_cells()
        #self.set_attribute(bol, 
        
    def set_item(self, mode):
        self.auto_setting_item = True
        try:
            self.set_active(self.modelist.index(mode))
        except ValueError:
            # This should not happen at all - but it did once ;)
            self.set_active(0)

        self.auto_setting_item = False

class EqualizerBox(gtk.HBox):
    def __init__(self, pyjama):
        self.pyjama = pyjama

        ## Number of eq-bands
        self.n = self.pyjama.player.equalizer_bands

        self.preset_dict =  self.get_presets_from_file(bands=self.n)
        self.current_preset = "Default"

        ## used to store eq-values for each band
        self.values = []
        for i in range(self.n):
            val = self.pyjama.settings.get_value("SOUND", "band%i" % i, 0.0, float)
            self.values.append(val)

        ## If current preset (from settings) is not in self.preset_dict,
        # add it as "User preset"            
        found = False            
        for item in self.preset_dict:
            if functions.compare_float_lists(self.preset_dict[item], self.values): #self.preset_dict[item] == self.values:
                found = True
                self.current_preset = item
        if not found:
            self.current_preset = "User Preset"
            self.preset_dict[self.current_preset] = copy.copy(self.values)

        ## also stores eq-values for each band - stored for discrard-fct
        # won't changed
        self.start_values = copy.copy(self.values)

        if self.n==10:
            labels=('29 Hz','59 Hz','119 Hz','227 Hz','474 Hz','947 Hz',
                '1.98 kHz','3.7 kHz','7.5 kHz','15.0 kHz')
        elif self.n==3:
            labels=('100 Hz','1.1 kHz','11.0 kHz')
        else:
            labels=[]
            for a in range(self.n):
                labels.append("")

        ## Adjustments
        self.adjs={}
        
        gtk.HBox.__init__(self)
        self.show()

        frame = gtk.Frame("Equalizer")
        frame.show()
        self.pack_start(frame, False, False, 20)

        hbox_bottom = gtk.HBox()
        hbox_bottom.show()

        frame.add(hbox_bottom)
        for i in range(self.n):
            self.adjs[i]=gtk.Adjustment(value=self.values[i],
                                        lower=-24, upper=12, 
                                        step_incr=0.1)
            self.adjs[i].connect("value_changed", self.cb_eq_value_changed,i)
            scale=gtk.VScale(self.adjs[i])
            scale.set_inverted(True)
            scale.set_size_request(-1, 200)
            scale.show()
            vbox=gtk.VBox()
            vbox.pack_start(scale)
            lbl = gtk.Label()
            lbl.set_markup("<span size='xx-small'>%s</span>" % labels[i])
            #~ lbl.set_size_request(35, -1)
            vbox.pack_start(lbl, False, False, 5)
            #button=gtk.Button("clear")
            button = StockButton(gtk.STOCK_CLEAR)
            #~ button.set_size_request(35, -1)
            #button.set_relief(gtk.RELIEF_NONE)
            button.connect("clicked", self.cb_eq_clear_clicked,i)
            button.show()
            
            vbox.pack_start(button, False, False, 0)
            vbox.show_all()
            hbox_bottom.pack_start(vbox, False, False, 3)


        vbox=gtk.VBox()
        vbox.show()
        f = gtk.Frame("Presets")
        f.show()
        cbPresets = PresetsCombo(self.preset_dict.keys())
        cbPresets.set_item(self.current_preset)
        cbPresets.connect("changed", self.cb_preset_changed)
        cbPresets.show()
        bEdit = StockButton(gtk.STOCK_PREFERENCES)
        bEdit.show()
        bEdit.set_tooltip_text("Edit Profiles")
        bEdit.connect("clicked", self.cb_btn_clicked)
        hbox = gtk.HBox()
        hbox.show()
        hbox.pack_start(cbPresets, False, True, 10)
        hbox.pack_start(bEdit, False, True, 10)
        f.add(hbox)
        vbox.pack_start(f, False, True, 10)
        #~ hbox.pack_start(p, False, False, 3)
        hbox_bottom.pack_start(vbox, False, True, 3)

        self.get_presets_from_file()
    
    def cb_btn_clicked(self, widget):
        try:
            f  =os.path.join(self.pyjama.home, "eq_presets")
            EditDialog(f)
        except:
            self.pyjama.Events.raise_event("error", None, "Error loading / saving '%s'" % f)
        for child in self.get_children():
            child.destroy()
        self.__init__(self.pyjama)

    def get_presets_from_file(self, sFile = None, bands=10):
        if sFile is None: sFile = os.path.join(functions.preparedirs(), "eq_presets")

        default_presets =   {
                            'Default':[0,0,0,0,0,0,0,0,0,0],
                            'Rock':[11,8,6,4,2,2,4,6,8,11],
                            'Hall':[-6,-3,0,3,6,6,3,0,-3,-6]
                            }

        if os.path.exists(sFile):
            fh = open(sFile, "r")
            content = None
            if fh:
                content = fh.readlines()
                fh.close()
            else:
                return default_presets
            if content is not None:
                presets = {}
                for line in content:
                    if not line.strip().startswith("#") and len(line)>11:
                        if "#" in line:
                            line = line[:line.find("#")]
                        p = line.replace("\n", "").replace(",", ".").split(" ")
                        while "" in p: p.remove("")
                        if len(p) == bands+1:
                            p = p[:11]
                            presets[p[0]] = p[1:]
                if len(presets) <= 0:
                    return default_presets
                if not "Default" in presets:
                    presets["Default"] = [0,0,0,0,0,0,0,0,0,0]
                return presets
        else:
            print ("File %s not found" % sFile)
            
        return default_presets

    def cb_preset_changed(self, widget):
        preset = widget.get_active_text()
        self.current_preset = preset

        for i in range(self.n):
            curval = self.preset_dict[preset][i]

            self.values[i]=curval
            self.adjs[i].set_value(float(curval))
        
        self.pyjama.player.set_equalizer(self.preset_dict[preset])

    def cb_eq_clear_clicked(self, widget, num):
        self.values[num]=0
        self.adjs[num].set_value(0)

        self.pyjama.player.set_equalizer(self.values)
                
    def cb_eq_value_changed(self, widget, num):
        self.values[num]=widget.get_value()

        self.pyjama.player.set_equalizer(self.values)

    def save(self):
        for i in range(self.n):
            self.pyjama.settings.set_value("SOUND", "band%i" % i, self.values[i], float)

    def discard(self):
        self.pyjama.player.set_equalizer(self.start_values)

    def dialog(self):
        dia = gtk.Dialog()
        dia.vbox.pack_start(self)

        dia.set_modal(True)
        dia.set_title("Equalizer")
        dia.set_icon_from_file(os.path.join(functions.install_dir(), "images", "view-media-equalizer.png"))

        #~ bbox = dia.get_action_area()

        dia.add_button(gtk.STOCK_CANCEL, -2)
        dia.add_button(gtk.STOCK_OK, -1)

        dia.set_default_response(-1)



        ret = dia.run()
        if ret == -1:
            self.save()
        else:
            self.discard()
        dia.destroy()

class EditDialog(gtk.Dialog):
    def __init__(self, sFile):
        self.sFile = sFile
        
        gtk.Dialog.__init__(self)
        
        self.set_modal(True)
        self.set_title("Equalizer")
        self.set_icon_from_file(os.path.join(functions.install_dir(), "images", "pyjama.png"))
        self.set_default_size(400, 300)

        self.swText = gtk.ScrolledWindow()
        self.swText.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
        self.tvEdit = gtk.TextView()
        self.buffer = gtk.TextBuffer()

        self.tvEdit.set_buffer(self.buffer)
        self.swText.add(self.tvEdit)

        self.tvEdit.show()
        self.swText.show()

        bbox = self.get_action_area()
        bbox.show()

        bSave = gtk.Button(stock=gtk.STOCK_SAVE)
        bSave.connect("clicked", self.cb_btn_clicked, "save")
        bSave.show()
        bCancel = gtk.Button(stock=gtk.STOCK_CANCEL)
        bCancel.connect("clicked", self.cb_btn_clicked, "cancel")
        bCancel.show()

        bbox.add(bCancel)
        bbox.add(bSave)

        self.vbox.pack_start(self.swText)
        
        try:
            self.buffer.set_text(open(sFile, "r").read())
        except:
            print ("Error opening %s" % sFile)
            raise        
        self.run()
            
    def cb_btn_clicked(self, widget, action):
        if action == "save":
            try:
                fh = open(self.sFile, "w")
                fh.write(self.buffer.get_text(self.buffer.get_start_iter(), self.buffer.get_end_iter()))
                fh.close()                
            except:
                print ("Error writing %s" % sFile)
                self.destroy()
                raise
        self.destroy()
