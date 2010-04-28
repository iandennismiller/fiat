from Fiat.Core.Utils import loggable, unimplemented
from Fiat.Base.DB import BaseDB
import os, re

class couchdb(BaseDB):

    def __init__(self, App, config):
        super(couchdb, self).__init__(App, config)

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
