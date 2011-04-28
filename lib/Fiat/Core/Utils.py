import distutils.dir_util
import os, tempfile, shutil, tarfile, string, re, logging
from os.path import join, splitext, split, exists

from functools import wraps
from decorator import decorator

@decorator
def loggable(f, *args, **kws):
    """
    when a method in the globescrape library is loggable, then
    that method's instantiation will send log messages to its
    global logger handle, stored in self.Exec.logger
    """
    self = args[0]
    self.Exec.indent += 1
    self.Exec.logger.debug("%s call: %s.%s" % ('>' * self.Exec.indent, f.__module__, f.__name__))
    ret = f(*args, **kws)
    self.Exec.logger.debug("%s exit: %s.%s" % ('<' * self.Exec.indent, f.__module__, f.__name__))
    self.Exec.indent -= 1
    return ret    

@decorator
def loggable_info(f, *args, **kws):
    """
    when a method in the globescrape library is loggable, then
    that method's instantiation will send log messages to its
    global logger handle, stored in self.Exec.logger
    """
    self = args[0]
    self.Exec.indent += 1
    self.Exec.logger.info("%s call: %s.%s" % ('>' * self.Exec.indent, f.__module__, f.__name__))
    ret = f(*args, **kws)
    self.Exec.logger.info("%s exit: %s.%s" % ('<' * self.Exec.indent, f.__module__, f.__name__))
    self.Exec.indent -= 1
    return ret    


def loggable2(f):
    def new_f(self, *args, **kws):
        self.Exec.indent += 1
        self.Exec.logger.debug("%s call: %s.%s" % ('>' * self.Exec.indent, f.__module__, f.__name__))
        ret = f(self, *args, **kws)
        self.Exec.logger.debug("%s exit: %s.%s" % ('<' * self.Exec.indent, f.__module__, f.__name__))
        self.Exec.indent -= 1
        
        return ret
    return new_f

def unimplemented(f):
    def new_f(self, *args, **kws):
        self.Exec.logger.warn("unimplemented base class was called: %s.%s" % (f.__module__, f.__name__))
    return new_f

def copy_directory(source, target):
    core_copy_directory(source, target, shutil.copy2)

def link_directory(source, target):
    core_copy_directory(source, target, os.link)

# http://tarekziade.wordpress.com/2008/07/08/shutilcopytree-small-improvement/
def core_copy_directory(source, target, fn):
    if not os.path.exists(target):
        os.mkdir(target)
    for root, dirs, files in os.walk(source):
        if '.svn' in dirs:
            dirs.remove('.svn')  # don't visit .svn directories           
        for file in files:
            if splitext(file)[-1] in ('.pyc', '.pyo', '.fs'):
                continue
            from_ = join(root, file)           
            to_ = from_.replace(source, target, 1)
            to_directory = split(to_)[0]
            if not exists(to_directory):
                os.makedirs(to_directory)
            #copy2(from_, to_)
            try:
                fn(from_, to_)
            except OSError as (num, msg):
                logging.getLogger("fiat").info("%s %s" % (msg, to_))

