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

import os
import gtk
import gtk.glade

import sys

from modules import functions

from threading import Thread


try:
    import webkit as webkit_browser
except:
    print "AN ERROR OCCURED:"
    print "-------------------------------------------------"
    print "Probably you need to install python-webkit"
    raise ImportError, 'webkit'      


FRAME_STRING = _("Integrated Webkit Browser")

def threaded(f):
    def wrapper(*args, **kwargs):
        t = Thread(target=f, args=args, kwargs=kwargs)
        t.start()
    return wrapper

class BrowserPage(webkit_browser.WebView):
    def __init__(self):
        webkit_browser.WebView.__init__(self)

class WebStatusBar(gtk.Statusbar):
    def __init__(self):
        gtk.Statusbar.__init__(self)
        self.iconbox = gtk.EventBox()
        self.iconbox.add(gtk.image_new_from_stock(gtk.STOCK_INFO,
                                                  gtk.ICON_SIZE_BUTTON))
        self.pack_start(self.iconbox, False, False, 6)
        self.iconbox.hide_all()
        self.set_has_resize_grip(False)

    def display(self, text, context=None):
        print "disp"
        cid = self.get_context_id("pywebkitgtk")
        if "123" in sys.argv:
            print "pop"
            self.pop(cid)
        self.push(cid, str(text))
        

#~ @threaded
class main():
    def __init__(self, pyjama):
        self.pyjama = pyjama 
        self.home = functions.preparedirs()

        self.pyjama.Events.connect_event("alldone", self.ev_alldone)

    def prepare_browser(self):
        # for older versions
        try:
            self.pyjama.preferences.register_plugin("Webkit-Plugin", self.create_preferences, self.save_preferences)
        except:
            pass

        self.browser = BrowserPage()

        self.pyjama.Events.connect_event("showing_artist_page", self.ev_artistpage)
        self.pyjama.Events.connect_event("showing_album_page", self.ev_albumpage)
#        self.browser = BrowserPage()

        self.browser.connect('load-started', self.cb_loading_start)
        self.browser.connect('load-finished', self.cb_loading_finished)
        self.browser.connect("title-changed", self.cb_title_changed)

        #~ self.browser.connect("populate-popup", self.cb_populate_popup)
        self.browser.connect('load-progress-changed', self.cb_loading_progress)
        self.browser.connect("hovering-over-link", self.cb_hover_link)
        self.browser.connect("status-bar-text-changed", self.cb_statusbar_text_changed)
#        self.browser.connect("console-message", self.cb_javascript_console_message)

        self.browser.show()

        toolbar = gtk.Toolbar()
        toolbar.set_icon_size(gtk.ICON_SIZE_SMALL_TOOLBAR)
        toolbar.set_style(gtk.TOOLBAR_BOTH_HORIZ)
        toolbar.show()

        ## Back-button
        self.back = gtk.ToolButton()
#        x.set_label("")
#        home.set_is_important(True)
        self.back.set_stock_id(gtk.STOCK_GO_BACK)
        self.back.set_tooltip_text("Show previous page")
        self.back.connect("clicked", self.cb_toolbutton_clicked, "back")
        toolbar.insert(self.back, -1)
        self.back.show()

        ## Home-button
        home = gtk.ToolButton()
#        x.set_label("")
#        home.set_is_important(True)
        home.set_stock_id(gtk.STOCK_HOME)
        home.set_tooltip_text("View Jamendo's start page")
        home.connect("clicked", self.cb_toolbutton_clicked, "home")
        toolbar.insert(home, -1)
        home.show()

        ## forward-button
        self.forward = gtk.ToolButton()
#        x.set_label("")
#        home.set_is_important(True)
        self.forward.set_stock_id(gtk.STOCK_GO_FORWARD)
        self.forward.set_tooltip_text("Show next page in history")
        self.forward.connect("clicked", self.cb_toolbutton_clicked, "fwd")
        toolbar.insert(self.forward, -1)
        self.forward.show()

        ## address bar
        self.addressbar = gtk.ToolItem()
        self.addressbar.entry = gtk.Entry()
        self.addressbar.entry.set_size_request(300, -1)
        self.addressbar.entry.connect("key-press-event", self.cb_entry_keypress)
        self.addressbar.add(self.addressbar.entry)
        self.addressbar.entry.show()
        self.addressbar.show()
        toolbar.insert(self.addressbar, -1)
        ## go-button
        self.go = gtk.ToolButton()
