from optparse import OptionParser
import sys, os, logging, traceback
from Fiat.Core.Utils import Utils

class Exec(object):
    
    def __init__(self):
        self.config = {}
        self.registry = {}
        self.indent = 0

        self.init_logger()
        self.command_line = OptionParser()
        self.Utils = Utils(self)

    def load_plugins(self):
        import Fiat.Plugin.Auto
        Fiat.Plugin.Auto.Auto(self)

    def import_config(self):
        config_file = os.path.join(os.path.expanduser('~'), ".fiat/global.py")
        execfile(config_file, globals(), self.config)

        sys.path.append(os.path.join(os.getcwd(), "fiat"))

        try:
            module = __import__("project")
        except ImportError:
            self.logger.warn("There is no file ./fiat/project.py")

        if vars().has_key('module'):
            self.Project = module.project(self)

            self.Project.config['make_path'] = os.getcwd()
            self.Project.config['build_path'] = "%s/tmp/build" % self.Project.config['make_path'] 

            try:
                instance_name = os.environ['instance']
                self.Project.ActiveInstance = self.Project.Instance[instance_name]
            except KeyError:
                if len(self.Project.Instance.keys()) == 1:
                    self.logger.warn("Using default Active Instance (in bash, try 'export instance=SOMETHING')")
                    default_instance_name = self.Project.Instance.keys()[0]
                    self.Project.ActiveInstance = self.Project.Instance[default_instance_name]

        try:
            self.logger.info("Active Instance is '%s'" % self.Project.ActiveInstance.meta["name"])
        except AttributeError:
            self.logger.warn("unable to set Active Instance")

    def import_class(self, parent, prefix, container, klass, config = {}):
        module_name = "%s.%s" % (prefix, container)

        try:
            module = __import__(module_name)
        except ImportError:
            self.logger.error("unable to import module '%s'" % module_name)
            return

        try:
            loaded_class = getattr(sys.modules[module_name], klass)
            self.logger.debug("imported class '%s' from %s" % (klass, module_name))
        except AttributeError:
            self.logger.error("unable to import class '%s' from %s" % (klass, module_name))
            return

        return loaded_class(parent, config)
        
    def init_logger(self):
        self.logger = logging.getLogger("fiat")
        self.logger.setLevel(logging.WARNING)
        formatter = logging.Formatter("%(asctime)s\t%(levelname)s\t%(message)s")
        ch = logging.StreamHandler()
        ch.setFormatter(formatter)
        self.logger.addHandler(ch)

    def call_stages(self, options):
        exists = 0
        
        for stage in ("clean", "build", "simulate", "deploy", "spinup"):
            try:
                run_this_stage = getattr(options, stage)
            except AttributeError:
                run_this_stage = False
            
            if run_this_stage:
                exists += 1
                self.registry[stage]()
        
        if exists > 0:
            return True
        else:
            return False

    def call_chosen_function(self, options):
        for option in self.registry.keys():
            if getattr(options, option):
                self.logger.info("calling " + option)
                function = self.registry[option]
                if getattr(options, option) == True:
                    function()
                else:
                    function(getattr(options, option))

    def register_task(self, name, args, help, function):
        self.logger.debug("registering %s " % name)
        if args > 0:
            self.command_line.add_option("--" + name, help=help)
        else:
            self.command_line.add_option("--" + name, action="store_true", help=help)
         
        self.registry[name] = function
        
    def parse_cmdline(self):
        self.command_line.add_option("-v", action="count", dest="verbosity")
        (options, args) = self.command_line.parse_args()

        if options.verbosity == 1:
            self.logger.setLevel(logging.INFO)
        elif options.verbosity >= 2:
            self.logger.setLevel(logging.DEBUG)
        return options
    
    def instance_on_cmdline(self):
        """
        Test if an instance is provided as the very first option
        on the command line.
        
            >>> self.instance_on_cmdline()
            False
        """
        self.command_line.add_option("-i", "--instance", action="store", type="string", dest="instance")
        try:
            if sys.argv[1] == '-i':
                os.environ['instance'] = sys.argv[2]
        except:
            pass
    
    def run(self):
        self.instance_on_cmdline()
        self.import_config()
        self.load_plugins()
        
        options = self.parse_cmdline()
        try:
            if not self.call_stages(options):
                self.call_chosen_function(options)
                self.logger.info("fiat finished successfully")
        except SystemExit:
            pass
        except:
            self.logger.error(sys.exc_info())
            traceback.print_exc()

