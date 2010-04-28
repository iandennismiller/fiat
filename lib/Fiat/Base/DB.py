from Fiat.Core.Utils import loggable, unimplemented
import os, re

class BaseDB(object):
    
    def __init__(self, App, config_dict):
        self.App = App
        self.Instance = App.Instance
        self.Project = App.Instance.Project
        self.Exec = App.Instance.Project.Exec
        
        self.Exec.logger.debug("init DB '%s' for App '%s'" % (self.__class__.__name__, App.__class__.__name__))
        
        #self.config = App.db_auth
        self.config = config_dict
        
    def escape(self, source_content):
        source_content = re.sub(r'\\', r'\\\\', source_content)
        source_content = re.sub(r'"', r'\\"', source_content)
        source_content = re.sub(r'\'', r"\\'", source_content)
        source_content = re.sub(r'\t', r'\\t', source_content)
        source_content = re.sub(r'\n', r'\\n', source_content)
        source_content = re.sub(r'\r', r'\\r', source_content)
        return source_content

    @loggable
    def deploy_and_import(self, local_path, filename, remote_temp_path):
        local_file = os.path.join(local_path, filename)
        remote_file = os.path.join(remote_temp_path, filename)

        self.Instance.Host.rsync_up(local_file, remote_file)
        self.import_sql(remote_file)
        self.Instance.Host.ssh("rm %s" % remote_file)

    @loggable
    def deploy_db(self):
    	self.deploy_and_import(
    		local_path = os.path.join(self.Project.config['make_path'], "var/sql"),
    		filename = "%s.sql" % self.App.meta["type"], 
    		remote_temp_path = self.Instance.Host.config['scratch_path'])

    @loggable
    def dump_and_download(self, local_path, filename, remote_temp_path, gzip=False):
        self.dump_sql(os.path.join(remote_temp_path, filename), gzip)
        self.Instance.Host.rsync_down(os.path.join(remote_temp_path, filename), local_path)
        self.Instance.Host.ssh(cmd="rm %s" % os.path.join(remote_temp_path, filename))

    @loggable
    def checkin_database(self):
        self.dump_and_download(
            local_path = os.path.join(self.App.Instance.Project.config['make_path'], "var/sql"),
            filename = "%s.sql" % self.App.meta["type"], 
            remote_temp_path = self.App.Instance.Host.config['scratch_path'])

    @unimplemented
    def shell(self):
        pass
    
    @unimplemented
    def dump_sql(self, sql_file, gzip=False):
        pass
    
    @unimplemented
    def import_sql(self, sql_file):
        pass
    
    @unimplemented
    def create_db(self):
        pass    

def db_backup(self):
	dest_path = os.path.join(Context().env['make_path'], "var/backup")
	Fiat.DB.mysql.datestamp_dump(dest_path)

