from Fiat.Core.Utils import loggable
import string, re, sys

class BaseApp(object):

    def __init__(self, Instance, config_dict):
        self.Instance = Instance
        self.Project = Instance.Project
        self.Exec = Instance.Project.Exec
        
        self.Exec.logger.debug("init App '%s' for Instance '%s'" % (self.__class__.__name__, Instance.__class__.__name__))

        self.config = config_dict
        
        db_config = self.load_config()
        self.load_db(self.config["db_type"], db_config)
        
        app_type = self.meta["type"]
        
        self.Exec.register_task(name="%s.db.create" % app_type, args=0, help="create a database", function=self.DB.create_db)
        self.Exec.register_task(name="%s.db.deploy" % app_type, args=0, help="deploy a database", function=self.DB.deploy_db)
        self.Exec.register_task(name="%s.db.checkin" % app_type, args=0, help="check in database", function=self.DB.checkin_database)
        self.Exec.register_task(name="%s.db.shell" % app_type, args=0, help="enter database shell", function=self.DB.shell)
        # db backup (versioning)

    def load_db(self, name, config):
        self.DB = self.Exec.import_class(self, prefix="Fiat.DB", container=name, klass=name, config=config)

    @loggable
    def load_config(self):
        config_filename = self.config["config_filename"]
        
        config_lines = open(config_filename).readlines()
        self.config_contents = string.join(config_lines)

        db_auth = {
            'db_host': self.conf_match(self.config_parse['db_host']),
            'db_user': self.conf_match(self.config_parse['db_user']),
            'db_pass': self.conf_match(self.config_parse['db_pass']),
            'db_name': self.conf_match(self.config_parse['db_name']),       
            }
            
        return db_auth

    def conf_match(self, var_expr):
        m = re.search(self.config_parse['regexp'] % var_expr, self.config_contents)
        if m:
            return m.group(1)

    def build(self):
        self.Exec.logger.error("Unconfigured application build")
