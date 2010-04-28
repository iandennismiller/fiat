#!/usr/bin/env python

from distutils.core import setup
#def setup():
#    pass
    
import glob, os, re

includes = []
#includes_target = 'share/skel/'
includes_target = 'share/fiat/'
includes_dir = 'share'

for root, dirs, filenames in os.walk(includes_dir):
    if root is includes_dir:
        final = includes_target
    else:
        final = includes_target + root[len(includes_dir)+1:] + '/'
    files = []
    
    if not re.search(r'.svn', root):
        for file in filenames:
            if (file[0] != '.'):
                files.append(os.path.join(root, file))
        includes.append((final, files))

svn_revision = '$Rev$'
m = re.match(r'\$R..: (\d+) \$', svn_revision)
if m:
    rev = m.group(1)
else:
    rev = 0

setup(name='fiat',
      version='r%s' % rev,
      description='fiat - make it so',
      author='Ian Dennis Miller',
      author_email='ian@saperea.com',
      url=' http://code.google.com/p/fiat/',
      packages=['Fiat', 'Fiat.App', 'Fiat.Base', 'Fiat.Core', 'Fiat.DB', 'Fiat.Host', 'Fiat.Plugin'],
      package_dir = {'': 'lib'},
      long_description="Fiat manages projects, specializing in web applications",
      scripts=['bin/fiat'],
      data_files = includes,
      license="GPL v2",
      platforms=["any"],
     )

     