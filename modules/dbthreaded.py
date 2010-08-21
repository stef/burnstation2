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

## @package clDB
# clDB holds database related functions


import os, sys
import time
try:
    from pysqlite2 import dbapi2 as sqlite3
except ImportError:
    import sqlite3

import Queue, thread
from threading import Thread

####
from modules import functions
from modules.clGstreamer010 import Track
from modules.errors import DatabaseQueryException

ConnectCmd = "connect"
SqlCmd = "SQL"
StopCmd = "stop"

class Query:
    def __init__(self, cmd=None, params=[]):
        if cmd is None: cmd = SqlCmd
        self.cmd = cmd
        self.params = params

_threadex_settings = thread.allocate_lock()
qthreads_settings = 0
sqlqueue_settings = Queue.Queue()
class SettingsThread(Thread):
    def __init__(self, path, nr):
        Thread.__init__(self)
        self.path = path
        self.nr = nr
        self.started = time.time()

    def run(self):
        global qthreads_settings
        con = sqlite3.connect(self.path)
        cur = con.cursor()
        while True:
            s = sqlqueue_settings.get()
            if "print-queries" in sys.argv:
                print "Conn %d -> %s -> %s" % (self.nr, s.cmd, s.params)
            if s.cmd == SqlCmd:
                commitneeded = False
                res = []
#               s.params is a list to bundle statements into a "transaction"
                for sql in s.params:
                    error = False
                    inst = None
                    try:
                        if type(sql) == type(()):
                            cur.execute(sql[0],sql[1])
                        else:
                            cur.execute(sql)# [0],sql[1]
                    except Exception, inst:
                        error = True
                    if not sql.upper().startswith("SELECT"): 
                        commitneeded = True
                    if not error:
                        try:
                            for row in cur.fetchall(): res.append(row)
                        except Exception, inst:
                            error = True
                if not error:
                    try:
                        if commitneeded: con.commit()
                    except Exception, inst:
                        error = True
                if not error:
                    s.resultqueue.put(res)
                else:
                    error = DatabaseQueryException()
                    error.inst = inst
                    s.resultqueue.put(error)
            else:
                _threadex_settings.acquire()
                qthreads_settings -= 1
                _threadex_settings.release()
#               allow other threads to stop
                sqlqueue_settings.put(s)
                s.resultqueue.put(None)
                break

_threadex_db = thread.allocate_lock()
qthreads_db = 0
sqlqueue_db = Queue.Queue()
class DBThread(Thread):
    def __init__(self, path, nr):
        Thread.__init__(self)
        self.path = path
        self.nr = nr
        self.started = time.time()
        
    def run(self):
        print self.started
        global qthreads_db
        con = sqlite3.connect(self.path)
        cur = con.cursor()
        while True:
            s = sqlqueue_db.get()
            if "print-queries" in sys.argv:
                print "Conn %d -> %s -> %s" % (self.nr, s.cmd, s.params)
            if s.cmd == SqlCmd:
                #~ print self.started
                commitneeded = False
                res = []
#               s.params is a list to bundle statements into a "transaction"
                for sql in s.params:
                    cur.execute(sql)# [0],sql[1]
                    if not sql.upper().startswith("SELECT"): 
                        commitneeded = True
                    for row in cur.fetchall(): res.append(row)
                if commitneeded: con.commit()
                s.resultqueue.put(res)
            else:
                _threadex_db.acquire()
                qthreads_db -= 1
                _threadex_db.release()
#               allow other threads to stop
                sqlqueue_db.put(s)
                s.resultqueue.put(None)
                break

