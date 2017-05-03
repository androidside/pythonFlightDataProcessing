'''
Created on 01 may 2017

@author: Marc Casalprim
'''

class Field(object):
    '''
    Class describing a field
    '''


    def __init__(self, fieldName,dtype='f8',indexName=None,indexType='i8',label=None,conversion=1):
        '''
        Constructor
        '''
        if indexName is None: indexName=fieldName.rsplit('.',1)[0]+'.mceFrameNumber' #the index seems to be always in this format
        if label is None: label=fieldName.split('.')[-1] #we get the last word of the fieldname for the label
        if label == 'mceFrameNumber': #it seems to be a index, we index it by itself
            label=fieldName
            dtype=indexType
            indexName=fieldName

        self.fieldName = fieldName
        self.dtype = dtype
        self.indexName = indexName
        self.indexType = indexType
        self.label = label
        self.conversion = conversion #multiplying factor, to convert the units if we want


import os
def getFieldsContaining(substring,folder):
    """ Return a list of fields in the folder containing substring """
    print 'Generating fields list...'
    fieldsList=[]
    for filename in os.listdir(folder):
        if substring in filename:
            field=Field(filename,dtype=getFormat(filename, folder))
            fieldsList.append(field)
    if len(fieldsList)==1: return fieldsList[0]
    return fieldsList

def getFieldsRegex(regex,folder):
    """ Return a list of fields in the folder matching the regular expression regex """
    import re
    print 'Generating fields list...'
    fieldsList=[]
    for filename in os.listdir(folder):
        if re.match(regex, filename) is not None:
            field=Field(filename,dtype=getFormat(filename, folder))
            fieldsList.append(field)
    if len(fieldsList)==1: return fieldsList[0]
    return fieldsList

def getFormat(fieldName,folder):
    """ Return the dtype of the fieldName using the format file in folder """
    formatFile= open(folder+'format')
    dic={'INT32':'i4',
         'INT64':'i8',
         'UINT8':'u1',
         'FLOAT32':'f4',
         'FLOAT64':'f8'}
    try:
        for line in formatFile:
            if fieldName in line:
                dtype=dic[line.split()[2]]
                return dtype
    finally:
        formatFile.close()