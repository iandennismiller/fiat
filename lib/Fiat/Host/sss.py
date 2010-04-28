from Fiat.DB.mysql import mysql
from Fiat.Base.Host import BaseHost
from Fiat.Core.Utils import loggable

class sss(BaseHost):
    
    def __init__(self, Instance, project_config):

        super(sss, self).__init__(Instance)
        
        if 'install_path' in project_config:
            install_path = project_config['install_path']
        else:
            install_path = "/home/saperea/%s" % self.Project.meta['project']

        if 'ssh_port' in project_config:
            ssh_port = project_config["ssh_port"]
        else:
            ssh_port = 22

        self.config = {
            "ssh_user": "saperea",
            "ssh_host": project_config["ssh_host"],
            "ssh_port": ssh_port,
            "scratch_path": "/home/saperea/tmp",
            "install_path": install_path,
        }
