'''
Created on Jun 22, 2017

Plot raw data from a field. Without time. Useful when the archive ended abruptly and the dimensions do not match. Merging archives if we want.

@author: Marc Casalprim
'''
print 'Imports...'
from utils.config import flightDisksFolders,plt,M
from utils.dataset import load_single_field
from utils.field import Field


if __name__ == '__main__':

    folders=flightDisksFolders


    field='bettii.ThermometersDemuxedCelcius.mceFrameNumber'
    data=[]
    
    print "Folder name      \t"+field
    for folder in folders:
        d=load_single_field(folder+field,datatype=Field.DTYPES[field])
        data=data+list(d)
        name=folder.split('/')[-2]
        print name+":\t"+str(len(d))+" raw values."
    print "Plotting.."

    plt.plot(data)
    plt.suptitle(field)
    print "Show.."
    plt.show()
 
    