# -*- coding: utf-8 -*-
"""
Created on Tue Jul  4 14:58:58 2017

@author: munshi
"""

import libbase as base
import libconll as conll
import libutilities as utils
import libexceptions as exp
import libvector as vec
import libdata as data

import traceback

from keras.models import Sequential
from keras.layers import Activation
from keras.optimizers import SGD
from keras.layers import Dense
from keras.utils import np_utils

input_file = '/mnt/RAID0SHDD2X1TB/deskin-parser/data/data.clean'

try:
    cfr = conll.CoNLLFileReader(input_file) # file reader object
    td = data.slidingWindowVectorData(cfr) # training data
except:
    traceback.print_exc()


layer_one_dimension = 768
layer_two_dimension = 768

# define the architecture of the network
model = Sequential()
model.add(Dense(layer_one_dimension, input_dim=td.get_input_dimension(), init="uniform", activation="relu"))
model.add(Dense(layer_two_dimension, init="uniform", activation="relu"))
model.add(Dense(td.get_output_dimension()))
model.add(Activation("softmax"))
