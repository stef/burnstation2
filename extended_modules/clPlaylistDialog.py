#!/usr/bin/env python
# -*- coding: utf-8 -*-

# ----------------------------------------------------------------------------
# pyjama - python jamendo audioplayer
# Copyright (c) 2009 Daniel Nögel
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

import gobject
import gtk

from modules import clWidgets

(
    COLUMN_FIXED,
    COLUMN_NAME,
    COLUMN_ID
) = range(3)


class PlaylistDialog(gtk.Dialog):
    def __init__(self, parent):
        self.par = parent

        gtk.Dialog.__init__(self)
#        try:
#            self.set_screen(parent.get_screen())
#        except AttributeError:
#            self.connect('destroy', lambda *w: gtk.main_quit())
        self.set_title(_("Jamendo Playlist Import"))

        self.set_border_width(8)
        self.set_size_request(400, 350)

        label = gtk.Label(_("Enter a jamendo username below to show all his playlists.\nTo import a playlist check the checkbox in the list."))
        self.vbox.pack_start(label, False, False)

        HBox = gtk.HBox()
        self.entry = gtk.Entry()
        self.entry.connect("activate", self.cb_entry_activate)
        bSearch = gtk.Button(gtk.STOCK_FIND)
        bSearch.set_use_stock(True)
        bSearch.connect("clicked", self.cb_entry_activate)
        HBox.pack_start(self.entry, True, True)
        HBox.pack_start(bSearch, False, True)
        self.vbox.pack_start(HBox, False, False)

        sw = gtk.ScrolledWindow()
        sw.set_shadow_type(gtk.SHADOW_ETCHED_IN)
        sw.set_policy(gtk.POLICY_NEVER, gtk.POLICY_AUTOMATIC)
        self.vbox.pack_start(sw)


        # create tree model
        model = gtk.ListStore(
            gobject.TYPE_BOOLEAN,
            gobject.TYPE_STRING,
            gobject.TYPE_UINT)
        

        # create tree view
        self.treeview = gtk.TreeView(model)
        self.treeview.set_rules_hint(True)
        self.treeview.set_search_column(COLUMN_NAME)

        sw.add(self.treeview)

        # add columns to the tree view
        self.__add_columns(self.treeview)

        # Buttons
        self.add_button(gtk.STOCK_CANCEL, -1)
        bOK = self.add_button(gtk.STOCK_OK, 1)
#        bOK.connect("clicked", self.cb_bOK_clicked)
        self.show_all()

    def populate_list(self, data):
        lstore = self.treeview.get_model()
        lstore.clear()

        for item in data:
            iter = lstore.append()
            lstore.set(iter,
                COLUMN_FIXED, False,
                COLUMN_NAME, item['name'],
                COLUMN_ID, item['id']
                )
        return lstore

    def fixed_toggled(self, cell, path, model):
        # get toggled iter
        iter = model.get_iter((int(path),))
        fixed = model.get_value(iter, COLUMN_FIXED)

        # do something with the value
        fixed = not fixed

        # set new value
        model.set(iter, COLUMN_FIXED, fixed)

    def __add_columns(self, treeview):
        model = treeview.get_model()

        # column for fixed toggles
        renderer = gtk.CellRendererToggle()
        renderer.connect('toggled', self.fixed_toggled, model)

        column = gtk.TreeViewColumn(_('Import'), renderer, active=COLUMN_FIXED)

        # set this column to a fixed sizing(of 50 pixels)
        column.set_sizing(gtk.TREE_VIEW_COLUMN_FIXED)
        column.set_fixed_width(50)

        treeview.append_column(column)

        # column for id
#        column = gtk.TreeViewColumn('Bug Number', gtk.CellRendererText(),
#                                    text=COLUMN_NUMBER)
#        column.set_sort_column_id(COLUMN_NUMBER)
#        treeview.append_column(column)

        # column for description
        column = gtk.TreeViewColumn('Name', gtk.CellRendererText(),
                                     text=COLUMN_NAME)
        column.set_sort_column_id(COLUMN_NAME)
        treeview.append_column(column)

    def cb_entry_activate(self, widget):
        txt  = self.entry.get_text().replace(" ", "+")
        playlists = self.par.user_playlists(txt)
        print playlists
        if playlists == []:
            dia = clWidgets.MyDialog(_('No playlists found'),
                                      self.par.pyjama.window.get_toplevel(),
                                      gtk.DIALOG_MODAL | gtk.DIALOG_DESTROY_WITH_PARENT, 
                                        (gtk.STOCK_OK, gtk.RESPONSE_ACCEPT),        gtk.STOCK_DIALOG_WARNING, _('No playlists could be found for %s' % txt))
            dia.run()
            dia.destroy()
        else:
            self.populate_list(playlists)



