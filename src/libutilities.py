# -*- coding: utf-8 -*-
"""
- Created on Wed Jul 26 10:29:43 2017
- Deskin - Orange Labs - Lannion - France

.. module:: libutilities
    :platform: UNIX/Linux
    :synopsis: Collection of the common methods for deskin parser functionalities

.. moduleauthor:: Munshi Asadullah <munshi.asadullah@orange.com>

*The common methods and constants useful for deskin parser functionality and
not restricted to a singel module or a single class. One can call these
variables global dependencies for the parser functionality*
"""

import os
import hashlib

import libexceptions as exp

# constants: vector definition --------------------------------------------
# TODO: add or update if needed -------------------------------------------
TOKEN = 0
""" Pertaining to token or surface form of a unit element"""

LEMMA = 1
""" Pertaining to lemma of a unit element"""

GPOS = 2
""" Pertaining to general PoS of a unit element"""

POS = 3
""" Pertaining to deailes or more granuler PoS of a unit element"""

MORPH = 4
""" Pertaining to morphological definition of a unit element"""

RELATION = 5
""" Pertaining to dependency relation of a unit element"""

ONE_HOT_VECTOR = 6
""" One hot encoded vector"""

EXTERNAL_EMBEDDING = 7
""" Some sort of external embedding"""

SIMPLE_RELATION = 8
""" Defining the connection of an unit element to a relation through the
existance of the element in a particuler relation
"""

DETAIL_RELATION = 9
""" Defining the connection of an unit element to a relation through both 
the existance of the element in a particuler relation and whether it is the 
head or the dependance.
"""

ONE_HOT_VECTOR_DIMENSION_MULTIPLYER = 1.5
""" In case of one hot encoded vector definition the vector size multiplier 
allows the accomodation of new entitis to be incorporated in the vector.
"""

# constants: token definition type ----------------------------------------
# TODO: add or update if needed -------------------------------------------
BASIC_TEN_SLOT_TYPE = 10
""" The basic format of a line (a token definition) in CoNLL format 
"""

COMPOUND_DEFINITION = 11
""" A newer addition that represents the contraction (e.g. du = de + le) that
has been split into two tokens. The representation is the token IDs that are 
originaly together.
"""
#=====================

# constants: metadata related
# TODO: add or update if needed
META_EXTENSION = '.cmeta'
""" Extension for the metadata file
"""

HASH_BLOCKSIZE = 65536
""" Default buffer size for file hash generation
"""

FILE_HASH_VALUE = 12
SENTENCE_CONFIGURATION = 13
TOKEN_DISTRIBUTION = 14
LEMMA_DISTRIBUTION = 15
GPOS_DISTRIBUTION = 16
POS_DISTRIBUTION = 17
MORPHOLOGY_DISTRIBUTION = 18
RELATION_DISTRIBUTION = 19
""" Metadata data structure keys for json export and import (range 12-19)
"""
#=====================

def generate_hash(source_file=None): # - DEF::START ---------------------------
    """ Method to generate the hash value (SHA1) for the given input file 
    (*source_file*). Primary use is the comparison of a file in two different 
    time to test consistency.
    
    :param str source_file: The full path of the file to be hashed.
    :return: The hash code for the input file.
    :rtype: str
    :raise Exception: Source file path is not valid.
    
    >>> generate_hash(source_file='/my/own/path/fakedata.conll')
    '328eabe02b7e4540531681be603d51c5a0d97c53'
    
    .. Note::
        The source file cannot be None, has to be a String containing complete 
        path and must exist.
    """
    if doesTheFileExist(file_path=source_file):
        # now we are ready to generate the hash value
        hasher = hashlib.sha1()
        with open(source_file, 'rb') as sFile:
            buff = sFile.read(HASH_BLOCKSIZE)
            while len(buff) > 0:
                hasher.update(buff)
                buff = sFile.read(HASH_BLOCKSIZE)
        return hasher.hexdigest()
# ----------------------------------------------------------------- DEF:: END -

def is_integer(test_val=None): # - DEF::START ---------------------------------
    """ Method to test if the test value (*test_val*) is a valid integer or not. 
    If the test value is an integer **True** will be returned other wise a **False** 
    will be returned.    
    
    :param test_val: The value to be tested
    :type test_val: str or int or float
    :return: True or False
    :rtype: bool
        
    >>> is_integer(test_val="23")
    True
    >>> is_integer(test_val=2.0)
    True
    >>> is_integer(test_val="2.33")
    False
    """
    try:
        int(test_val)
    except:
        return False
    return True
# ----------------------------------------------------------------- DEF:: END -

def doesTheFileExist(file_path=None): # - DEF::START --------------------------
    """ Method to check if file path (*file_path*) is correct and the file 
    actually exists.
    
    :param str file_path: The full path of the file to be tested.
    :return: True.
    :rtype: bool
    :raise noneFilePathError: If the the file path is None.
    :raise nonStringFilePathError: If the the file path is not a String.
    :raise zeroLengthStringPathError: If the the file path is a zero length String.
    :raise pathDoesNotExistError: If file path doesnot exist.
    :raise newFileIOError: The directory exists but the file does not.
    :raise pathIsDirectoryException: If the path is a directory.

    >>> doesTheFileExist(file_path='/my/own/path/fakedata.conll')
    True
    """
    if file_path == None:
        raise exp.noneValueError('None was passed as file path')
    elif not isinstance(file_path, basestring):
        raise TypeError('File path is not a string.\nFound: <{}>'.format(type(file_path)))
    elif not len(file_path):
        raise exp.zeroLengthValueError('Empty string was passes as file path')
    elif not os.path.exists(file_path):
        if os.path.isdir(file_path):
            raise exp.pathTypeIOError('Path is not a file\nFound: <{}>'.format(file_path))
        elif os.path.isdir(os.path.dirname(file_path)):
            raise exp.newFileIOError('Found parent directory but the file deos not exist')
        raise exp.invalidPathIOError('Path does not exist.\nFound: <{}>'.format(file_path))
   
    return True
# ----------------------------------------------------------------- DEF:: END -

