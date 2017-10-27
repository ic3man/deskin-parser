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

import libbase as base

from codecs import open as utfOpen

from numpy import array as nparray
from numpy import zeros as npzeros
from numpy import concatenate as npcat

import libconll as conll
import libutilities as utils
import libexceptions as exp
       
# CLASS ******************************************
class listOneHotVectorReader(base.vectorReader):
    
    def __init__(self, element_list=None, dimension_multiplier=1.3):
        # test element list ---------------------------------------------------
        if element_list == None:
            raise exp.noneValueError('Element list cannot be "None"')
        elif not isinstance(element_list, list):
            raise TypeError('Element list must be a list object.\nFound: <{}>'.format(type(element_list)))
        elif not len(element_list):
            raise exp.zeroLengthValueError('Element list cannot be empty.')
        else:
            self.elements = element_list
        # test dimension ------------------------------------------------------
        if dimension_multiplier == None:
            dimension_multiplier = 1.3
        elif dimension_multiplier < 1.0:
            raise exp.smallerValueError('Dimension multiplier cannot be smaller than 1.\nFound: {}'.format(dimension_multiplier))
        self.dimension =  int(round(len(self.elements)*dimension_multiplier))
    
    def updateReader(self, update_elements=None):
        if update_elements == None:
            raise exp.noneValueError('Additional element list cannot be "None"')
        elif not isinstance(update_elements, list):
            raise TypeError('Additional element list must be a list object.\nFound: <{}>'.format(type(update_elements)))
        elif not len(update_elements):
            raise exp.zeroLengthValueError('Additional element list cannot be empty.')
        else:
            # filter elements and add them to the elements list
            self.elements.extend([e for e in update_elements if e not in self.elements])
            if len(self.elements) > self.dimension:
                raise exp.greaterValueError('Exceeding vector dimension limit.\n{}(old):{}(new)'.format(self.dimension, len(self.elements)))
        
    def get_vector(self, key=None):
        if key == None:
            raise exp.noneValueError('Vector search key cannot be "None"')
        try:
            vpos = self.elements.index(key)
        except KeyError:
            raise KeyError('Key doesnot exist in the vocabulary.\nFound: {}'.format(key))
        vector = npzeros(self.dimension)        
        vector[vpos] = 1.0
        return vector

# CLASS ******************************************
class classMembersOneHotVectorReader(base.vectorReader):
    
    def __init__(self, class_list_map=None, dimension_multiplier=1.3):
        # test element list ---------------------------------------------------
        if class_list_map == None:
            raise exp.noneValueError('The class list map cannot be "None"')
        elif not isinstance(class_list_map, dict):
            raise TypeError('The class list map must be a dict object.\nFound: <{}>'.format(type(class_list_map)))
        elif not len(class_list_map):
            raise exp.zeroLengthValueError('The class list map cannot be empty.')
        else:
            self.elements = class_list_map
            self.classes = class_list_map.keys()
        # test dimension ------------------------------------------------------
        if dimension_multiplier == None:
            dimension_multiplier = 1.3
        elif dimension_multiplier < 1.0:
            raise exp.smallerValueError('Dimension multiplier cannot be smaller than 1.\nFound: {}'.format(dimension_multiplier))
        self.dimension = {k: int(round(len(self.elements.get(k))*dimension_multiplier)) for k in sorted(self.elements.keys())}
    
    def updateReader(self, update_elements=None):
        if update_elements == None:
            raise exp.noneValueError('Additional class list map cannot be "None"')
        elif not isinstance(update_elements, dict):
            raise TypeError('Additional class list map must be a dict object.\nFound: <{}>'.format(type(update_elements)))
        elif not len(update_elements):
            raise exp.zeroLengthValueError('Additional class list map cannot be empty.')
        else:
            for k in update_elements.keys():
                if k not in self.classes:
                    self.classes.append(k)
                    self.elements[k] = update_elements.get(k)
                    self.dimension[k] = len(update_elements.get(k))
                else:
                    self.elements[k] = self.elements.get(k, [])
                    self.elements[k].extend([e for e in update_elements.get(k) if e not in self.elements[k]])                
                    if len(self.elements.get(k)) > self.dimension.get(k):
                        raise exp.greaterValueError('Exceeding vector dimension limit for the class: {}.\n{}(old):{}(new)'.format(k, self.dimension, len(self.elements)))
    
    def get_vector(self, key=None):
        if key == None:
            raise exp.noneValueError('Vector search key cannot be "None"')
        elif not isinstance(key, dict):
            raise TypeError('Vector search key must be a dict object.\nFound: <{}>'.format(type(key)))
        for k in key.keys():
            if k not in self.classes:
                raise KeyError('Class doesnot exist in the vocabulary.\nFound: {}'.format(k))
            elif key.get(k) not in self.elements.get(k):
                raise KeyError('A value for the class::{} doesnot exist.\nFound: {}'.format(k, key.get(k)))
        vectorList = []
        for c in self.classes:
            vectorPart = npzeros(self.dimension.get(c))
            if c in key.keys():
                vectorPart[self.elements.get(c).index(key.get(c))] = 1.0
            vectorList.append(vectorPart)        
        return npcat(vectorList)

