from Fiat.Base.App import BaseApp
from Fiat.Core.Utils import loggable
import os

class phpwiki(BaseApp):

    def __init__(self, Instance, config_dict):
        self.meta = {
            "type": "phpwiki",
            "version": Instance.Project.Exec.config['phpwiki_version'],
            }
        
        self.config_parse = {
            'regexp': r'\s*\$%s\s*=\s*\'(.*?)\'\;',
            'db_host': r'mysql_server',
            'db_user': r'mysql_user',
            'db_pass': r'mysql_pwd',
            'db_name': r'mysql_db',
        }
    
        super(phpwiki, self).__init__(Instance, config_dict)

        self.Exec.register_task(name="phpwiki.install", args=0, help="install phpwiki", function=self.install)

    @loggable
    def install(self):
        self.DB.create_db()
        
        install_path = os.path.join(self.Project.config['make_path'], "var", "phpwiki")
        
        self.Exec.Utils.unpack_tarball("phpwiki", self.Exec.config["phpwiki_version"], install_path)

        self.Project.clean()
        self.Project.build()
        self.Project.deploy()
        
        local_sql_path = os.path.join(install_path, "schemas")
        remote_temp_path = self.Instance.Host.config['scratch_path']

        # this is going to use the mysql schema by default...
        self.DB.deploy_and_import(local_sql_path, "schema.mysql", remote_temp_path)
        
    @loggable
    def build(self, dest="wiki"):
        self.Exec.Utils.cp_build("var/phpwiki", dest)
    