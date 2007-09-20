#!/usr/bin/env python
#
# This library is free software, distributed under the terms of
# the GNU Lesser General Public License Version 3, or any later version.
# See the COPYING file included in this archive

""" Wrapper script to run all included test scripts """

import os, sys
import unittest

def runTests():
    testRunner = unittest.TextTestRunner()
    suite = unittest.TestSuite()
    
    tests = os.listdir(os.curdir)
    tests = [n[:-3] for n in tests if n.startswith('test') and n.endswith('.py')]

    for test in tests:
        m = __import__(test)
        if hasattr(m, 'suite'):
            suite.addTest(m.suite())
    
    testRunner.run(suite)
    
    
if __name__ == '__main__':
    # Add parent folder to sys path so it's easier to use
    sys.path.insert(0,os.path.abspath('..'))
    runTests()