#        x.set_label("")
#        home.set_is_important(True)
        self.go.set_stock_id(gtk.STOCK_OK)
        self.go.set_tooltip_text("Navigate to this page")
        self.go.connect("clicked", self.cb_toolbutton_clicked, "go")
        toolbar.insert(self.go, -1)
        self.go.show()

        ## Space
        space_fs = gtk.ToolItem()
        space_fs.set_expand(True)
        toolbar.insert(space_fs, -1)
        space_fs.show()

        ## Hide-button
        x = gtk.ToolButton()
        x.set_label("Hide this browser")
        x.set_is_important(True)
        x.set_stock_id(gtk.STOCK_GO_DOWN)
        x.set_tooltip_text("Hide this browser again")
        x.connect("clicked", self.cb_toolbutton_clicked, "hide")
        toolbar.insert(x, -1)
        x.show()

        self.frame = gtk.Frame(FRAME_STRING)
        self.frame.show()

        self.sw = gtk.ScrolledWindow()
        self.sw.props.hscrollbar_policy = gtk.POLICY_AUTOMATIC
        self.sw.props.vscrollbar_policy = gtk.POLICY_AUTOMATIC
        self.sw.show()

        self.sw.add(self.browser)

        self.vbox = gtk.VBox(False)
        self.vbox.pack_start(toolbar, False, True)
        self.vbox.pack_start(self.sw, True, True)

        self.statusbar = WebStatusBar()
        self.statusbar.show()
        self.vbox.pack_start(self.statusbar, False, False)

        self.frame.add(self.vbox)


    def set_progress(self, progress):
        print "Setting progress"
        self.statusbar.display("Loading page: %i%% done" % progress)

    def cb_entry_keypress(self, widget, event):
        print "keypress"
        if event.hardware_keycode == 36:
            self.cb_toolbutton_clicked(None, "go")

#    def ev_new_window(self, Widget, retval, chromemask):
#        self.pyjama.Events.raise_event("error",  "Mozplug is not able to display this page,\n since this would require to open a new window.\n Mozplug does not support opening new windows.")
#        return 
#        b = self.new_browser()
##        b.set_chromemask(chromemask)
#        retval = b
#        return True

#    def new_browser(self):
#        import functions
#        curdir = os.path.abspath(os.path.curdir)
#        curdir = os.path.join(curdir, "plugins")
#        self.gladefile = os.path.join(functions.install_dir(), "plugins" , "mozplug", "mozplug.glade")
#        try:
#            self.wTree = gtk.glade.XML(self.gladefile)  
#        except RuntimeError:
#            print "Error loading glade file"
#            print "tried to load it from: ", self.gladefile
#        window = self.wTree.get_widget("window1")
#        fixed = self.wTree.get_widget("fixed1")

#        window.show_all()
#        browser = gtkmozembed.MozEmbed()
#        fixed.put(browser, 0,0)
#        return  browser


    def cb_toolbutton_clicked(self, widget, action=None):
        print "toolbutton clicked"
        if action == "hide":
            self.pyjama.window.vpaned.set_position(300)
            self.pyjama.window.vpaned2.set_position(1000)
        elif action == "back":
            self.browser.go_back()
        elif action == "fwd":
            self.browser.go_forward()
        elif action == "home":
            self.cururl = "http://www.jamendo.com"
            self.browser.open(self.cururl)
            self.settingurl = False 
        elif action == "go":
            url = self.addressbar.entry.get_text()
            self.cururl = url
            self.browser.open(self.cururl)
            self.settingurl = False

    def cb_hover_link(self, view, title, url):
        if view and url:
            self.statusbar.display(url)
        else:
            self.statusbar.display('')

    def cb_statusbar_text_changed(self, view, text):
        print "sb text changed"
        self.statusbar.display(text)

    def cb_loading_progress(self, view, progress):
        print "loading progress"
        self.set_progress(progress)

    def cb_populate_popup(self, view, mnu):
        print "populate popup"
        print view
        print mnu
        return True
    
    def cb_title_changed(self, widget, frame, title):
        print "title changed"
        self.frame.set_label("%s        -        %s" % (FRAME_STRING, title))

    def cb_loading_start(self, view, frame):
        print "loading start"
        main_frame = self.browser.get_main_frame()
        if frame is main_frame:
            self.frame.set_label("%s        -        %s" % (FRAME_STRING, frame.get_title()))

    def cb_loading_finished(self, view, frame):
        print "loading finished"
        main_frame = self.browser.get_main_frame()
        if frame is main_frame:
            self.frame.set_label("%s        -        %s" % (FRAME_STRING, frame.get_title()))

        self.back.set_sensitive(self.browser.can_go_back())
        self.forward.set_sensitive(self.browser.can_go_forward())


        url = frame.get_uri()
        if url:
            url = url.decode('utf-8').strip()
        else:
            url = ""

        self.addressbar.entry.set_text(url)


        if url[-8:] == self.cururl[-8:]: url = self.cururl
        if url != self.cururl:
#            print url
#            print self.cururl
            self.settingurl = True
            self.cururl = url
            arr = url.split("/")
            if len(arr) >= 2:
                if arr[-2] == "album":
                    id = arr[-1].replace("#", "")
                    print "Album: ", id
                    albumdetails = self.pyjama.jamendo.albuminfos(id)
                    self.pyjama.layouts.show_layout("album", albumdetails, who_called = "ev_location_changed-mozplug")
                elif arr[-2] == "artist":
                    id = arr[-1].replace("#", "")
                    for char in [".", "/", ".", "\\", ","]:
                        id = id.replace(char, " ")
                    sql = """
                        SELECT
                            artists.id
                        FROM
                            artists
                        WHERE
                            artists.name='%s'
                        """ % str(id)
                    ret = self.pyjama.db.query(sql)
                    if ret:
                        artistid = ret[0][0]
                    else:
                        return None
                    print "Artist:", artistid
                    artist = self.pyjama.db.artistinfos(artistid)
                    self.pyjama.layouts.show_layout("artist", artist, who_called = "ev_location_changed-mozplug")

