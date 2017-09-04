# -*- coding: utf-8 -*-
"""
- Created on Wed Aug 23 13:51:46 2017
- Deskin - Orange Labs - Lannion - France

.. module:: libexceptions
    :platform: UNIX/Linux
    :synopsis: Collection of user-defined exceptions used in the API

.. moduleauthor:: Munshi Asadullah <munshi.asadullah@orange.com>

*The user-defined exceptions are put together in this libreary.*
"""
class dpGenericException(Exception):# - CLASS::START --------------------------
    """ *The base exception class for the deskinparser API. This can replace
    the requirement of an error or warning message generator and make the error
    tracking easier. Mostly going to be used as the base class for specific
    exceptions.*
    
    :param str expType: The type of exception e.g. ERROR, WARNING etc..
    :param expID: Unique ID associated with an exception.
    :type expID: int or float or str
    :param str expTitle: Title of the exception message.
    :param str expDetail: Description of the exception message.
    :param object expValue: The value that causes the exception.
    """
    def __init__(self, expType='GENERIC', expID=-1, 
                 expTitle='generic debug event', 
                 expDetail='generic debug event - details unknown', 
                 expValue=None): # - DEF::START -------------------------------
        self.type = expType
        self.id = expID
        self.title = expTitle
        self.detail = expDetail
        self.value = expValue

    def __str__(self): # - DEF::START -----------------------------------------
        return ('* {}[{}]::{}\n<{}>\nValue::{}\n').format(self.type, self.id, 
            self.title, self.detail, (repr(self.value)))
    
    def get_value(self):# - DEF::START ----------------------------------------
        return self.value
#==============================================================================

class invalidFilePathException(dpGenericException):# - CLASS::START -----------
    """ *The base class for the exceptions regarding file acces issues concerning
    path value or path errors. This is also the root exception raised for file
    access issues*
    
    :param expID: Unique ID associated with an exception.
    :type expID: int or float or str
    :param str expDetail: Description of the exception message.
    :param object expValue: The value that causes the exception.
    """
    def __init__(self, expID=0, expDetail=None, expValue=None): # - DEF::START 
        super(invalidFilePathException, self).__init__(expType='ERROR', 
            expID=expID, expTitle='Invalid File Path', expDetail=expDetail, 
            expValue=expValue)
#==============================================================================

class noneFilePathError(invalidFilePathException):# - CLASS::START ------------
    """ *The exception class is raised if the file path provided having a value
    None.*
    
    :param expID: Unique ID associated with an exception.
    :type expID: int or float or str
    :param str expDetail: Description of the exception message.
    :param object expValue: The value that causes the exception.
    """
    def __init__(self, expID=0, expValue=None): # - DEF::START ----------------
        super(noneFilePathError, self).__init__(expID=expID, 
            expDetail='File path cannot be "None".', expValue=expValue)
#==============================================================================

class nonStringFilePathError(invalidFilePathException):# - CLASS::START -------
    """ *The exception class is raised if the provided file path is not a String*
    
    :param expID: Unique ID associated with an exception.
    :type expID: int or float or str
    :param str expDetail: Description of the exception message.
    :param object expValue: The value that causes the exception.
    """
    def __init__(self, expID=0, expValue=None): # - DEF::START ----------------
        super(nonStringFilePathError, self).__init__(expID=expID, 
            expDetail='File path must be a String', expValue=expValue)
#==============================================================================

class zeroLengthStringPathError(invalidFilePathException):# - CLASS::START ----
    """ *The exception class is raised if the provided file path is a zero 
    length String*
    
    :param expID: Unique ID associated with an exception.
    :type expID: int or float or str
    :param str expDetail: Description of the exception message.
    :param object expValue: The value that causes the exception.
    """
    def __init__(self, expID=0, expValue=None): # - DEF::START ----------------
        super(zeroLengthStringPathError, self).__init__(expID=expID, 
            expDetail='File path must be a non zero length String', 
            expValue=expValue)
#==============================================================================

class pathDoesNotExistError(invalidFilePathException):# - CLASS::START --------
    """ *The exception class is raised if the provided file path is not a path
    at all ... nither file nor a directory*
    
    :param expID: Unique ID associated with an exception.
    :type expID: int or float or str
    :param str expDetail: Description of the exception message.
    :param object expValue: The value that causes the exception.
    """
    def __init__(self, expID=0, expValue=None): # - DEF::START ----------------
        super(pathDoesNotExistError, self).__init__(expID=expID, 
            expDetail='File path must be a real path', expValue=expValue)
#==============================================================================

class pathIsDirectoryException(invalidFilePathException):# - CLASS::START -----
    """ *The exception class is raised if the provided file path is a  directory
    rather than a file*
    
    :param expID: Unique ID associated with an exception.
    :type expID: int or float or str
    :param str expDetail: Description of the exception message.
    :param object expValue: The value that causes the exception.
    """
    def __init__(self, expID=0, expValue=None): # - DEF::START ----------------
        super(pathIsDirectoryException, self).__init__(expID=expID, 
            expDetail='File path is a directory', expValue=expValue)
#==============================================================================

