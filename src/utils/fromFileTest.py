'''
Created on Jun 5, 2017

@author: bettii
'''
import numpy as np
import os
def load_single_field(fieldname,datatype,nValues=None,start=None):
    type_str_native = ">"+datatype
    type_str_final = "<"+datatype # change endianness
    
    if nValues is None:
        field = np.fromfile(fieldname,dtype=np.dtype(type_str_native))
    else:
        bpv=int(datatype[-1]) #bytes per value
        f = open(fieldname, "rb")
        try:
            if start is None:
                nBytes=nValues*bpv 
                f.seek(-nBytes, os.SEEK_END)
            else:
                nBytes=start*bpv
                f.seek(nBytes, os.SEEK_SET)
    
        
            field = np.fromfile(f,dtype=np.dtype(type_str_native),count=nValues)
        finally:
            f.close()

    field = field.astype(type_str_final)
    return field

folder = "F:/LocalAuroraArchive/17-05-24_18_12_19/"
bad=folder+'error_r9_c0'
bad=folder+'error_r0_c0'
good=folder+'error_r0_c13'
print Dataset(bad,'i8',nValues=10)