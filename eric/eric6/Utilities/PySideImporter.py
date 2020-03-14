# -*- coding: utf-8 -*-

# Copyright (c) 2011 - 2020 Detlev Offenbach <detlev@die-offenbachs.de>
#

"""
Module to check for the presence of PySide/PySide2 by importing it.
"""

import sys

if __name__ == "__main__":
    pySideVariant = "2"
    if len(sys.argv) == 2:
        pySideVariant = sys.argv[1].replace("-", "")
    
    if pySideVariant == "1":
        try:
            import PySide       # __IGNORE_EXCEPTION__ __IGNORE_WARNING__
            ret = 0
        except ImportError:
            ret = 1
    
    elif pySideVariant == "2":
        try:
            import PySide2       # __IGNORE_EXCEPTION__ __IGNORE_WARNING__
            ret = 0
        except ImportError:
            ret = 1
    
    else:
        ret = 1
    
    sys.exit(ret)
    
#
# eflag: noqa = M702
