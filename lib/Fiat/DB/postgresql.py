from Fiat.Core.Utils import loggable, unimplemented
from Fiat.Base.DB import BaseDB
import os, re

class postgresql(BaseDB):

    def __init__(self, App, config):
        super(postgresql, self).__init__(App, config)

    def shell(self):
        dict = self.config
        if dict['db_host'] != '':
            dict['db_host'] = "-h%(db_host)s" % dict
        if dict['db_pass'] != '':
            dict['db_pass'] = "-p%(db_pass)s" % dict
            
        cmd = "psql -A %(db_host)s -U%(db_user)s %(db_pass)s %(db_name)s" % dict
        self.Instance.Host.ssh(cmd=cmd, verbose=False, terminal=True)

    def dump_sql(self, sql_file, gzip=False):
        if gzip:
            gzip_cmd = " |gzip"
        else:
            gzip_cmd = ""

        dict = self.config
        dict["sql_file"] = sql_file
        dict["gzip_cmd"] = gzip_cmd

        if dict['db_host'] != '':
            dict['db_host'] = "-h%(db_host)s" % dict
        if dict['db_pass'] != '':
            dict['db_pass'] = "-p%(db_pass)s" % dict

        cmd = "pg_dump %(db_host)s -U%(db_user)s %(db_pass)s %(db_name)s %(gzip_cmd)s > %(sql_file)s" % dict
        self.App.Instance.Host.ssh(cmd, verbose=False)

    def import_sql(self, sql_file):
        dict = self.config
        dict["sql_file"] = sql_file
        if dict['db_host'] != '':
            dict['db_host'] = "-h%(db_host)s" % dict
        
        cmd = "dropdb %(db_name)s; createdb %(db_name)s; PGPASSWORD=%(db_pass)s psql %(db_host)s -U%(db_user)s %(db_name)s < %(sql_file)s" % dict
        self.Instance.Host.ssh(cmd, verbose=False)

    @unimplemented
    def create_db(self):
        dict = self.config

        """
        su postgres
        createuser -W %(db_user)s: n, y, n, PASSWORD
        """

        cmd = "createdb %(db_name)s" % dict
        
        self.Instance.Host.ssh(cmd, verbose=False)