#    def ev_link_message(self, Widget):
#        pass
##        print Widget.get_link_message()

#    def ev_progress(self,  mozWidget, cur, max):
#        print max, ": ", cur

    def ev_artistpage(self, artistinfos): 
        print "artistpage"
        url = artistinfos[0]['artist_url']
        self.goto_url( url, showup_browser=False )
        self.settingurl = False  


    def ev_albumpage(self, albuminfos):
        print "albumpage"
        settings = self.pyjama.settings
        url = settings.get_value("URLs", 'album_url').replace("URL", "%s" % albuminfos['id'])
        self.goto_url( url, showup_browser=False )
        self.settingurl = False  


    def ev_alldone(self):
        print "alldone"
        if len(self.pyjama.window.vpaned2.get_children()) > 1:
            self.pyjama.Events.raise_event("error", None, "Cannot run the Webkit-Browser-Plugin:\nAnother browser seems to be running. Please disable 'mozplug' in <i>Extras->Plugins</i>")
            return

        self.prepare_browser()

        self.cururl = "http://www.xn--ngel-5qa.de/pyjama/mozplug.html"
        self.browser.open(self.cururl)
        self.settingurl = False

        register =  self.pyjama.settings.get_value("WEBKIT", 'REGISTER_AS_BROWSER', -1)
        if register == -1:
            self.pyjama.settings.set_value("WEBKIT", "REGISTER_AS_BROWSER", "True")
            register = True
        if register == True:
            # register mozplug as pyjama's default browser!
            self.pyjama.browser.set_browser(self.goto_url_event)        

#        self.pyjama.window.vpaned2.pack2(self.mozillaWidget, True, True)
#        self.mozillaWidget.show()
        self.pyjama.window.vpaned2.pack2(self.frame, True, True)
        self.vbox.show()
        self.pyjama.window.vpaned2.set_position(100010)

        # add menu entry to pyjama
        menu = self.pyjama.window.menubar
        sep = menu.append_entry(menu.get_rootmenu("Browse"), "---", "---mozplug")
        entry = menu.append_entry(menu.get_rootmenu("Browse"), _("Integrated Browser"), "mozplug")
        menu.set_item_image(entry,gtk.STOCK_NETWORK)
        entry.connect("activate", self.cb_entry_activate)
        self.__accel_group = gtk.AccelGroup()
        entry.add_accelerator("activate", self.__accel_group, gtk.keysyms.F4, 0, gtk.ACCEL_VISIBLE)
        self.pyjama.window.add_accel_group(self.__accel_group)

    def cb_entry_activate(self, widget):
        print "entry activate"
        self.pyjama.window.vpaned.set_position(0)
        self.pyjama.window.vpaned2.set_position(0)

    def goto_url_event(self, url, showup_browser=True):
        print "goto"
        if showup_browser:
            self.pyjama.window.vpaned.set_position(150)
            self.pyjama.window.vpaned2.set_position(0)

        self.cururl = url
        self.browser.open(url)

    def goto_url(self, url, showup_browser=True):
        print "goto_url"
        self.browser.stop_loading()
        if showup_browser:
            self.pyjama.window.vpaned.set_position(150)
            self.pyjama.window.vpaned2.set_position(0)
        if not self.settingurl:
            self.cururl = url
            self.browser.open(self.cururl)
        else:
            self.settingurl = True

#    def goto_url2(self, url):
#        if not self.settingurl:
#            self.cururl = url
#            self.browser.open(url)
#        else:
#            self.settingurl = True

    def create_preferences(self):
        settingbrowser = self.pyjama.settings.get_value("WEBKIT", 'REGISTER_AS_BROWSER', True)

        vbox = gtk.VBox(spacing=10)
        hbox = gtk.HBox(spacing=10)
        vbox.pack_start(hbox, False, True, 10)

        self.check = gtk.CheckButton(_("Let Webkit-Plugin open Jamendo pages"))
        self.check.set_active(settingbrowser)
        hbox.pack_start(self.check, False, True, 10)

        vbox.show_all()
        return vbox
        
    def save_preferences(self):
        self.pyjama.settings.set_value("WEBKIT", 'REGISTER_AS_BROWSER', self.check.get_active())
        if self.check.get_active():
            # register mozplug as pyjama's default browser!
            if "webkit-plugin" in self.pyjama.plugins.loaded:
                self.pyjama.browser.set_browser(self.pyjama.plugins.loaded['webkit-plugin'].goto_url) 
        else:
            self.pyjama.browser.set_default_browser()
