from Fiat.Context import Context
from Fiat.Base.Webapp import Webapp
from Fiat.Task.build import cp_make_to_build
import os, distutils, shutil

class wakaba(Webapp):

	def __init__(self):
		config_file = os.path.join(Context().env['make_path'], Context().host['wakaba_config'])

		config_parse = {
			'regexp': r'\s*use constant %s \=\> \'(.*?)\';',
			'host': r'SQL_HOST',
			'user': r'SQL_USERNAME',
			'pass': r'SQL_PASSWORD',
			'name': r'SQL_DBNAME',
		}
	
		super(wakaba, self).__init__("wakaba", Context().project['wakaba_version'], config_file, config_parse)

	def get_src(self):
		untarred_into = self.wget_untar()
		
#		shutil.rmtree(os.path.join(untarred_into, "upload/setup"))

	def build(self, subdir = "wakaba"):
 		cp_make_to_build("var/wakaba", subdir)

def get_src(dummy):
	wakaba().get_src()

def mysql_shell(dummy):
	wakaba().mysql_shell()

def init_db(dummy):
	wakaba().init_db()

def deploy_db(dummy):
	wakaba().deploy_db()

def checkin_db(dummy):
	wakaba().checkin_db()

def register():
	Context().register_task(name="wakaba.src", args=0, help="set up wakaba source in var", function=get_src)
	Context().register_task(name="wakaba.mysql", args=0, help="launch mysql shell", function=mysql_shell)
	Context().register_task(name="wakaba.db.init", args=0, help="initialize wakaba database", function=init_db)
	Context().register_task(name="wakaba.db.deploy", args=0, help="deploy wakaba database", function=deploy_db)
	Context().register_task(name="wakaba.db.checkin", args=0, help="check in wakaba database", function=checkin_db)
