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
        self.input_data_matrix = {}
        self.outut_data_matrix = {}
        self.__populate_data_metrix()
        
    def __populate_data_metrix(self):     
        self.input_reader.reset()     
        curSentence = self.input_reader.get_current_sentence()
        while True:
            sentID = self.input_reader.get_current_sentence_id()        
            curSentence.sort(key = lambda x: int(x.getValue(utils.TID)))
            # input generation
            inputVectors = [self.vector_reader.get_vector(self.input_reader.get_current_sentence_id(), t.getValue(utils.TID)) for t in curSentence]
            for i in range(self.window_width - 1):
                inputVectors[:0] = [npzeros(self.vector_reader.get_vector_dimension())]
                inputVectors.apped(npzeros(self.vector_reader.get_vector_dimension()))
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
                curSentence.apped(utils.NULL)
            startIndex = 0
            endIndex = self.window_width
            counter = 0
            while True:            
                dataPoint1 = npzeros((self.window_width+3)*self.window_width)
                dataPoint2 = [None]*((self.window_width+3)*self.window_width)
                curBlock = [e for e in curSentence[startIndex:endIndex]]
                for i in range(self.window_width):
                    e = curBlock[i]
                    if e == utils.NULL:
                        continue
                    tid = int(e.getValue(utils.TID))
                    hid = int(e.getValue(utils.RELATION_HEAD))
                    if hid == 0:
                        dataPoint1[(self.window_width+3)*i] = 1.0
                        dataPoint2[(self.window_width+3)*i] = e.getValue(utils.RELATION)
                    else:
                        hIndex = next((j for j, item in enumerate(curBlock) if int(item.getValue(utils.TID)) == hid), -1)
                        if hIndex == -1:
                            if tid > hid:
                                dataPoint1[(self.window_width+3)*i+1] = 1.0
                                dataPoint2[(self.window_width+3)*i+1] = e.getValue(utils.RELATION)
                            elif tid < hid:
                                dataPoint1[(self.window_width+3)*i+2] = 1.0
                                dataPoint2[(self.window_width+3)*i+2] = e.getValue(utils.RELATION)
                        else:
                            dataPoint1[(self.window_width+3)*i+hIndex] = 1.0
                            dataPoint2[(self.window_width+3)*i+hIndex] = e.getValue(utils.RELATION)
                self.output_data_matrix[(sentID, counter)] = [dataPoint1, dataPoint2]
                if endIndex == len(inputVectors):
                    break
                else:
                    startIndex += 1
                    endIndex += 1
                    counter += 1
            try:
                curSentence = self.file_reader.get_next_sentence()
            except exp.lastElementWarning:
                break 
