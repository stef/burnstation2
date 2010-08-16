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
from time import time
import functions

# Gettext - Übersetzung
functions.translation_gettext()
#def _(string):
#    return string


###################################################################
#
# download and extrackt themes 
# RETURNS: 0 = ok, 1 = download error, 2 = extraction error
# 
def download_pack():
    home=functions.preparedirs()
    print ("Downloading themepack")
    ret = os.system("wget -cO %s xn--ngel-5qa.de/pyjama/release/themepack.tar.gz" % os.path.join(home, "themepack.tar.gz"))
    if ret <> 0:
        print ("Error downloading the themepack")
        return 1
    else:
        print ("Extracting themepack to '~/.pyjama/themes'")
        ret = os.system("tar -C %s -xf %s" % (home, os.path.join(home, "themepack.tar.gz")))
        if ret <> 0:
            print ("Error extracting the themepack")
            return 2
        else:
            print ("All done")
            return 0

