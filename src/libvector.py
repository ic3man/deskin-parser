# -*- coding: utf-8 -*-
"""
Created on Tue Jul 18 11:21:34 2017

Deskin - Orange Labs - Lannion - France

.. module:: libvector
    :platform: UNIX/Linux
    :synopsis: Base class to convert a sentence into a vector

.. moduleauthor:: Munshi Asadullah <munshi.asadullah@orange.com>

*The module to generate vecors for a given file. Each vector shall represent 
one token and will be grouped by each sentence.*
"""

import os
import sys

#import libconll

import libutilities as utils
import libexceptions as exp

class unitVectorConfiguration:
    """ The class to be used to define the input vectors for the parsing task. 
        A default configuration will be initialized along with the API 
        providing options to configure as per necessary.
    """
    
    BASE_CONFIGURATION = { utils.TOKEN     : utils.ONE_HOT_VECTOR,
                           utils.LEMMA     : utils.ONE_HOT_VECTOR,
                           utils.GPOS      : utils.ONE_HOT_VECTOR,
                           utils.POS       : utils.ONE_HOT_VECTOR,
                           utils.MORPH     : utils.ONE_HOT_VECTOR,
                           utils.RELATION  : utils.SIMPLE_RELATION }
    """ The base configuration is the basis of how the unit vectors shall be
        defined. The update to this configuration will occure, during the 
        execution of the constructor or afterward through the updates of other
        models e.g. update of "EXTERNAL_EMBEDDING" will also update this
        configuration model.
    """
    
    EXTERNAL_EMBEDDING = { utils.TOKEN     : None,
                           utils.LEMMA     : None,
                           utils.GPOS      : None,
                           utils.POS       : None,
                           utils.MORPH     : None,
                           utils.RELATION  : None }
    """ The external embedding model allowes the use of externer embeddings for
        different elements of a unit vector. The changes for this model can be 
        made during the execution of the constructor or afterward through
        update method ().
    """
    
    def __init__(self, 
                 reader=None,
                 external = None,
                 relation = None,
                 debug=False): # DEF:: START ----------------------------------
        """ The default constructor for defining unit vector
        """
        if reader == None:
            print 'error' # TODO::
        self.reader = reader
        self.metadata = self.reader.get_metadata()
        self.external = external if self.validate_external_embedding(external) else None
        self.update_configuration(relation)
    
    def validate_external_embedding(embedding_map=None): # DEF:: START ------------------------------
        pass
    
    def update_configuration(self, rel_type=None):
        pass
        