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

import numpy as np

#input_file = '/mnt/RAID0SHDD2X1TB/deskin-parser/data/data.clean'
#input_file = '/mnt/RAID0SHDD2X1TB/deskin-parser/data/fr-ud-train.tilt-201703-proj.conllu.clean.train.conll'
input_file = '/home/ic3man/work/deskin-parser/data/fr-ud-train.tilt-201703-proj.conllu.clean.train.conll'

try:
    cfr = conll.CoNLLFileReader(input_file) # file reader object
    td = data.slidingWindowVectorData(cfr) # training data
except:
    traceback.print_exc()


dm = td.get_dataset(train=0.7, test=0.3)
train_in, train_out = dm.get('train')
test_in, test_out = dm.get('test')


layer_one_dimension = 100
layer_two_dimension = 100

# define the architecture of the network
model = Sequential()
model.add(Dense(layer_one_dimension, input_dim=td.get_input_dimension(), init="uniform", activation="relu"))
model.add(Dense(layer_two_dimension, init="uniform", activation="relu"))
model.add(Dense(td.get_output_dimension()))
model.add(Activation("softmax"))


print '>>>', type(train_in[0]), train_in[0].shape

model.compile(loss='binary_crossentropy', optimizer='adam', metrics=['accuracy'])
print(model.summary())
model.fit(np.array(train_in), np.array(train_out), nb_epoch=10, batch_size=1)

scores = model.evaluate(np.array(test_in), np.array(test_out), verbose=0)
print("Accuracy: %.2f%%" % (scores[1]*100))
