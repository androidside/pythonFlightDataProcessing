'''
Prints the frame numbers that are in each Archive folder
'''


print 'Imports...'
from utils.config import flightDisksFolders,flightTelemetryFolders
from utils.dataset import load_single_field




if __name__ == '__main__':

    folders=flightDisksFolders

    fieldsList=[]
    print "Folder name      \tstart mceFN\tfinal mceFN"
    field='bettii.RTLowPriority.mceFrameNumber'
    for folder in folders:
        d=load_single_field(folder+field,datatype='i4')
        d=d[d>0]
        d.sort()
        print d[:10]
        name=folder.split('/')[-2]
        #print name+":\t"+str(d[0])+"       \t"+str(d[-1])