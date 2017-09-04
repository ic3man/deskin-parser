# -*- coding: utf-8 -*-
"""
Created on Tue Jul  4 14:58:58 2017

@author: munshi
"""

import libconll as lc

input_file = '/mnt/RAID0SHDD2X1TB/deskinparser/data.clean'

cr = lc.CoNLLReader(input_file=input_file, debug=False)
#cr = lc.CoNLLReader(input_file=input_file, debug=True)

md = cr.get_metadata()

print md.get_sentence_count()

#sc = md.get_sentence_configuration()
sc = md.get_morphological_class_value_map()

for i in range(5):
    print sc.get(sc.keys()[i])
    print

