from fabric.api import env, run, local
import os, sys

def release_docs():
    sys.path.append(".")
    from fabauth import get_auth
    
    c = {
        "rsync_auth": get_auth()['rsync'],
        "sphinx_path": './sphinx',
    }
    
    cmd = """
    rm -rf /tmp/api;
    sphinx-build -b html %(sphinx_path)s /tmp/api;
    rsync -a /tmp/api %(rsync_auth)s;
    rm -rf /tmp/api;
    """ % c
    #print cmd
    local(cmd, capture=False)