## Settings Database Class
# This settings-class is going to become
# a more powerfull settings interface than
# the current ConfigParser is.
# Of course you can still use the ConfigParser
# but have in mind, that this class also allows
# you to have own tables and real db queries.
## \todo 
# - Implementation
class DB_Settings():
    ## The Constructor
    # @param self The Object pointer
    # @param pyjama Reference to pyjama
    def __init__(self, pyjama):
        ## Reference to pyjama
        self.pyjama = pyjama
        ## Database file
        self.db = os.path.join(functions.preparedirs(), "settings.db")
        ## Holds the databse connection
        self.connection = None

        self.query_counter = 0

        if not os.path.exists(self.db):
            self.open() 
            self.create_database()
        else:
            self.open() 

    ## Set a option's value
    # @param self The Object pointer
    # @param section The table to write to
    # @param option The option as string
    # @param value The value to set as string
    # @return bool
    def set_value(self, section, option, value, table="settings"):
        option = str(option).replace("'", "''")

        sql = "SELECT COUNT(*) FROM '%s' WHERE section='%s' and option='%s'" % (table, section, option)
        ret = self.query(sql)

        if ret[0][0] == 0:
            sql = "INSERT INTO '%s' (section, option, value) values('%s', '%s', '%s')"% (table, section, option, value)
        else:
            sql = "UPDATE '%s' SET value='%s' WHERE section='%s' and option='%s'"% (table, value, section, option)

        ret = self.query(sql)

        return ret

    def increase_value(self, section, option, table="settings"):
        option = str(option).replace("'", "''")
        sql = "SELECT value FROM %s WHERE section='%s' and option='%s'" % (table, section, option)
        ret = self.query(sql)

        if ret == []:
            sql = "INSERT INTO %s (section, option, value) values('%s', '%s', '1')" % (table, section, option)
        else:
            sql = "UPDATE %s SET value=value+1 WHERE section='%s' and option='%s'" % (table, section, option)

        ret = self.query(sql)

        return ret

    ## Reads a value from an option
    # @param self The Object pointer
    # @param section The table to read from
    # @param option An option as string
    # @param default A default value
    # @return The option's value or default if section or option do not exist
    def get_value(self, section, option, default=None, table="settings"):
        option = str(option).replace("'", "''")
        
        sql = "SELECT value FROM %s WHERE section='%s' and option='%s'" % (table, section, option)
        ret = self.query(sql)

        if ret == [] or ret == -1: 
            return default
        else:
            if len(ret[0]) == 1: 
                return ret[0][0]
            else:
                return ret[0]

#    def create_table(self, option):
#        sql = """
#        CREATE TABLE %s (
#          uid INTEGER PRIMARY KEY,
#          option INTEGER,
#          value INTEGER
#        )
#        """ % option
#        self.connection.execute(sql)
#        self.connection.commit()

    def create_table(self, table_name):
        sql = "select count(name) from sqlite_master where name = '%s'" % table_name
        ret = self.query(sql)

        if ret[0][0] == 0:
            sql = """
            CREATE TABLE %s (
              uid INTEGER PRIMARY KEY,
              section STRING,
              option STRING,
              value string
            )
            """ % table_name
            ret = self.query(sql)
            return "created"
        else:
            return "existant"

    ## Create Database if not existant
    # @param self The Object Pointer
    def create_database(self):
        print("Creating settings database 'settings.db'")

#        sql = """
#        CREATE TABLE tracks (
#          uid INTEGER PRIMARY KEY,
#          id INTEGER,
#          listencounter INTEGER
#        )
#        """
#        self.connection.execute(sql)
#        self.connection.commit()

        sql = """
        CREATE TABLE settings (
          uid INTEGER PRIMARY KEY,
          section STRING,
          option STRING,
          value string
        )
        """
        ret = self.query(sql)

    ## Open Database connection
    # @param self The Object pointer
    def open(self):
        global qthreads_settings
        _threadex_settings.acquire()
        qthreads_settings += 1
        _threadex_settings.release()
        wrap = SettingsThread(self.db, qthreads_settings)
        wrap.start()

    def quit(self):
        s = Query(StopCmd)
        s.resultqueue = Queue.Queue()
        sqlqueue_settings.put(s)
