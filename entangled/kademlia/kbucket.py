#!/usr/bin/env python
#
# This library is free software, distributed under the terms of
# the GNU Lesser General Public License Version 3, or any later version.
# See the COPYING file included in this archive
#
# The docstrings in this module contain epytext markup; API documentation
# may be created by processing this file with epydoc: http://epydoc.sf.net

import constants

class BucketFull(Exception):
    """ Raised when the bucket is full """


class KBucket(object):
    """ Description - later
    """
    def __init__(self):
        self._contacts = list()

    def addContact(self, contact):
        """ Add contact to _contact list in the right order. This will move the
        contact to the end of the k-bucket if it is already present.
        
        @raise kademlia.kbucket.BucketFull: Raised when the bucket is full and
                                            the contact isn't in the bucket
                                            already
        
        @param contact: The contact to add
        @type contact: kademlia.contact.Contact
        """
        if contact in self._contacts:
            # Move the existing contact to the end of the list
            # TODO: maybe use the new contact (IP address may have changed, etc)
            self._contacts.append( self._contacts.pop( self._contacts.index(contact) ) )
        elif len(self._contacts) < constants.k:
            self._contacts.append(contact)
        else:
            raise BucketFull("No space in bucket to insert contact")


    def getContacts(self, count=-1):
        """ Returns a list containing up to the first count number of contacts
        
        @param count: The amount of contacts to return (if 0 or less, return
                      all contacts)
        @type count: int
        
        @raise IndexError: If the number of requested contacts is too large
        
        @return: Return up to the first count number of contacts in a list
                If no contacts are present an empty is returned
        @rtype: list
        """
        # Return all contacts in bucket
        if count <= 0:
            count = len(self._contacts)

        # Get current contact number
        currentLen = len(self._contacts)

        # If count greater than k - return only k contacts
        # !!VERIFY!! behaviour
        if count > constants.k:
            count = constants.k
            raise IndexError('Count value too big adjusting to bucket size')

        # Check if count value in range and,
        # if count number of contacts are available
        if not currentLen:
            contactList = list()

        # length of list less than requested amount
        elif currentLen < count:
            contactList = self._contacts[0:currentLen]
        # enough contacts in list
        else:
            contactList = self._contacts[0:count]

        return contactList

    def removeContact(self, contact):
        """ Remove given contact from list
        
        @param contact: The contact to remove
        @type contact: kademlia.contact.Contact
        
        @raise ValueError: The specified contact is not in this bucket
        """
        self._contacts.remove(contact)

