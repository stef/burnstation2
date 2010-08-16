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

# An example for this script was taken from:
# John Dong <jdong@ubuntu.com>
#
# He states:
# "Feel free to use/tweak/modify to your free will."
# 

import gtk
import gobject
try:
    import pynotify
    NOTIFICATIONS = True
except ImportError:
    print "Module 'pynotify' not found"
    print "Not using notifications"
    NOTIFICATIONS = False

import os
import functions

class TrayMenu(gtk.Menu):
    def __init__(self, parent):
        self.main = parent
        gtk.Menu.__init__(self)

        self.play_button_status = "play"
        self.draw_menu_items()

    def draw_menu_items(self, play=None):
        self.mnuShow = gtk.ImageMenuItem(_("Show Pyjama"))
        w, h = gtk.icon_size_lookup(gtk.ICON_SIZE_MENU)
        image = "hspbp-burnstation.png"
        img = gtk.Image()
        if not os.path.exists(image):
            image = os.path.join(functions.install_dir(), "images", image)
            if not os.path.exists(image):
                print ("Image not found")
            else:
                pix = gtk.gdk.pixbuf_new_from_file_at_size(image, w, h)
                img.set_from_pixbuf(pix)
                self.mnuShow.set_image(img)
        self.mnuShow.connect('activate', self.main.window.show_window)


        self.mnuPlay = gtk.ImageMenuItem(gtk.STOCK_MEDIA_PLAY)
        self.mnuPlay.connect('activate', self.main.window.on_bPlay_clicked)


        self.mnuNext = gtk.ImageMenuItem(gtk.STOCK_MEDIA_NEXT)
        self.mnuNext.connect('activate', self.main.window.on_bNext_clicked)

        self.mnuPrev = gtk.ImageMenuItem(gtk.STOCK_MEDIA_PREVIOUS)
        self.mnuPrev.connect('activate', self.main.window.on_bPrev_clicked)

        self.mnuQuit = gtk.ImageMenuItem(gtk.STOCK_QUIT)
        self.mnuQuit.connect('activate', self.main.window.really_quit)


        self.append(self.mnuShow)
        self.append(self.mnuPlay)
        self.append(self.mnuNext)
        self.append(self.mnuPrev)
        self.append(self.mnuQuit)
        
    def switch_play_button(self, play):
        self.play_button_status = play
        self.mnuPlay.destroy()
        if play=="play":
            self.mnuPlay = gtk.ImageMenuItem(gtk.STOCK_MEDIA_PLAY)
            self.mnuPlay.connect('activate', self.main.window.on_bPlay_clicked)
        else:
            self.mnuPlay = gtk.ImageMenuItem(gtk.STOCK_MEDIA_PAUSE)
            self.mnuPlay.connect('activate', self.main.window.on_bPlay_clicked)

        self.insert(self.mnuPlay, 1)


class TrayIcon():
    def __init__(self, parent, title = "Pyjama", text = "Python Jamendo Audiocenter"):
        self.parent = parent
        self.menu = TrayMenu(parent)
        if NOTIFICATIONS:
            pynotify.init("pynotify")
        self.notify = None
#        self.icon=gtk.status_icon_new_from_icon_name("warning")
        self.icon = gtk.status_icon_new_from_file(os.path.join(functions.install_dir(), "images", "pyjama.png"))
        self.icon.set_visible(False)
#        self.icon.connect('activate', self.parent.switch_window_state)
        self.icon.connect('activate', self.parent.window.show_window)
        self.icon.connect('popup-menu', self.cb_popup_menu, self.menu)
        self.icon.connect('scroll-event', self.cb_scroll)
        self.icon.set_tooltip("%s\n%s" % (title, text))
        self.icon.set_visible(True)
        

    def cb_popup_menu(self, widget, button, time, event):
        event.show_all()
        event.popup(None, None, None, 3, time)

    def cb_scroll(self, widget, event):
        new_volume = self.parent.window.hsVolume.get_value()
        if event.direction == gtk.gdk.SCROLL_UP:
            new_volume += 5
        elif event.direction == gtk.gdk.SCROLL_DOWN:
            new_volume -= 5
        self.parent.window.hsVolume.set_value(new_volume)

    def show_notification(self, caption, text, img = "pyjama", size = None):
        if not NOTIFICATIONS: return
        if size == None: size = self.parent.settings.get_value("PYJAMA", "notification_cover_size")
        pixbuf = None
        if img != "pyjama":
            pixbuf = gtk.gdk.pixbuf_new_from_file_at_size(img, size, size)
            if not self.notify:
                self.notify = pynotify.Notification(caption, text)
            else:
                self.notify.update(caption, text)
            self.notify.set_icon_from_pixbuf(pixbuf)
        else:
            if not self.notify:
                self.notify = pynotify.Notification(caption, text, img)
            else:
                self.notify.update(caption, text, img)
        self.notify.set_urgency(pynotify.URGENCY_NORMAL)
        self.notify.attach_to_status_icon(self.icon)
        self.notify.set_timeout(self.parent.settings.get_value("PYJAMA", "NOTIFICATION_DELAY"))
        self.notify.show()
