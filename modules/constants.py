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

import sys
import tempfile

#############
# CONSTANTS #
#############

INSTALL_DIR_POSIX = "/usr/share/apps/pyjama"
INSTALL_DIR = "/usr/share/apps/pyjama"

if "tmpdir" in sys.argv:
    PYJAMA_HOME_DIRECTORY_NAME = tempfile.mkdtemp("pyjama")
else:
    # If you want to change pyjama's home directory name,
    # please edit this line:
    PYJAMA_HOME_DIRECTORY_NAME = ".pyjama"
