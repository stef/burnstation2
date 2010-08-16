#!/usr/bin/env python
import logging
from time import time
from modules.functions import VERSION
logging.basicConfig(level=logging.ERROR)
#from threading import Thread

from modules.clWidgets import MyLinkButton

try:
    from scrobbler import Scrobbler
except:
    logging.error('scrobbler not found')
    raise

try:
    import gtk
except:
    logging.error('gtk not found')
    raise

try:
    # for python 2.6
    from hashlib import md5
except ImportError:
    from md5 import md5

from threading import Thread
def threaded(f):
    def wrapper(*args, **kwargs):
        t = Thread(target=f, args=args, kwargs=kwargs)
        t.start()
    return wrapper

#@threaded
class main():
    ## The Constructor
    # @param self Object pointer
    # @param pyjama Reference to the pyjama object
    def __init__(self, pyjama):
        self.pyjama = pyjama
        self.Events = self.pyjama.Events

        self.Events.connect_event("nowplaying", self.ev_nowplaying)
        self.Events.connect_event('player-status', self.ev_player_status)

        self.pyjama.preferences.register_plugin("LastFM", self.create_preferences, self.save_preferences)

        # login to last.fm
        self.scrobbler = None

        if self.get_session():
            logging.debug('last.fm plugin loaded')
        else:
            logging.debug('last.fm plugin loaded but scrobbling isn\'t available')
        
            #raise

        self.last_scrobbled = None

#    def get_session(self):
#        thr = Thread(target = self.get_session_do, args = ())
#        thr.start()
    @threaded
    def get_session(self):
        if self.pyjama.settings.get_value('LASTFM','SCROBBLING'):

            login=str(self.pyjama.settings.get_value('LASTFM','LOGIN'))
            password=str(self.pyjama.settings.get_value('LASTFM','PASS'))

            try:
                # pyjama has own last.fm clien id 'pyj'
                self.scrobbler=Scrobbler(client=('pyj',VERSION))
                self.scrobbler.login(login, password)
            except Exception, e:
                logging.error(e)
                self.scrobbler=None
                return False
            else:
                #self.logged=True
                return True
        else:
            return False


#    def ev_nowplaying(self,track):
#        thr = Thread(target = self.ev_nowplaying_do, args = (track,))
#        thr.start()
    @threaded
    def ev_nowplaying(self, track):
        """ for sending now playing notification to last.fm """
        logging.debug('nowplaying: %s' % track)

        if self.scrobbler is None:
            self.get_session()

        if self.pyjama.settings.get_value('LASTFM','SCROBBLING') and self.scrobbler is not None:
            try:
                self.scrobbler.now_playing(track.artist_name, track.name, album=track.album_name, length=track.duration)
            except (self.scrobbler.SessionError, self.scrobbler.AuthError), e:
                logging.error('can\'t send nowplaying info to last.fm')
                self.get_session()
            except Exception, e:
                logging.error(e)
            else:
                logging.info('nowplaying %s - %s send to last.fm' % (track.artist_name, track.name))
                self.pyjama.setInfo("lastfm - nowplaying send")

        else:
            logging.debug('nowplaying info doesn\'t send - scrobbling is off')

#    def ev_scrobble(self,track):
#        thr = Thread(target = self.ev_scrobble_do, args = (track,))
#        thr.start()
    @threaded
    def ev_scrobble(self,track):
        """ for scrobbling to last.fm """
        logging.debug('track: %s' % track)

        if self.scrobbler is None:
            self.get_session()

        if self.pyjama.settings.get_value('LASTFM','SCROBBLING') and self.scrobbler is not None:

            try:
                self.scrobbler.submit(track.artist_name,track.name,int(time()),length=track.duration)
                self.scrobbler.flush()
            except (self.scrobbler.SessionError, self.scrobbler.AuthError), e:
                logging.warn('last.fm plugin: can\'t scrobble song')
                self.get_session()
            except Exception, e:
                logging.error(e)
                #raise
            else:
                logging.info('song %s - %s send to last.fm' % (track.artist_name, track.name))
                self.pyjama.setInfo("lastfm - scrobbled")

        else:
            logging.debug('song doesn\' scrobbled - scrobbling is off')
    @threaded
    def ev_player_status(self, status, cursec = None, duration = None):
        if status == "playing":
            percentage =  (1.0 / duration) * cursec
            if percentage > 1: percentage = 0

            # scrobble test
            if (percentage > 0.5 or (cursec > 240 and cursec <= duration)) and duration > 30 and self.pyjama.player.cur_playing.id != self.last_scrobbled:
                #print "send this to last.fm ;) <<<< ", self.cursec, '/',  self.duration
                self.ev_scrobble(self.pyjama.player.cur_playing)
                self.last_scrobbled = self.pyjama.player.cur_playing.id

    def create_preferences(self):
        login_value=self.pyjama.settings.get_value('LASTFM','LOGIN','login', str)
        pass_value=self.pyjama.settings.get_value('LASTFM','PASS', 'password', str)
        scrobble_value=self.pyjama.settings.get_value('LASTFM','SCROBBLING', False)

        logging.debug('settings on start: %s:%s %s' % (login_value,pass_value,str(scrobble_value)))
        
        vbox = gtk.VBox()

        hbox = gtk.HBox()
        vbox.pack_start(hbox, False, True, 10)
        hbox.show()

        hbox2 = gtk.HBox()
        vbox.pack_start(hbox2, False, True, 10)
        hbox2.show()


        # scrobble check button
        self.check = gtk.CheckButton(_("Scrobble to last.fm?"))
        self.check.set_active(scrobble_value)
        vbox.pack_start(self.check, False, True, 10)

        # login field
        llabel=gtk.Label(_('Login:'))

        llabel.set_property('has-tooltip', True)
        llabel.set_property('tooltip-text', 'Your login name')
        hbox.pack_start(llabel, False, True, 10)

        if login_value != "login":
            lbl = MyLinkButton("http://last.fm/user/%s"  % login_value, "Open my page @lastfm")
            lbl.show()
            lbl.connect("clicked", self.cb_lbl_clicked)
            vbox.pack_end(lbl, False, True ,10)

        self.login = gtk.Entry(max=0)
        self.login.set_text(login_value)
        hbox.pack_end(self.login, False, True, 10)

        # password field
        plabel=gtk.Label(_('Password:'))
        llabel.set_property('tooltip-text', 'Your login password')
        hbox2.pack_start(plabel, False, True, 10)

        self.password = gtk.Entry(max=0)
        self.password.set_text(pass_value)
        self.password.set_visibility(False)

        hbox2.pack_end(self.password, False, True, 10)

        vbox.show_all()
        return vbox

    def save_preferences(self):
        self.pyjama.settings.set_value('LASTFM','LOGIN', self.login.get_text())
        logging.debug('new login: %s' % self.login.get_text())

        self.pyjama.settings.set_value('LASTFM','PASS', self.password.get_text())
        logging.debug('new pass: %s' % self.password.get_text())

        self.pyjama.settings.set_value('LASTFM','SCROBBLING', self.check.get_active())
        logging.debug('new scrobble vaule: %s' % self.check.get_active())


    def cb_lbl_clicked(self, widget):
        self.pyjama.Events.raise_event("open_url", widget.uri, True)
