'''
Created on Jun 5, 2017

@author: bettii
'''
from utils.field import Field,getFieldsContaining
from utils.dataset import load_fields,plt
from utils.detector import data2matrices,getIndexRangeLastStroke

if __name__ == '__main__':
    folder = "F:/LocalAuroraArchive/17-05-24_18_12_19/"
    
    fieldsList=getFieldsContaining("error_",folder,dtype='i8',indexName='masterMceFrameNumber')
    fieldsList.append(Field('bettii.DelayLines.CDLposTarget',label='target'))
    
    data=load_fields(fieldsList, folder, nValues=5000, start=500) #simulation
    #data=load_fields(fieldsList, folder, nValues=L) #from end
    print "Processing..."
    CDLposTarget=data['target']
    CDLmceFN=data['bettii.DelayLines.mceFrameNumber']
    masterMceFn=data['masterMceFrameNumber']
    index=getIndexRangeLastStroke(CDLposTarget, CDLmceFN, masterMceFn)
    plt.plot(CDLmceFN,CDLposTarget)
    plt.axvline(x=masterMceFn[index[0]])
    plt.axvline(x=masterMceFn[index[-1]])
    plt.show()
    det=data2matrices(data,index=index)