class PlaylistManageDialog(gtk.Dialog):
    def __init__(self, parent):
        self.par = parent

        gtk.Dialog.__init__(self)
#        try:
#            self.set_screen(parent.get_screen())
#        except AttributeError:
#            self.connect('destroy', lambda *w: gtk.main_quit())
        self.set_title(_("Playlist Manager"))

        self.set_border_width(8)
        self.set_size_request(400, 350)

        label = gtk.Label(_("Select the playlists you want to delete and click the delete button."))
        label.set_line_wrap(True)
        self.vbox.pack_start(label, False, True)


        sw = gtk.ScrolledWindow()
        sw.set_shadow_type(gtk.SHADOW_ETCHED_IN)
        sw.set_policy(gtk.POLICY_NEVER, gtk.POLICY_AUTOMATIC)
        self.vbox.pack_start(sw)


        # create tree model
        model = gtk.ListStore(
            gobject.TYPE_BOOLEAN,
            gobject.TYPE_STRING)
        

        # create tree view
        self.treeview = gtk.TreeView(model)
        self.treeview.set_rules_hint(True)
        self.treeview.set_search_column(COLUMN_NAME)

        sw.add(self.treeview)

        # add columns to the tree view
        self.__add_columns(self.treeview)

        # Buttons
        bDelete = self.add_button(gtk.STOCK_DELETE, 1)
#        bOK.connect("clicked", self.cb_bOK_clicked)
        self.add_button(gtk.STOCK_CANCEL, -1)
        self.show_all()

    def populate_list(self, data):
        lstore = self.treeview.get_model()
        lstore.clear()

        for name, ids in data:
            iter = lstore.append()
            lstore.set(iter,
                COLUMN_FIXED, False,
                COLUMN_NAME, name
                )
        return lstore

    def fixed_toggled(self, cell, path, model):
        # get toggled iter
        iter = model.get_iter((int(path),))
        fixed = model.get_value(iter, COLUMN_FIXED)

        # do something with the value
        fixed = not fixed

        # set new value
        model.set(iter, COLUMN_FIXED, fixed)

    def __add_columns(self, treeview):
        model = treeview.get_model()

        # column for fixed toggles
        renderer = gtk.CellRendererToggle()
        renderer.connect('toggled', self.fixed_toggled, model)

        column = gtk.TreeViewColumn(_('Delete'), renderer, active=COLUMN_FIXED)

        # set this column to a fixed sizing(of 50 pixels)
        column.set_sizing(gtk.TREE_VIEW_COLUMN_FIXED)
        column.set_fixed_width(50)

        treeview.append_column(column)

        # column for id
#        column = gtk.TreeViewColumn('Bug Number', gtk.CellRendererText(),
#                                    text=COLUMN_NUMBER)
#        column.set_sort_column_id(COLUMN_NUMBER)
#        treeview.append_column(column)

        # column for description
        column = gtk.TreeViewColumn('Name', gtk.CellRendererText(),
                                     text=COLUMN_NAME)
        column.set_sort_column_id(COLUMN_NAME)
        treeview.append_column(column)

class SaveDialog(gtk.Dialog):
    def __init__(self, parent):
        self.par = parent

        gtk.Dialog.__init__(self)
#        try:
#            self.set_screen(parent.get_screen())
#        except AttributeError:
#            self.connect('destroy', lambda *w: gtk.main_quit())
        self.set_title(_("Save Playlist"))

        self.set_border_width(8)
#        self.set_size_request(200, 150)

        label = gtk.Label(_("Enter a new Playlist name or select a playlist to overwrite."))
        label.set_line_wrap(True)
        self.vbox.pack_start(label, False, True)

        # Combo Entry
        liststore = gtk.ListStore(gobject.TYPE_STRING)
        combo = gtk.ComboBoxEntry(liststore)
        cell = gtk.CellRendererText()
        combo.pack_start(cell, False)
        combo.set_wrap_width(1)
        combo.set_tooltip_text(_("Select or enter playlist name"))

        combo.set_model(liststore)
        self.entry = combo.child
        self.entry.connect("activate", self.cb_save)

        sql = "SELECT option FROM settings WHERE section='playlists'"
        playlists = self.par.pyjama.settingsdb.query(sql)
        if playlists:
#        if self.par.pyjama.settings.section_exists("Playlists"):
#            playlists = self.par.pyjama.settings.config.options("Playlists")
            for name in playlists:
                liststore.append(name)

            if len(playlists)>0:
                combo.set_active(0)    

        self.vbox.pack_start(combo, False, True)

        # Buttons
        bSave = self.add_button(gtk.STOCK_SAVE, 1)
        self.add_button(gtk.STOCK_CANCEL, -1)
        self.show_all()

    def cb_save(self, widget):
        self.response(1)
