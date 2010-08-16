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

import gtk, gobject
from threading import Thread
from time import sleep

class main():
    def __init__(self, pyjama):
        self.__pyjama = pyjama

        self.dialo = gtk.MessageDialog(self.__pyjama.window, 0, gtk.MESSAGE_INFO, 0, _("Jamendo is being queried"))

        self.dialog = gtk.Dialog()
        self.dialog.set_modal(True)
        self.dialog.set_title("Querying Jamendo")
        label = gtk.Label("If this query wan't cached, yet, it will be cached now.\nPlease notice that I cannot influence jamendo's response time")
        label.set_justify(gtk.JUSTIFY_CENTER)
        self.dialog.vbox.pack_start(label, False, True)
        label.show()


        self.__pyjama.Events.connect_event("jamendo-query", self.ev_jamendo_query)
#        self.__pyjama.Events.connect_event("alldone", self.ev_alldone)

#        self.running = False

#        self.statusbar = gtk.Statusbar()
#        self.statusbar.set_has_resize_grip(True)
#        self.statusbar.push(self.statusbar.get_context_id("Status"), _("Querying Jamendo"))

#        self.progressbar = gtk.ProgressBar()
#        self.progressbar.set_pulse_step(0.1)
#        self.progressbar.show()
#        self.statusbar.add(self.progressbar)


#    def ev_alldone(self):
#        self.__pyjama.window.vbox.pack_end(self.statusbar, False, True, 0)

    def ev_jamendo_query(self, status):
        if status == "start":
            self.dialog.show()
            self.dialog.present()
#            self.running = True
#            gobject.timeout_add(2, self.cb_pulse_bar)
#            thr = Thread(target = self.cb_pulse_bar, args = ())
#            thr.start()
#            self.statusbar.show()
            self.__pyjama.window.do_events()
            #~ self.__pyjama.x.start()
            #~ self.__pyjama.window.do_events()
        elif status == "end":
            self.dialog.hide()
            #~ self.__pyjama.x.stop()
            #~ self.__pyjama.window.do_events()
#            self.statusbar.hide()
#            self.running = False


#    def cb_pulse_bar(self):
#        i = 0
#        while self.running:
#            i += 1
#            self.progressbar.pulse()
#            self.__pyjama.window.do_events()
#            sleep (0.01)
##            print ("as")
#        #return self.running
#        print i

