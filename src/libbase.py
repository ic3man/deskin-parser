# -*- coding: utf-8 -*-
"""
Created on Fri Oct 20 09:25:02 2017

Deskin - Orange Labs - Lannion - France

.. module:: libvector
    :platform: UNIX/Linux
    :synopsis: Base class to convert a sentence into a vector

.. moduleauthor:: Munshi Asadullah <munshi.asadullah@orange.com>

*The module to generate vecors for a given file. Each vector shall represent 
one token and will be grouped by each sentence.*
"""

import libexceptions as exp

# CLASS *********************
class fileReader:
    
    file_pointer = None
    current_sentence = 1        
    sentence_buffer = []
    
    def get_key_elements(self, key=None):
        raise exp.implimentationError('Class method not initialized yet.')
    
    def get_current_sentence_id(self):
        return self.current_sentence
    
    def get_current_sentence(self):
        raise exp.implimentationError('Class method not initialized yet.')
    
    def get_next_sentence(self):
        raise exp.implimentationError('Class method not initialized yet.')
    
    def get_previous_sentence(self):
        raise exp.implimentationError('Class method not initialized yet.')

# CLASS *********************
class vectorReader:

    def get_vector(self, key=None):
        raise exp.implimentationError('Class method not initialized yet.')
    
    def updateReader(self, new_elements=None):
        raise exp.implimentationError('Class method not initialized yet.')

# CLASS *********************
class fileVectorReader:
    
    def set_one_hot_reader(self):
        raise exp.implimentationError('Class method not initialized yet.')
    
    def set_reader(self):
        raise exp.implimentationError('Class method not initialized yet.')
    
    def vectorize(self):
        raise exp.implimentationError('Class method not initialized yet.')
    
    def get_vector(self):
        raise exp.implimentationError('Class method not initialized yet.')
    
    def get_vector_dimension(self):
        raise exp.implimentationError('Class method not initialized yet.')

# CLASS *********************
class annotatedString:
    
    annotation_map = {}
    
    def getAnnotationKeyList(self):
        raise exp.implimentationError('Class method not initialized yet.')
    
    def setValue(self, annotation_key=None):
        raise exp.implimentationError('Class method not initialized yet.')
    
    def getValue(self, annotation_key=None):
        raise exp.implimentationError('Class method not initialized yet.')
