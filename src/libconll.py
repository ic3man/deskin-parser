# -*- coding: utf-8 -*-
"""
Created on Thu Jun 22 16:50:26 2017

Deskin - Orange Labs - Lannion - France

.. module:: libconll
    :platform: UNIX/Linux
    :synopsis: CoNLL format text processing library

.. moduleauthor:: Munshi Asadullah <munshi.asadullah@orange.com>

*Module containing classes to process a CoNLL format text file for further use.
The Primary use is as a sentence stream for quick travarsal of the content.*
"""

import os
import sys

import json

from codecs import open as utfOpen

import libutilities as utils
import libexceptions as exp

# CLASS:: data-structure for the metadata of a CoNLL format file --------------
# =============================================================================
class CoNLLMetaData:
    """ *The class that shall provide the data structure and the supporting 
    methods to store, manipulate and access metadata extracted from a file in 
    CoNLL format. CoNLL metadata initialization method will allow us to make 
    decisions regarding metadata analysis, loading and saving.*
        
    :param str input_file: The input file in CoNLL format
    :param str meta_file: The metadata file associated with the input_file
    :return: Nothing.
    :raise invalidFilePathException: If the input file path is invalid.
    
    .. Note::
        The decisions making process of loading metadata or generate 
        and eventually saving can be decribed by the following algorithm,
        
        - If the meatfile exists *i.e.* a valid path is provides and the file \
        exists, we shall check if there is any thing in the file *i.e.* the \
        length of the file is not zero.
        - Now we shall try to open the file.
        - Once opened we shall check if all the data keys are present.
        - If so we shall retrieve the input hash value and compare it with the \
        calculated input file hash value to determine if the input file is the \
        actual input file associeated with the metadata.
        - Failiure at any of the previous steps will invoce the analysis method \
        thus genarating the metadata ans saving it.
        - If metadata file name provided exist the new metadata will be saved \
        by rewriting the file.
        - Otherwise if the directory path of the metafile name exist or the \
        metfile name is an existing directory itself, the new metadata will be \
        saved in that directory.
        - For any other case the metafile will be generated in the same path \
        where the input file is.
    """
    def __init__(self, input_file=None, meta_file=None): # DEF:: START --------
        # check input file path -----------------------------------------------
        try:
            utils.doesTheFileExist(file_path=input_file)
        except exp.invalidFilePathException as e:
            print >> sys.stderr, e
            raise exp.invalidFilePathException(expID='001-INPUT', 
                                               expDetail='Input file path error detected.', 
                                               expValue=input_file)
        # split the file path and the file name -------------------------------
        head, tail = os.path.split(input_file)
        # class variables -----------------------------------------------------
        self.file_location = head #-------------------------------------------- input file path
        self.file_name, self.file_extension = os.path.splitext(tail) #--------- input file name and extension
        self.file_hash_value = None #------------------------------------------ hash value of the input file (for change in file monitoring)
        self.sentence_configuration = {} #------------------------------------- sentence number to file pointer offset map (starting with sentence 0)
        self.token_distribution_map = {}
        self.lemma_distribution_map = {}
        self.gpos_distribution_map = {}
        self.pos_distribution_map = {}
        self.morphology_distribution_map = {}
        self.relation_distribution_map = {}
        # slelct the metadata file ... either the provided path or local path -        
        try:
            utils.doesTheFileExist(file_path=meta_file)              
        except (exp.noneFilePathError, 
                exp.nonStringFilePathError, 
                exp.zeroLengthStringPathError, 
                exp.pathDoesNotExistError):
            meta_file = self.file_location + '/' + self.file_name + utils.META_EXTENSION
        except exp.pathIsDirectoryException:
            meta_file = meta_file + '/' + self.file_name + utils.META_EXTENSION
        # analyze or load metadata --------------------------------------------
        if not self.load_metadate(meta_file=meta_file, current_hash=utils.generate_hash(source_file=input_file)):
            self.analyze(in_file=input_file)
            self.save_metadata(meta_file=meta_file)

    def get_sentence_count(self):
        """ *Returns the number of sentences in the file.*
        
        :param: Nothing
        :return: The number of sentencs.
        :rtype: int
        """
        return len(self.sentence_configuration)
    
    def get_sentence_configuration(self, sentence_number=None):
        """ *Returns the sentence configurations for the input file either all 
        the sentences or for a specific sentence. The formal way to get all 
        configurations is to call the fuction without any arguments.*
        
        :param int sentence_number: The specific sentence configuaration to return.
        :return: One or all the sentence configurations.
        :rtype: list(list(str, int)) or dict(int, list(list(str, int)))
        
        .. Note::
            Sentence configuration is a list of tuples ... token ID as found 
            followed by the type of token that was found.
        """
        if sentence_number == None:
            return self.sentence_configuration
        return self.sentence_configuration.get(sentence_number)
    
    def get_token_count(self):
        """ *Returns the total number of unique tokens in the input file.*
        
        :return: number of unique tokens.
        :rtype: int
        """
        return len(self.token_distribution_map)
    
    def get_token_list(self):
        """ *Returns the list of unique tokens in the input file.*
        
        :return: list of unique tokens.
        :rtype: list[str]
        """
        return self.token_distribution_map.keys()
        
    def get_token_distribution(self):
        """ *Map of token distribution i.e. map of token to its frequency.*
        
        :return: map of token to its frequency.
        :rtype: map[str, int]
        """
        return self.token_distribution_map
        
    def get_lemma_count(self):
        return len(self.lemma_distribution_map)
    
    def get_lemma_list(self):
        return self.lemma_distribution_map.keys()
        
    def get_lemma_distribution(self):
        return self.lemma_distribution_map
    
    def get_generic_pos_count(self):
        return len(self.gpos_distribution_map)
    
    def get_generic_pos_list(self):
        return self.gpos_distribution_map.keys()
        
    def get_generic_pos_distribution(self):
        return self.gpos_distribution_map
    
    def get_pos_count(self):
        return len(self.pos_distribution_map)
    
    def get_pos_list(self):
        return self.pos_distribution_map.keys()
        
    def get_pos_distribution(self):
        return self.pos_distribution_map
    
    def get_relation_count(self):
        return len(self.relation_distribution_map)
    
    def get_relation_distribution(self):
        return self.relation_distribution_map
    
    def get_morphological_class_value_map(self):
        return {k:v.keys() for k,v in self.morphology_distribution_map.items()}
    
    def detect_token_type(self, tok=None):
        if tok == None: # empty token is a no no ------------------------------
            return None
        # in the presence of a valid token we can start figuring out the type of the token definition
        tokFragment = [e.strip() for e in tok.strip().split()]
        if len(tokFragment) == 10: # the standard 10 slot CoNLL format
            return utils.BASIC_TEN_SLOT_TYPE
        elif len(tokFragment) == 1: # compund description e.g. 3-4
            compound_parts = tokFragment[0].strip().split('-')
            if len(compound_parts) > 1 and all([utils.is_integer(e) for e in compound_parts]):
                return utils.COMPOUND_DEFINITION
        # ================================================================================================
        # TODO: update this if...else sequence to make changes to the token types or add a totally new one
        # ================================================================================================
        return None
    
    def save_metadata(self, meta_file=None):
        json_data = {utils.FILE_HASH_VALUE:         self.file_hash_value,
                     utils.SENTENCE_CONFIGURATION:  self.sentence_configuration,
                     utils.TOKEN_DISTRIBUTION:      self.token_distribution_map,
                     utils.LEMMA_DISTRIBUTION:      self.lemma_distribution_map,
                     utils.GPOS_DISTRIBUTION:       self.gpos_distribution_map,
                     utils.POS_DISTRIBUTION:        self.pos_distribution_map,
                     utils.MORPHOLOGY_DISTRIBUTION: self.morphology_distribution_map,
                     utils.RELATION_DISTRIBUTION:   self.relation_distribution_map }
        with utfOpen(meta_file, mode='w', encoding='UTF-8') as fp:
           json.dump(json_data, fp)
        
    def load_metadate(self, meta_file=None, current_hash=-1):
        json_data = None
        try:
            if utils.doesTheFileExist(file_path=meta_file):
                # check if the metadata file is empty or not
                if os.stat(meta_file).st_size == 0:
                    return False
            # now load the file
            fp = utfOpen(meta_file, mode='r', encoding='UTF-8')
            # loading metadata
            json_data = json.load(fp)
            # we are done with file
            fp.close()
        except:
            return False
        # check if invalid data type is loaded
        if not isinstance(json_data, dict):
            return False
        # check if all the keys are present
        elif set(json_data.keys()) != set(utils.META_KEYS):
            return False       
        # check if the hash value from the meta file matches the recalculated
        # hash value indicating changes in the original file ------------------
        elif json_data.get(utils.FILE_HASH_VALUE) != current_hash:
            return False
        else:
            try:
                self.file_hash_value = json_data.get(utils.FILE_HASH_VALUE)
                self.sentence_configuration = json_data.get(utils.SENTENCE_CONFIGURATION)
                self.token_distribution_map = json_data.get(utils.TOKEN_DISTRIBUTION)
                self.lemma_distribution_map = json_data.get(utils.LEMMA_DISTRIBUTION)
                self.gpos_distribution_map = json_data.get(utils.GPOS_DISTRIBUTION)
                self.pos_distribution_map = json_data.get(utils.POS_DISTRIBUTION)
                self.morphology_distribution_map = json_data.get(utils.MORPHOLOGY_DISTRIBUTION)
                self.relation_distribution_map = json_data.get(utils.RELATION_DISTRIBUTION)
            except KeyError:
                return False
        return True
        
    def update_morphology_map(self, morph_string=None, debug=False):
        if debug: # debug input file name ---------------------
            print >> sys.stderr, '>>> debug:: CoNLLMetaData :: update_morphology_map()'
            print >> sys.stderr, 'morph (value):: {}'.format(morph_string)
            print >> sys.stderr, 'morph (type):: {}\n'.format(type(morph_string))
        # $ end debug $ -------------------------------------------------------
        if morph_string == '_' or morph_string == None or not len(morph_string.strip()):
            return
        for g in [e.strip().split('=') for e in morph_string.strip().split('|')]:
            self.morphology_distribution_map[g[0]] = self.morphology_distribution_map.get(g[0], {})
            self.morphology_distribution_map[g[0]][g[1]] = self.morphology_distribution_map[g[0]].get(g[1], 0) + 1
    
    def analyze(self, in_file=None, debug=False):
        # generate hash value -------------------------------------------------
        self.file_hash_value = utils.generate_hash(in_file)
        # open file for processing --------------------------------------------
        fp = utfOpen(in_file, mode='r', encoding='UTF-8')
        # initiate local variables --------------------------------------------
        offsetValue = fp.tell()
        lineCounter = 0
        sentenceCounter = 0 
        sentenceBuffer = []
        # process the file line by line ---------------------------------------
        for line in fp: # read a lines ----------------------------------------
            lineCounter += 1 # increment line counter -------------------------
            if not len(line.strip()): # --------------------------------------- either a sentence boundery or just an empty line
                if not len(sentenceBuffer): # --------------------------------- just an empty line before any sentence is buffered
                    offsetValue = fp.tell()
                    continue # let's go back to work --------------------------
                for tokDef in sentenceBuffer: # ------------------------------- cycle through the sentence buffer
                    tokType = self.detect_token_type(tokDef) # ---------------- detect the token type
                    if tokType == utils.BASIC_TEN_SLOT_TYPE: # ------------ actions to be taken if a basic 10 slot line is found
                        tid, sur, lem, gpos, pos, morph, head, rel, idc0, idc1 = [e.strip() for e in tokDef.strip().split()]
                        # check if token ID (tid) is valid --------------------
                        if not len(tid) or tid == '_' or not utils.is_integer(test_val=tid):
                            errLine = lineCounter - len(sentenceBuffer) + sentenceBuffer.index(tokDef) + 1
                            utils.debugPrinter(dClass='CoNLLMetaData',
                                                   dDef='analyze()',
                                                   dDescript='token id value erroe',
                                                   dMsg='invalid token id detected on line {} of {} ... exiting to system'.format(errLine, self.get_file_name()),
                                                   dElement=tokDef)
                            sys.exit(-1) # can't continue with wrong token ID -
                        
                        self.token_distribution_map[sur.lower()] = self.token_distribution_map.get(sur.lower(), 0) + 1
                        self.lemma_distribution_map[lem.lower()] = self.lemma_distribution_map.get(lem.lower(), 0) + 1
                        self.gpos_distribution_map[gpos.lower()] = self.gpos_distribution_map.get(gpos.lower(), 0) + 1
                        self.pos_distribution_map[pos.lower()] = self.pos_distribution_map.get(pos.lower(), 0) + 1
                        if debug: # debug input file name ---------------------
                            print >> sys.stderr, '>>> debug:: CoNLLMetaData :: analyze()'
                            print >> sys.stderr, 'morph (line {}):: {}'.format(lineCounter, morph)
                            print >> sys.stderr, 'morph (type):: {}\n'.format(type(morph))
                        # $ end debug $ -------------------------------------------------------
                        self.update_morphology_map(morph_string=morph, debug=debug)
                        self.relation_distribution_map[rel.lower()] = self.relation_distribution_map.get(rel.lower(), 0) + 1
                        self.sentence_configuration[sentenceCounter][-1].append([tid, tokType])
                    elif tokType == utils.COMPOUND_DEFINITION:
                        self.sentence_configuration[sentenceCounter][-1].append([tid, tokType])
                    else:
                        utils.debugPrinter(dClass='CoNLLMetaData',
                                           dDef='analyze()',
                                           dDescript='token type error',
                                           dMsg='invalid token type detected on line {} of {}'.format(lineCounter, self.get_file_name()),
                                           dElement=tokDef)
                sentenceBuffer = [] #------------------------------------------ reset the sentence buffer
            else:
                # just found the first token of the first sentence or any other sentence on that matter
                if not sentenceCounter or not len(sentenceBuffer):
                    sentenceCounter += 1
                    # initiate sentence configuration for the new sentence
                    # each sentence configuration is comprised of two elements
                    # an integer for the starting line number
                    # followed by a list of token types expected
                    self.sentence_configuration[sentenceCounter] = [lineCounter, offsetValue, []]
                sentenceBuffer.append(line.strip())
            offsetValue = fp.tell()

        fp.close()#------------------------------------------------------------ close the file
