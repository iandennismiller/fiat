from Fiat.DB.mysql import mysql
from Fiat.Base.Host import BaseHost
from Fiat.Core.Utils import loggable

class local(BaseHost):
    
    def __init__(self, Instance, project_config):

        super(local, self).__init__(Instance)
        
    @loggable
    def cmsms_permissions(self, subdir = "cms"):
    	ssh_cmd = """
    	chgrp web %(path)s/tmp/cache %(path)s/tmp/templates_c %(path)s/uploads %(path)s/uploads/images; \
    	chmod 775 %(path)s/tmp/cache %(path)s/tmp/templates_c %(path)s/uploads %(path)s/uploads/images; \
    	chmod 775 %(path)s/tmp; \
    	chgrp web %(path)s/admin/*.php;
    	""" % { 'path': "/home/public/%s" % subdir }

        self.ssh(cmd=ssh_cmd)

