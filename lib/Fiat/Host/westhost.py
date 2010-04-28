from Fiat.DB.mysql import mysql
from Fiat.Base.Host import BaseHost
from Fiat.Core.Utils import loggable

class westhost(BaseHost):
    
    def __init__(self, Instance, dict):

        self.config = {
            "westhost_username": dict["username"],
            "ssh_user": "username",
            "ssh_host": "hostname.com.whsites.net",
            "ssh_port": 22,
            "scratch_path": "/home/%s/scratch" % dict["username"],
            "install_path": "/home/%s/v1" % dict["username"],
        }
        
        super(westhost, self).__init__(Instance)
