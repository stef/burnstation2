#!/usr/bin/env python
# -*- coding: utf-8 -*-

#
# This file contains several doxygen pages
#

## \mainpage Pyjama - Python Jamendo Audiocenter Documentation
 # 
 # \section intro_sec Introduction
 #
 # On these pages you will find developer related information
 # about Pyjama.
 # I hope that these informations will help you develop new
 # plugins or join me developing Pyjama.
 #
 # To get started please have a look at the 'Namespace' or the 'Classes'
 # sections you can see on the top of the page. 
 # 
 # The most central classes will probably be clMain.main(), clWindow.winGTK() and
 # clLayouts.Layouts() since these classes handle most of pyjama's actions.
 #
 # In order to develop Plugins you probably want to have a look at Pyjama's
 # <a href = "Plugins.html"><b>plugin</b></a> and <a href = "Events.html"><b>event interface</b></a>.
 #
 # \section Basic Structure
 # Please have a look at the following page to get an idea what the Pyjama object hierarchy looks like \n
 # \ref structure 
 

 ## \page structure Basic Structure
 #  Here a brief structure of the program
 #
 #
 #  \dot
 #  digraph example {
 #       node [shape=record, fontname=Helvetica, fontsize=10];
 #      pyjama [ label="pyjama.py" URL="namespacepyjama.html"];
 #      clWindow [ label="clWindow.gtkWIN" URL="namespaceclWindow.html"];
 #      clMain [ label="clMain.main()" URL=""];
 #      dumptools [ label="download_db.dump_tools()" URL=""];
 #      tray [ label="notification.TrayIcon()" URL=""];
 #      player [ label="clGstreamer010.Player()" URL=""];
 #      jamendo [ label="clJamendo.Jamendo()" URL=""];
 #      db [ label="clDB.DB()" URL=""];
 #      browser [ label="clBrowserInterface.Browser()" URL=""];
 #      layouts [ label="clLayouts.Layouts()" URL=""];
 #      plugin [ label="clPlugin.Plugins(()" URL=""];
 #
 #      pyjama -> clWindow [ arrowhead="open", style="line" ];
 #      clWindow -> clMain [ arrowhead="open", style="line" ];
 #      clMain -> dumptools [ arrowhead="open", style="line" ];
 #      clMain -> tray [ arrowhead="open", style="line" ];
 #      clMain -> player [ arrowhead="open", style="line" ];
 #      clMain -> jamendo [ arrowhead="open", style="line" ];
 #      clMain -> db [ arrowhead="open", style="line" ];
 #      clMain -> browser [ arrowhead="open", style="line" ];
 #      clMain -> layouts [ arrowhead="open", style="line" ];
 #      clMain -> plugin [ arrowhead="open", style="line" ];

 #  }
 #  \enddot
 #  Note that the classes in the above graph are clickable 
 #  (in the HTML output).





## \page Tracks Pyjama's Tracks
# In any Pyjama version > 0.2.1 Pyjama uses a new track object. This was necessary
# since the old track-dicts where very confusing and caused a lot of errors.
# You can import the new track-object from clGstreamer010:
# from clGstreamer010 import Track
#
# From now on only track objects can be added to the playlist.
#
# Here a list of fields every track object has to have:
# - Track.name
#   - Name of this track
# - Track.duration
#   - Duration of this track in seconds
# - Track.numalbum
#   - Number of the track in the corresponding album
# - Track.id
#   - ID of the track
# - Track.id3genre
#   - space seperated list of id3genres for this track
# - Track.album_id
#   - ID of the track's album
# - Track.album_name
#   - name of the track's album
# - Track.arist_id
#   - ID of the track's artist
# - Track.artist_name
#   - name of the track's artist
# - Track.stream
#   - jamendo stream url of this track
#
# There is a new attribute: Track.position_in_playlist is None by default and will be set to an int when the track is actually being played. In pyjama > 0.3 this attribute will be set when the track is being added to a playlist.
#
# The functions clDB.DB.get_multiple_trackinfos() and clDB.DB.get_trackinfos2() now also return Track objects. The new Track object behaves like a dict to calls like Track['name'] but prints out a deprecation warning. You should replace such calls.

## \page Events Pyjama's Event interface
#
# Pyjama comes with an own simple event interface.\n
# It basically holds four methods which make it quite easy to react on events or create own events:\n
# - pyjama.Events.add_event(EVENT_NAME)
#   - Creates an event called EVENT_NAME
# - pyjama.Events.connect_event(EVENT_NAME, CALLBACK_FUNCTION)
#   - Connects to the event EVENT_NAME and calles CALLBACK_FUNCTION whenever this event is raised
# - pyjama.Events.raise_event(EVENT_NAME, *ARGS)
#   - Raises the event EVENT_NAME with the params *ARGS
# - pyjama.Events.disconnect_event(EVENT_NAME, CALLBACK_FUNCTION)
#   - Disconnects CALLBACK_FUNCTION from the event EVENT_NAME
#
# Please notice that some events (e.g. 'pluginloaded') send some additional params to the callback
# function. In order to prevent errors please check, if your callback function takes these params.
#
# Eventlist:
# The following events might interest you:
# - pluginloaded
# - nowplaying
# - alldone
# - showing_album_page
# - showing_artist_page
# - firstrun
# - error
# - layout_changed
# - populate_listmenu
# - popular_playlistmenu
# - scrolled_window_resized
# - playlist_tooltip
#
# For more information have a look at the clEvent module.


