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

## @package functions
# The function module holds some general
# functions.

import gettext
import os, sys
import shutil
from time import strftime, gmtime
import re
import gtk

import constants

import urllib2, httplib

import xml.etree.ElementTree as ET #read_xspf_playlist


#httplib.HTTPConnection.debuglevel = 1

## Returns the directory from which pyjama was started.
# This might be the install directory or the script's
# directory.
# @return A string containing a path
def install_dir():
    dirname = os.path.dirname(sys.argv[0])
    abspath =  os.path.abspath(dirname)

    if os.name == "nt":
        if os.path.exists(os.path.join(abspath, "modules", "clGstreamer010.py")):
            #libs here
            return abspath
        else:
            return os.path.join(os.getenv('PROGRAMFILES'), "pyjama")
    else:
        if os.path.exists(os.path.join(abspath, "modules", "clGstreamer010.py")):
            #libs here
            return abspath
        else:
            return constants.INSTALL_DIR_POSIX

## Takes a given url, opens it and returns
# the url it redirects to
# @param url The url to resolve
def resolve_redirect(self, url):
    request = urllib2.Request(location)
    opener = urllib2.build_opener()
    ret = opener.open(request)
    location = ret.url
    return location


def read_xspf_playlist(playlist):
    namespace = "{http://xspf.org/ns/0/}"

    try:
        tree = ET.parse(playlist)
        root = tree.getroot()
        tracklist = root.find("%strackList" % namespace)
    except:
        return None
    
    if tracklist:
        tracks = tracklist.findall("%strack" % namespace)

        streamlist = []

        for elem in tracks:
            stream = elem.find("%slocation" % namespace).text
            if stream:
                streamlist.append(stream)

        if len(streamlist) > 0:
            return streamlist

                
## Compares to list of floats.
# @param list1 First list
# @param list2 Second list
# @param epsilon=0.09 Allowed deviation
# @return True if list are equal, else False
def compare_float_lists(list1, list2, epsilon=0.09):
    if len(list1) != len(list2): return False

    for counter in range(0, len(list1)-1):
        item1 = float(list1[counter])
        item2 = float(list2[counter])
        if item1 - epsilon < item2 < item1 + epsilon or item2 - epsilon < item1 < item2 + epsilon:
            pass
        else:
            return False
    return True

## Getting the installed pyjama version
# deprecated: just use "from modules.functions import VERSION" instead
# @return 
# - "0.0.0" if an error occured
# - Another string if succesfull
def get_version():  
    pass
#def get_version():
#    try:
#        txt=open(os.path.join(install_dir(), "about.glade"), "r").read()

#        re1='.*?'	# Non-greedy match on filler
#        re2='()'	# Tag 1
#        re3='(\\d+)'	# Integer Number 1
#        re4='(\\.)'	# Any Single Character 1
#        re5='(\\d+)'	# Integer Number 2
#        re6='(\\.)'	# Any Single Character 2
#        re7='(\\d+)'	# Integer Number 3
#        re8='(<\\/property>)'	# Tag 2

#        rg = re.compile(re1+re2+re3+re4+re5+re6+re7+re8,re.IGNORECASE|re.DOTALL)
#        m = rg.search(txt)
#        if m:
#            tag1=m.group(1)
#            int1=m.group(2)
#            c1=m.group(3)
#            int2=m.group(4)
#            c2=m.group(5)
#            int3=m.group(6)
#            tag2=m.group(7)
##            print "%s.%s.%s" % (int1, int2, int3)
#            return "%s.%s.%s" % (int1, int2, int3)
#        else:
#            return "0.0.0"
#    except Exception, inst:
#        return "0.0.0"

VERSION="0.3.0.78" #!!Version line 


## Getting and making pyjama- dirs
# @param set_privilegs Tries to set 0777 privilegs to the pyjama
# directory in your home folder in order to prevent the root
# from accidentially owning it.
# @return A string containing pyjama's home directory (~/.pyjama)
def preparedirs(set_privilegs = False):
    home = os.getenv("HOME")
    if home == None: # WINDOWS
        home = os.path.join(os.getenv("HOMEDRIVE"), os.getenv("HOMEPATH"))
    HOME_DIR_NAME = constants.PYJAMA_HOME_DIRECTORY_NAME
    home_pyjama = os.path.join(home, HOME_DIR_NAME)
    if set_privilegs:
        if os.path.exists(os.path.join(home, HOME_DIR_NAME)):
            os.system("chmod -R 0777 %s" % os.path.join(home, HOME_DIR_NAME))
        if os.path.exists(os.path.join(home, HOME_DIR_NAME, "images")) == False:
            os.makedirs(os.path.join(home, HOME_DIR_NAME, "images"))
        if os.path.exists(os.path.join(home, HOME_DIR_NAME, "cache")) == False:
            os.makedirs(os.path.join(home, HOME_DIR_NAME, "cache"))
        if os.path.exists(os.path.join(home, HOME_DIR_NAME, "cache", "long")) == False:
            os.makedirs(os.path.join(home, HOME_DIR_NAME, "cache", "long"))
        if os.path.exists(os.path.join(home, HOME_DIR_NAME, "cache", "short")) == False:
            os.makedirs(os.path.join(home, HOME_DIR_NAME, "cache", "short"))
        if os.path.exists(os.path.join(home, HOME_DIR_NAME, "themes")) == False:
            os.makedirs(os.path.join(home, HOME_DIR_NAME, "themes"))
        if not os.path.isfile(os.path.join(home_pyjama, "eq_presets")):
            shutil.copy(os.path.join(install_dir(), "eq_presets"), os.path.join(home_pyjama, "eq_presets"))
        if not os.path.isfile(os.path.join(home_pyjama, "pyjama.cfg")):
            shutil.copy(os.path.join(install_dir(), "pyjama.cfg"), os.path.join(home_pyjama, "pyjama.cfg"))
            if not os.path.isfile(os.path.join(home_pyjama, "pyjama.cfg")):
                print "Error copying config file to user's pyjama directory"
                print "Please try to do so on your own"
        os.chmod(home_pyjama, 0777)
    return home_pyjama