#       sleep until all threads are stopped
        while qthreads_settings > 0: time.sleep(0.1)



    ## Close Database connection
    # @param self The Object poi
    def close(self):
        self.connection.close()

    ## Queries the SQLite database
    # @param self The Object pointer
    # @param query A SQL Query
    def query(self, query):        
        s = Query(None, [query])
        s.resultqueue = Queue.Queue()
        sqlqueue_settings.put(s)
        self.query_counter += 1
        ret = s.resultqueue.get()

        if isinstance(ret, DatabaseQueryException):
            desc = "There was an error while querying the settings database:\n"
            desc += str(ret.inst)
            self.pyjama.Events.raise_event("error", None, desc)
            return -1
        else:
            return ret

        try:
            cur = self.connection.cursor()
            cur.execute(query)
            rows = cur.fetchall()
            return rows
        except Exception, inst:
            desc = "There was an error while querying the settings database"
            self.pyjama.Events.raise_event("error", inst, desc)
            return -1


## Main Database Class
#
# Holds methods to search the databse
# for albums, artists, tracks and
# related informations
class DB():
    ## The constructor
    # @param self The object pointer
    # @param par Pyjama reference
    def __init__(self, par):
        ## reference to pyjama
        self.parent = par
        ## pyjama's home directory
        self.home=functions.preparedirs()
        ## pyjama's database file
        self.db = os.path.join(self.home, "pyjama.db")

        self.tracks, self.albums, self.artists = 0, 0, 0
        self.query_counter = 0

        ## stores results for threaded queries
        self.results = {}

        # not implemented, yet
        self.queue = []

        ## holds the connection to our database
        self.connection = None
        self.open()

        self.database_ok = True
        if not os.path.exists(os.path.join(functions.preparedirs(),"pyjama.db")):
            self.database_ok = False
        else:
            sql = "select count(name) from sqlite_master where name = 'albums' or name = 'artists' or name = 'tracks'" 
            try:
                tablecount =  self.__query(sql)
                if tablecount[0][0] < 3:
                    print("Some tables in the database seems to be missing, found only %i tables" % tablecount[0][0])
                    print ("Marking the database as corrupt")
                    self.database_ok = False
            except Exception:
                self.database_ok = False

        if self.database_ok:
            try:
                ## number of tracks in the database
                self.tracks = self.__query("SELECT COUNT (*) FROM tracks WHERE 1")[0][0]
                ## number of albums in the database
                self.albums = self.__query("SELECT COUNT (*) FROM albums WHERE 1")[0][0]
                ## number of artists in the database
                self.artists = self.__query("SELECT COUNT (*) FROM artists WHERE 1")[0][0]
            except TypeError, inst:
                self.database_ok = False
                desc =  "\n\n+-------------------------------------------------------+\n"
                desc += "|          A neccessary table wasn't found.             |\n"
                desc += "| Pyjama will now download and convert the needed files |\n"
                desc += "|         If any problems occur, run 'pyjama -u'        |\n"
                desc += "+-------------------------------------------------------+"
                #self.parent.Events.raise_event("error", inst, desc)
                print desc
    #            sys.exit(1)

            if self.tracks < 135000 or self.albums < 19000 or self.artists < 10000:
                print ("There seem to be a lot of entries missing in the database")
                print ("Marking the database as corrupt")
                self.database_ok = False
        else:
            self.quit()


        # run this in its own thread
#        self.watch_queue()


    ## Opens a database connection
    # @return None
    # @param self The Object pointer
    def open(self):
        global qthreads_db
        global _qthreadex_db
        global sqlqueue_db
        _threadex_db = thread.allocate_lock()
        qthreads_db = 0
        sqlqueue_db = Queue.Queue()
        
        _threadex_db.acquire()
        qthreads_db += 1
        _threadex_db.release()
        wrap = DBThread(self.db, qthreads_db)
        wrap.start()

    ## Closes the database connection
    # @return None
    # @param self The Object pointer
    def close(self):
        self.connection.close()

    def quit(self):
        s = Query(StopCmd)
        s.resultqueue = Queue.Queue()
        sqlqueue_db.put(s)
