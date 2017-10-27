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

input_file = '/mnt/RAID0SHDD2X1TB/deskin-parser/data/data.clean'

try:
    cfr = conll.CoNLLFileReader(input_file)
    data.slidingWindowVectorData(cfr)
except:
    traceback.print_exc()