#def get_pyjama_dir():
#    return os.path.join(os.getenv("HOME"), ".pyjama")

## List with some theme paths
theme_dirs = [os.path.join(preparedirs(),"themes"), gtk.rc_get_theme_dir(), os.path.join(install_dir(), "themes") ]

## Returns a list of available Themes
# @return A list of themes
def sorteddirlist():
    theme_list = []
    for t in theme_dirs:
        if os.path.exists(t):
            for theme in os.listdir(os.path.join(t)):
                theme_path = os.path.join(t, theme, "gtk-2.0", "gtkrc")
                if os.path.exists(theme_path) and not theme in theme_list:
                    theme_list.append(theme)
    return sorted(theme_list)
    


## Load a theme
# @param theme A theme name or the number of a theme
# @return 
# - An error message and None as tuple if an error occured
# - tk.rc_parse() and theme name as tuple if succesfull
def showtheme(theme, reparse=False):
    home = preparedirs()
    if theme.isdigit():
        dirs = sorteddirlist()
        if int(theme)-1 < len(dirs):
           theme = dirs[int(theme)-1]
        else:
           return _("No theme for entry '%s'") % theme, None
    fl = None
    for t in theme_dirs:
        f = os.path.join(t, theme, "gtk-2.0", "gtkrc")
        if  os.path.exists(f):
            fl = f
    if not fl:
        return _("No theme for entry '%s'") % theme, None
    else:
        return gtk.rc_parse(fl), theme



## Checks file write permissions for the current user
# @return Bool
def is_writeable(path):
    return os.access(path, os.W_OK)



from htmlentitydefs import name2codepoint as n2cp
import re
## Decoding Display Names
# In the old dbdumps Jamendo had some string
# that did not work well with pango. This
# function should remove those strings
# @return string
def decode_htmlentities(string):
    entity_re = re.compile("&(#?)(\d{1,5}|\w{1,8});")
    return entity_re.subn(__substitute_entity, string)[0]
def __substitute_entity(match):
    ent = match.group(2)
    if match.group(1) == "#":
        return unichr(int(ent))
    else:
        cp = n2cp.get(ent)

        if cp:
            return unichr(cp)
        else:
            return match.group()

## Format time
# @parram seconds Time in seconds
# @return time string
# @todo Fix ValueErrors
def sec2time(seconds):
    seconds = int(seconds)
    if seconds > (60*60):
        try:
            time_string = strftime("%H:%M:%S", gmtime(int(seconds)))
        except ValueError:
            return "00:00:00"
    else:
        try:
            time_string = strftime("%M:%S", gmtime(int(seconds)))
        except ValueError:
            return "00:00"
    return time_string