class Utils(object):
    def __init__(self, Exec):
        self.Exec = Exec
        
        Exec.register_task(name="create", args=1, help="create new project", function=self.svn_create)
        Exec.register_task(name="overlay", args=1, help="overlay from skel onto project", function=self.overlay_skel)
        Exec.register_task(name="skels", args=0, help="list available skel overlays", function=self.list_skel)

    @loggable
    def create_build_path(self):
        if os.path.isdir(self.Exec.Project.config['build_path']):
            self.Exec.logger.info('build path already exists')
        else:
            try:
                os.mkdir(self.Exec.Project.config['build_path'])
            except OSError:
                os.system("mkdir -p %s" % self.Exec.Project.config['build_path'])
                #os.mkdir(os.path.dirname(os.path.join(self.Exec.Project.config['build_path'])))
                #os.mkdir(self.Exec.Project.config['build_path'])
            self.Exec.logger.info('created build path: %s' % self.Exec.Project.config['build_path'])

    @loggable
    def sed(self, source, change_from, change_to):
        infile = open(os.path.join(self.Exec.Project.config['build_path'], source))
        contents = infile.read()
        new_contents = re.sub(change_from, change_to, contents)
        infile.close()
        outfile = open(os.path.join(self.Exec.Project.config['build_path'], source), "w")
        outfile.write(new_contents)
        outfile.close()
        #print new_contents

    @loggable
    def compass(self, target, compress=False):
        do_compress = ""
        if compress:
            do_compress = "-s compressed"
        cmd = '/opt/local/bin/compass -u %s %s' % (do_compress, os.path.join(self.Exec.Project.config['make_path'], target))
        os.system(cmd)

    @loggable
    def jsmin(self, source):
        cmd = '/usr/bin/java -jar /Users/idm/Code/Lib/yuicompressor-2.4.2.jar -o %(f)s %(f)s' % {'f': os.path.join(self.Exec.Project.config['build_path'], source)}
        os.system(cmd)
        #print cmd
        # os.system("%s '%s'" % (self.Exec.config['svn_admin_ssh'], ssh_cmd))

    @loggable
    def remove_build_path(self):
        try:
            shutil.move(self.Exec.Project.config['build_path'], '/tmp/removed')
            shutil.rmtree('/tmp/removed')
            self.Exec.logger.info('removed %s' % self.Exec.Project.config['build_path'])
        except OSError:
            self.Exec.logger.warn('unable to remove %s' % self.Exec.Project.config['build_path'])
        except IOError:
            self.Exec.logger.warn('already removed %s' % self.Exec.Project.config['build_path'])

    @loggable
    def cp_build(self, source, dest=""):
        full_source = os.path.join(self.Exec.Project.config['make_path'], source)
        full_dest = os.path.join(self.Exec.Project.config['build_path'], dest)

        self.Exec.logger.debug('copy %s to %s' % (full_source, full_dest))
        
        if os.path.isfile(full_source):
            (filepath, filename) = os.path.split(full_source)
            #shutil.copyfile(full_source, os.path.join(full_dest, filename))
            #copy2(full_source, os.path.join(full_dest, filename))
            os.link(full_source, os.path.join(full_dest, filename))
            self.Exec.logger.debug('successfully copied file: %s' % full_dest)
        else:
            #copy_directory(full_source, full_dest)
            link_directory(full_source, full_dest)
            #os.system("rsync -a %s %s" % (full_source, full_dest))
            self.Exec.logger.debug('successfully copied path: %s' % full_dest)

    @loggable
    def unpack_tarball(self, type, version, install_path):

        tarball = os.path.join(self.Exec.config['tarball_path'], "%s-%s.tar.gz" % (type, version))

        tempdir = tempfile.mkdtemp()
        untarred_into = tempdir

        self.Exec.logger.info('untar %s into %s' % (tarball, tempdir))

        tar = tarfile.open(name=tarball, mode='r:gz')
        tar.extractall(path=tempdir)
        tar.close()

        # if there is only one directory in the tarball, then assume
        # the source isn't in the root path of the tarball
        if len(os.listdir(tempdir)) == 1:
            untarred_into = os.path.join(tempdir, os.listdir(tempdir)[0])

        self.Exec.logger.info('copy unpacked tarball to %s' % install_path)
        shutil.rmtree(install_path, ignore_errors=True)
        shutil.copytree(untarred_into, install_path)
        shutil.rmtree(tempdir)

    @loggable
    def svn_create(self, path_name):
        
        tempdir = tempfile.mkdtemp()
        os.makedirs(os.path.join(tempdir, "branch"))
        os.makedirs(os.path.join(tempdir, "tag"))
        os.makedirs(os.path.join(tempdir, "trunk"))

        ssh_cmd = """
        /usr/bin/svnadmin create %(p)s;
        rm %(p)s/conf/svnserve.conf;
        ln -s /etc/subversion/svnserve.conf %(p)s/conf/svnserve.conf
        """ % {'p': os.path.join(self.Exec.config['svn_admin_path'], path_name)}

        os.system("%s '%s'" % (self.Exec.config['svn_admin_ssh'], ssh_cmd))
        os.system("svn import -m 'initial import' %s %s" % (tempdir, os.path.join(self.Exec.config['svn_url'], path_name)))
        os.system("svn checkout %s/trunk ./%s" % (os.path.join(self.Exec.config['svn_url'], path_name), path_name))
        os.system("svn propset svn:ignore tmp ./%s" % path_name)

        shutil.rmtree(tempdir)
        self.Exec.logger.info("finish svn create")

    @loggable
    def overlay_skel(self, skel_name):
        tempdir = tempfile.mkdtemp()

        copy_source = "%s/%s" % (self.Exec.config['skel_path'],skel_name)

        print "svn export %s %s/t" % (copy_source, tempdir)
        os.system("svn export %s %s/t" % (copy_source, tempdir))

        self.Exec.logger.info("overlaying skeleton from %s" % copy_source)

        distutils.dir_util.copy_tree("%s/t" % tempdir, ".")

        shutil.rmtree(tempdir)

    def list_skel(self):
        print "\nAvailable skeleton overlays:\n"

        for dir in os.listdir(self.Exec.config['skel_path']):
            print dir
    