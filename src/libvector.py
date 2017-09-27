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

#import os
#import sys

from codecs import open as utfOpen
from numpy import array as nparray
from numpy import zeros as npzeros

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
    
    def get_vector(self, key=None):
        raise exp.implimentationError('Class method not initialized yet.')
        
# CLASS ******************************************
class oneHotVectorReader(externalEmbeddingReader):
    
    def __init__(self, element_list=None, dimension=None):
        # test element list ---------------------------------------------------
        if element_list == None:
            raise exp.noneValueError('Element list cannot be "None"')
        elif not isinstance(element_list, list):
            raise TypeError('Element list must be a list object.\nFound: <{}>'.format(type(element_list)))
        elif not len(element_list):
            raise exp.zeroLengthValueError('Element list cannot be empty.')
        elif not all([isinstance(e, str) for e in element_list]):
            raise TypeError('Element list must be a list of str objects.')
        else:
            self.input = element_list
        # test dimension ------------------------------------------------------
        if dimension == None:
            self.dimension = len(self.input)
        elif dimension < len(self.input):
            raise exp.smallerValueError('Dimension cannot be smaller than the list size.\n{}(list)::{}(dimension)'.format(len(self.input), dimension))
        else:
            self.dimension = dimension
    
    def get_vector(self, key=None):
        if key == None:
            raise exp.noneValueError('Vector search key cnnot be "None"')
        try:
            vpos = self.input.index(key)
        except KeyError:
            raise KeyError('String doesnot exist in the input file.\nFound: {}'.format(key))
        vector = npzeros(self.dimension)
        vector[vpos] = 1.0
        return vector

# CLASS ******************************************
class word2vecTextReader(externalEmbeddingReader):
    
    def __init__(self, input_file=None):
        try:
            super(externalEmbeddingReader, self).__init__(input_file=input_file)
            self.file_pointer, self.dimensions, self.vector_count = self.init_format()
            self.vector_map = self.map_vectors()
        except:
            raise exp.initializationError('Failed to initalize reader object')
        
    def init_format(self):
        fp = utfOpen(self.input, 'r', 'UTF-8')
        dim, count = [int(e) for e in fp.readline().srtip().split()]
        return fp, dim, count
    
    def map_vectors(self):
        vmap = {}
        for i in range(self.vector_count):
            cseek = self.file_pointer.tell()
            key = self.file_pointer.readline().strip().split()[0].strip()
            vmap[key] = cseek
        return vmap
    
    def get_vector(self, key=None):
        if key == None:
            raise exp.noneValueError('Vector search key cnnot be "None"')
        try:
            vpos = self.vector_map.get(key)
        except KeyError:
            return False
        self.file_pointer.seek(vpos)
        return nparray(self.file_pointer.readline().strip().split()[1:].strip())

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
        self.metadata = self.reader.get_metadata()        
        # initiate base configuration -----------------------------------------
        self.vector_configuration = { utils.TOKEN     : (utils.ONE_HOT_VECTOR, 1.0),
                                      utils.LEMMA     : (utils.ONE_HOT_VECTOR, 1.0),
                                      utils.GPOS      : (utils.ONE_HOT_VECTOR, 1.0),
                                      utils.POS       : (utils.ONE_HOT_VECTOR, 1.0),
                                      utils.MORPH     : (utils.ONE_HOT_VECTOR, 1.0),
                                      utils.RELATION  : (utils.ONE_HOT_VECTOR, 1.0) }                                      
        # by default no embeddings shall be used ------------------------------
        self.relation_type = utils.SIMPLE_RELATION
        self.sentence_map = {}
    
    def update_configuration(self, key=None, vector_type=None, type_param=None):
        """ *The key method to manipulate the vector configuration. Each call may
        configure one vector part specified by the key. If custome embedding is 
        selected as the vector type, a valid embedding data file with correct 
        format value (default is Word2Vec Text Format) must be provided.*
        
        :param int key: The key to be configured. 
        :param int vector_type: The type of vector the key should be.
        :param externalEmbeddingReader embedding_reader: For external embedding the reader object (see note).
        :return: Nothing.
        :raise noneValueError: If the key is none.
        :raise noneValueError: If the embedding reader is none.
        :raise KeyError: If the key does not exist in the vector configuration.
        :raise ValueError: If the vector_type is not valid.
        :raise TypeError: If the embedding reader object is not of valid type.
        
        .. Note::
            The externalEmbeddingReader class is a generic class that is needed
            to be used to define specific classes for the embedding reader objects.
            
        """
        if key == None:
            raise exp.noneValueError('Configuration key cannot be "None"')
        elif key not in self.vector_configuration.keys():
            raise KeyError('The provided key doesnot exist.\nFound: {}'.format(key))
        # TODO:: if other vector types are to be introduced this list must be updated
        elif vector_type not in [None, utils.ONE_HOT_VECTOR, utils.EXTERNAL_EMBEDDING]:
            raise ValueError('Invalid vector ype.\nFound: {}'.format(vector_type))
        # If new vector types are introduced ... type specific conditional checks
        # should be implemented in this block. --------------------------------
        elif vector_type == utils.ONE_HOT_VECTOR:
            if type_param == None:
                raise exp.noneValueError('Vector dimension multiplier cannot be "None"')
            elif not isinstance(type_param, float):
                raise TypeError('The vector dimension multiplier must be float.\nFound: {}'.format(type(type_param)))
        elif vector_type == utils.EXTERNAL_EMBEDDING:
            if type_param == None:
                raise exp.noneValueError('Embedding reader cannot be "None"')
            elif not isinstance(type_param, externalEmbeddingReader):
                raise TypeError('The embedding reader object must be an instance of the generic "externalEmbeddingReader" class.\nFound: {}'.format(type(type_param)))
        else:
            self.vector_configuration[key] = [vector_type, type_param]
    
    def get_base_dimension(self, key=None):
        if key == None:
            raise exp.noneValueError('Configuration key cannot be "None"')
        elif key == utils.TOKEN:
            return self.metadata.get_token_count()
        else:
            raise KeyError('The provided key doesnot exist.\nFound: {}'.format(key))
    
    def get_element_list(self, key=None):
        if key == None:
            raise exp.noneValueError('Configuration key cannot be "None"')
        elif key == utils.TOKEN:
            return self.metadata.get_token_list()
        #TODO:: Many more :(
        else:
            raise KeyError('The provided key doesnot exist.\nFound: {}'.format(key))
    
    def generate_vector_profile(self, dim_multiplier=None):
        vprofile = {}
        # setting default or custome dimension multiplier ---------------------
        if dim_multiplier == None or not isinstance(dim_multiplier*1.0, dict):
            dim_multiplier = utils.ONE_HOT_VECTOR_DIMENSION_MULTIPLIER
        for key in self.vector_configuration.keys():
            vtype, vreader = self.vector_configuration.get(key)
            if vtype == utils.ONE_HOT_VECTOR:
                vprofile[key] = oneHotVectorReader(self.get_element_list(key), self.get_base_dimension(key)*dim_multiplier)
            elif vtype == utils.EXTERNAL_EMBEDDING:
                vprofile[key] = vreader
        return vprofile
    
    def vectorize(self):
        profile = self.generate_vector_profile()
        for k in sorted(profile.keys()):
            pass



