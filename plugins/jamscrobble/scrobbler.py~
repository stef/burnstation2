"""
A pure-python library to assist sending data to AudioScrobbler (the LastFM
backend)
"""
import urllib, urllib2
from time import mktime
from datetime import datetime, timedelta
try:
    from hashlib import md5
except ImportError:
    from md5 import md5

class Scrobbler():
    """
    Class for scrobbling music to last.fm.
    """
    def __init__(self, client=('tst','0.1'), hs_delay=0, max_cache=5, protocol_version='1.2.1'):
        """
        Initialize Scrobbler Object

        Keyword arguments:
        client              -> tuple: (client-id, client-version), client information, default ('tst','0.1') (see http://www.audioscrobbler.net/development/protocol/ for more info)
        hs_delay            -> int, wait this many seconds until next handshake, default 0
        max_cache           -> int, keep only this many songs in the cache, default 5
        protocol_verison    -> string, verison of the audioscrobbler protocol, default '1.2.1' (see http://www.audioscrobbler.net/development/protocol/)
        """
        self.ClientId   = client[0]
        self.ClientVersion= client[1]

        self.SessionId  = None
        self.PostUrl    = None
        self.NowUrl     = None
        self.HardFails  = 0
        self.LastHs     = None # Last handshake time
        self.HsDelay    = hs_delay # wait this many seconds until next handshake
        self.Cache = []
        self.CacheLength = 0 # number of songs in cache
        self.MaxCache   = max_cache # keep only this many songs in the cache
        self.ProtocolVersion = protocol_version

    def login(self, user, password, in_md5=False):
        """Authencitate with AS (The Handshake)

        user        -> string, audioscrobbler username
        password    -> string, plain text or md5 hash of user password
        in_md5         -> boolean, if password is a md5 hash set it True, default False
        """

        if self.LastHs is not None:
            next_allowed_hs = self.LastHs + timedelta(seconds=self.HsDelay)
            if datetime.now() < next_allowed_hs:
                delta = next_allowed_hs - datetime.now()
                raise self.ProtocolError("""Please wait another %d seconds until next handshake
                        (login) attempt.""" % delta.seconds)

        self.LastHs = datetime.now()

        tstamp = int(mktime(datetime.now().timetuple()))
        url    = "http://postaudioscrobbler.jamendo.com/"
        if in_md5:
            pwhash = password
        else: 
            pwhash = md5(password).hexdigest()
        token  = md5( "%s%d" % (pwhash, int(tstamp))).hexdigest()
        values = {
         'hs': 'true',
         'p': self.ProtocolVersion,
         'c': self.ClientId,
         'v': self.ClientVersion,
         'u': user,
         't': tstamp,
         'a': token
         }
        data = urllib.urlencode(values)
        req = urllib2.Request("%s?%s" % (url, data) )
        response = urllib2.urlopen(req)
        result = response.read()
        lines = result.split('\n')

        if lines[0] == 'BADAUTH':
            raise self.AuthError('Bad username/password')

        elif lines[0] == 'BANNED':
            raise Exception('''This client-version was banned by Audioscrobbler. Please
                        contact the author of this module!''')
        elif lines[0] == 'BADTIME':
            raise ValueError('''Your system time is out of sync with Audioscrobbler.
                        Consider using an NTP-client to keep you system time in sync.''')
        elif lines[0].startswith('FAILED'):
            self.__handle_hard_error()
            raise self.BackendError("Authencitation with AS failed. Reason: %s" %
                lines[0])

        elif lines[0] == 'OK':
            # wooooooohooooooo. We made it!
            self.SessionId = lines[1]
            self.NowUrl    = lines[2]
            self.PostUrl   = lines[3]
            self.HardFails = 0

        else:
            # some hard error
            self.___handle_hard_error()



    def now_playing(self, artist, track, album="", length="", trackno="", mbid=""):
        """
        Tells audioscrobbler what is currently running in your player. This won't
        affect the user-profile on last.fm. To do submissions, use the "submit"
        method

        artist   -> string, the artist name
        track    -> string, the track name
        album    -> string, the album name, default empty string
        length   -> int, the song length in seconds, default empty
        trackno  -> int, the track number, default empty
        mbid     -> string, the MusicBrainz Track ID, default empty string

        return True on success, False on failure
        """

        if self.SessionId is None:
            raise self.AuthError("Please 'login()' first. (No session available)")

        if self.NowUrl is None:
            raise self.PostError("Unable to post data. Nowplaying URL [NowUrl] was empty!")

        if length != "" and type(length) != type(1):
            raise TypeError("length should be of type int")

        if trackno != "" and type(trackno) != type(1):
            raise TypeError("trackno should be of type int")

        values = {'s': self.SessionId,
                'a': unicode(artist).encode('utf-8'),
                't': unicode(track).encode('utf-8'),
                'b': unicode(album).encode('utf-8'),
                'l': length,
                'n': trackno,
                'm': mbid }

        data = urllib.urlencode(values)
        req = urllib2.Request(self.NowUrl, data)
        response = urllib2.urlopen(req)
        result = response.read()

        if result.strip() == "OK":
            return True
        elif result.strip() == "BADSESSION" :
            raise self.SessionError('Invalid session')
        else:
            #return False
            raise Exception('Error during sending info to last.fm')
        
    def submit(self, artist, track, time, source='P', rating="", length="", album="",
              trackno="", mbid="", autoflush=False):
        """
        Append a song to the submission cache. Use 'flush()' to send the cache to
        AS. You can also set "autoflush" to True.

        From the Audioscrobbler protocol docs:
        ---------------------------------------------------------------------------

        The client should monitor the user's interaction with the music playing
        service to whatever extent the service allows. In order to qualify for
        submission all of the following criteria must be met:

        1. The track must be submitted once it has finished playing. Whether it has
           finished playing naturally or has been manually stopped by the user is
           irrelevant.
        2. The track must have been played for a duration of at least 240 seconds or
           half the track's total length, whichever comes first. Skipping or pausing
           the track is irrelevant as long as the appropriate amount has been played.
        3. The total playback time for the track must be more than 30 seconds. Do
           not submit tracks shorter than this.
        4. Unless the client has been specially configured, it should not attempt to
           interpret filename information to obtain metadata instead of tags (ID3,
           etc).

        artist  -> string, artist name
        track   -> string, track name
        time    -> int, time the track *started* playing in the UTC timezone (see
                       datetime.utcnow()).

                      Example: int(time.mktime(datetime.utcnow()))
                      default empty
        source  -> string, source of the track. One of:
                      'P': Chosen by the user
                      'R': Non-personalised broadcast (e.g. Shoutcast, BBC Radio 1)
                      'E': Personalised recommendation except Last.fm (e.g.
                           Pandora, Launchcast)
                      'L': Last.fm (any mode). In this case, the 5-digit Last.fm
                           recommendation key must be appended to this source ID to
                           prove the validity of the submission (for example,
                           "L1b48a").
                      'U': Source unknown
                      default 'P'
        rating  -> string, the rating of the song. One of:
                      'L': Love (on any mode if the user has manually loved the
                           track)
                      'B': Ban (only if source=L)
                      'S': Skip (only if source=L)
                      '':  Not applicable
                      default empty string
        length  -> int, the song length in seconds, default empty
        album   -> string, the album name, default empty string
        trackno -> int, the track number, default empty
        mbid    -> string, MusicBrainz Track ID, default empty string
        autoflush -> boolean, automatically flush the cache to AS, default False
        """


        source = source.upper()
        rating = rating.upper()

        if source == 'L' and (rating == 'B' or rating == 'S'):
            raise self.ProtocolError("""You can only use rating 'B' or 'S' on source 'L'.
                See the docs!""")

        if source == 'P' and length == '':
            raise self.ProtocolError("""Song length must be specified when using 'P' as
                source!""")

        if type(time) != type(1):
            raise ValueError("""The time parameter must be of type int (unix
                timestamp). Instead it was %s""" % time)

        self.__add_to_cache(
            { 'a': unicode(artist).encode('utf-8'),
            't': unicode(track).encode('utf-8'),
            'i': time,
            'o': source,
            'r': rating,
            'l': length,
            'b': unicode(album).encode('utf-8'),
            'n': trackno,
            'm': mbid
            }
         )

        if autoflush or self.CacheLength >= self.MaxCache:
            self.flush()

    def flush(self):
        """ Sends the cached songs to AS. """

        if self.SessionId is None:
            raise self.AuthError("Please 'login()' first. (No session available)")

        if self.PostUrl is None:
            raise self.PostError("Unable to post data. Post URL [PostUrl] was empty!")

        self.__load_cache()

        values = {}

        for i, item in enumerate(self.Cache):
            for key in item:
                values[key + "[%d]" % i] = item[key]

        values['s'] = self.SessionId

        data = urllib.urlencode(values)
        req = urllib2.Request(self.PostUrl, data)
        response = urllib2.urlopen(req)
        result = response.read()
        lines = result.split('\n')

        if lines[0] == "OK":
            self.Cache = []
            # self.__clean_cache()
            return True
        elif lines[0] == "BADSESSION" :
            raise self.SessionError('Invalid session')
        elif lines[0].startswith('FAILED'):
            self.__handle_hard_error()
            raise self.BackendError("Authencitation with AS failed. Reason: %s" %
            lines[0])
        else:
            # some hard error
            self.__handle_hard_error()
            raise Exception('Error during submiting songs to AS')
            #return False    

    def __add_to_cache(self, track):
        """ Add track to cache. """
        self.Cache.append(track)
        self.CacheLength += 1

    def __load_cache(self):
        """ Load song's cache into self.Cache"""
        self.CacheLength=len(self.Cache)

    def __handle_hard_error(self):
        """Handles hard errors."""

        if self.HsDelay == 0:
            self.HsDelay = 60
        elif self.HsDelay < 120*60:
            self.HsDelay *= 2
        if self.HsDelay > 120*60:
            self.HsDelay = 120*60

        self.HardFails += 1
        if self.HardFails == 3:
            self.SessionId = None

    class BackendError(Exception):
        """Raised if the AS backend does something funny"""
        pass
    class AuthError(Exception):
       """Raised on authencitation errors"""
       pass
    class PostError(Exception):
       """Raised if something goes wrong when posting data to AS"""
       pass
    class SessionError(Exception):
       """Raised when problems with the session exist"""
       pass
    class ProtocolError(Exception):
       """Raised on general Protocol errors"""
       pass

