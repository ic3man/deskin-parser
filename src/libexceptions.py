# -*- coding: utf-8 -*-
"""
- Created on Wed Aug 23 13:51:46 2017
- Deskin - Orange Labs - Lannion - France

.. module:: libexceptions
    :platform: UNIX/Linux
    :synopsis: Collection of user-defined exceptions used in the API

.. moduleauthor:: Munshi Asadullah <munshi.asadullah@orange.com>

*The user-defined exceptions are put together in this libreary. The names are 
quite expainatory.*
"""

# ============================================================== RuntimeError =

class initializationError(RuntimeError):
    def __init__(self, *args, **kwargs):
        RuntimeError.__init__(self, *args, **kwargs)

# ================================================================ ValueError =

class noneValueError(ValueError):
    def __init__(self, *args, **kwargs):
        ValueError.__init__(self, *args, **kwargs)

class zeroLengthValueError(ValueError):
    def __init__(self, *args, **kwargs):
        ValueError.__init__(self, *args, **kwargs)

class unequalValueError(ValueError):
    def __init__(self, *args, **kwargs):
        ValueError.__init__(self, *args, **kwargs)

class metadataValueError(ValueError):
    def __init__(self, *args, **kwargs):
        ValueError.__init__(self, *args, **kwargs)

# ================================================================= TypeError =

class undefinedTypeError(TypeError):
    def __init__(self, *args, **kwargs):
        TypeError.__init__(self, *args, **kwargs)

# =================================================================== IOError =

class invalidPathIOError(IOError):
    def __init__(self, *args, **kwargs):
        IOError.__init__(self, *args, **kwargs)

class pathTypeIOError(IOError):
    def __init__(self, *args, **kwargs):
        IOError.__init__(self, *args, **kwargs)

class newFileIOError(IOError):
    def __init__(self, *args, **kwargs):
        IOError.__init__(self, *args, **kwargs)

# ================================================================== KeyError =

class notAllKeyError(KeyError):
    def __init__(self, *args, **kwargs):
        KeyError.__init__(self, *args, **kwargs)

# =============================================================== UserWarning =

class skipStepWarning(UserWarning):
    def __init__(self, *args, **kwargs):
        UserWarning.__init__(self, *args, **kwargs)

class emptyLineWarning(UserWarning):
    def __init__(self, *args, **kwargs):
        UserWarning.__init__(self, *args, **kwargs)

class firstElementWarning(UserWarning):
    def __init__(self, *args, **kwargs):
        UserWarning.__init__(self, *args, **kwargs)

class lastElementWarning(UserWarning):
    def __init__(self, *args, **kwargs):
        UserWarning.__init__(self, *args, **kwargs)
