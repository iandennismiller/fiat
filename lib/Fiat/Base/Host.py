from Fiat.Core.Utils import loggable
import os, optparse

class BaseHost(object):
    
    def __init__(self, Instance):
        self.Instance = Instance
        self.Project = Instance.Project
        self.Exec = Instance.Project.Exec
        
        self.Exec.logger.debug("init Host '%s' for Instance '%s'" % (self.__class__.__name__, Instance.__class__.__name__))
        
        self.meta = {
            "name": self.__class__.__name__
        }
        
        try:
            self.Exec.register_task(name="ssh", args=0, help="open shell on host", function=self.ssh)
        except optparse.OptionConflictError:
            pass

    @loggable
    def ssh(self, cmd=None, verbose=True, terminal=False):
        dict = self.config
        dict["cmd"] = cmd
        
        if cmd == None:
            os.system("ssh -p %(ssh_port)s %(ssh_user)s@%(ssh_host)s" % dict)
        else:
            if terminal == True:
            	ssh_command = "ssh -t -p %(ssh_port)i %(ssh_user)s@%(ssh_host)s '%(cmd)s'" % dict
                os.system(ssh_command)
            else:
            	ssh_command = "ssh -p %(ssh_port)i %(ssh_user)s@%(ssh_host)s '%(cmd)s'" % dict
            	if verbose:
                    self.Exec.logger.info("ssh '%(cmd)s'" % dict)
            	output = os.popen(ssh_command).read()
            	if verbose:
            	    self.Exec.logger.info("ssh result: '%s'" % output)
            	return output

    @loggable        
    def rsync_build(self):
        source = os.path.join(self.Project.config['build_path'], ".")
        destination = os.path.join(self.config["install_path"], "")
        self.rsync_up(source, destination)

    @loggable
    def rsync_up(self, source, destination):
        try:
            if self.Project.config['simulate']:
                self.Exec.logger.info("simulating deploy")
                simulate = 'nv'
            else:
                simulate = ""
        except KeyError:
            simulate = ""

        dict = self.config
        dict["simulate"] = simulate
        dict["source"] = source
        dict["destination"] = destination

        self.Exec.logger.info("rsync %(source)s to %(destination)s" % dict)

        rsync_cmd = "rsync -acz%(simulate)s -e 'ssh -o port=%(ssh_port)i' %(source)s " + \
            "%(ssh_user)s@%(ssh_host)s:%(destination)s| grep -v /$"

        os.system(rsync_cmd % dict)

    @loggable
    def rsync_down(self, source, destination):
        dict = self.config
        dict["source"] = source
        dict["destination"] = destination

        self.Exec.logger.info("rsync %(source)s to %(destination)s" % dict)

        rsync_cmd = "rsync -a -e 'ssh -o port=%(ssh_port)i' %(ssh_user)s@%(ssh_host)s:%(source)s %(destination)s"

        os.system(rsync_cmd % dict)

    @loggable
    def scp_from(self, source):
        dict = self.config
        dict["source"] = source
        dict["destination"] = self.Project.config["make_path"]
        
        self.Exec.logger.info("copy %(source)s to %(destination)s/tmp" % dict)

        os.system("scp -r -C -P %(ssh_port)s %(ssh_user)s@%(ssh_host)s:%(source)s %(destination)s/tmp" % dict)

    @loggable
    def scp_to(self, source):
        dict = self.config
        dict["source"] = source
        dict["destination"] = self.config["scratch_path"]
        
        self.Exec.logger.info("copy %(source)s to %(destination)s" % dict)

        os.system("scp -r -C -P %(ssh_port)s %(source)s %(ssh_user)s@%(ssh_host)s %(destination)s" % dict)
    