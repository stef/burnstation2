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

## @package errors
# This module holds several exceptions that might
# be raised by pyjama. 

#
# Jamendo Errors
#
## From this Class any Jamendo exception derives
class JamendoQueryException(Exception):
    pass

## This exception will be raised when the user
# queries jamendo to frequently (1s limit)
class ToFast(JamendoQueryException):
    pass

## This exception is raised when interaction with
# jamendo failed for some reasion. Pyjama will 
# popup an error dialog in those cases, too.
class ConnectionError(JamendoQueryException):
    pass



#
# Database Errors
#
class DatabaseQueryException(Exception):
    def __init__(self):
        self.inst = None
        self.traceback = None


## This Exception will be raised when querying
# the database failed. Pyjama will also popup
# and error dialog with traceback infos.
class QueryException(DatabaseQueryException):
    pass
