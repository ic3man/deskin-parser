# -*- coding: utf-8 -*-
"""
Created on Wed Aug 23 13:53:28 2017

@author: munshi
"""


def getDebugSourceString(source_stack=[]): # - DEF(0101):: START --------------
    
    """ A local method to generate the sring to display the origin of a debug
    event from the source stack.
        
    Args:
        - **source_stack** (list): The source stack of the origin of a debug 
    event. Each element is a list of 3 strings, where the first element is the 
    name of the **Class**, followed by the name of the  **Module** and finally 
    the name of the **Method**.
        
    Kwargs:
        None
    
    Returns:
        (str): The printable source stack trace
    
    Raises:
        None

    >>> getDebugSourceString(source_stack=['C0', 'M0', 'F0'], ['C1', 'M1', 'F1'])
    -C0[M0]::F0
    +-C1[M1]::F1
    """
    # check if the stack is a list
    if not isinstance(source_stack, list):
        print >> sys.stderr, 'FATAL-ERROR:: debug-source stack must be a list'
        print >> sys.stderr, ('Found:: {}').format(type(source_stack))
        print >> sys.stderr, '(0101) exiting to system ...'
        sys.exit(-1)
    # return if the list is empty
    if not len(source_stack):
        return None
    # initiate return string
    ret_str = ''
    # initiate stack element counter
    counter = -1
    # cycle through the origin stack
    for e in source_stack:
        # check if each stack element is a list of size 3
        if not isinstance(e, list) or len(e) != 3:
            print  >> sys.stderr, 'FATAL-ERROR:: debug-source stack element({}) \
                                   is not a list of size 3'.format(counter)
            print  >> sys.stderr, 'Stack Content:: {}'.format(source_stack)
            print  >> sys.stderr, '(0101) exiting to system ...'
            sys.exit(-1)
        # display formatting for 1+ elements
        if len(ret_str):
            ret_str += '\n' + (' '*counter) + '+-'
        # display formatting for the 1st elements
        else:
            ret_str += '*'
        # update counter
        counter += 1
        # print class[module]::def() format
        ret_str += '{}[{}]::{}'.format(e)
    # return the debug source string
    return ret_str
# ----------------------------------------------------------------- DEF:: END -

def debugPrinter(dType='GENERIC', 
                 dID=5618, 
                 dSource=[], 
                 dTitle='debug event', 
                 dDetail='!!!this is a debug event - details unknown!!!',
                 dElement=None): # - DEF(5618):: START ------------------------
    
    """ Method to print usefule debugging information regarding some sort of \
    error or warning occured during execution.
        
    Args:
        - **dType** (str): The debug event type e.g. error, warning etc.
        - **dID** (str/int/float/double): Unique ID of a debug event.
        - **dSource** (list): The trace of where the debug event originated
        - **dTitle** (str): The title of the debug event
        - **dDetail** (str): The detailed description of the debug event
        - **dElement** (any): The values that triggred the debug event
    
    Kwargs:
        None
    
    Returns:
        None
    
    Raises:
        None

    >>> debugPrinter(dType='ERROR', dID='fake:001', dSource=[], 
                     dTitle='fake debug event', 
                     dDetail='an event that never existed',
                     dElement=['One', 'two'])
    ERROR[fake:001]
    None
    *Title  :: fake debug event
    *Details:: an event that never existed
    *Value  :: ['One', 'two'] 
    """
    dSource.append([sys.modules[__name__], None, __name__])
    print [sys.modules[__name__], None, __name__]
    print >> sys.stderr, ('{}[{}]\n{}\n*Title  :: {}\n*Details:: {}\n'
                          '*Value  :: {}\n').format(dType, dID, 
                                                 getDebugSourceString(dSource), 
                                                 dTitle, dDetail, dElement)
# ----------------------------------------------------------------- DEF:: END -