## Convert numeric genre-id to genre names
# @param id The id3 ID as INT
# @result string
def id2genre(id):
    genres = [
    "Blues", "Classic Rock", "Country", "Dance", "Disco", "Funk", 
    "Grunge", "Hip-Hop", "Jazz", "Metal", "New Age", "Oldies", "Other", 
    "Pop", "R&amp;B", "Rap", "Reggae", "Rock", "Techno", "Industrial", 
    "Alternative", "Ska", "Death Metal", "Pranks", "Soundtrack", 
    "Euro-Techno", "Ambient", "Trip-Hop", "Vocal", "Jazz+Funk", "Fusion", 
    "Trance", "Classical", "Instrumental", "Acid", "House", "Game", 
    "Sound Clip", "Gospel", "Noise", "Alt. Rock", "Bass", "Soul", 
    "Punk", "Space", "Meditative", "Instrum. Pop", "Instrum. Rock", 
    "Ethnic", "Gothic", "Darkwave", "Techno-Indust.", "Electronic", 
    "Pop-Folk", "Eurodance", "Dream", "Southern Rock", "Comedy", 
    "Cult", "Gangsta", "Top 40", "Christian Rap", "Pop/Funk", "Jungle", 
    "Native American", "Cabaret", "New Wave", "Psychadelic", "Rave", 
    "Showtunes", "Trailer", "Lo-Fi", "Tribal", "Acid Punk", "Acid Jazz", 
    "Polka", "Retro", "Musical", "Rock &amp; Roll", "Hard Rock", "Folk", 
    "Folk/Rock", "National Folk", "Swing", "Fusion", "Bebob", "Latin", 
    "Revival", "Celtic", "Bluegrass", "Avantgarde", "Gothic Rock", 
    "Progress. Rock", "Psychadel. Rock", "Symphonic Rock", "Slow Rock", 
    "Big Band", "Chorus", "Easy Listening", "Acoustic", "Humour", 
    "Speech", "Chanson", "Opera", "Chamber Music", "Sonata", "Symphony", 
    "Booty Bass", "Primus", "Porn Groove", "Satire", "Slow Jam", 
    "Club", "Tango", "Samba", "Folklore", "Ballad", "Power Ballad", 
    "Rhythmic Soul", "Freestyle", "Duet", "Punk Rock", "Drum Solo", 
    "A Capella", "Euro-House", "Dance Hall", "Goa", "Drum &amp; Bass", 
    "Club-House", "Hardcore", "Terror", "Indie", "BritPop", "Negerpunk", 
    "Polsk Punk", "Beat", "Christian Gangsta Rap", "Heavy Metal", 
    "Black Metal", "Crossover", "Contemporary Christian", "Christian Rock",
    "Merengue", "Salsa", "Thrash Metal", "Anime", "Jpop", "Synthpop" 
    ]
    if id == None:
        return "n/A"
    return genres[int(id)]

## Gettext for translating _() strings
# For usual you won't have to call this
def translation_gettext():
    path = "locale"
    if not os.path.exists(path):
        path = os.path.join(install_dir(), "locale")
    try:
        trans = gettext.translation('pyjama', path)
    except IOError:
        trans = gettext.translation('pyjama', path, ["en_GB"])
        print "No language file for you found - using english language file"
    trans.install()

## Checks if some necessary modules can be found
# @return Number of errors as INT
def check_modules():
    err = 0
    nf1, nf2 = False, False

    try:
        import pygtk
    except ImportError:
        err += 1
        print ("Module '%s' not found") % "pygtk"

    try:
        import gtk
    except ImportError:
        err += 1
        print ("Module '%s' not found") % "gtk"

    try:
        import gtk.glade
    except ImportError:
        err += 1
        print ("Module '%s' not found") % "gtk.glade"
        
    try:
        import simplejson
    except ImportError:
        err += 1
        print ("Module '%s' not found") % "simplejson"

    try:
        import gst
    except ImportError:
        err += 1
        print ("Module '%s' not found") % "gst (gstreamer)"
        
    try:
        import xml.sax
    except ImportError:
        err += 1
        print ("Module '%s' not found") % "xml.sax"

    try:
        import sqlite3
    except ImportError:
        nf1 = True
        
    try:
        import pysqlite2
    except ImportError:
        nf2 = True
        if nf1 and nf2:
            err += 1
            print ("You need to have sqlite3 or pysqlite2 or libsqlite3-0 installed")

    if err == 0:
        print ("All modules found")
    else:
        print ("%s module(s) missing") % err

    return err

def license2text(license):
    if len(license) <= 10:
        l = license.lower()
        if l == "gplv3":
            name = "GNU GENERAL PUBLIC LICENSE Version 3"
            url = ""
        elif l == "gplv2":
            name = "GNU GENERAL PUBLIC LICENSE Version 2"
            url = ""
        elif l == "gpl":
            name = "GNU GENERAL PUBLIC LICENSE"
            url = ""
        elif "cc" in l:
            name = "Creative Commons"
            url = ""
        elif l == "lgpl":
            name = "GNU LESSER GENERAL PUBLIC LICENSE"
            url = ""
        elif l == "lgpl2":
            name = "GNU LESSER GENERAL PUBLIC LICENSE Version 2"
            url = ""
        elif l == "lgpl2.1":
            name = "GNU LESSER GENERAL PUBLIC LICENSE Version 2.1"
            url = ""
        elif l == "lgpl3":
            name = "GNU LESSER GENERAL PUBLIC LICENSE Version 3"
            url = ""
        elif l == "gfdl":
            name = "GNU Free Documentation License"
            url = ""
        elif l == "gfdl1.2":
            name = "GNU Free Documentation License Version 2"
            url = ""
        elif l == "apache":
            name = "Apache License Version 2"
            url = ""
        elif l == "artistic":
            name = "Artistic License"
            url = ""
        elif l == "bsd":
            name = "BSD License"
            url = ""
        else:
            print ("Don't know the given license '%s'. " % license)
            return license
        if url != "":
            return "This plugin is licensed under '%s'. Please visit %s for more information" % (name, url )
        else:
            return "This plugin is licensed under '%s'." % name
    else:
        return license