#       sleep until all threads are stopped
        while qthreads_db > 0: time.sleep(0.1)

    ## queries the database
    # @return list
    # @param self The Object pointer
    # @param query a string with a sql command
    def query(self, query):
        if not self.parent.window.check_alldone():
            self.parent.Events.raise_event("error", None, "You are not allowed to query the database before the main-module was loaded succesfully. If you are writing a plugin, please connect to the 'alldone' event.")
            return -2

        s = Query(None, [query])
        s.resultqueue = Queue.Queue()
        sqlqueue_db.put(s)
        self.query_counter += 1
        return s.resultqueue.get()


#        try:
#            self.open()
#            cur = self.connection.cursor()
#            cur.execute(query)
#            rows = cur.fetchall()
#       
#            self.close()
#        
#            return rows
#        except Exception, inst:
#            desc = "There was an error while querying the database"
#            self.parent.Events.raise_event("error", inst, desc)
#            return -1

    ## Private methode
    # Use query() for your plugins
    def __query(self, query):
        s = Query(None, [query])
        s.resultqueue = Queue.Queue()
        sqlqueue_db.put(s)
        self.query_counter += 1
        return s.resultqueue.get()

#        try:
#            self.open()
#            cur = self.connection.cursor()
#            cur.execute(query)
#            rows = cur.fetchall()
#       
#            self.close()
#        
#            return rows
#        except Exception, inst:
#            desc = "There was an error while querying the database"
#            self.parent.Events.raise_event("error", inst, desc)
#            return -1

#    ## add a query to the queue
#    # /todo Rename this fkt to query()
#    def query_to_come(self, query):
#        self.query.insert(0, query)

#    def watch_queue(self):
#        # run this in a thread
#        while 1:
#            while len(self.queue) > 0:
#                query = queue.pop()
#                self.__do_query()

#    ## queries the database - never call this function directly
#    # use query() instead
#    # @return list
#    # @param self The Object pointer
#    # @param query a string with a sql command
#    def __do_query(self, query):
#        self.query_counter += 1

#        try:
#            self.open()
#            cur = self.connection.cursor()
#            cur.execute(query)
#            rows = cur.fetchall()
#       
#            self.close()
#        
#            return rows
#        except Exception, inst:
#            desc = "There was an error while querying the database"
#            self.parent.Events.raise_event("error", inst, desc)
#            return -1

    ## get several informations for a spicific artist-id
    # @return dictionary
    # @param self The Object pointer
    # @param id An artist id as int or string
    # @param thread_id If this function is called by a thread,
    # this is the thread's id
    def artistinfos(self, id, thread_id = 0):
        sql = """
            SELECT
                artists.name, artists.country, artists.image, artists.url, artists.id, albums.name, albums.id, artists.albumcount
            FROM
                artists, albums
            WHERE
                artists.id=%s and albums.artist_id=artists.id
            """ % str(id)
        ret = self.query(sql)
        counter = 0
        artist = {}
        for info in ret:
            artist[counter] = {}
            artist[counter]['artist_name'] = info[0]
            artist[counter]['artist_country'] = info[1]
            artist[counter]['artist_image'] = info[2]
            artist[counter]['artist_url'] = info[3]
            artist[counter]['artist_id'] = info[4]
            artist[counter]['album_name'] = info[5]
            artist[counter]['album_id'] = info[6]
            artist[counter]['artist_albumcount'] = info[7]
            counter += 1
        self.results[thread_id]=artist
        return artist

    def multiple_albuminfos(self, ids):
        album_string = "("
        for album in ids:
            album_string += " albums.id=%s or" % album
        album_string = album_string[:-3] + ") and albums.artist_id=artists.id"

        sql = """
            SELECT
                albums.id, albums.name, artists.id, artists.name
            FROM
                albums, artists
            WHERE
                %s
            """ % album_string

        ret = self.query(sql)
        return ret

