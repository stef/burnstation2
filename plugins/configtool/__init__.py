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

from modules import functions
from modules import clWidgets

import os,sys
import gtk, gtk.glade, gobject
import pango

# See Tooltip class for further explanaition
every_widget_gets_own_tooltip_instance = True

descs = {
    'URLs':{
        'VERSION_URL':'', 
        'ALBUM_URL':''
    },
    'PATHs':{
        'INSTALL_DIR_POSIX':'',
        'INSTALL_DIR':''
    },
    'JAMENDO':{
        'CACHING_TIME_SHORT':'How long should cached queries be stored, which might change?\n<b>Value given in seconds</b>',
        'CACHING_TIME_LONG':'How long should cached queries be stored, which won\'t change?\n<b>Value given in seconds</b>',
        'FORMAT':'When downloading torrents: MP3 or OGG?\nOGG has higher quality and is bigger in size. As most people like MP3, OGG Torrents might be not available.\n<b>Possible values are mp32 or ogg3</b>',
        'FORMAT_STREAM':'MP3 provides lower quality but seeking, OGG has better quality but does not support streaming (on jamendo)\n<b>Values could be mp31 or ogg2</b>',
        'TAGS':'List of tags you can search for\n<b>Fill in whatever you want. Will take effect after restarting pyjama</b>'
    },
    'PMC':{
        'RELEASE':'Which PMC news did you receive last?\n<b>Internal</b>'
    },
    'MOZPLUG':{
        'REGISTER_AS_BROWSER':'Should Mozplug open external URLs like album pages and donation-links?\n<b>In most cases this option can be checked</b>'
    },
    'CONFIGTOOL':{
        'BLACKLIST':'Wich sections should not be shown?\n<b>Space seperated</b>'
    },
    'PYJAMA':{
        'FIRST_RUN':'Was Pyjama started before?\n<b>False should be a good value ;)</b>',
        'STANDARD_THEME':'Which theme should be loaded as default?\nSet this fielt to \'None\' if you don\'t want pyjama to be themed.\n<b>Changig the theme will restart Pyjama as soon you apply this!</b>\n\nFollowing directories will be searched for themes:\n* /home/USERNAME/.pyjama/plugins\n* /usr/share/themes\n* PYJAMA_INSTALL_DIR/plugins',
        'SHOW_WINDOW_IN_TASKBAR':'Should Pyjama\'s main window be shown in taskbar?',
        'SHOW_TOOLBAR_TEXT':'Check if you want to show icons and text in toolbar\n<b>Default is unchecked</b>',
        'NOTIFICATION_DELAY':'How long should notifications be shown?\n<b>Value in ms</b>',
        'NOTIFICATION_COVER_SIZE':'How big should the covers in notifications be?\n<b>75-600</b>'
    },
    'PERFORMANCE':{
        'MAX_THREADS':'How many threads may run at once?\n<b>Best value depends on your connection\'s latency and bandwidth</b>',
        'THREAD_WAIT':'How long should Pyjama wait for pending threads?\n<b>1 (second) is a good value</b>',
        'HISTORY_SIZE':'How many entries should be stored in history\n<b>Too much values will result in higher memory usage.</b>',
        'DB_SEARCH_LIMIT':'How many results should be fetched on searches?\n<b>High values result in long searches</b>',
        'TIMER_INTERVAL':'Internal Timer\n<b>Do not change</b>'
    },
    'SOUND':{
        'DEFAULT_VOL':'Which volume do you want pyjama to start with?\n<b>Valid Values from 0 to VOL_MAX</b>',
        'VOL_MAX':'Maximum volume one can set.\n<b>0-1000. Everythin above 100 means digital amplification</b>'
    },
    'PLUGINS':{
        'BLACKLIST':'Which plugins should <b>not</b> be loaded?\n<b>Space seperated</b>'
    }
}

class theme_selection(gtk.ComboBox):
    def __init__(self, value):
        liststore = gtk.ListStore(gobject.TYPE_STRING)
        gtk.ComboBox.__init__(self, liststore)
        cell = gtk.CellRendererText()

        self.pack_start(cell, True)
        self.add_attribute(cell, 'text', 0)

        self.insert_text(0, "None")
        self.insert_text(1, value)
        self.set_active(1)

        counter = 1
        themes = functions.sorteddirlist()
        for theme in themes:
            counter += 1
            self.insert_text(counter, theme)
        self.show()


class NotebookTab(gtk.Frame):
    def __init__(self):
        gtk.Frame.__init__(self)
        
