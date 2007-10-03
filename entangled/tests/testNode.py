#!/usr/bin/env python
#
# This library is free software, distributed under the terms of
# the GNU Lesser General Public License Version 3, or any later version.
# See the COPYING file included in this archive

import hashlib
import unittest

import kademlia.node
import kademlia.constants

class NodeIDTest(unittest.TestCase):
    """ Test case for the Node class's ID """
    def setUp(self):
        self.node = kademlia.node.Node()

    def testAutoCreatedID(self):
        """ Tests if a new node has a valid node ID """
        self.failUnlessEqual(type(self.node.id), str, 'Node does not have a valid ID')
        self.failUnlessEqual(len(self.node.id), 20, 'Node ID length is incorrect! Expected 160 bits, got %d bits.' % (len(self.node.id)*8))

    def testUniqueness(self):
        """ Tests the uniqueness of the values created by the NodeID generator 
        """
        generatedIDs = []
        for i in range(100):
            newID = self.node._generateID()
            # ugly uniqueness test
            self.failIf(newID in generatedIDs, 'Generated ID #%d not unique!' % (i+1))
            generatedIDs.append(newID)
    
    def testKeyLength(self):
        """ Tests the key Node ID key length """
        for i in range(20):
            id = self.node._generateID()
            # Key length: 20 bytes == 160 bits
            self.failUnlessEqual(len(id), 20, 'Length of generated ID is incorrect! Expected 160 bits, got %d bits.' % (len(id)*8))

    def testDistance(self):
        """ Test to see if distance method returns correct result"""
        
        # testList holds a couple 3-tuple (variable1, variable2, result)
        basicTestList = [('123456789','123456789', 0L), ('12345', '98765', 34527773184L)]

        for test in basicTestList:
            result = self.node._distance(test[0], test[1])
            self.failIf(result != test[2], 'Result of _distance() should be %s but %s returned' % (test[2], result))

        baseIp = '146.64.19.111'
        ipTestList = ['146.64.29.222', '192.68.19.333']

        distanceOne = self.node._distance(baseIp, ipTestList[0])
        distanceTwo = self.node._distance(baseIp, ipTestList[1])

        self.failIf(distanceOne > distanceTwo, '%s should be closer to the base ip %s than %s' % (ipTestList[0], baseIp, ipTestList[1]))

class NodeDataTest(unittest.TestCase):
    """ Test case for the Node class's data-related functions """
    def setUp(self):
        self.node = kademlia.node.Node()
        self.cases = (('a', 'hello there\nthis is a test'),
                     ('b', unicode('jasdklfjklsdj;f2352352ljklzsdlkjkasf\ndsjklafsd')),
                     ('e', 123),
                     ('f', [('this', 'is', 1), {'complex': 'data entry'}]),
                     ('aMuchLongerKeyThanAnyOfThePreviousOnes', 'some data'))
        
    def testStore(self):
        """ Tests if the node can store (and privately retrieve) some data """
        for key, value in self.cases:
            self.node.store(key, value, self.node.id)
        for key, value in self.cases:
            self.failUnless(key in self.node._dataStore, 'Stored key not found in node\'s DataStore: "%s"' % key)

class NodeContactTest(unittest.TestCase):
    """ Test case for the Node class's contact management-related functions """
    def setUp(self):
        self.node = kademlia.node.Node()
    
    def testAddContact(self):
        """ Tests if a contact can be added and retrieved correctly """
        import kademlia.contact
        # Create the contact
        h = hashlib.sha1()
        h.update('node1')
        contactID = h.digest()
        contact = kademlia.contact.Contact(contactID, '127.0.0.1', 91824, self.node._protocol)
        # Now add it...
        self.node.addContact(contact)
        # ...and request the closest nodes to it using FIND_NODE
        closestNodes = self.node._findCloseNodes(contactID, kademlia.constants.k)
        self.failUnlessEqual(len(closestNodes), 1, 'Wrong amount of contacts returned; expected 1, got %d' % len(closestNodes))
        self.failUnless(contact in closestNodes, 'Added contact not found by issueing _findCloseNodes()')
        
    def testAddSelfAsContact(self):
        """ Tests the node's behaviour when attempting to add itself as a contact """
        import kademlia.contact
        # Create a contact with the same ID as the local node's ID
        contact = kademlia.contact.Contact(self.node.id, '127.0.0.1', 91824, None)
        # Now try to add it
        self.node.addContact(contact)
        # ...and request the closest nodes to it using FIND_NODE
        closestNodes = self.node._findCloseNodes(self.node.id, kademlia.constants.k)
        self.failIf(contact in closestNodes, 'Node added itself as a contact')


class NodeLookupTest(unittest.TestCase):
    """ Test case for the Node class's iterative node lookup algorithm """
    def setUp(self):
        import kademlia.contact
        self.node = kademlia.node.Node()
        self.remoteNodes = []
        for i in range(10):
            remoteNode = kademlia.node.Node()
            remoteContact = kademlia.contact.Contact(remoteNode.id, '127.0.0.1', 91827+i, self.node._protocol)
            self.remoteNodes.append(remoteNode)
            self.node.addContact(remoteContact)

    def testIterativeFindNode(self):
        """ Ugly brute-force test to see if the iterative node lookup algorithm runs without failing """
        import kademlia.protocol
        kademlia.protocol.reactor.listenUDP(91826, self.node._protocol)
        for i in range(10):
            kademlia.protocol.reactor.listenUDP(91827+i, self.remoteNodes[i]._protocol)
        df = self.node.iterativeFindNode(self.node.id)
        df.addBoth(lambda _: kademlia.protocol.reactor.stop())
        kademlia.protocol.reactor.run()


def suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(NodeIDTest))
    suite.addTest(unittest.makeSuite(NodeDataTest))
    suite.addTest(unittest.makeSuite(NodeContactTest))
    suite.addTest(unittest.makeSuite(NodeLookupTest))
    return suite

if __name__ == '__main__':
    # If this module is executed from the commandline, run all its tests
    unittest.TextTestRunner().run(suite())
