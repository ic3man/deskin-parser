# -*- coding: utf-8 -*-
"""
Created on Wed Oct 25 15:36:00 2017

Deskin - Orange Labs - Lannion - France

.. module:: libdata
    :platform: UNIX/Linux
    :synopsis: The module to generate data for training and testing the parser.

.. moduleauthor:: Munshi Asadullah <munshi.asadullah@orange.com>

*The module to generate vecors for a given file. Each vector shall represent 
one token and will be grouped by each sentence.*
"""

import libbase as base

from codecs import open as utfOpen

from numpy import array as nparray
from numpy import zeros as npzeros
from numpy import concatenate as npcat

import libconll as conll
import libutilities as utils
import libexceptions as exp
import libvector as vec

import pandas as pd
       
# CLASS ******************************************
class slidingWindowVectorData:
    
    def __init__(self, file_reader=None, vector_config=None, window_width=10):
        if file_reader == None:
            raise exp.noneValueError('File reader cannot be "None"')
        elif not isinstance(file_reader, base.fileReader):
            raise TypeError('File reader must be a fileReader onject.\nFound: {}'.format(type(file_reader)))
        else:
            self.input_reader = file_reader
            # initiate a vector reader using the file reader object
            self.vector_reader = vec.CoNLLFileVector(file_reader)
            if self.vector_reader == None:
                raise exp.noneValueError('File vector reader cannot be "None"')
            elif not isinstance(self.vector_reader, base.fileVectorReader):
                raise TypeError('File vector reader must be a fileVectorReader onject.\nFound: {}'.format(type(self.vector_reader)))
            # configure file vector reader by setting specific vector readers
            if vector_config == None:
                self.vector_reader.set_one_hot_reader(utils.TOKEN)
                self.vector_reader.set_one_hot_reader(utils.GPOS)
            else:
                if not isinstance(vector_config, dict):
                    raise TypeError('Vector configuration must be a dictionary.\nFound: {}'.format(type(vector_config)))
                else:
                    for k in vector_config.keys():
                        self.vector_reader.set_reader(k, vector_config.get(k))
            self.vector_reader.vectorize()
        if window_width < 2:
            raise ValueError('Window width cannot be less than {}.\nFound: {}'.format(2, window_width))
        else:
            self.window_width = window_width
        self.relation_reader = vec.listOneHotVectorReader(element_list=self.input_reader.get_key_elements(key=utils.RELATION))
        self.input_data_matrix = {}
        self.output_data_matrix = {}
        self.__populate_data_metrix()
        
    def __populate_data_metrix(self):
        self.input_reader.reset()
        curSentence = self.input_reader.get_current_sentence()
        while True:
            """
            print '>>SENT[', self.input_reader.get_current_sentence_id(), ']',  len(curSentence)
            print curSentence
            print
            """
            # input data generation
            sentID = self.input_reader.get_current_sentence_id()
            curSentence.sort(key = lambda x: x.getValue(utils.TID))
            # input generation
            inputVectors = [self.vector_reader.get_vector(self.input_reader.get_current_sentence_id(), t.getValue(utils.TID)) for t in curSentence]
            for i in range(self.window_width - 1):
                inputVectors[:0] = [self.vector_reader.get_null_vector()]
                inputVectors.append(self.vector_reader.get_null_vector())
            startIndex = 0
            endIndex = self.window_width
            counter = 0
            while True:
                dataPoint = npcat([inputVectors[i] for i in range(startIndex, endIndex)])
                self.input_data_matrix[(sentID, counter)] = dataPoint
                if endIndex == len(inputVectors):
                    break
                else:
                    startIndex += 1
                    endIndex += 1
                    counter += 1
            
            # Output generation
            for i in range(self.window_width - 1):
                curSentence[:0] = [utils.NULL]
                curSentence.append(utils.NULL)

            startIndex = 0
            endIndex = self.window_width
            counter = 0
            while True:            
                dataPoint = []
                for e in curSentence[startIndex:endIndex]:
                    if e == utils.NULL:
                        dataPoint.append([self.relation_reader.get_null_vector()]*(self.window_width+3))
                    else:
                        hid = e.getValue(utils.RELATION_HEAD)
                        rmap = [self.relation_reader.get_null_vector()]*(self.window_width+3)
                        rel = self.relation_reader.get_vector(key=e.getValue(utils.RELATION))
                        if hid == 0:
                            rmap[0] = rel
                            dataPoint.append(rmap)
                        else:
                            hIndex = next((j for j, item in enumerate(curSentence) if item != utils.NULL and item.getValue(utils.TID) == hid), -1)
                            if hIndex == -1:
                                raise KeyError('Invalid token ID found')
                            elif hIndex < startIndex:
                                rmap[1] = rel
                                dataPoint.append(rmap)
                            elif hIndex >= endIndex:
                                rmap[2] = rel
                                dataPoint.append(rmap)
                            else:
                                rmap[3+hIndex-startIndex] = rel
                                dataPoint.append(rmap)
                self.output_data_matrix[(sentID, counter)] = npcat([npcat(e) for e in dataPoint])
                if endIndex == len(inputVectors):
                    break
                else:
                    startIndex += 1
                    endIndex += 1
                    counter += 1
            curSentence = None
            try:
                curSentence = self.input_reader.get_next_sentence()
            except exp.lastElementWarning:
                break 
    
    def get_datapoint_index_list(self):
        return self.input_data_matrix.keys()
    
    def get_input_dimension(self):
        return len(self.input_data_matrix.values()[0])

    def get_output_dimension(self):
        return len(self.output_data_matrix.values()[0])