"""
PythonScriptFile.py for ZAnnot Product

Author: Brent Hendricks
(C) 2005 Rice University

This software is subject to the provisions of the GNU Lesser General
Public License Version 2.1 (LGPL).  See LICENSE.txt for details.
"""

import os.path
from Globals import package_home
from Products.PythonScripts.PythonScript import PythonScript


class PythonScriptFile(PythonScript):

    def __init__(self, filename, _prefix=None,__name__=None):

        # Figure out where the file is
        if _prefix is None: _prefix=SOFTWARE_HOME
        elif type(_prefix) is not type(''):
            _prefix = package_home(_prefix)

        # Come up with a good name...
        if not __name__:
            __name__=os.path.split(filename)[-1]

        # Default to '.py' extension
        if not os.path.splitext(filename)[1]:
            filename = filename + '.py'
        self.filename = os.path.join(_prefix, filename)

        PythonScript.__init__(self, __name__)
        
        f = open(self.filename)
        body = f.read()
        f.close()
        self.ZPythonScript_edit('', body)
