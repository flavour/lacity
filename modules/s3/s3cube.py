# -*- coding: utf-8 -*-

"""
    S3 Contingency Table Toolkit

    @author: Dominic König <dominic[at]aidiq[dot]com>

    @copyright: 2011 (c) Sahana Software Foundation
    @license: MIT

    @requires: U{B{I{Python 2.7}} <http://www.python.org>}
    @requires: U{B{I{SciPy}} <http://www.scipy.org>}
    @requires: U{B{I{NumPy}} <http://www.numpy.org>}
    @requires: U{B{I{MatPlotLib}} <http://matplotlib.sourceforge.net>}
    @requires: U{B{I{PyvtTbl}} <http://code.google.com/p/pyvttbl>}
    @requires: U{B{I{SQLite3}} <http://www.sqlite.org>}

    Permission is hereby granted, free of charge, to any person
    obtaining a copy of this software and associated documentation
    files (the "Software"), to deal in the Software without
    restriction, including without limitation the rights to use,
    copy, modify, merge, publish, distribute, sublicense, and/or sell
    copies of the Software, and to permit persons to whom the
    Software is furnished to do so, subject to the following
    conditions:

    The above copyright notice and this permission notice shall be
    included in all copies or substantial portions of the Software.

    THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
    EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES
    OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
    NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT
    HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY,
    WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
    FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR
    OTHER DEALINGS IN THE SOFTWARE.
"""

__all__ = ["S3Cube"]

import sys

from gluon import current
from gluon.storage import Storage
try:
    from pyvttbl import DataFrame
    PYVTTBL = True
except ImportError:
    print >> sys.stderr, "WARNING: S3Cube unresolved dependencies: scipy, numpy and matplotlib required for analyses"
    PYVTTBL = False
if sys.version_info[0] != 2 or \
   sys.version_info[1] != 7:
    print >> sys.stderr, "WARNING: S3Cube unresolved dependencies: Python 2.7 required for analyses"
    PYVTTBL = False

from s3method import S3Method

# =============================================================================

class S3Cube(S3Method):
    """ RESTful method handler to generate contingency tables """

    def __init__(self):

        self.rows = None
        self.cols = None
        self.fact = None

    def apply_method(self, r, **attr):

        if not PYVTTBL:
            r.error(501, "Function not available on this server")

        output = dict()

        current.response.view = "list.html"
        return output

# =============================================================================

class S3CubeDimension(object):

    def __init__(self):
        raise NotImplementedError

# =============================================================================

class S3CubeFact(S3CubeDimension):

    def __init__(self):
        raise NotImplementedError

# =============================================================================
