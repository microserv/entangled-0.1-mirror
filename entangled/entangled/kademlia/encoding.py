#!/usr/bin/env python
#
# This library is free software, distributed under the terms of
# the GNU Lesser General Public License Version 3, or any later version.
# See the COPYING file included in this archive
#
# The docstrings in this module contain epytext markup; API documentation
# may be created by processing this file with epydoc: http://epydoc.sf.net

class Encoding(object):
    """ Interface for RPC message encoders/decoders
    
    All encoding implementations used with this library should inherit and
    implement this.
    """
    def encode(self, data):
        """ Encode the specified data
        
        @param data: The data to encode
                     This method has to support encoding of the following
                     types: C{str}, C{int} and C{long}
                     Any additional data types may be supported as long as the
                     implementing class's C{decode()} method can successfully
                     decode them.
        
        @return: The encoded data
        @rtype: str
        """
    def decode(self, data):
        """ Decode the specified data string
        
        @param data: The data (byte string) to decode.
        @type data: str
        
        @return: The decoded data (in its correct type)
        """

class Bencode(Encoding):
    """ Implementation of the Bencode algorithm used by Bittorrent """
    
    def encode(self, data):
        """ Encoder implementation of the Bencode algorithm
        
        @param data: The data to encode
        @type data: int, long, tuple, list, dict or str
        
        @return: The encoded data
        @rtype: str
        """
        if type(data) in (int, long):
            return 'i%de' % data
        elif type(data) == str:
            return '%d:%s' % (len(data), data)
        elif type(data) in (list, tuple):
            encodedListItems = ''
            for item in data:
                encodedListItems += self.encode(item)
            return 'l%se' % encodedListItems
        elif type(data) == dict:
            encodedDictItems = ''
            keys = data.keys()
            keys.sort()
            for key in keys:
                encodedDictItems += self.encode(key)
                encodedDictItems += self.encode(data[key])
            return 'd%se' % encodedDictItems
        else:
            raise TypeError, "Cannot bencode '%s' object" % type(data)
    
    def decode(self, data):
        """ Decoder implementation of the Bencode algorithm 
        
        @param data: The encoded data
        @type data: str
        
        @note: This is a convenience wrapper for the recursive decoding
               algorithm, C{_decodeRecursive}
       
        @return: The decoded data, as a native Python type
        @rtype:  int, list, dict or str
        """
        return self._decodeRecursive(data)[0]
    
    @staticmethod
    def _decodeRecursive(data, startIndex=0):
        """ Actual implementation of the recursive Bencode algorithm
        
        Do not call this; use C{decode()} instead
        """
        if data[startIndex] == 'i':
            endPos = data[startIndex:].find('e')+startIndex
            return (int(data[startIndex+1:endPos]), endPos+1)
        elif data[startIndex] == 'l':
            startIndex += 1
            debugData = data[startIndex:]
            decodedList = []
            while data[startIndex] != 'e':
                debugData = data[startIndex:]
                listData, startIndex = Bencode._decodeRecursive(data, startIndex)
                debugData = data[startIndex:]
                decodedList.append(listData)
            return (decodedList, startIndex+1)
        elif data[startIndex] == 'd':
            startIndex += 1
            decodedDict = {}
            while data[startIndex] != 'e':
                key, startIndex = Bencode._decodeRecursive(data, startIndex)
                value, startIndex = Bencode._decodeRecursive(data, startIndex)
                decodedDict[key] = value
            return (decodedDict, startIndex)
        else:
            splitPos = data[startIndex:].find(':')+startIndex
            length = int(data[startIndex:splitPos])
            startIndex = splitPos+1
            endPos = startIndex+length
            bytes = data[startIndex:endPos]
            return (bytes, endPos)