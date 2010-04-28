import sys, os

class BaseInstance(object):
    
    def __init__(self, Project):
        self.Project = Project
        self.App = {}
        self.Exec = Project.Exec

        self.Exec.logger.debug("init Instance '%s' for Project '%s'" % (self.__class__.__name__, Project.__class__.__name__))

        self.meta = {
            "name": self.__class__.__name__
            }
        
        self.setup()
        
    def load_app(self, name, config):
        self.App[name] = self.Exec.import_class(self, prefix="Fiat.App", container=name, klass=name, config=config)
        
    def load_host(self, name, config):
        self.Host = self.Exec.import_class(self, prefix="Fiat.Host", container=name, klass=name, config=config)

    def setup(self):
        self.Exec.logger.warn("Unconfigured instance: %s" % __name__)

    def pre_build(self):
        self.Exec.logger.debug("Unconfigured stage: Instance pre_build")

    def main_build(self):
        self.Exec.logger.debug("Unconfigured stage: Instance main_build")

    def post_build(self):
        self.Exec.logger.debug("Unconfigured stage: Instance post_build")

    def pre_deploy(self):
        self.Exec.logger.debug("Unconfigured stage: Instance pre_deploy")

    def main_deploy(self):
        self.Exec.logger.debug("Unconfigured stage: Instance deploy")
        self.Host.rsync_build()        

    def post_deploy(self):
        self.Exec.logger.debug("Unconfigured stage: Instance post_deploy")

    def spinup(self):
        self.Exec.logger.debug("Unconfigured stage: Instance spinup")
    
