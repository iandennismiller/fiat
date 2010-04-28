Core
====

The Core functionality of Fiat is covered here.  If you are
familiar with the topics on this page, then you will know enough
to handle simple tasks using Fiat.

:mod:`Fiat.Base.Project` -- Base project
-----------------------------------------

All that's required to use Fiat with your project is to create a
path called **fiat** and put a file in it called **project.py**.  The
simplest project.py looks like this::

	from Fiat.Base.Instance import BaseInstance
	from Fiat.Base.Project import BaseProject

	class project(BaseProject):

	    def setup(self):
	        self.meta = {
	            "project": "fiat",
	            "version": 0.2,
	            }

	        self.load_instance("dev")
	        self.auto_monitor_paths = ["lib/Fiat"]
       
	class dev(BaseInstance):
	    pass

This file identifies a new project called "fiat", and indicates
that there one instance of this project called "dev".  In most
cases, an instance will actually live on a host, but this project
doesn't specify any remote hosts.  Also, projects generally
consists of applications, but again, this project doesn't specify
any applications.

.. automodule:: Fiat.Base.Project

.. autoclass:: BaseProject
	:show-inheritance:
	:members:
	:inherited-members:
	:undoc-members:

:mod:`Fiat.Base.Instance` -- Base instance
--------------------------------------------

.. automodule:: Fiat.Base.Instance

.. autoclass:: BaseInstance
	:show-inheritance:
	:members:
	:inherited-members:
	:undoc-members:

:mod:`Fiat.Core.Exec` -- Core Fiat Executable
----------------------------------------------

.. automodule:: Fiat.Core.Exec

.. autoclass:: Exec
	:show-inheritance:
	:members:
	:inherited-members:
	:undoc-members:

:mod:`Fiat.Core.Utils` -- Fiat Utility library
-----------------------------------------------

.. automodule:: Fiat.Core.Utils

.. autoclass:: Utils
	:show-inheritance:
	:members:
	:inherited-members:
	:undoc-members:
