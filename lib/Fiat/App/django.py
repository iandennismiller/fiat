from Fiat.Base.App import BaseApp
from Fiat.Core.Utils import loggable
import os

class django(BaseApp):

    def __init__(self, Instance, config_dict):
        self.meta = {
            "type": "django",
            #"version": Instance.Project.Exec.config['osticket_version'],
            }
        
        self.config_parse = {
            'regexp': r'%s\s*=\s*\'(.*?)\'',
            'db_host': r'DATABASE_HOST',
            'db_user': r'DATABASE_USER',
            'db_pass': r'DATABASE_PASSWORD',
            'db_name': r'DATABASE_NAME',
        }

        super(django, self).__init__(Instance, config_dict)

        #self.Exec.register_task(name="django.install.start", args=0, help="install osticket", function=self.install_start)
        #self.Exec.register_task(name="osticket.install.finish", args=0, help="finish installing osticket", function=self.install_finish)

"""
def post_deploy():
	import Fiat.Task.deploy

	install_path = Context().host["install_path"]
	westhost_username = Context().host["westhost_username"]

#	Fiat.Task.deploy.sshrun("cp %s/apache/django_apache.conf /etc/httpd/conf.d/%s.conf" % (install_path, westhost_username))

def spinup():
	import Fiat.Task.deploy

	install_path = Context().host["install_path"]

	Fiat.Task.deploy.sshrun("/%s/apache/django_restart.sh" % install_path)

"""