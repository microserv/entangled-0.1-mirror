#!/usr/bin/env python
#
# This library is free software, distributed under the terms of
# the GNU Lesser General Public License Version 3, or any later version.
# See the COPYING file included in this archive

import hashlib
import unittest

import entangled.kademlia.node
import entangled.kademlia.constants

class NodeIDTest(unittest.TestCase):
    """ Test case for the Node class's ID """
    def setUp(self):
        self.node = entangled.kademlia.node.Node()

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


class NodeDataTest(unittest.TestCase):
    """ Test case for the Node class's data-related functions """
    def setUp(self):
        self.node = entangled.kademlia.node.Node()
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
        self.node = entangled.kademlia.node.Node()
    
    def testAddContact(self):
        """ Tests if a contact can be added and retrieved correctly """
        import entangled.kademlia.contact
        # Create the contact
        h = hashlib.sha1()
        h.update('node1')
        contactID = h.digest()
        contact = entangled.kademlia.contact.Contact(contactID, '127.0.0.1', 91824, self.node._protocol)
        # Now add it...
        self.node.addContact(contact)
        # ...and request the closest nodes to it using FIND_NODE
        closestNodes = self.node._routingTable.findCloseNodes(contactID, entangled.kademlia.constants.k)
        self.failUnlessEqual(len(closestNodes), 1, 'Wrong amount of contacts returned; expected 1, got %d' % len(closestNodes))
        self.failUnless(contact in closestNodes, 'Added contact not found by issueing _findCloseNodes()')
        
    def testAddSelfAsContact(self):
        """ Tests the node's behaviour when attempting to add itself as a contact """
        import entangled.kademlia.contact
        # Create a contact with the same ID as the local node's ID
        contact = entangled.kademlia.contact.Contact(self.node.id, '127.0.0.1', 91824, None)
        # Now try to add it
        self.node.addContact(contact)
        # ...and request the closest nodes to it using FIND_NODE
        closestNodes = self.node._routingTable.findCloseNodes(self.node.id, entangled.kademlia.constants.k)
        self.failIf(contact in closestNodes, 'Node added itself as a contact')


class NodeLookupTest(unittest.TestCase):
    """ Test case for the Node class's iterative node lookup algorithm """
    def setUp(self):
        import entangled.kademlia.contact
        self.node = entangled.kademlia.node.Node()
        self.remoteNodes = []
        for i in range(10):
            remoteNode = entangled.kademlia.node.Node()
            remoteContact = entangled.kademlia.contact.Contact(remoteNode.id, '127.0.0.1', 91827+i, self.node._protocol)
            self.remoteNodes.append(remoteNode)
            self.node.addContact(remoteContact)

#    def testIterativeFindNode(self):
#        """ Ugly brute-force test to see if the iterative node lookup algorithm runs without failing """
#        import entangled.kademlia.protocol
#        entangled.kademlia.protocol.reactor.listenUDP(91826, self.node._protocol)
#        for i in range(10):
#            entangled.kademlia.protocol.reactor.listenUDP(91827+i, self.remoteNodes[i]._protocol)
#        df = self.node.iterativeFindNode(self.node.id)
#        df.addBoth(lambda _: entangled.kademlia.protocol.reactor.stop())
#        entangled.kademlia.protocol.reactor.run()


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
