# -*- coding: utf-8 -*-
#

import sys, os
sys.path.append('/Users/idm/Code/google_code/fiat/lib')

# -- General configuration -----------------------------------------------------
extensions = ['sphinx.ext.autodoc']
templates_path = ['_templates']
source_suffix = '.rst'
master_doc = 'index'

project = u'fiat'
copyright = u'2009, Ian Dennis Miller'
version = '0.2'
release = '0.2'

# List of directories, relative to source directory, that shouldn't be searched
# for source files.
exclude_trees = []

# The name of the Pygments (syntax highlighting) style to use.
pygments_style = 'sphinx'

# -- Options for HTML output ---------------------------------------------------
html_theme = 'default'
html_static_path = ['_static']
# Output file base name for HTML help builder.
htmlhelp_basename = 'fiatdoc'

# -- Options for LaTeX output --------------------------------------------------
# Grouping the document tree into LaTeX files. List of tuples
# (source start file, target name, title, author, documentclass [howto/manual]).
latex_documents = [
  ('index', 'fiat.tex', u'fiat Documentation',
   u'Ian Dennis Miller', 'manual'),
]