# CLASS:: END =================================================================



# CLASS:: a class of sudo stream of CoNLL format sentences --------------------
# =============================================================================
class CoNLLReader: 
    
    def __init__(self, 
                 input_file=None, 
                 meta_file=None, 
                 debug=False):

        if debug: # debug input file name -------------------------------------
            print >> sys.stderr, '>>> debug:: CoNLLReader :: __init__()'
            print >> sys.stderr, 'input file:: {}\n'.format(input_file)
        # $ end debug $ -------------------------------------------------------
       
       # load metadta --------------------------------------------------------
        self.metadata = CoNLLMetaData(input_file=input_file, 
                                      meta_file=meta_file, debug=debug)
        # check for successful metadata loading -------------------------------
        if not self.metadata:
            utils.debugPrinter(dClass='CoNLLReader',
                               dDef='__init__()',
                               dDescript='input file error',
                               dMsg='either invalid input file is found or failed to load metadata ... exiting to system',
                               dElement=input_file)
            sys.exit(-1) # exit to system -------------------------------------
        # load file pointer of the input file ---------------------------------
        self.file_pointer = utfOpen(input_file, mode='r', encoding='UTF-8')
        self.current_sentence = 1        
        self.sentence_buffer = []
            
    def get_metadata(self):
        return self.metadata
    
    def read_sentence(self):
        lineC, position, config = self.metadata.get_sentence_configuration(sentence_number=self.current_sentence)
        self.file_pointer.seek(position)
        sentenceBuffer = []
        for line in self.file_pointer:
            # either a sentence boundery or just an empty line ----------------
            if not len(line.strip()):
                # just an empty line before any sentence is buffered ----------
                if not len(sentenceBuffer):
                    utils.debugPrinter( dType='WARNING',
                                        dClass='CoNLLReader',
                                        dDef='read_sentence()',
                                        dDescript='empty line in a sentence block',
                                        dMsg='sentence buffer empty ... empty line detected on line {} in sentence {}'.format(lineC, self.current_sentence),
                                        dElement=sentenceBuffer)
                    continue # this is a precaution and should not happend ----
                for i in range(len(sentenceBuffer)):#-------------------------------  cycle through the sentence buffer
                    tokDef = sentenceBuffer[i]
                    tokType = config[i]
                    if tokType == utils.BASIC_TEN_SLOT_TYPE:
                        self.sentence_buffer.append([e.strip() for e in tokDef.strip().split()])
                return
            else:
                sentenceBuffer.append(line.strip())
                lineC += 1
    
    def get_current_sentence(self):
        if not len(self.sentence_buffer):
            self.read_sentence()
        return self.sentence_buffer
    
    def get_next_sentence(self):
        if self.current_sentence == self.metadata.get_total_sentence_count():
            utils.debugPrinter( dType='WARNING',
                                dClass='CoNLLReader',
                                dDef='get_next_sentence()',
                                dDescript='last sentence',
                                dMsg='EOF found ... current sentence is the last sentence',
                                dElement=self.current_sentence)
            return False
        self.current_sentence += 1
        self.read_sentence()
        return self.sentence_buffer
    
    def get_previous_sentence(self):
        if self.current_sentence == 1:
            utils.debugPrinter( dType='WARNING',
                                thdClass='CoNLLReader',
                                dDef='get_previous_sentence()',
                                dDescript='first sentence',
                                dMsg='current sentence is e first sentence',
                                dElement=self.current_sentence)
            return False
        self.current_sentence -= 1
        self.read_sentence()
        return self.sentence_buffer

# CLASS:: END =================================================================
