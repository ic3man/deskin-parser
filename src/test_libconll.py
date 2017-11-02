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


# define the architecture of the network
model = Sequential()
model.add(Dense(768, input_dim=3072, init="uniform", activation="relu"))
model.add(Dense(384, init="uniform", activation="relu"))
model.add(Dense(2))
model.add(Activation("softmax"))
