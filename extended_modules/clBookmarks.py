#!/usr/bin/env python
# -*- coding: utf-8 -*-

# ----------------------------------------------------------------------------
# pyjama - python jamendo audioplayer
# Copyright (c) 2009 Daniel Nögel
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, at version 3 of the License.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
# ----------------------------------------------------------------------------

import gtk
import pickle
import base64

import hashlib
import os

from modules import functions
from modules import clEntry

import clBookmarkDialog

def serialize(object):
    ret = pickle.dumps(object, 0)
    return base64.b64encode(ret)

def unserialize(string):
    ret = base64.b64decode(string)
    return pickle.loads(ret)
    

class main():
    def __init__(self, pyjama):
        self.bookmarks = []
        self.pyjama = pyjama
        self.bookmarks_dir = os.path.join(self.pyjama.home, "bookmarks")

        # bookmark name reserved for the home page
        self.home_bookmark_name = "__!!home!!__"

        # create bookmarks directory in ~/.pyjama
        home = self.pyjama.home
        if os.path.exists(os.path.join(home,  "bookmarks")) == False:
            try:
                os.makedirs(os.path.join(home, "bookmarks"))
                print "Created %s" % os.path.join(home, "bookmarks")
            except:
                self.pyjama.Events.raise_event("error", _("Could not create folder '%s' - most probably\npyjama does not have the right privilegs to create that folder" % os.path.join(home, "bookmarks")))
                return

        # hide from configtool
        bl = self.pyjama.settings.get_value("CONFIGTOOL", "blacklist", "PATHs URLs")
        if not "Bookmarks" in bl:
            bl += " Bookmarks"
            self.pyjama.settings.set_value("CONFIGTOOL", "blacklist", bl)

        self.pyjama.Events.connect_event("alldone", self.ev_alldone)

#        gladefile = os.path.join(functions.install_dir(), "plugins" , "bookmarks", "bookmarks.glade")
#        try:
#            self.wTree = gtk.glade.XML(gladefile)  
#            self.dialog = self.wTree.get_widget("dialog1")
#            self.ok = self.wTree.get_widget("button1")
#            self.ok.connect("clicked", self.ev_ok_clicked)
#        except Exception, inst:
#            self.pyjama.Events.raise_event("error", inst, "Error loading glade file %s" % gladefile)
#            self.dialog = None

    ######################################################################
    #                                                                    #
    #                           Functions                                #
    #                                                                    #
    ######################################################################

    def edit_bookmarks(self, widget):
