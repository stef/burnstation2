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

## @package clBrowserInterface
# Manages pyjama's browser interface

#
# You are probably looking for the integrated webbrowser or PMC
# have a look at mozplug-plugin in the first case or pmc in
# the second one!
# This file only manages urls and opens them in your default
# browser or mozplug
#

import webbrowser

## Browser Interface class
class Browser():
    ## Constructor
    # @param self Object Pointer
    # @param pyjama Pyjama Reference
    def __init__(self, pyjama):
        ## Pyjama Reference
        self.pyjama = pyjama
        self.pyjama.Events.add_event("open_url")
        self.pyjama.Events.connect_event("open_url", self.ev_open_url)
        ## The current Browser to be used
        self.browser = self.webbrowser # user's default browser

    ## Set a new browser
    # @param self Object Pointer
    # @param function_to_call Function to when a browser is opend
    def set_browser(self, function_to_call):
        self.browser = function_to_call

    ## Set the browser to be used to default
    # @param self Object Pointer
    def set_default_browser(self):
        self.browser = self.webbrowser

    ## called when then "open_url" event is raised
    # @param self Object Pointer
    # @param url The url that has been passed to the "open_url" event
    # @param force_default When set to True, the url is opened in the default browser
    # default value is False
    def ev_open_url(self, url, force_default=False):
        if force_default:
            self.webbrowser(url)
        else:
            self.browser(url)

    ###################################################################
    #
    # Open a given URL in the standard webbrowser
    # RETURNS: ?
    #
    ## The default webbrowser
    # @param self Object Pointer
    # @param url The URL to open
    def webbrowser(self, url):
        return webbrowser.open_new_tab(url) # mod_webbrowser is the module webbrowser // some naming issues :)        
