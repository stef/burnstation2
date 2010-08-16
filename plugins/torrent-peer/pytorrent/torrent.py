from connection import Command, TorrentGetCommand, TorrentGetFileCommand, TorrentCommand
import os.path

STOPPED = "stopped"
CHECKING = "checking"
DOWNLOADING = "downloading"
SEEDING = "seeding"

def static_property(key):
    return property(lambda x: x._properties.get(key))

def dynamic_property(key):
    def query(self):
        command = TorrentGetCommand(key, self._id)
        torrent = self._connection.execute(command)
        return torrent.get(key)
    return property(query)

def dynamic_file_property(key):
    def query(self):
        command = TorrentGetFileCommand(self._torrent._id, self._id)
        file = self._connection.execute(command)
        return file.get(key)
    return property(query) 

class File(object):
    def __init__(self, torrent, id, data):
        self._client = torrent._client
        self._connection = torrent._connection
        self._torrent = torrent
        self._id = id
        self._name = data["name"]
        self._properties = data
        
    def _get_finished(self):
        return self.downloaded_size == self.size
        
    def _get_wanted(self):
        command = TorrentGetCommand("wanted", self._torrent._id)
        torrent = self._connection.execute(command)
        return torrent["wanted"][self._id] == 1
    
    def _set_wanted(self, value):
        if value:
            field = "files-wanted"
        else:
            field = "files-unwanted"
        command = TorrentCommand("torrent-set", self._torrent._id)
        command[field] = [self._id]
        self._connection.execute(command)
    
    def _get_path(self):
        return os.path.join(self._client.download_dir, self._name)
    
    def __str__(self):
        return self._name
    
    id = property(lambda x: x._id)
    name = property(lambda x: x._name)
    path = property(_get_path)
    finished = property(_get_finished)
    wanted = property(_get_wanted, _set_wanted)
    size = static_property("length")
    downloaded_size = dynamic_file_property("bytesCompleted")
    
class Torrent(object):
    static_fields = ["id", "name", "dateAdded", 
                     "announceResponse", "announceURL",
                    "comment", "creator",
                     "dateCreated", "hashString", 
                     "files", "totalSize"]
    
    def __init__(self, client, data):
        self._client = client
        self._connection = client._connection
        self._id = data["id"]
        self._name = data["name"]
        self._properties = data
        self._files = []
        for id, file in enumerate(data["files"]):
            self._files.append(File(self, id, file))
        
    def remove(self):
        command = TorrentCommand("torrent-remove", self._id)
        self._connection.execute(command)
        self._id = None
        self._name = None
        self._properties = {}
        
    def start(self):
        command = TorrentCommand("torrent-start", self._id)
        self._connection.execute(command)
        
    def stop(self):
        command = TorrentCommand("torrent-stop", self._id)
        self._connection.execute(command) 
       
    def _get_downloaded_size(self):
        command = TorrentGetCommand("files", self._id)
        torrent = self._connection.execute(command)
        size = 0
        for file in torrent["files"]:
            size += file["bytesCompleted"]
        return size
        
    def _get_status(self):
        command = TorrentGetCommand("status", self._id)
        status = self._connection.execute(command)["status"]
        if status & 1 or status & 2:
            return CHECKING
        elif status & 4:
            return DOWNLOADING
        elif status & 8:
            return SEEDING
        else:
            return STOPPED
        
    def _get_finished(self):
        for file in self.files:
            if not file.finished:
                return False
        return True
    
    def __str__(self):
        return self._name
    
    id = property(lambda x: x._id)
    name = property(lambda x: x._name)
    files = property(lambda x: x._files)
    file = property(lambda x: x._files[0])
    status = property(_get_status)
    finished= property(_get_finished)
    
    date_added = static_property("dateAdded")
    announce_response = static_property("announceResponse")
    announce_url = static_property("announceURL")
    comment = static_property("comment")
    creator = static_property("creator")
    date_created = static_property("dateCreated")
    hash = static_property("hashString")
    size = static_property("totalSize")
    downloaded_size = property(_get_downloaded_size)
    
    eta = dynamic_property("eta")
    leechers = dynamic_property("leechers")
    peers = dynamic_property("peers")
    peers_connected = dynamic_property("peersConnected")
    peers_getting = dynamic_property("peersGettingFromUs")
    peers_sending = dynamic_property("peersSendingToUs")
    download_rate = dynamic_property("rateDownload")
    upload_rate = dynamic_property("rateUpload")
    seeders = dynamic_property("seeders")
    weebseeds_sending = dynamic_property("webseedsSendingToUs")
    
    