#        self.label = gtk.Label("Test")
        self.set_label(None)

        self.scrolledwindow = gtk.ScrolledWindow()
        self.scrolledwindow.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
        self.layout = gtk.Layout()

        self.add(self.scrolledwindow)
        self.scrolledwindow.add(self.layout)

        self.show_all()

        self.bool_items = {}
        self.int_items = {}
        self.string_items = {}

    def add_bool(self, name, value, pos, desc):
        x, y = pos
        self.add_label(name, y)
        self.bool_items[name] = gtk.CheckButton()

        widget = self.bool_items[name]
        widget.set_active(value)
        self.layout.put(widget, x, y)
        widget.show()

        # this failes for me on some xfce desktops somehow
        try:
            widget.set_has_tooltip(True)
            widget.connect('query-tooltip', self.query_tooltip, desc)
        except:
            pass

    def add_int(self, name, value, pos, desc):
        x, y = pos
        self.add_label(name, y)
        self.int_items[name] = gtk.SpinButton()

        widget = self.int_items[name]
        widget.connect("change-value", self.ev_spinbutton_change)
        widget.set_increments(1, 10)
        widget.set_range(0, 999999999)
        widget.set_value(value)
        self.layout.put(widget, x, y)
        widget.show()

        # this failes for me on some xfce desktops somehow
        try:
            widget.set_has_tooltip(True)
            widget.connect('query-tooltip', self.query_tooltip, desc)
        except:
            pass



    def add_string(self, name, value, pos, desc):
        x, y = pos
        self.add_label(name, y)

        if name == "standard_theme":
            self.string_items[name] = theme_selection(value)  
        else:
            self.string_items[name] = gtk.Entry()

        widget = self.string_items[name]

        if name != "standard_theme":
            widget.set_text(value)
            self.layout.put(widget, x, y)
        else:
            evb = gtk.EventBox()
            evb.set_visible_window(True)
            evb.set_above_child(False)
            evb.add_events(gtk.gdk.MOTION_NOTIFY)
            evb.add(widget)
            evb.show()
            self.layout.put(evb, x, y)

            widget = evb
        widget.show()

        # this failes for me on some xfce desktops somehow
        try:
            widget.set_has_tooltip(True)
            widget.connect('query-tooltip', self.query_tooltip, desc)
        except:
            pass

    def add_label(self, name, y):
        label = gtk.Label(name)
        y = y+5
        self.layout.put(label, 10, y)
        label.set_tooltip_text(name)
        label.show()

    def ev_spinbutton_change(self, spinbutton, scrolltype):
        spinbutton.update()

    def query_tooltip(self, widget, x, y, keyboard_tip, tooltip, desc):
        tooltip.set_markup(desc)
        return True

class main():
    def __init__(self, pyjama):
        self.pyjama = pyjama
        self.home = functions.preparedirs()
        self.install_dir = functions.install_dir()

        ev = self.pyjama.Events
        ev.connect_event("alldone", self.ev_alldone)

        gladefile = os.path.join(self.install_dir, "plugins" , "configtool", "configtool.glade")
        try:
            self.wTree = gtk.glade.XML(gladefile)  
        except RuntimeError:
            print "Error loading glade file"
            print "tried to load it from: ", gladefile

        self.tview = self.wTree.get_widget("textview2")
        buf = gtk.TextBuffer()
        buf.set_text(_("Configtool is a simple dynamic config editor for Pyjama. Please take care when editing your config file. If you should have made a mistake and Pyjama does not run properly any more, just delete the file \"~/.pyjama/pyjama.cfg\"\n Please notice, that some values will only take effect after restarting Pyjama."))
        self.tview.set_buffer(buf)

        self.dialog = self.wTree.get_widget("dialog1")
        self.dialog.connect('delete_event', self.quit)
        self.dialog.set_icon_from_file(os.path.join(functions.install_dir(), "images", "pyjama.png"))

        self.notebook = self.wTree.get_widget("notebook1")
        self.bCancel = self.wTree.get_widget("bCancel")
        self.bOK = self.wTree.get_widget("bOK")

        self.bCancel.connect("clicked", self.ev_bCancel)
        self.bOK.connect("clicked", self.ev_bOK)

#        self.notebook.remove_page(0)

        self.tabs = {}

        self.blacklist =  self.pyjama.settings.get_value("CONFIGTOOL", "blacklist", -1)
        if self.blacklist == -1:
            self.pyjama.settings.set_value("CONFIGTOOL", "blacklist", "PATHs URLs")
            self.blacklist = "PATHs URLs"