#        self.pyjama.Events.raise_event("error", "Editing Bookmarks wasn't implemented, yet")
#        return
        # load dialog
        dialog = clBookmarkDialog.Dialog(self, self.bookmarks)
        response = dialog.run()
        if response == 1:
            bookmarks =  dialog.bookmarks
            deleted = dialog.deleted
            menu = self.pyjama.window.menubar
            self.bookmarks = []
            for bookmark in deleted:
                name = bookmark['name']
                content = bookmark['hash']

                # delete all entries
                mnu = menu.get_submenu(base64.b64encode(name))
                mnu.destroy()
                
                sql = "DELETE FROM settings WHERE section='bookmarks' and option = '%s'" % name
                playlists = self.pyjama.settingsdb.query(sql)            
            for bookmark in bookmarks:
                name = bookmark['name']
                content = bookmark['hash']

                # delete all entries
                mnu = menu.get_submenu(base64.b64encode(name))
                mnu.destroy()
                
                sql = "DELETE FROM settings WHERE section='bookmarks' and option = '%s'" % name
                playlists = self.pyjama.settingsdb.query(sql)
                
            for bookmark in bookmarks:
                name = bookmark['name']
                content = bookmark['hash']


                # Append to bookmarks and write to settingsdb
                self.pyjama.settingsdb.set_value("bookmarks", name, content)

                # Append menu entry
                menu = self.pyjama.window.menubar
                entry = menu.append_entry(menu.get_rootmenu("Bookmarks"), name, base64.b64encode(name))
                entry.connect("activate", self.ev_load_bookmark, name)

                self.bookmarks.append({'name':name, 'hash':content})
            #~ for del_bookmark in deleted:
                #~ self.pyjama.settings.remove_option("Bookmarks", del_bookmark)
        dialog.destroy()


    def add_bookmark(self, widget, name=None):

        data = self.pyjama.historyCurrent
        content = serialize(data)

        if name is None:
            # ask for name
            result = clEntry.input_box(title=_('Bookmark'),
                message=_('Please enter a Name for this bookmark'),
                default_text=_("Bookmark"))
            if result is None:
                return
            name = str(result)
        else:
            name = self.home_bookmark_name
        
        # Save bookmark
        self.pyjama.settingsdb.set_value("bookmarks", name, content)

        if name is not None:
            # Append menu entry
            menu = self.pyjama.window.menubar
            entry = menu.append_entry(menu.get_rootmenu("Bookmarks"), name, base64.b64encode(name))
            entry.connect("activate", self.ev_load_bookmark, name)
            entry.show()
            self.bookmarks.append({'name':name, 'hash':content})

    def read_bookmark_folder(self):
        if self.pyjama.settings.config.has_section("Bookmarks"):
            for md5_hash, name in self.pyjama.settings.config.items("Bookmarks"):
                if name != self.home_bookmark_name and md5_hash != self.home_bookmark_name:
                    #~ # Append menu entry
                    #~ menu = self.pyjama.window.menubar
                    #~ entry = menu.append_entry(menu.get_rootmenu("Bookmarks"), name, md5_hash)
                    #~ entry.connect("activate", self.ev_load_bookmark, md5_hash)
                    
                    self.pyjama.settingsdb.set_value("bookmarks", name, self.bookmarkfromhash(md5_hash))
                    print ("Moved bookmark '%s' from config-file to database" % name)
                    self.pyjama.settings.remove_option("Bookmarks", md5_hash)
                else:
                    self.pyjama.settingsdb.set_value("bookmarks", self.home_bookmark_name, self.bookmarkfromhash(self.home_bookmark_name))
                    print ("Moved startpage from config-file to database")
                    self.pyjama.settings.remove_option("Bookmarks", md5_hash)

        sql = "SELECT option, value FROM settings WHERE section='bookmarks'"
        bookmarks = self.pyjama.settingsdb.query(sql)
        if  bookmarks:
            for name, value in bookmarks:
                if name != self.home_bookmark_name:
                    # Append menu entry
                    menu = self.pyjama.window.menubar
                    entry = menu.append_entry(menu.get_rootmenu("Bookmarks"), name, base64.b64encode(name))
                    entry.connect("activate", self.ev_load_bookmark, name)
                    self.bookmarks.append({'name':name, 'hash':value})
                else:
                    self.pyjama.set_home_fkt(self.home)
        
    def bookmarkfromhash(self, hash):
        try: 
            fh = open(os.path.join(self.bookmarks_dir, hash), "r")
        except:
            self.pyjama.Events.raise_event("error", _("Could not read bookmark file"))
            return
        content = fh.read()
        fh.close()
        
        content = pickle.loads(content)
        return serialize(content)

    ######################################################################
    #                                                                    #
    #                                Events                              #
    #                                                                    #
    ######################################################################

    def ev_ok_clicked(self, widget):
        self.dialog.destroy()

    def ev_alldone(self):
        # Create Bookmarks menu
        menu = self.pyjama.window.menubar
        bookmarks = menu.insert_root_before("Extras", _("Bookmarks"), "Bookmarks")

        translation_array = [_("Add Bookmark"), _("Edit Bookmarks"), _("Set this page as homepage")]

        sub = ["Add Bookmark", "Edit Bookmarks", "Set this page as homepage", "---"]  
        self.bookmark_menu = menu.create_submenu(rootmenu=bookmarks, submenu=sub)

        add_bookmark = menu.get_submenu("Add Bookmark")
        menu.set_item_image(add_bookmark, gtk.STOCK_ADD )
        add_bookmark.connect("activate", self.add_bookmark)

        edit_bookmarks = menu.get_submenu("Edit Bookmarks")
        menu.set_item_image(edit_bookmarks, gtk.STOCK_EDIT )
        edit_bookmarks.connect("activate", self.edit_bookmarks)

        set_homepage = menu.get_submenu("Set this page as homepage")
        menu.set_item_image(set_homepage, gtk.STOCK_HOME )
        set_homepage.connect("activate", self.cb_set_homepage)

        # Create accel group
        self.accel_group = gtk.AccelGroup()
        add_bookmark.add_accelerator("activate", self.accel_group, ord("d"), gtk.gdk.CONTROL_MASK, gtk.ACCEL_VISIBLE)
        self.pyjama.window.add_accel_group(self.accel_group)

        self.read_bookmark_folder()

    def ev_load_bookmark(self, widget, name):
        #~ # Read file
        #~ try: 
            #~ fh = open(os.path.join(self.bookmarks_dir, md5_hash), "r")
        #~ except:
            #~ self.pyjama.Events.raise_event("error", _("Could not read bookmark file"))
            #~ return
        #~ content = fh.read()
        #~ fh.close()

        # unserialise and show
        #~ data = pickle.loads(content)
        bookmark = self.pyjama.settingsdb.get_value("bookmarks", name)
        if bookmark:
            data = unserialize(bookmark)
            self.pyjama.layouts.show_layout(data['layout'], data['data1'], data['data2'], data['data3'], data['data4'], who_called="ev_load_bookmark")

    def cb_set_homepage(self, widget):
        self.pyjama.set_home_fkt(self.home)
        self.add_bookmark(None, self.home_bookmark_name)

    def home(self):
        self.ev_load_bookmark(None, self.home_bookmark_name)
