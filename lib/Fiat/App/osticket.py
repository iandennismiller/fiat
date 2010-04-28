from Fiat.Base.App import BaseApp
from Fiat.Core.Utils import loggable
import os

class osticket(BaseApp):

    def __init__(self, Instance, config_dict):
        self.meta = {
            "type": "osticket",
            "version": Instance.Project.Exec.config['osticket_version'],
            }
        
        self.config_parse = {
            'regexp': r'\s*define\(\'%s\'\s*,\s*\'(.*?)\'\);',
            'db_host': r'DBHOST',
            'db_user': r'DBUSER',
            'db_pass': r'DBPASS',
            'db_name': r'DBNAME',
        }

        super(osticket, self).__init__(Instance, config_dict)

        self.Exec.register_task(name="osticket.install.start", args=0, help="install osticket", function=self.install_start)
        self.Exec.register_task(name="osticket.install.finish", args=0, help="finish installing osticket", function=self.install_finish)
    
    @loggable
    def install_start(self):
        self.DB.create_db()

        install_path = os.path.join(self.Project.config['make_path'], "var", "osticket")
        
        self.Exec.Utils.unpack_tarball("osticket", self.Exec.config["osticket_version"], install_path)

        self.Project.clean()
        self.Project.build()
        
        self.Exec.Utils.cp_build("var/osticket/upload/ostconfig.php", "ticket")
        
        self.Project.deploy()
        
        # set permissions for config 
        ssh_cmd = "chmod 666 %(path)s/ticket/ostconfig.php" % {"path": self.Instance.Host.config["install_path"]}
        
        self.Instance.Host.ssh(cmd=ssh_cmd)
    
    def install_finish(self):
        pass

    @loggable
    def build(self, dest="ticket"):
        self.Exec.Utils.cp_build("var/osticket/upload", dest)
