'''
Created on Jun 22, 2017

Plot data from a field. The peaks of field data are filtered using utils.dataset.filterArray. Merging archives if we want.

@author: Marc Casalprim
'''

print 'Imports...'
from utils.config import flightDisksFolders,plt
from utils.dataset import load_single_field,filterArray
from utils.field import Field

if __name__ == '__main__':

    folders=flightDisksFolders
    
    field='bettii.RTLowPriority.RawStarcameraMceFrameNumberWhenSCTriggered'
    time_field='bettii.RTLowPriority.mceFrameNumber'

    print "Folder name      \t"+field
    data=[]
    time=[]
    #folders=['F:/GondolaFlightArchive/17-06-09_01_51_04/']
    for folder in folders:
        d=load_single_field(folder+field,datatype=Field.DTYPES[field])
        t=load_single_field(folder+time_field,datatype=Field.DTYPES[time_field])
        data=data+list(d)
        L=len(d)
        time=time+list(t[:L])
        name=folder.split('/')[-2]
        print name+":\t"+str(len(d))+" raw values. "+str(len(t))+' FN values.'
    
    print "Filtering..." #calls filterArray several times to remove peaks of incrementing width
    data=filterArray(data)
    data=filterArray(data,N=2000,R=0.5)
    #data=filterArray(data,N=20000,R=0.5)
    
    print "Plotting.."
    M=100 #downsampling factor
    plt.plot(time[::M],data[::M])
    plt.ylabel(field)
    plt.xlabel(time_field)
    print "Show.."
    plt.show()