#    ## get track-informations for several track-ids
#    # @return dictionary
#    # @param self The Object pointer
#    # @param ids A list of ids as strings
#    def multiple_albumtracks(self, ids):
#        where_clause = ") OR ("
#        strings = []
#        for id in ids:
#            strings.append( "tracks.albumID='%s'" % id)
#        where_clause = "(" + where_clause.join(strings) + ")"
#        sql = """
#            SELECT
#                tracks.dispname, tracks.lengths, tracks.trackno, tracks.id, albums.id, albums.dispname, artists.id, artists.dispname, artists.name
#            FROM
#                albums, artists
#            INNER JOIN tracks ON albums.artistID=tracks.albumID
#            """# % where_clause #order by tracks.albumID
#        ret = self.query(sql)
#        counter = 0
#        tracks={}
#        for track in ret:
#            tracks[counter] = {}
#            #tracks[counter]['uid'] = time()
#            tracks[counter]['dispname'] = track[0]
#            tracks[counter]['lengths'] = track[1]
#            tracks[counter]['trackno'] = track[2]
#            tracks[counter]['id'] = track[3]
#            tracks[counter]['album_id'] = track[4]
#            tracks[counter]['album_dispname'] = track[5]
#            tracks[counter]['artist_id'] = track[6]
#            tracks[counter]['artist_dispname'] = track[7]
#            tracks[counter]['artist_name'] = track[8]
##            tracks[counter]['stream'] = "query" 
#            tracks[counter]['stream'] = "http://api.jamendo.com/get2/stream/track/redirect/?id=%i&streamencoding=%s" % (track[3], self.parent.settings.get_value("JAMENDO", "format_stream", "mp31"))
#            counter += 1
#        return tracks

    def check_cache(self, tr):
        tmp = os.path.join(os.path.realpath('cache'), str(tr.artist_id), str(tr.album_id), str(tr.id) + '.mp3')
        if os.path.isfile(tmp):
            tr.local = 'file://' + tmp

    ## Get trackinfos for a list of tracks
    # @return dictionary
    # @param self The Object pointer
    # @param tracks a list of strings 
    def get_multiple_trackinfos(self, tracks):
        track_string = "("
        for track in tracks:
            track_string += " tracks.id=%s or" % track
        track_string = track_string[:-3] + ") and tracks.artist_id=artists.id and albums.id=tracks.album_id"
        sql = """
            SELECT
                tracks.name, tracks.duration, tracks.numalbum, tracks.license, tracks.album_id, tracks.artist_id, artists.name, albums.name, tracks.uid, tracks.id3genre, tracks.id
            FROM
                tracks, artists, albums
            WHERE 
                %s
            """ % track_string

        ret = self.query(sql)

        tracks=[]
        for track in ret:
            tr = Track()
            tr.name = track[0]
            tr.duration = track[1]
            tr.numalbum = track[2]
            tr.license = track[3]
            tr.album_id = track[4]
            tr.artist_id = track[5]
            tr.artist_name = track[6]
            tr.album_name = track[7]
            tr.uid = track[8]
            tr.id3genre = track[9]
            tr.id = track[10]
            tr.stream = "http://api.jamendo.com/get2/stream/track/redirect/?id=%i&streamencoding=%s" % (track[10], self.parent.settings.get_value("JAMENDO", "format_stream", "mp31"))
            self.check_cache(tr)
            tracks.append(tr)
        return tracks

    ## Get trackinfos for a single track
    # @return dictionary
    # @param self The Object pointer
    # @param trackid a track-id as string or int
    def get_trackinfos2(self, trackid):
        sql = """
            SELECT
                tracks.name, tracks.duration, tracks.numalbum, tracks.license, tracks.album_id, tracks.artist_id, artists.name, albums.name, tracks.uid, tracks.id3genre, tracks.id
            FROM
                tracks, albums, artists
            WHERE
                tracks.id=%s and albums.id=tracks.album_id and artists.id=tracks.artist_id
            """ % str(trackid)
        ret = self.query(sql)
        if ret == []:
            return []
        ret = ret[0]
        tr = Track()
        tr.name = ret[0]
        tr.duration = ret[1]
        tr.numalbum = ret[2]
        tr.license = ret[3]
        tr.album_id = ret[4]
        tr.artist_id = ret[5]
        tr.artist_name = ret[6]
        tr.album_name = ret[7]
        tr.uid = ret[8]
        tr.id3genre = ret[9]
        tr.id = ret[10]
        tr.stream = "http://api.jamendo.com/get2/stream/track/redirect/?id=%i&streamencoding=%s" % (ret[10], self.parent.settings.get_value("JAMENDO", "format_stream", "mp31"))
        self.check_cache(tr)