## \page Plugins Pyjama's Plugin interface
#
# Pyjama has a quite simple plugin interface which - so I think - will enable you
# to develop what ever you want as a plugin. For now I am the developer of most
# of pyjama's plugins but I hope this will change soon. If you need another interface,
# a new event or another way to interact with pyjama, please just write a mail and ask
# for it!
#
# The following section was taken from the plugin's readme file:
# <hr>
#
# <pre>
# A short guide to plugins for pyjama
#+-----------------------------------+
#
# Pyjama uses a new plugin system since version 0.1.29.
# This is a short guide how to do plugins for pyjama now.
#
# Requirements
#+------------+
#    1) plugins have to be stored in pyjama's plugin folder
#    2) every plugin has its own folder there
#    3) each plugin needs a .info file in its folder
#    4) each plugin needs a file called "__init__.py" in its folder
#
# .info file
#+----------+
#    1) this file has to have the same name as its folder
#    2) it holds:
#        - "name" to store the plugin's full name
#        - "version" to store the plugin's current version
#        - "order" to influence in which order the plugins are loaded
#          the higher this value is the later pyjama will load the plugin
#        - "author" to store the author's name
#        - "description" for a short description of the plugin
#        - "copyright" for a short copyright line
#        - "license" the license of the plugin.
#        - "homepage" 
#
#    A proper .info file might look like this:
#
#    Name = Example Plugin 123
#    Order = 500
#    Version = 0.17
#    Author = Me
#    Description = Just testing
#    Copyright = By me 2009-FFFFFF
#    license = GPLv3
#    homepage = http://www.xn--ngel-5qa.de
#
# __init__.py
#+-----------+
#    * this file is needed to treat the while directory as a module
#    * it needs to have a class called "main"
#    * pyjama will pass a object holding all pyjama objects to this class 
#
# Example
#+-------+
#    the directory scheme should be something like this:
#
#    pyjama/
#        plugins/
#            my_plugin/
#                __init__.py
#                my_plugin.info
#            anotherplugin/
#                __init__.py
#                anotherplugin.info
#
#!! Please have a look at pyjama's example plugin - it is quite simple !!
#</pre>
#
# <b> Preferences </b>
# If you want to show preferences for your plugin, you should use pyjama's preferences dialog. 
# This can be done in three simple steps:
# - you need ne function that creates a container (i.e. gtk.VBox), puts some widgets on it and returns the container
# - you need a second function that will be called by pyjama after the user has closed the preferences dialog pressing "Ok"
# - tell pyjama about your preferences and call: self.pyjama.preferences.register_plugin("NAME", first_function, second_function)
#
# As said before: Have a look at the example plugin!


## \page layouts Layouts
#
# Layouts are main user interface in pyjama: They are used to show the albums in pyjama's album-browser, the artist informations on artist-pages and your favorite albums in the starred-albums-plugin.
# If this page confuses you more than it helps you, please have a look at the quite simple stared_albums-plugin. The folder 'clLayouts' contains even more example for the layout interface.
#
#
# <b>Here some information how to create your own layout:</b>
#
# - create a new class called "MyLayout", derived from gtk.Layout
# - create a subclass called "Toolbar" - derived from gtk.HBox
# - MyLayout at least needs the following methode:
#   - draw(self, arg1, arg2, arg3, arg4)
#
# 
# <b>The draw methode:</b>
#
# The draw methode of your layout is called whenever your layout ist meant to be shown. Pyjama passes 4 params to this methode - use this params to generate the data you need for your layout (e.g. hits per page, page number, order etc). In this methode the information is placed on the layout and shown: For example an album-browser would query jamendo for some albums, download the covers and show them on the layout.
#
#
# <b>Register a layout</b>
#
# Now we need to tell pyjama, that we've created a new layout. As you'll be most probably developing a plugin, just connect to the "alldone" event and call the following function:
# pyjama.layouts.register_layout("my-layout", MyLayout(self.pyjama))
# - "my-layout" is just a identifier string for your layout. You'll need it, to show your layout
# - MyLayout(self.pyjama) is the actual Layout class - in this example a reference to the pyjama-object is passed to it. At this point you do not need to generate any data or something - just init your layout, don't show or calculate anything.
#
#
# <b>Showing the layout</b>
#
# Now, how do we show the layout? The best way is to create a menu or toolbar entry in the plugin's alldone-methode. Whenever this menu or toolbar entry is being clicked, call:
# - pyjama.layouts.show_layout("my-layout", 10, 1, "listens", "rock")
#
# Pyjama will now call the draw methode of your MyLayout class with the params 10, 1, "listens" and "rock". This is how the params come to your draw() methode ;).
# Please remember: You cannot pass more than 4 params to your draw() methode. Actually you cannot even pass less than 4 values: If you call show_layout("my-layout", 10, 1), pyjama will pass None als arg3 and arg4 to your draw() methode. 
#
#
# <b>Arranging the layout</b>
#
# If you want to be notified, when the size of your parent container changes, please connect to pyjama's "scrolled_window_resized" event.
