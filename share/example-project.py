from Fiat.Base.Instance import BaseInstance
from Fiat.Base.Project import BaseProject

#from Fiat.App.cmsms import cmsms
#from Fiat.App.phpwiki import phpwiki
#from Fiat.App.osticket import osticket

#from Fiat.Host.nfsn import nfsn
#from Fiat.Host.highriseweb import highriseweb
#from Fiat.Host.westhost import westhost

#from Fiat.DB.mysql import mysql
#from Fiat.DB.postgresql import postgresql

class project(BaseProject):

    def setup(self):
        self.meta = {
            "project": "SOMETHING",
            "version": 0.1,
            }

        self.load_instance("live")
        #self.load_instance("stage")
        #self.load_instance("dev")
        
    def main_build(self):
        pass
        #self.ActiveInstance.App["cmsms"].build(dest="cms")
        #self.ActiveInstance.App["phpwiki"].build(dest="wiki")
        #self.ActiveInstance.App["osticket"].build(dest="ticket")

class live(BaseInstance):

    def setup(self):
        nfsn_config = {
            "username": "SOMEUSER"
            }

        #self.load_host("nfsn", nfsn_config)
        
        cmsms_config = {
            "config_filename": "fiat/nfsn/cms/config.php",
            "url": "http://www.example.com/cms",
            "admin_user": "admin",
            "admin_pass": "SOMETHING",
            }
            
        #self.load_app("cmsms", "mysql", cmsms_config)
        
    #def post_deploy(self):
    #    self.Host.cmsms_permissions()
