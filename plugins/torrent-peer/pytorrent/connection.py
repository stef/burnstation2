import httplib
import simplejson
import time
import exceptions
import socket

class TransmissionException(exceptions.Exception):
    def __init__(self, command, error):
        self.command = command or ""
        self.error = error or ""
        
    def __str__(self):
        return self.command+" failed: "+self.error

class TransmissionConnection:
    def __init__(self, host, port):
        self._host = host
        self._port = port
        self._httpconn = None
        self._connect()
        
    def _connect(self):  
        for i in range(0, 10):
            try:
                self._httpconn = httplib.HTTPConnection(self._host, self._port)
                self._httpconn.connect()
                return
            except:
                time.sleep(0.5)
            
    def execute(self, command):
        try:
            command_str = str(command)
            self._httpconn.request("POST", "/transmission/rpc", command_str)
            response = self._httpconn.getresponse()
            result_str = response.read()
            result = simplejson.loads(result_str)
            if result["result"] != "success":
                raise TransmissionException(command.method, result["result"])
            else:
                return command.extract_result(result)
        except socket.error:
            self._connect()
            return self.execute(command)            
            
        
class Command:
    def __init__(self, method):
        self.method = method
        self.arguments = {}
    
    def extract_result(self, data):
        return data["arguments"]
    
    def __str__(self):
        map = {}
        map["method"] = self.method
        map["arguments"] = self.arguments
        return simplejson.dumps(map)
    
    def __setitem__(self, k, v):
        self.arguments[k] = v
    
    def __getitem__(self, k):
        return self.arguments[k]
    
class TorrentCommand(Command):
    def __init__(self, method, ids=None):
        Command.__init__(self, method)
        if ids and not isinstance(ids, list):
            ids = [ids]
        self.ids = ids
        
    def __str__(self):
        if self.ids:
            self.arguments["ids"] = self.ids
        return Command.__str__(self)
         
class TorrentGetListCommand(TorrentCommand):
    def __init__(self, fields=[], ids=None):
        TorrentCommand.__init__(self, "torrent-get", ids)

        if not isinstance(fields, list):
            fields = [fields]
        self.fields = fields
        
    def extract_result(self, data):
        return data["arguments"]["torrents"]
    
    def __str__(self):
        self.arguments["fields"] = self.fields
        return TorrentCommand.__str__(self)

class TorrentGetCommand(TorrentGetListCommand):
    def extract_result(self, data):
        return data["arguments"]["torrents"][0]

class TorrentGetFileCommand(TorrentGetListCommand):
    def __init__(self, torrent_id, file_id):
        TorrentGetListCommand.__init__(self, "files", torrent_id)
        self.file_id = file_id
    
    def extract_result(self, data):
        return data["arguments"]["torrents"][0]["files"][self.file_id]
