#!/usr/bin/env python
#
# This library is free software, distributed under the terms of
# the GNU Lesser General Public License Version 3, or any later version.
# See the COPYING file included in this archive

import unittest

import kademlia.contact

class ContactOperatorsTest(unittest.TestCase):
    """ Basic tests case for boolean operators on the Contact class """
    def setUp(self):
        self.firstContact = kademlia.contact.Contact('firstContactID', '127.0.0.1', 1000, 1)
        self.secondContact = kademlia.contact.Contact('2ndContactID', '192.168.0.1', 1000, 32)
        self.secondContactCopy = kademlia.contact.Contact('2ndContactID', '192.168.0.1', 1000, 32)
        self.firstContactDifferentValues = kademlia.contact.Contact('firstContactID', '192.168.1.20', 1000, 50)
        
    def testBoolean(self):
        """ Test "equals" and "not equals" comparisons """
        self.failIfEqual(self.firstContact, self.secondContact, 'Contacts with different IDs should not be equal.')
        self.failUnlessEqual(self.firstContact, self.firstContactDifferentValues, 'Contacts with same IDs should be equal, even if their other values differ.')
        self.failUnlessEqual(self.secondContact, self.secondContactCopy, 'Different copies of the same Contact instance should be equal')
        
def suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(ContactOperatorsTest))
    return suite

if __name__ == '__main__':
    # If this module is executed from the commandline, run all its tests
    unittest.TextTestRunner().run(suite())
    