#        tracks.append(tr)
        return tr

  
        
#http://api.jamendo.com/get2/track_name+track_duration+track_url+license_url+album_id+album_name+artist_id+artist_idstr+artist_name/track/jsonpretty/album_artist/

    ## Get all artist's tracks
    # @return dictionary
    # @param self The Object pointer
    # @param id an artist's id as string or int
    def artisttracks(self, id):
        sql = """
            SELECT
                tracks.name, tracks.duration, tracks.numalbum, tracks.license, tracks.album_id, tracks.artist_id, artists.name, albums.name, tracks.uid, tracks.id3genre, tracks.id
            FROM
                tracks, albums, artists
            WHERE
                tracks.album_id=albums.id and tracks.artist_id=%s and albums.artist_id=%s and artists.id=tracks.artist_id
            """ % (str(id), str(id))
        ret = self.query(sql)                
        tracks=[]
        for track in ret:
            tr = Track()
            tr.name = track[0]
            tr.duration = track[1]
            tr.numalbum = track[2]
            tr.license = track[3]
            tr.album_id = track[4]
            tr.artist_id = track[5]
            tr.artist_name = track[6]
            tr.album_name = track[7]
            tr.uid = track[8]
            tr.id3genre = track[9]
            tr.id = track[10]
            tr.stream = "http://api.jamendo.com/get2/stream/track/redirect/?id=%i&streamencoding=%s" % (track[10], self.parent.settings.get_value("JAMENDO", "format_stream", "mp31"))
            self.check_cache(tr)
            tracks.append(tr)
        return tracks

    ## get all tracks of an album
    # @return dictionary
    # @param self The Object pointer
    # @param id an album's id
    def albumtracks(self, id):
        sql = """
            SELECT
                tracks.name, tracks.duration, tracks.numalbum, tracks.license, tracks.album_id, tracks.artist_id, artists.name, albums.name, tracks.uid, tracks.id3genre, tracks.id
            FROM
                tracks, albums, artists
            WHERE
                tracks.album_id=%s and albums.id=%s and artists.id=albums.artist_id
            """ % (str(id), str(id))
        ret = self.query(sql)
        tracks=[]
        for track in ret:
            tr = Track()
            tr.name = track[0]
            tr.duration = track[1]
            tr.numalbum = track[2]
            tr.license = track[3]
            tr.album_id = track[4]
            tr.artist_id = track[5]
            tr.artist_name = track[6]
            tr.album_name = track[7]
            tr.uid = track[8]
            tr.id3genre = track[9]
            tr.id = track[10]
            tr.stream = "http://api.jamendo.com/get2/stream/track/redirect/?id=%i&streamencoding=%s" % (track[10], self.parent.settings.get_value("JAMENDO", "format_stream", "mp31"))
            self.check_cache(tr)
            tracks.append(tr)
        return tracks

    ## search tags
    # @return dictionary
    # @param self The Object pointer
    # @param string a string to search for
    def Search_tag(self, string):
    
        sql = """
            SELECT
                albums.name, albums.id, artists.name, artists.id
            FROM
                albums, artists, tags
            WHERE
                tags.idstr='""" + string + """' and albums.id=tags.album_id LIMIT """ + str(self.parent.settings.get_value("PERFORMANCE", "db_search_limit"))
        ret = self.query(sql)
        tags = {}
        counter = 0
        for tag in ret:
            tags[counter] = {}
            tags[counter]['album_name'] = tag[0]
            tags[counter]['album_id'] = tag[1]
            tags[counter]['artist_name'] = tag[2]
            tags[counter]['artist_id'] = tag[3]
            counter += 1
        print tags
        return tags


    ## Search tracks
    # @return dictionary
    # @param self The Object pointer
    # @param string a string to search for
    def search_track(self, string):
    
        sql = """
            SELECT
                tracks.name, tracks.duration, tracks.numalbum, tracks.id, tracks.license, tracks.id3genre, albums.id, albums.name, artists.id, artists.name, tracks.uid
            FROM
                tracks, albums, artists
            WHERE
                tracks.name LIKE '%""" + string + """%' and tracks.album_id=albums.id and albums.artist_id=artists.id LIMIT """ + str(self.parent.settings.get_value("PERFORMANCE", "db_search_limit"))
        ret = self.query(sql)
        tracks=[]
        for track in ret:
            tr = Track()
            tr.name = track[0]
            tr.duration = track[1]
            tr.numalbum = track[2]
            tr.id = track[3]
            tr.license = track[4]
            tr.id3genre = track[5]
            tr.album_id = track[6]
            tr.album_name = track[7]
            tr.artist_id = track[8]
            tr.artist_name = track[9]
            tr.uid = track[10]
            tr.stream = "http://api.jamendo.com/get2/stream/track/redirect/?id=%i&streamencoding=%s" % (track[3], self.parent.settings.get_value("JAMENDO", "format_stream", "mp31"))
            self.check_cache(tr)
            tracks.append(tr)
        return tracks

    ## Search artists
    # @return dictionary
    # @param self The Object pointer
    # @param string a string to search for
    def search_artist(self, string):
        sql = """
            SELECT
                artists.name, artists.id
            FROM
                artists
            WHERE
                artists.name LIKE '%""" + string + """%' LIMIT """ + str(self.parent.settings.get_value("PERFORMANCE", "db_search_limit"))
        ret = self.query(sql)
        artists = {}
        counter = 0
        for artist in ret:
            artists[counter] = {}
            artists[counter]['artist_name'] = artist[0]
            artists[counter]['artist_id'] = artist[1]
