from __future__ import nested_scopes
from Fiat.Base.Plugin import BasePlugin
import os, time, sys, subprocess
from os.path import split

"""
This file contains actions that can be triggered automatically as
a result of project files being modified.
The directories to watch are stored in fiat's project.py, in the
project class.
"""

def watch_directories (paths, func, delay=1.0):
    """(paths:[str], func:callable, delay:float)
    Continuously monitors the paths and their subdirectories
    for changes.  If any files or directories are modified,
    the callable 'func' is called with a list of the modified paths of both
    files and directories.  'func' can return a Boolean value
    for rescanning; if it returns True, the directory tree will be
    rescanned without calling func() for any found changes.
    (This is so func() can write changes into the tree and prevent itself
    from being immediately called again.)
    """

    # Basic principle: all_files is a dictionary mapping paths to
    # modification times.  We repeatedly crawl through the directory
    # tree rooted at 'path', doing a stat() on each file and comparing
    # the modification time.

    all_files = {}
    def f (unused, dirname, files):
        # Traversal function for directories
        
        for filename in files:
            path = os.path.join(dirname, filename)

            if '.svn' in dirname.split('/') or filename == '.svn':
                continue
            #print path

            try:
                t = os.stat(path)
            except os.error:
                # If a file has been deleted between os.path.walk()
                # scanning the directory and now, we'll get an
                # os.error here.  Just ignore it -- we'll report
                # the deletion on the next pass through the main loop.
                continue

            mtime = remaining_files.get(path)
            if mtime is not None:
                # Record this file as having been seen
                del remaining_files[path]
                # File's mtime has been changed since we last looked at it.
                if t.st_mtime > mtime:
                    changed_list.append(path)
            else:
                # No recorded modification time, so it must be
                # a brand new file.
                changed_list.append(path)

            # Record current mtime of file.
            all_files[path] = t.st_mtime

    # Main loop
    rescan = False
    while True:
        changed_list = []
        remaining_files = all_files.copy()
        all_files = {}
        for path in paths:
            os.path.walk(path, f, None)
        removed_list = remaining_files.keys()
        if rescan:
            rescan = False
        elif changed_list or removed_list:
            rescan = func(changed_list, removed_list)

        time.sleep(delay)

class Auto(BasePlugin):
    def __init__(self, Exec):
        super(Auto, self).__init__(Exec)
        
        self.Exec.register_task(name="auto", args=1, help="automate deploy or test", function=self.watch_paths)

    def watch_paths(self, arg):
        def f (changed_files, removed_files):
            #os.system("clear")
            if arg == "test":
                self.auto_test()
            elif arg == "deploy":
                self.auto_deploy()
            elif arg == "doc":
                self.auto_doc()
            return False

        try:
            getattr(self.Exec.Project, "auto_monitor_paths")
            watch_directories(self.Exec.Project.auto_monitor_paths, f, 1)
        except AttributeError:
            watch_directories('.', f, 1)
        
    def auto_doc(self):
        doc_root = os.path.join(self.Exec.Project.config['make_path'], 'doc/sphinx')
        doc_dest = os.path.join(self.Exec.Project.config['make_path'], 'var/sphinx/html')
        
        cmd = 'sphinx-build -a -E %s %s' % (doc_root, doc_dest)
        os.system(cmd)

    def auto_deploy(self):
        self.Exec.registry["clean"]()
        self.Exec.registry["build"]()
        self.Exec.registry["deploy"]()
        self.Exec.logger.info("auto-deploy successful")
    
    def auto_test(self):
        os.system("clear")
        self.Exec.Project.run_test()
        
        #nosetests_cmd = "/opt/local/Library/Frameworks/Python.framework/Versions/2.6/bin/nosetests"
        #cmd = "%s --with-id --id-file=/tmp/noseids -w %s -v" % (nosetests_cmd, self.Exec.Project.test_path)
        #os.system(cmd)
    