# CLASS ******************************************
class word2vecTextReader(base.vectorReader):
    
    def __init__(self, input_file=None):
        try:
            if utils.doesTheFileExist(input_file):
                self.input = input_file
            self.file_pointer, self.vector_count, self.dimension = self.__init_format()
            self.vector_map = self.__map_vectors()
        except:
            raise exp.initializationError('Failed to initalize reader object')
        
    def __init_format(self):
        fp = utfOpen(self.input, 'r', 'UTF-8')
        vocabSize, vecSize = [int(e) for e in fp.readline().srtip().split()]
        return fp, vecSize, vocabSize
    
    def __map_vectors(self):
        vmap = {}
        for i in range(self.vector_count):
            cseek = self.file_pointer.tell()
            key = self.file_pointer.readline().strip().split()[0].strip()
            vmap[key] = cseek
        return vmap
    
    def getDimension(self):
        return self.dimension
    
    def getVectorCount(self):
        return self.vector_count
    
    def updateReader(self, new_elements=None):
        return
    
    def get_vector(self, key=None):
        if key == None:
            raise exp.noneValueError('Vector search key cannot be "None".')
        try:
            vpos = self.vector_map.get(key)
        except KeyError:
            return npzeros(self.getDimension())
        self.file_pointer.seek(vpos)
        return nparray(self.file_pointer.readline().strip().split()[1:].strip())

# CLASS *************
class CoNLLFileVector(base.fileVectorReader):
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
    def __init__(self, file_reader=None):
        # test reader ---------------------------------------------------------
        if file_reader == None:
            raise exp.noneValueError('Data file reader cannot be "None"')
        elif not isinstance(file_reader, base.fileReader):
            raise TypeError('Reader must be a fileReader object.\nFound: <{}>'.format(type(file_reader)))
        else:
            self.file_reader = file_reader
        # initiate base configuration -----------------------------------------
        self.vector_configuration = { utils.TOKEN     : None,
                                      utils.LEMMA     : None,
                                      utils.GPOS      : None,
                                      utils.POS       : None,
                                      utils.MORPH     : None }
        # by default no embeddings shall be used ------------------------------
        self.sentence_map = {}
    
    def set_one_hot_reader(self, key=None, dimension_multiplier=1.3):
        if key == None:
            raise exp.noneValueError('Configuration key cannot be "None"')
        elif key not in self.vector_configuration.keys():
            raise KeyError('The provided key doesnot exist.\nFound: {}'.format(key))
        else:
            if dimension_multiplier == None:
                dimension_multiplier = 1.3
            elif dimension_multiplier < 1.0:
                raise exp.smallerValueError('Dimension multiplier cannot be smaller than 1.0.\nFound: {}'.format(dimension_multiplier))
            key_elements = self.file_reader.get_key_elements(key=key)
            if isinstance(key_elements, list):
                self.vector_configuration[key] = listOneHotVectorReader(key_elements, dimension_multiplier)
            elif isinstance(key_elements, dict):
                self.vector_configuration[key] = classMembersOneHotVectorReader(key_elements, dimension_multiplier)
            else:
                raise TypeError('Invalid Key Element data type found, expected list or dict.\nFound: {}'.format(type(key_elements)))
                    
    def set_reader(self, key=None, reader=None):
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
        elif reader == None:
            raise exp.noneValueError('The reader object cannot be "None"')
        elif not isinstance(reader, base.fileReader):
            raise TypeError('The reader must be a fileReader object.\nFound: {}'.format(type(reader)))
        else:
            self.vector_configuration[key] = reader
    
    def vectorize(self):
        self.file_reader.reset()
        if all([e == None for e in self.vector_configuration.values()]):
            raise exp.noneValueError('All values of vector configuration is "None"')
        elif any([e != None and not isinstance(e, base.vectorReader) for e in self.vector_configuration.values()]):
            raise TypeError('Invalid vector configuration value found.\nFound: {}'.format(self.vector_configuration))
        vectorKeys = sorted([k for k in self.vector_configuration.keys() if self.vector_configuration.get(k) != None])
        curSentence = self.file_reader.get_current_sentence()        
        while True:            
            if curSentence == None:
                raise exp.noneValueError('Sentence cannot be "None"')
            elif not isinstance(curSentence, list):
                raise TypeError('Sentence must be a list')
            elif not all([isinstance(e, base.annotatedString) for e in curSentence]):
                raise TypeError('Sentence must be a list of "annotatedString"')
            curSentenceMap = {}
            for tok in curSentence:
                vector_list = []
                for key in vectorKeys:
                    vector_list.append(self.vector_configuration.get(key).get_vector(tok.getValue(key)))
                curSentenceMap[tok.getValue(utils.TID)] = npcat(vector_list)
            self.sentence_map[self.file_reader.get_current_sentence_id()] = curSentenceMap
            try:
                curSentence = self.file_reader.get_next_sentence()
            except exp.lastElementWarning:
                break

    def get_vector(self, sentence_id=None, token_id=None):
        if sentence_id == None:
            raise exp.noneValueError('Sentence ID cannot be "None"')
        elif token_id == None:
            raise exp.noneValueError('Token ID cannot be "None"')
        elif sentence_id not in self.sentence_map.keys():
            raise KeyError('The provided sentence ID doesnot exist.\nFound: {}'.format(sentence_id))
        
        elif token_id not in self.sentence_map.get(sentence_id).keys():
            raise KeyError('The provided token ID doesnot exist.\nFound: {}'.format(token_id))
        else:
            return self.sentence_map.get(sentence_id).get(token_id)
    
    def get_vector_dimension(self):
        return len(self.sentence_map.get(1).get(1))
    
    