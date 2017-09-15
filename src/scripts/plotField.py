'''
Created on Jun 22, 2017

Plot data from a field, using DataSet class. Merging archives if we want.

@author: Marc Casalprim
'''
print 'Imports...'
from utils.config import flightDisksFolders,plt
from utils.dataset import DataSet,pd,plotColumns, filterDataframe
from utils.field import Field


if __name__ == '__main__':

    folders=flightDisksFolders
    
    fieldsList=[]
    fieldsList=[Field('bettii.RTLowPriority.RawStarcameraMceFrameNumberWhenSCTriggered',label='triggers',range=3e7)]
    ds = DataSet(fieldsList=fieldsList,foldersList=folders,verbose=True,rpeaks=False)
    

    M=100
    ds.df = ds.df.iloc[::M] #Downsample
    
    if False: #filter?
        ds.df=filterDataframe(ds.df)
    
    print "Plot..."
    ds.df.triggers.plot()
    plt.show()