#        self.read_settings()


    def quit(self, ev1, ev2):
        self.dialog.hide()
        return True

    def read_settings(self):
            sections = self.pyjama.settings.config.sections()
            for section in sections:
                if not section in self.blacklist:
                    self.add_tab(section)
                    try:
                        items = self.pyjama.settings.config.items(section)
                    except Exception, inst:
                        self.pyjama.Events.raise_event("error", inst, "There was an error reading the config file\nif this error appears each time you run pyjama\nplease report this Bug via PMC")
                        items = []
                    x = 150
                    y = 10
                    for item, value in items:
                        coords = (x,y)
                        pos = value.find("#")
                        pos = value.find(";")
                        if pos > -1:
                            value = value[0:pos]
                        if section in descs:
                            if item.upper() in descs[section]:
                                desc =  descs[section][item.upper()]
                            else:
                                desc = None
                        else:
                            desc = None
                        if value.isdigit():
                            value = int(value)
                            self.tabs[section].add_int(item, value, coords, desc)
                        elif (self.pyjama.settings.isbool(value)):
                            value = self.pyjama.settings.parsebool(value)
                            self.tabs[section].add_bool(item, value, coords, desc)
                        else:
                            self.tabs[section].add_string(item, value, coords, desc)
                        y += 40
                        self.tabs[section].layout.set_size(200,y)

    def ev_bCancel(self, ev):
        self.dialog.hide()

    def ev_bOK(self, ev):
        theme = self.pyjama.settings.get_value("PYJAMA", "standard_theme")
        for section in self.tabs:
            tab = self.tabs[section]
            for option in tab.string_items:
                widget = tab.string_items[option]
                if  option == "standard_theme":
                    newtheme = self.pyjama.window.get_active_text(widget)
                    self.pyjama.settings.config.set( section, option, str(newtheme) )
                else:
                    self.pyjama.settings.config.set( section, option, str(widget.get_text()) )
            for option in tab.bool_items:
                widget = tab.bool_items[option]
                if option == "show_toolbar_text":
                    x = widget.get_active()
                    if x:
                        self.pyjama.window.toolbar.set_style(gtk.TOOLBAR_BOTH)
                    else:
                        self.pyjama.window.toolbar.set_style(gtk.TOOLBAR_ICONS)
                self.pyjama.settings.config.set( section, option, str(widget.get_active()) )
            for option in tab.int_items:
                widget = tab.int_items[option]
                self.pyjama.settings.config.set( section, option, str(widget.get_value_as_int()) )

        self.dialog.hide()


        fh = open(os.path.join(self.home, "pyjama.cfg"),"w")
        if fh:
            self.pyjama.settings.config.write(fh)    
        else:
            print "Error writing configuration to %s" % os.path.join(self.home, "pyjama.cfg")
        fh.close()
        
        if theme != newtheme: 
            dirname = os.path.dirname(sys.argv[0])
            abspath =  os.path.abspath(dirname)
            run = os.path.join(abspath, sys.argv[0])
            self.pyjama.window.really_quit()
            os.system("%s -t %s &" % (run, newtheme))

#        opt = self.pyjama.window.options
#        self.pyjama.icon.icon.set_visible(False)
#        self.pyjama.player.stop()
#        self.pyjama.window.destroy()
#        functions.showtheme(self.pyjama.settings.get_value("PYJAMA", "standard_theme"))
#        import clWindow
#        clWindow.winGTK(opt)



    def add_tab(self, caption):
        #!!
        self.tabs[caption] = NotebookTab()
        label = gtk.Label(caption.capitalize())
        self.notebook.append_page(self.tabs[caption], label)

    def ev_alldone(self):
        # Add Button to toolbar
        toolbar = self.pyjama.window.toolbar
        self.bConfigTool = gtk.ToolButton("Configtool")
        self.bConfigTool.set_stock_id(gtk.STOCK_PREFERENCES)
        self.bConfigTool.set_tooltip_text(_("Show Configtool"))
        self.bConfigTool.connect("clicked", self.on_bConfigTool_clicked)
        try:
            pos = toolbar.get_item_index(toolbar.space_fs)
        except:
            pos = -2
        toolbar.insert(self.bConfigTool, pos+1)
        self.bConfigTool.show()

        # add menu entry
        menu = self.pyjama.window.menubar
        root = menu.get_rootmenu("Extras")
        if root:
            menu.append_entry(root, "---", "configtoolseperator")
            mnu = menu.append_entry(root, "Configtool", "configtool")
            menu.set_item_image(mnu, gtk.STOCK_PREFERENCES)
            mnu.connect("activate", self.on_bConfigTool_clicked)

    def on_bConfigTool_clicked(self, ev):
        for tab in xrange(len(self.tabs)+1):
            self.notebook.remove_page(1)
        self.tabs = {}
        self.dialog.show_all()
        self.read_settings()
        return

