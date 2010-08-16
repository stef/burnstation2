from daemon import Daemon
from connection import TransmissionConnection, Command, TorrentGetCommand, TorrentGetListCommand
from torrent import Torrent
import base64
import urllib2
    
def session_property(key):
    return property(lambda x: x._session.get(key))

class TorrentClient(object):
    def __init__(self, hostname=None, port=9090):
        self.daemon = None
        if not hostname:
            self.daemon = Daemon(["transmission-daemon", "-f", "-p", str(port)])
            self.daemon.start()
            hostname = "localhost"
        self._connection = TransmissionConnection(hostname, port)
        self._session = self._connection.execute(Command("session-get"))
        
    def __del__(self):
        if self.daemon:
            self.daemon.stop()
            
    def add_torrent(self, auto=None, metadata=None, filename=None, file=None, url=None):
        if auto:
            if isinstance(auto, str):
                if "://" in auto:
                    data = urllib2.urlopen(auto).read()
                else:
                    data = open(auto, "r").read()
            elif hasattr(auto, "read"):
                data = auto.read()
            elif hasattr(auto, "content"):
                data = auto.content
            else:
                raise AttributeError()
        else:
            if metadata:
                data = metadata
            elif filename:
                data = open(filename, "r").read()
            elif url:
                data = urllib2.urlopen(url).read()
            elif file:
                data = file.read()

        data = base64.encodestring(data)
        
        command = Command("torrent-add")
        command["metainfo"] = data
        command["paused"] = True
            
        torrent = self._connection.execute(command)
        return self.get_torrent(torrent["torrent-added"]["id"])
            
    def get_torrent(self, id):
        command = TorrentGetCommand(Torrent.static_fields, id)
        torrent = self._connection.execute(command)
        return Torrent(self, torrent)

    def _get_torrents(self):
        command = TorrentGetListCommand(Torrent.static_fields)
        list = self._connection.execute(command)
        torrent_list = map(lambda t: Torrent(self, t), list)
        return torrent_list
    
    download_dir = session_property("download-dir")
    torrents = property(_get_torrents)
