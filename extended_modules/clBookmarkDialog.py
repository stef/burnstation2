#!/usr/bin/env python
'''Tree View/editable Cells

This demo demonstrates the use of editable cells in a Gtkself.treeview..
If you're new to the Gtkself.treeview. widgets and associates, look into the
GtkListStore example first.'''
# pygtk version: Maik Hertha <maik.hertha@berlin.de>

import gobject
import gtk

#   columns
(
  COLUMN_NAME,
  COLUMN_HASH,
  COLUMN_EDITABLE
) = range(3)


class Dialog(gtk.Dialog):
    def __init__(self, parent=None, bookmarks=[]):
        gtk.Dialog.__init__(self)

        self.bookmarks = bookmarks
        self.deleted = []

        self.set_modal(True)
        self.set_title(_("Bookmarks"))
        self.set_border_width(5)
        self.set_default_size(320, 400)


        label = gtk.Label(_("Here you can edit your Bookmarks. Doubleclick on a field to change its name.\nSelect a field by singleclicking it and delete it with clicking 'remove'"))
        label.set_line_wrap(True)
        label.set_single_line_mode(False)
        self.vbox.pack_start(label, expand=False, fill=True)

        sw = gtk.ScrolledWindow()
        sw.set_shadow_type(gtk.SHADOW_ETCHED_IN)
        sw.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
        self.vbox.pack_start(sw)

        # create model
        model = self.__create_model()

        # create tree view
        self.treeview = gtk.TreeView(model)
        self.treeview.set_rules_hint(True)
        self.treeview.get_selection().set_mode(gtk.SELECTION_SINGLE)

        self.__add_columns(self.treeview)

        sw.add(self.treeview)

        # some buttons
        hbox = gtk.HBox(True, 4)
        self.vbox.pack_start(hbox, False, False)

#        button = gtk.Button(stock=gtk.STOCK_ADD)
#        button.connect("clicked", self.on_add_item_clicked, model)
#        hbox.pack_start(button)

        button = gtk.Button(stock=gtk.STOCK_REMOVE)
        button.connect("clicked", self.on_remove_item_clicked, self.treeview)
        hbox.pack_start(button)

        self.add_button(gtk.STOCK_CANCEL, -1)
        self.add_button(gtk.STOCK_OK, 1)

        self.populate_list(self.bookmarks)

        self.show_all()

    def __create_model(self):

        # create list store
        model = gtk.ListStore(
            gobject.TYPE_STRING,
            gobject.TYPE_STRING,
            gobject.TYPE_BOOLEAN
       )
        return model

#        # add items
#        for item in bookmarks:
#            iter = model.append()

#            model.set (iter,
#                  COLUMN_NAME, item[COLUMN_NAME],
#                  COLUMN_HASH, item[COLUMN_HASH],
#                  COLUMN_EDITABLE, True
#           )
#        return model


    def __add_columns(self, treeview):

        model = treeview.get_model()

#        # number column
#        renderer = gtk.CellRendererText()
#        renderer.connect("edited", self.on_cell_edited, model)
#        renderer.set_data("column", COLUMN_NUMBER)

#        column = gtk.self.treeview.Column("Number", renderer, text=COLUMN_NUMBER,
#                               HASH=COLUMN_HASH)
#        self.treeview..append_column(column)

        # NAME column
        renderer = gtk.CellRendererText()
        renderer.connect("edited", self.on_cell_edited, model)
        renderer.set_data("column", COLUMN_NAME)

        column = gtk.TreeViewColumn(_("Your Bookmarks"), renderer, text=COLUMN_NAME, editable=COLUMN_EDITABLE)
        treeview.append_column(column)

    def populate_list(self, bookmark_list):
        model = self.treeview.get_model()
        for item in bookmark_list:
            new_item = [item['name'], item['hash']]
            #bookmarks.append(new_item)

            iter = model.append()
            model.set (iter,
                COLUMN_NAME, new_item[COLUMN_NAME],
                COLUMN_HASH, new_item[COLUMN_HASH],
                COLUMN_EDITABLE, True
           )

#    def on_add_item_clicked(self, button, model):
#        new_item = ["Description here", True]
#        bookmarks.append(new_item)

#        iter = model.append()
#        model.set (iter,
#            COLUMN_NAME, new_item[COLUMN_NAME],
#            COLUMN_HASH, new_item[COLUMN_HASH]
#       )


    def on_remove_item_clicked(self, button, treeview):

        selection = treeview.get_selection()
        model, iter = selection.get_selected()

        if iter:
            path = model.get_path(iter)[0]
            model.remove(iter)

#            del self.bookmarks[ path ]
            self.deleted.append({"name":self.bookmarks[path]['name'], "hash":self.bookmarks[path]['hash']})
            del self.bookmarks[path]


    def on_cell_edited(self, cell, path_string, new_text, model):

        iter = model.get_iter_from_string(path_string)
        path = model.get_path(iter)[0]
        column = cell.get_data("column")

        if column == COLUMN_NAME:
            old_text = model.get_value(iter, column)
            self.bookmarks[path]['name'] = new_text

            model.set(iter, column, self.bookmarks[path]['name'])



