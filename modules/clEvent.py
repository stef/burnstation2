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

# This Script was found on:
# http://www.valuedlessons.com/2008/04/events-in-python.html


## @package clEvent
# Pyjama's custom event module

## The EventHandler class represents the Event itself.
# A EventHandler is created for earch plugin created.
# Usually you do not have to use this class.
# Please have a look at clEvent.Events
class EventHandler:
    def __init__(self):
        ## List of functions which will be called by this EventHandler
        self.handlers = [] #set()

    ## Adds an function to the handler list
    def handle(self, handler):
        #self.handlers.insert(0,handler)
        self.handlers.append(handler)
        return self

    ## Removes a function from the handler list
    def unhandle(self, handler):
        try:
            self.handlers.remove(handler)
        except:
            raise ValueError("Handler is not handling this event, so cannot unhandle it.")
        return self

    ## Calls each function in the handler list
    # @param *args Arguments
    # @param **kargs Keyword arguments
    def fire(self, *args, **kargs):
        for handler in self.handlers:
#            if "alldone" in str(handler): print handler
            handler(*args, **kargs)

    ## Returns the number of functions connected to this event
    def getHandlerCount(self):
        return len(self.handlers)

    __iadd__ = handle
    __isub__ = unhandle
    __call__ = fire
    __len__  = getHandlerCount

## Pyjama's event class is the EventHandler class interface
class Events:
    def __init__(self):
#        self.pluginloaded = EventHandler()
#        self.nowplaying = EventHandler()
#        self.alldone = EventHandler()
        ## A dictionary with all events created
        self.dict = {}

    ## Creates a new event
    # @param self Object Pointer
    # @param eventname The new event's name
    # @return None
    def add_event(self, eventname):
        self.dict[eventname] = EventHandler()

    ## Connects to an existing event
    # @param self Object Pointer
    # @param eventname Name of the event to connect to
    # @param fkt The function to call when this event is raised
    # @return None
    def connect_event(self, eventname, fkt):
        self.dict[eventname] += fkt

    ## Disconnects a function from an event
    # @param self Object Pointer
    # @param eventname Name of the event to disconnect from
    # @param fkt The function to disconnect
    # @return None
    def disconnect_event(self, eventname, fkt, *argv):
        self.dict[eventname] -= fkt

    ## Raises an event
    # @param self Object Pointer
    # @param eventname Name of the event to raise
    # @param *argv Arguments to pass to the connected functions
    # @param *kargs Keyword arguments to pass to the connected functions
    # @return None
    def raise_event(self, eventname, *argv, **kargs):
        self.dict[eventname](*argv, **kargs)