#            artists[counter]['album_dispname'] = artist[2]
#            artists[counter]['album_id'] = artist[3]
            counter += 1
        return artists

    ## Search albums
    # @return dictionary
    # @param self The Object pointer
    # @param string a string to search for 
    def search_album(self, string):
    
        sql = """
            SELECT
                albums.name, albums.id, artists.name, artists.id
            FROM
                albums, artists
            WHERE
                albums.name LIKE '%""" + string + """%' and albums.artist_id=artists.id LIMIT """ + str(self.parent.settings.get_value("PERFORMANCE", "db_search_limit"))
        ret = self.query(sql)
        albums = {}
        counter = 0
        for album in ret:
            albums[counter] = {}
            albums[counter]['album_name'] = album[0]
            albums[counter]['album_id'] = album[1]
            albums[counter]['artist_name'] = album[2]
            albums[counter]['artist_id'] = album[3]
            counter += 1
        return albums

    ## Get an album's tags
    # @return list
    # @param self The Object pointer
    # @param id an album to search for as string or int
    def gettags(self, id):
        
        sql = """
            SELECT
                tags
            FROM
                albums
            WHERE
                id=%s
            """ % str(id)
        ret = self.query(sql)
        return ret

#    def albuminfos(self, id):
#        strQuery = "track/id/album/data/json/ID?ali=full&ari=full+object&tri=full&item_o=track_no_asc&showhidden=1&shownotmod=1"
#        strQuery = strQuery.replace("ID", str(id))
#        ret = self.__queryold__(strQuery)
#        return ret







#    def albumtracks(self, id): 		
#        ret = self.get("track_id+track_name+track_stream+track_duration+album_name", "track", "album_track/?album_id=" + str(id)+"&streamencoding=ogg2") 		
#        return ret
#        

#    def artistalbums(self, idstr):
#        ret = self.get("album_id+album_name+album_playlist", "artist", "?idstr=" + idstr + "&ali=full")
#        print ret
#        return ret

#    def artistlist(self):
#        ret =  self.get("id+idstr+name", "artist", "?artist_hasalbums&n=50")
#        return ret


