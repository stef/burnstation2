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

import os

import clArtistBrowser
from modules import functions

class main():
    def __init__(self, pyjama):
        self.__pyjama = pyjama
        self.__pyjama.Events.connect_event("alldone", self.ev_alldone)

    def ev_alldone(self):
        # Register Layout
        self.__pyjama.layouts.register_layout("artistbrowser", clArtistBrowser.ArtistBrowser(self.__pyjama))

        # Create menu entry:
        menu = self.__pyjama.window.menubar
        entry = menu.append_entry(menu.get_rootmenu("Browse"), _("Artists") + " (experimental)", "artistbrowser")
        entry.connect("activate", self.cb_show_alrtist_browser)
        menu.set_item_image(entry, os.path.join(functions.install_dir(), "images", "star.png"))
#        entry.set_sensitive(False)
        menu.show()

    def cb_show_alrtist_browser(self, widget):
        self.__pyjama.layouts.show_layout("artistbrowser", 10, 1, "0-9", who_called = "clArtistBrowser.__init__")
