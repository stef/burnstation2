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

## @package pyjama
# This is pyjama's startup file. It checks for params, runs corresponding 
# actions and finally calls clWindow.winGTK() to startup pyjama

import gtk
# this line kills gtkmozembed when a flash plugin is installed
gtk.gdk.threads_init()
# Time formatting
from time import strftime, gmtime, time, sleep
# Option Parser
from optparse import OptionParser, OptionGroup
# Fehlerverfolgung
import traceback
import os
import sys

import shutil

## A simple function that print a box to console
# @param txt Text to put into that box
def printbox(txt):
    sign = "#"
    box_width = 60

    txt = txt.split("\n")
    for line in txt:
        line = line.strip()
        spaces = ((box_width - len(line)) //2)-2
        while (spaces * 2) + len(line) + 2 < box_width:
            line = line+ " "
        if line.strip() != "---":
            print (sign + " "*spaces + line + " "*spaces + sign)
        else:
            print (sign*box_width)

if os.name == "posix" or "mac":
    sys.path.append("/usr/share/apps/pyjama") # linux
else:
    sys.path.append(os.path.join(os.getenv('PROGRAMFILES'), "pyjama")) # windows

try:
    from modules import clXMLRPC
    XMLRPC_AVAILABLE = True
except Exception, inst:
    XMLRPC_AVAILABLE = False

## @cond skip
# Benutzerklassen
try:
    from modules import functions
    if "check-modules" in sys.argv:
        functions.check_modules()        
        sys.exit(0)
    from modules import clSettings
    from modules import clWindow
except ImportError, err:
    print (traceback.format_exc())
    txt = """---

    Pyjama could not find or load some of its modules
    This sometimes happens when you have copied
    pyjama.py to another path than the other pyjama
    files.
    Use a softlink instead or edit line 41 in pyjama.py
    and add sys.path.append("/usr/share/apps/pyjama")

    ---

    !Please also check, if you meet all dependencies!
    Especially the module 'simplejson' needs to be 
    installed.

    ---"""
    printbox(txt)
    sys.exit(1)
## @endcond

# Gettext - Übersetzung
functions.translation_gettext()
#def _(string):
#    return string

home = functions.preparedirs()
## get a settings instance to get default themes ...
settings = clSettings.settings(None)

# Check if a m3u is given as a param
# see clMain.py line 550ff
# not implemented, yet since I cannot deduce froum
# stream URL to track-id
#for arg in sys.argv:
#    if arg.endswith(".m3u"):
#        # check if another pyjama instance is running.
#        # Since xmlrpc seems to be somehow instable for 
#        # me, i will use the methode below
#        dest = os.path.join(home, "jamendo-playlist.m3u")
#        try:
#            shutil.copy(arg, dest)
#        except:
#            print("An error occured while trying to copy %s" % arg)
#        else:
#            sleep(0.5)
#            if os.path.exists(dest):
#                # No other instance running
#            else:
#                # Another instance is running so exit
#                sys.exit(0)

## @cond skip
######################################################################
#                                                                    #
#                             Update Hacks                           #
#                                                                    #
######################################################################

## PMC was blacklisted in older version
## This hack will activate it
#try:
#    bl = settings.get_value("PLUGINS", "BLACKLIST")
#    counter = settings.get_value("PYJAMA", "counter", 0)
#    if counter < 2:
#        settings.set_value("PYJAMA", "counter", "2")
#        if "pmc" in bl:
#            bl = bl.replace("pmc", "")
#            settings.set_value("PLUGINS", "BLACKLIST", bl)
#            print ("Removed pmc from blacklist.")
#except:
#    pass

## Configtool blacklistet itself 
## This hack will remove it from blacklist
#try:
#    bl = settings.get_value("CONFIGTOOL", "BLACKLIST")
#    counter = settings.get_value("PYJAMA", "counter", 0)
#    if counter < 3:
#        settings.set_value("PYJAMA", "counter", "3")
#        if "CONFIGTOOL" in bl:
#            bl = bl.replace("CONFIGTOOL", "")
#            settings.set_value("CONFIGTOOL", "BLACKLIST", bl)
#            print ("Removed configtool from blacklist.")
#except:
#    pass

# This hack will set the new standard-theme for pyjama
# for certain older relases
try:
    theme = settings.get_value("PYJAMA", "STANDARD_THEME", "None")
    counter = settings.get_value("PYJAMA", "counter", 0)
    if counter < 4 and theme != "None":
        settings.set_value("PYJAMA", "STANDARD_THEME", "None")
        settings.set_value("PYJAMA", "counter", "4")
        print ("Unset default theme")
except:
    pass

# This hack will remove the field 'all' from the taglist
try:
    theme = settings.get_value("JAMENDO", "TAGs", -1)
    counter = settings.get_value("JAMENDO", "counter", 0)
    if counter < 5 and theme != -1:
        settings.set_value("PYJAMA", "counter", "5")
        if "all " in theme:
            theme = theme.replace("all", "")
            settings.set_value("JAMENDO", "TAGs", theme)
            print ("removed 'all' from taglist")
except:
    pass

# This hack will add option format_stream and set it
# to mp31 since ogg does not support streaming on jamendo
try:
    format = settings.get_value("JAMENDO", "format_stream", -1)
    counter = settings.get_value("PYJAMA", "counter", 0)
    if counter < 6 and format != -1:
        settings.set_value("PYJAMA", "counter", "6")
        settings.set_value("JAMENDO", "format_stream", "mp31")
        "set stream format to mp3 since this will support seeking"
except:
    pass

# downloadGUI was blacklisted in older version
# This hack will activate it
try:
    bl = settings.get_value("PLUGINS", "BLACKLIST")
    counter = settings.get_value("PYJAMA", "counter", 0)
    if counter < 7 and "downloadGUI" in bl:
        settings.set_value("PYJAMA", "counter", "7")
        if "downloadGUI" in bl:
            bl = bl.replace("downloadGUI", "")
            settings.set_value("PLUGINS", "BLACKLIST", bl)
            print ("Removed downloadGUI from blacklist.")
except:
    pass

# configtool was replaced by pyjama's own preferences dialog
# this hack will blacklist the configtool plugin
try:
    bl = settings.get_value("PLUGINS", "BLACKLIST")
    counter = settings.get_value("PYJAMA", "counter", 0)
    if counter < 8 and not "configtool" in bl:
        settings.set_value("PYJAMA", "counter", "8")
        if not "configtool" in bl:
            bl = "%s %s"  % (bl, "configtool")
            settings.set_value("PLUGINS", "BLACKLIST", bl)
            print ("Added configtool to blacklist.")
except:
    pass

# Toolbar texts are disabled by default. This hack will
# enable them.
try:
    tb = settings.get_value("PYJAMA", "SHOW_TOOLBAR_TEXT", True)
    counter = settings.get_value("PYJAMA", "counter", 0)
    if counter < 9 and tb == False:
        settings.set_value("PYJAMA", "counter", "9")
        settings.set_value("PYJAMA", "SHOW_TOOLBAR_TEXT", True)
        print ("Showing toolbar texts enabled. ")
except:
    pass

try:
    tb = settings.get_value("PYJAMA", "SHOW_TOOLBAR_TEXT", True)
    counter = settings.get_value("PYJAMA", "counter", 0)
    if counter < 9 and tb == False:
        settings.set_value("PYJAMA", "counter", "9")
        settings.set_value("PYJAMA", "SHOW_TOOLBAR_TEXT", True)
        print ("Showing toolbar texts enabled. ")
except:
    pass


## @endcond

(
 PLAYPAUSE,
 PREV,
 NEXT,
 PLAYING
) = range(4)

def xmlrpc(command):
    if XMLRPC_AVAILABLE:
        try:
            xmlrpc = clXMLRPC.XMLRPC(None, clientonly=True)
        except:
            print("ERROR - no instance of pyjama found")
            return
    
        if xmlrpc.role == "client":
            try:
                xmlrpc.server.test("test123")
                if command == PLAYPAUSE:
                    xmlrpc.server.playpause()
                if command == NEXT:
                    xmlrpc.server.next()
                if command == PREV:
                    xmlrpc.server.prev()
                if command == PLAYING:
                    ret = xmlrpc.server.get_curplaying()
                    try:
                        for key in ret.iterkeys():
                            print("%s: %s" % (key, ret[key]))
                    except:
                        print(ret)
            except Exception, inst:
                print ("ERROR talking to pyjama: %s" % inst)
    else:
        print("ERROR - xmlrpc not available")

######################################################################
#                                                                    #
#                  parameter actions / theming                       #
#                                                                    #
######################################################################
## This functin is called after the option parser parsed pyjama.cfg
# @param options The options parser result
def run(options):
    ## Check some playback options
    if options.xmlrpc_playpause:
        xmlrpc(PLAYPAUSE)
        return
    elif options.xmlrpc_next:
        xmlrpc(NEXT)
        return
    elif options.xmlrpc_prev:
        xmlrpc(PREV)
        return
    elif options.xmlrpc_playing:
        xmlrpc(PLAYING)
        return
    
    
    if options.version:
        print (functions.VERSION)
        return None
    home = functions.preparedirs(set_privilegs=True)
    if "check-modules" in sys.argv:
        return None
    if options.cache_long:
        directory = os.path.join(home, "cache", "long")
        files = os.listdir(directory)
        for f in files:
            os.remove(os.path.join(directory, f))
        print ("Deleted all cache-entries for long-time-cache")
    if options.cache_short:
        directory = os.path.join(home, "cache", "short")
        files = os.listdir(directory)
        for f in files:
            os.remove(os.path.join(directory, f))
        print ("Deleted all cache-entries for short-time-cache")
#    if len(sorteddirlist()) == 0:
#        options.downloadthemes = True
    if options.downloadthemes:
        # IMPROVE THIS
        from modules import get_themepack 
        ret = get_themepack.download_pack()    
        if ret == 0:
            #pass
            options.listhemes = True
        else:
            return None
    #~ if options.downloadimages:
        #~ # IMPROVE THIS
        #~ from modules import get_imagepack 
        #~ ret = get_imagepack.download_pack()        
        #~ if ret == 0:
            #~ # no error
            #~ pass
        #~ else:
            #~ print ("An error occured")
            #~ print ("You can try again running 'pyjama -i'")
    if not os.path.exists(os.path.join(home, "pyjama.db")):
        print ("forcing update - no database found")
        options.update = True
    if options.listhemes:
        dirs = functions.sorteddirlist()
        counter = 1
        if len(dirs) == 0:
            print ("No themes installed")
            print ("You can get some by running 'pyjama -p'")
        else:
            print ("Following Themes were found:")
        for directory in dirs:
            print ("%i) %s" % (counter, directory))
            counter += 1
        return None
    val = settings.get_value("PYJAMA", "standard_theme")
    if val == "None" or val == None or val[0] == "#": 
        if not options.theme or options.theme=="None": options.nocolor=True
    if not options.nocolor and not options.theme:
            options.theme = val
    if options.theme and not options.nocolor:
        ret, theme = functions.showtheme(options.theme)
        if ret == None:
            print ("Loaded theme '%s'") % theme
        else:
            print (ret)
            return None
    win = clWindow.winGTK(options)
    try:
        #~ gtk.gdk.threads_enter()
        gtk.main()
        #~ gtk.gdk.threads_leave()
    except KeyboardInterrupt:
        win.main.quit()
        print (".... bye!")
        sys.exit(0)

if __name__ == "__main__":
    ## get a OptionParser instance to parse the options
    parser = OptionParser()

    parser.add_option("-u", "--update", action="store_true", dest="update", default=False, help=_("Get Jamendo's latest database dump"))
    parser.add_option("", "--update-jamendo", action="store_true", dest="update_jamendo", default=False, help=_("Get Jamendo's latest database dump directly from the slow Jamendo server[not recommended]"))

    parser.add_option("", "--clear-short", action="store_true", dest="cache_short", default=False, help="Delete local cache data (short)")

    parser.add_option("", "--clear-long", action="store_true", dest="cache_long", default=False, help="Delete local cache data (long)")

    parser.add_option("", "--version", action="store_true", dest="version", default=False, help=_("Return Pyjama's version"))

    theme_group = OptionGroup(parser, "Theme Control", "Which theme do you want pyjama to use?")
    theme_group.add_option("-t", "--theme", dest="theme", help=_("A gtk theme for pyjama. The theme as to be copied to '~/.pyjama/themes'. Example: pyjama --theme Aero-ion3.1. pyjama -t 1 would run the first theme found in your theme- directory."), metavar="theme")
    theme_group.add_option("-l", "--list", action="store_true", dest="listhemes", default=False, help=_("List all themes found"))
    theme_group.add_option("-p", "--download-themes", action="store_true", dest="downloadthemes", default=False, help=_("Download Themepack for Pyjama"))
    theme_group.add_option("-n", "--notheme", action="store_true", dest="nocolor", default=False, help=_("Don't do any color- modifications. Pyjama will exactly look like any of your applications"))
    parser.add_option_group(theme_group)
    #~ parser.add_option("-i", "--download-images", action="store_true", dest="downloadimages", default=False, help=_("Downloads round about 4MB of album covers from a mirror to speed up browsing through jamendo - this is usually done on the first run automatically"))

    output_group = OptionGroup(parser, "Verbose Control", "How verbose should pyjama be?")
    output_group.add_option("-v", "--verbose", action="store_true", dest="verbose", default=False, help=_("Print some informations"))
    output_group.add_option("-d", "--debug", action="store_true", dest="debug", default=False, help=_("Print a lot informations"))
    output_group.add_option("-e", "--debug-extreme", action="store_true", dest="debug_extreme", default=False, help=_("Print much to much information"))
    parser.add_option_group(output_group)


    playback_group = OptionGroup(parser, "Playback Control", "Use these options to control another pyjama instance. If not other pyjama instance is found, nothing will happen at all.\nPlease only enter ONE playback_group option. No other options will take effect")
    playback_group.add_option("", "--playpause", action="store_true", dest="xmlrpc_playpause", default=False, help=_("Play/Pause"))
    playback_group.add_option("", "--next", action="store_true", dest="xmlrpc_next", default=False, help=_("Next"))
    playback_group.add_option("", "--prev", action="store_true", dest="xmlrpc_prev", default=False, help=_("Previous"))
    playback_group.add_option("", "--curtrack", action="store_true", dest="xmlrpc_playing", default=False, help="Some infos for the track being played")
    parser.add_option_group(playback_group)



#    parser.add_option("", "--print-tracebacks", action="store_true", dest="print_tracebacks", default=False, help=_("Print error tracebacks"))

   
    (options, args) = parser.parse_args()
    #~ if "-h" or "-?" in sys.argv: parser.print_help()
    #~ sys.exit(0)
    
    run(options)
    
#print ('''

#                          ################ 
#                   ..............................
#              ####.................................###
#              #==#................................#==#
#              #==#............................... #==#
#              #==#............................... #==#
#              #=##............................... ##=#
#               ###      ....................      ###
#                        .....  ####### .....
#                        ....  #       # ....
#                        .... #         # ...
#                        ..... #       # ....
#                        ...... ####### .....
#                        ....................
#                        ....................
#                        ....................
#                       Thanks for using pyjama
#''')
