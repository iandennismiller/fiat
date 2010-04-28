from Fiat.Core.Utils import loggable, loggable_info
import sys, os

class BaseProject(object):

    def __init__(self, Exec):
        self.Exec = Exec
        self.Instance = {}
        self.config = {}

        self.setup()

        Exec.register_task(name="clean", args=0, help="clean build path", function=self.clean)
        Exec.register_task(name="build", args=0, help="build project instance", function=self.build)
        Exec.register_task(name="simulate", args=0, help="simulate project deploy", function=self.simulate)
        Exec.register_task(name="deploy", args=0, help="deploy project instance", function=self.deploy)
        Exec.register_task(name="spinup", args=0, help="spinup project instance", function=self.spinup)

    def load_instance(self, instance_name):
        instance_class = getattr(sys.modules["project"], instance_name)
        try:
            if os.environ['instance'] == instance_name:
                self.Instance[instance_name] = instance_class(self)
        except KeyError:
            self.Instance[instance_name] = instance_class(self)

    def setup(self):
        self.Exec.logger.warn("Unconfigured project")

        self.meta = {
            "project": "Unconfigured",
            "version": 0.1,
            }        

    @loggable_info
    def clean(self):
        self.Exec.Utils.remove_build_path()

    @loggable_info
    def build(self):
        """
        Run through the core build process, sortof like with
        Makefiles.
        """
        self.Exec.Utils.create_build_path()

        self.pre_build()
        self.ActiveInstance.pre_build()
        self.main_build()
        self.ActiveInstance.main_build()
        self.post_build()
        self.ActiveInstance.post_build()

        #self.Exec.Utils.remove_svn_files()

    @loggable_info
    def simulate(self):
        self.config['simulate'] = True

        self.pre_deploy()
        self.ActiveInstance.pre_deploy()
        self.ActiveInstance.main_deploy()

        self.config['simulate'] = False

    @loggable_info
    def deploy(self):
        self.pre_deploy()
        self.ActiveInstance.pre_deploy()
        self.ActiveInstance.main_deploy()
        self.post_deploy()
        self.ActiveInstance.post_deploy()

    @loggable
    def spinup(self):
        self.ActiveInstance.spinup()

    def pre_build(self):
        self.Exec.logger.debug("Unconfigured stage: Project pre_build")
        #self.Exec.Utils.cp_build("project_root/")

    def main_build(self):
        self.Exec.logger.debug("Unconfigured stage: Project build")
        
    def post_build(self):
        self.Exec.logger.debug("Unconfigured stage: Project post_build")
        self.Exec.Utils.cp_build("fiat/%s/" % self.ActiveInstance.Host.meta["name"])

    def pre_deploy(self):
        self.Exec.logger.debug("Unconfigured stage: Project pre_deploy")

    def post_deploy(self):
        self.Exec.logger.debug("Unconfigured stage: Project post_deploy")

