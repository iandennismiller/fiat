from Fiat.Core.Utils import loggable
from Fiat.Base.DB import BaseDB
import os, re

class mysql(BaseDB):

    def __init__(self, App, config):
        super(mysql, self).__init__(App, config)
    
    @loggable
    def shell(self):
        dict = self.config
        
        mysql_cmd = "mysql -A -h %(db_host)s -u %(db_user)s -p%(db_pass)s %(db_name)s" % dict
        self.Instance.Host.ssh(cmd=mysql_cmd, verbose=False, terminal=True)
    
    @loggable
    def dump_sql(self, sql_file, gzip=False):
        if gzip:
            gzip_cmd = " |gzip"
        else:
            gzip_cmd = ""

        dict = self.config
        dict["sql_file"] = sql_file
        dict["gzip_cmd"] = gzip_cmd

        cmd = "mysqldump --add-drop-table -h %(db_host)s -u %(db_user)s " + \
            "-p%(db_pass)s %(db_name)s %(gzip_cmd)s > %(sql_file)s"

        self.App.Instance.Host.ssh(cmd % dict, verbose=False)

    @loggable
    def import_sql(self, sql_file):
        dict = self.config
        dict["sql_file"] = sql_file
        
        cmd = "mysql -h %(db_host)s -u %(db_user)s -p%(db_pass)s %(db_name)s < %(sql_file)s" % dict
        self.Instance.Host.ssh(cmd, verbose=False)

    @loggable
    def create_db(self):
        dict = self.config

        sql = "create database %(db_name)s; create user \\\"%(db_user)s\\\" identified by \\\"%(db_pass)s\\\"; " + \
            "grant all privileges on %(db_name)s.* to \\\"%(db_user)s\\\";"
    
        dict["mysql_admin"] = self.Instance.Host.config["mysql_admin"]
        dict["mysql_pass"] = self.Instance.Host.config["mysql_pass"]
        dict["sql"] = sql % dict

        mysql_cmd = "mysql -h %(db_host)s -u %(mysql_admin)s -p%(mysql_pass)s -e \"%(sql)s\"" % dict
        
        self.Instance.Host.ssh(mysql_cmd, verbose=False)

def datestamp_dump(local_path):
    import datetime, os
    
    (db_host, db_user, db_pass, db_name) = get_auth()

    filename = "%s-%s.sql.gz" % (datetime.date.today(), db_name)

    remote_temp_path = Context().host['scratch_path']

    dump_and_download(local_path = local_path, filename = filename, 
        remote_temp_path = remote_temp_path, gzip=True)

    print "%s is %s bytes" % (filename, os.stat(os.path.join(local_path, filename)).st_size)
