'''
Plot raw data from a field. Merging archives if we want.
'''
print 'Imports...'
from utils.config import flightDisksFolders,plt
from utils.dataset import load_single_field
from utils.field import Field


if __name__ == '__main__':

    folders=flightDisksFolders
    
    field='bettii.FpgaState.state'
    time_field='bettii.FpgaState.mceFrameNumber'

    print "Folder name      \t"+field
    data=[]
    time=[]
    #folders=['F:/GondolaFlightArchive/17-06-09_01_51_04/']
    for folder in folders:
        d=load_single_field(folder+field,datatype=Field.DTYPES[field])
        t=load_single_field(folder+time_field,datatype=Field.DTYPES[time_field])
        
        L=min(len(d),len(t)) #force the two vectors to have the same length (sudden stop of the archiving)
        
        data=data+list(d[:L])
        time=time+list(t[:L]) 
        name=folder.split('/')[-2]
        print name+":\t"+str(len(d))+" raw values. "+str(len(t))+' FN values.'
    

    print "Plotting.."
    M=1 #downsampling factor
    plt.plot(time[::M],data[::M],'.')
    plt.ylabel(field)
    plt.xlabel(time_field)
    print "Show.."
    plt.show()