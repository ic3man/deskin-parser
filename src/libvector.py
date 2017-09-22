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



import libconll as conll
import libutilities as utils
import libexceptions as exp

# CLASS *********************
class externalEmbeddingReader:
    
    def __init__(self, input_file=None):
        try:
            if utils.doesTheFileExist(input_file):
                self.input = input_file
        except:
            raise IOError('Embedding file error')
        

# CLASS ******************************************
class word2vecTextReader(externalEmbeddingReader):
    
    def __init__(self, input_file=None):
        try:
            super(externalEmbeddingReader, self).__init__(input_file=input_file)
            self.checkInputFileFormat()
        except:
            raise exp.initializationError('Failed to initalize reader object')
        
    def checkInputFileFormat(self):
        pass

# CLASS *************
class CoNLLFileVector:
    """ *The class when initiated with a CoNLLReader object, shall provide the 
    framework to vectorize a file. It will also allow the vectorization to be
    configured. The base configuration is to use all the elements and one hot 
    vector encoding for all components.*
        
    :param libconll.CoNLLReader reader: The CoNLLReader object to be vectorized. 
    :return: Nothing.
    :raise noneValueError: If the value for reader is none.
    :raise TypeError: If the value for reader is not a CoNLLReader object.
    
    .. Note::
        **The vector configuration** is a dictionary of key of each part of token
        information (i.e. surface form, lemma etc.) to a tupple of type of 
        vector, vector data source and source format. The last 2 values are
        relevent if external embedding is used. If the type of vector is set
        to "None"
    
    .. Note::
        **The relation type** defines the vector configuration of the relations.
        The simple type is just the vector for the relation. The detailed type 
        adds a parity to define wheather the token is the source or the target
        of the relation.
    """
    def __init__(self, reader=None):
        # test reader ---------------------------------------------------------
        if reader == None:
            raise exp.noneValueError('Reader cannot be "None"')
        elif not isinstance(reader, conll.CoNLLReader):
            raise TypeError('Reader must be a CoNLLReader object.\nFound: <{}>'.format(type(reader)))
        else:
            self.reader = reader
        # initiate base configuration -----------------------------------------
        self.vector_configuration = { utils.TOKEN     : (utils.ONE_HOT_VECTOR, None),
                                      utils.LEMMA     : (utils.ONE_HOT_VECTOR, None),
                                      utils.GPOS      : (utils.ONE_HOT_VECTOR, None),
                                      utils.POS       : (utils.ONE_HOT_VECTOR, None),
                                      utils.MORPH     : (utils.ONE_HOT_VECTOR, None),
                                      utils.RELATION  : (utils.ONE_HOT_VECTOR, None) }
        # by default no embeddings shall be used ------------------------------
        self.relation_type = utils.SIMPLE_RELATION
        self.sentence_map = {}
    
    def update_configuration(self, key=None, vector_type=None, embedding_reader=None):
        """ *The key method to manipulate the vector configuration. Each call may
        configure one vector part specified by the key. If custome embedding is 
        selected as the vector type, a valid embedding data file with correct 
        format value (default is Word2Vec Text Format) must be provided.*
        
        :param libconll.CoNLLReader reader: The CoNLLReader object to be vectorized. 
        :return: Nothing.
        :raise noneValueError: If the value for reader is none.
        :raise TypeError: If the value for reader is not a CoNLLReader object.
        
        .. Note::
            
        """
        if key == None:
            raise exp.noneValueError('Configuration key cannot be "None"')
        elif key not in self.vector_configuration.keys():
            raise KeyError('The provided key doesnot exist.\nFound: {}'.format(key))
        # TODO:: if other vector types are to be introduced this list must be updated
        elif vector_type not in [None, utils.ONE_HOT_VECTOR, utils.EXTERNAL_EMBEDDING]:
            raise ValueError('Invalid vector ype.\nFound: {}'.format(vector_type))
        # If new vector types are introduced ... type specific conditional checks
        # should be implemented in this block.
        # check block ---------------------------------------------------------
        elif vector_type == utils.EXTERNAL_EMBEDDING:
            try:
                if utils.doesTheFileExist(embedding):
                    if embedding_format not in [utils.WORD2VEC_TEXT, utils.WORD2VEC_BINARY]:
                        raise ValueError('Invalid embedding format value found./nFound: {}'.format(embedding_format))
            except:
                raise ValueError('For external embedding ... a valid file must be provided')
        
            