'''
Plot data from a field. The peaks of field data are filtered using utils.dataset.filterArray. Merging archives if we want.
'''

print 'Imports...'
from utils.config import flightDisksFolders,plt
from utils.dataset import load_single_field,filterArray
from utils.field import Field

if __name__ == '__main__':

    folders=flightDisksFolders
    
    field='bettii.RTLowPriority.RawStarcameraMceFrameNumberWhenSCTriggered'
    time_field='bettii.RTLowPriority.mceFrameNumber'
    #===========================================================================
    # 17296211
    # 17645843
    #===========================================================================
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
    delay=(time-data)/400. #in seconds
    print "Plotting.."
    M=1 #downsampling factor
    plt.plot(time[::M],delay[::M])
    plt.ylabel('SC Delay [s]')
    plt.xlabel('Frame Number')
    print "Show.."
    plt.show()