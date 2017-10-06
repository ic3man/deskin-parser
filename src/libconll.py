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
    def __init__(self, input_file=None, meta_file=None, save_meta=True): # DEF:: START --------
        # check input file path -----------------------------------------------
        try:        
            utils.doesTheFileExist(file_path=input_file)
        except:
            raise IOError('Input File I/O error.')
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
        skip_loading = False
        try:
            utils.doesTheFileExist(file_path=meta_file)
        except exp.newFileIOError:
            skip_loading = True
        except (TypeError, ValueError, exp.invalidPathIOErro):
            meta_file = self.file_location + '/' + self.file_name + utils.META_EXTENSION
        except exp.pathTypeIOError:
            meta_file = meta_file + '/' + self.file_name + utils.META_EXTENSION
        # analyze or load metadata --------------------------------------------
        try:
            if skip_loading:
                raise exp.skipStepWarning
            # attempting to load metadata -------------------------------------
            self.load_metadate(meta_file=meta_file, current_hash=utils.generate_hash(source_file=input_file))
        except Warning:
            print >> sys.stderr, 'WARNING: running analysis ...'
            print >> sys.stderr, 'Metadata: {}'.format(meta_file)
        except StandardError as e:
            print >> sys.stderr, 'WARNING: Failed loading metadata file ... running analysis.'
            print >> sys.stderr, e            
        # running analysis ----------------------------------------------------
        self.analyze(in_file=input_file)
        # saving metadata -----------------------------------------------------
        if save_meta == None:
            raise exp.noneValueError('save_meta option flag cnnot be "None"')
        elif not isinstance(save_meta, bool):
            raise TypeError('save_meta option flag must be bool type.\nFound: <{}>'.format(type(save_meta)))
        elif save_meta:
            try:
                self.save_metadata(meta_file=meta_file)
            except Exception as e:
                print >> sys.stderr, 'WARNING: Metadata file not saved... re-analysis will be needed next time.'
                print >> sys.stderr, e

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
        :raise KeyError: If the **sentence_number** does not exist.
        
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
        """ *Returns the total number of unique lemmas in the input file.*
        
        :return: number of unique lemmas.
        :rtype: int
        """
        return len(self.lemma_distribution_map)
    
    def get_lemma_list(self):
        """ *Returns the list of unique lemmas in the input file.*
        
        :return: list of unique lemmas.
        :rtype: list[str]
        """
        return self.lemma_distribution_map.keys()
        
    def get_lemma_distribution(self):
        """ *Map of token distribution i.e. map of lemmas to its frequency.*
        
        :return: map of lemmas to its frequency.
        :rtype: map[str, int]
        """
        return self.lemma_distribution_map
    
    def get_generic_pos_count(self):
        """ *Returns the total number of unique generic PoS in the input file.*
        
        :return: number of unique generic PoS.
        :rtype: int
        """
        return len(self.gpos_distribution_map)
    
    def get_generic_pos_list(self):
        """ *Returns the list of unique generic PoS in the input file.*
        
        :return: list of unique generic PoS.
        :rtype: list[str]
        """
        return self.gpos_distribution_map.keys()
        
    def get_generic_pos_distribution(self):
        """ *Map of token distribution i.e. map of generic PoS to its frequency.*
        
        :return: map of generic PoS to its frequency.
        :rtype: map[str, int]
        """
        return self.gpos_distribution_map
    
    def get_pos_count(self):
        """ *Returns the total number of unique fine-grained PoS in the input file.*
        
        :return: number of unique fine-grained PoS.
        :rtype: int
        """
        return len(self.pos_distribution_map)
    
    def get_pos_list(self):
        """ *Returns the list of unique fine-grained PoS in the input file.*
        
        :return: list of unique fine-grained PoS.
        :rtype: list[str]
        """
        return self.pos_distribution_map.keys()
        
    def get_pos_distribution(self):
        """ *Map of token distribution i.e. map of fine-grained PoS to its frequency.*
        
        :return: map of fine-grained PoS to its frequency.
        :rtype: map[str, int]
        """
        return self.pos_distribution_map
    
    def get_relation_count(self):
        """ *Returns the total number of unique relation types in the input file.*
        
        :return: number of unique relation types.
        :rtype: int
        """
        return len(self.relation_distribution_map)
    
    def get_relation_list(self):
        """ *Returns the list of unique relation types in the input file.*
        
        :return: list of unique relation types.
        :rtype: list[str]
        """
        return self.relation_distribution_map.keys()
        
    def get_relation_distribution(self):
        """ *Returns the map of token distribution i.e. map of relation types 
        to its frequency.*
        
        :return: map of relation types to its frequency.
        :rtype: map[str, int]
        """
        return self.relation_distribution_map
    
    def get_morphological_class_value_map(self):
        """ *Returns the map of morphological class to its possible values.*
        
        :return: map of morphological classes to values.
        :rtype: dict[str, list]
        """
        return {k:v.keys() for k,v in self.morphology_distribution_map.items()}
    
    def detect_token_type(self, tok=None):
        """ *Detects and returns the type of token as defined in the utility 
        module.* 
        
        :param str tok: The token definition for detection.
        :return: token type defined in *libutilities* module.
        :raise TypeError: If token definition is not a string.
        :raise zeroLengthValueError: If the token definition is empty.
        :raise undefinedTypeError: If undefined token type is detected.
        
        .. Note::
            The token definitions types are defined in the utility module. 
            Additional types can be introduced and the if-else block is needed 
            to be updated to accomodate any new type.
        """
        # empty or non string token is a no no ------------------------------
        if tok == None or not isinstance(tok, basestring):
            raise TypeError('Token string must be a string.\nFound: {}'.format(type(tok)))
        elif not len(tok):
            raise exp.zeroLengthValueError('Token string cannot be empty')
        # in the presence of a valid token we can start figuring out the type of the token definition
        tokFragment = [e.strip() for e in tok.strip().split()]
        if len(tokFragment) == 10: # the standard 10 slot CoNLL format
            return utils.BASIC_TEN_SLOT_TYPE
        elif len(tokFragment) == 1: # compund description e.g. 3-4
            compound_parts = tokFragment[0].strip().split('-')
            if len(compound_parts) > 1 and all([utils.is_integer(e) for e in compound_parts]):
                return utils.COMPOUND_DEFINITION
        else:
            raise exp.undefinedTypeError('Undefined token configuration found.')
        # =====================================================================
        # TODO: update this if...elif...else sequence to make changes to the
        #       token types or add a totally new one
        # =====================================================================
        return None
    
    def save_metadata(self, meta_file=None):
        """ *Save the extracted metadata into the provided metadata file.*
        
        :param str meta_file: The metafile path to save the data.
        :return: Nothing
        :raise IOError: By `file access <https://docs.python.org/2/library/functions.html#open>`_.
        :raise ValueError: By `unicode file access <https://docs.python.org/2/library/codecs.html#codecs.open>`_.
        :raise ValueError: By `JSON dump <https://docs.python.org/2/library/json.html#json.dump>`_.
        :raise OverflowError: By `JSON dump <https://docs.python.org/2/library/json.html#json.dump>`_.
        :raise TypeError: By `JSON dump <https://docs.python.org/2/library/json.html#json.dump>`_.
        
        .. Note::
            The default value of **meta_file** is a sheer formality because of
            the structure of the class. This function should only be called by 
            the initialization method and that shall raise exceptions if there 
            is some sort of anomaly in the file name or in the file path.
        """
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
        """ *Load meta data to class variables from the provided file.*
        
        :param str meta_file: The metafile path.
        :param str current_hash: Hash value to be compared for consistency.
        :return: Nothing
        :raise IOError: By `file access <https://docs.python.org/2/library/functions.html#open>`_.
        :raise ValueError: By `unicode file access <https://docs.python.org/2/library/codecs.html#codecs.open>`_.
        :raise zeroLengthValueError: If metafile is empty.
        :raise TypeError: If loaded data is not a dict.
        :raise notAllKeyError: If loaded data does not contain all the JSON data keys.
        :raise unequalValueError: If current hash does not match the saved hash value.
        """
        try:
            utils.doesTheFileExist(file_path=meta_file)
            # check if the metadata file is empty or not
            if os.stat(meta_file).st_size == 0:
                raise exp.zeroLengthValueError('The metafile is empty.')
        except:
            raise IOError('Metadata file does not exist.')
        # now load the file
        fp = utfOpen(meta_file, mode='r', encoding='UTF-8')
        # loading metadata
        json_data = json.load(fp)
        # we are done with file
        fp.close()
        # check if invalid data type is loaded
        if not isinstance(json_data, dict):
            raise TypeError('JSON data must be a dict.\nFound: <{}>'.format(type(json_data)))
        # check if all the keys are present
        elif set(json_data.keys()) != set(range(utils.FILE_HASH_VALUE, utils.RELATION_DISTRIBUTION+1)):
            raise exp.notAllKeyError('Not all the JSON data keys are present.')
        # check if the hash value from the meta file matches the recalculated
        # hash value indicating changes in the original file ------------------
        elif json_data.get(utils.FILE_HASH_VALUE) != current_hash:
            raise exp.unequalValueError('The current hash of the input file does not match the metafile data.')
        else:
            self.file_hash_value = json_data.get(utils.FILE_HASH_VALUE)
            self.sentence_configuration = json_data.get(utils.SENTENCE_CONFIGURATION)
            self.token_distribution_map = json_data.get(utils.TOKEN_DISTRIBUTION)
            self.lemma_distribution_map = json_data.get(utils.LEMMA_DISTRIBUTION)
            self.gpos_distribution_map = json_data.get(utils.GPOS_DISTRIBUTION)
            self.pos_distribution_map = json_data.get(utils.POS_DISTRIBUTION)
            self.morphology_distribution_map = json_data.get(utils.MORPHOLOGY_DISTRIBUTION)
            self.relation_distribution_map = json_data.get(utils.RELATION_DISTRIBUTION)
        return
        
    def update_morphology_map(self, morph_string=None):
        """ *Updates the class variable for keeping the map of morphological 
        classes (e.g. gender, number etc.) to the map of possible values (e.g. 
        masculin, feminin etc. for gender) to their respective frequency.*
        
        :param str morph_string: The morphological information string.
        :return: map of maps of morphological class to value to frequency.
        :rtype: dict[str, dict[str, int]]
        """
        if morph_string == None or morph_string == '_' or not len(morph_string.strip()):
            return
        for g in [e.strip().split('=') for e in morph_string.strip().split('|')]:
            self.morphology_distribution_map[g[0]] = self.morphology_distribution_map.get(g[0], {})
            self.morphology_distribution_map[g[0]][g[1]] = self.morphology_distribution_map[g[0]].get(g[1], 0) + 1
    
    def analyze(self, in_file=None):
        """ *Load and analyze the input file to generate metadata and update 
        class level variables.*
        
        :param str in_file: The CoNLL format file to be analyzed.
        :return: Nothing.
        :raise IOError: If hash value generation for the input file fails.
        :raise IOError: By `file access <https://docs.python.org/2/library/functions.html#open>`_.
        :raise ValueError: By `unicode file access <https://docs.python.org/2/library/codecs.html#codecs.open>`_.
        :raise ValueError: If invalid, non integer token ID is found.
        :raise TypeError: If invalidtoken type is found.
        """
        # generate hash value -------------------------------------------------
        try:
            self.file_hash_value = utils.generate_hash(in_file)
        except Exception:
            raise IOError('Hash generation failed.')
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
                while len(sentenceBuffer): # ---------------------------------- cycle through the sentence buffer
                    tokDef = sentenceBuffer.pop(0)
                    try: # ---------------------------------------------------- detect the token type
                        tokType = self.detect_token_type(tok=tokDef)
                    except:
                        raise TypeError('Failed detecting token type found [line: {}]'.format(lineCounter-len(sentenceBuffer)+1))
                    # lets deal with a valid token ----------------------------
                    if tokType == utils.BASIC_TEN_SLOT_TYPE: # ------------ actions to be taken if a basic 10 slot line is found
                        tid, sur, lem, gpos, pos, morph, head, rel, idc0, idc1 = [le.strip() for le in tokDef.strip().split()]
                        # check if token ID (tid) is valid --------------------
                        if not utils.is_integer(test_val=tid):
                            raise ValueError('Invalid token id found [line: {}]'.format(lineCounter-len(sentenceBuffer)+1))
                        self.token_distribution_map[sur.lower()] = self.token_distribution_map.get(sur.lower(), 0) + 1
                        self.lemma_distribution_map[lem.lower()] = self.lemma_distribution_map.get(lem.lower(), 0) + 1
                        self.gpos_distribution_map[gpos.lower()] = self.gpos_distribution_map.get(gpos.lower(), 0) + 1
                        self.pos_distribution_map[pos.lower()] = self.pos_distribution_map.get(pos.lower(), 0) + 1
                        self.update_morphology_map(morph_string=morph)
                        self.relation_distribution_map[rel.lower()] = self.relation_distribution_map.get(rel.lower(), 0) + 1
                        self.sentence_configuration[sentenceCounter][-1].append([tid, tokType])
                    elif tokType == utils.COMPOUND_DEFINITION:
                        self.sentence_configuration[sentenceCounter][-1].append([tid, tokType])
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
    """ *This class when instantiated will provide a reader object that can be 
    used to access a CoNLL format text file. The specific benifits could be 
    the direct access to sentences by index.*
        
    :param str input_file: The input file in CoNLL format
    :param str meta_file: The metadata file associated with the input_file
    :return: Nothing.
    :raise metadataValueError: If the metadata object failed to initialize.
    """
    def __init__(self, input_file=None, meta_file=None):
        # load metadta ---------------------------------------------------------
        try:
            self.metadata = CoNLLMetaData(input_file=input_file, meta_file=meta_file)
        except:
            raise exp.metadataValueError('Metadata object returned an exception.')
        # load file pointer of the input file ---------------------------------
        self.file_pointer = utfOpen(input_file, mode='r', encoding='UTF-8')
        self.current_sentence = 1        
        self.sentence_buffer = []
            
    def get_metadata(self):
        """ *Returns the total number of unique relation types in the input file.*
    
        :return: The metadata data container for the input file.
        :rtype: CoNLLMetaData object
        """
        return self.metadata
    
    def read_sentence(self):
        """ *Reads the sentence referenced by the index number found in the 
        class variable current_sentence and load it in the sentence buffer.*
        
        :return: Nothing.
        :raise KeyError: If the sentence ID is unknown.       
        """
        try:        
            initLine, position, config = self.metadata.get_sentence_configuration(sentence_number=self.current_sentence)
        except KeyError:
            raise KeyError('Failed to load sentence configuration for the ID: {}.'.format(self.current_sentence))
        self.file_pointer.seek(position)
        sentenceBuffer = []
        lineOffset = 0
        for line in self.file_pointer:
            # either a sentence boundery or just an empty line ----------------
            if not len(line.strip()):
                # just an empty line before any sentence is buffered ----------
                if not len(sentenceBuffer):
                    try:
                        raise exp.emptyLineWarning('Unexpected empty line found in line: {}'.format(initLine+lineOffset))
                    except exp.emptyLineWarning as w:
                        print >> sys.stderr, w
                    lineOffset += 1
                    continue # this is a precaution but should not happend ----
                for i in range(len(sentenceBuffer)):#-------------------------------  cycle through the sentence buffer
                    if config[i] == utils.BASIC_TEN_SLOT_TYPE:
                        self.sentence_buffer.append([e.strip() for e in sentenceBuffer[i].strip().split()])
            else:
                sentenceBuffer.append(line.strip())
                lineOffset += 1
    
    def get_sentence(self):
        """ *Returns the current sentence buffer. However, if the buffer is empty 
        the read_sentence() method will be called to load the buffer first.*
        
        :return: The sentence buffer.
        :rtype: The sentence buffer data structure (see Note)
        :raise KeyError: If the sentence ID is unknown for the read call.
        
        ..Note::
            The data structure is a list of lists where the inner list is the 
            list of each component of a token definition in CoNLL format. The 
            buffer itself represents one sentence.
        """
        if not len(self.sentence_buffer):
            self.read_sentence()
        return self.sentence_buffer
    
    def get_next_sentence(self):
        """ *Loads the next sentence with respect to the current position
        specified by **current_sentence**.*
        
        :return: The sentence buffer.
        :rtype: The sentence buffer data structure.
        :raise lastElementWarning: If the current sentence is the last sentence.
        """
        if self.current_sentence == self.metadata.get_total_sentence_count():
            raise exp.lastElementWarning('Current sentence is the last sentence.')
        self.current_sentence += 1
        self.read_sentence()
        return self.sentence_buffer
    
    def get_previous_sentence(self):
        """ *Loads the previous sentence with respect to the current position
        specified by **current_sentence**.*
        
        :return: The sentence buffer.
        :rtype: The sentence buffer data structure.
        :raise firstElementWarning: If the current sentence is the first sentence.
        """
        if self.current_sentence == 1:
            raise exp.firstElementWarning('Current sentence is the first sentence.')
        self.current_sentence -= 1
        self.read_sentence()
        return self.sentence_buffer        

# CLASS:: END =================================================================
