import sys, os

class BasePlugin(object):
    
    def __init__(self, Exec):
        self.Exec = Exec

        self.Exec.logger.debug("init Plugin '%s'" % self.__class__.__name__)

        self.meta = {
            "name": self.__class__.__name__
            }
        
