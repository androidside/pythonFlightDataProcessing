'''
Created on Jun 22, 2017

Prints the frame numbers that are in each Archive inside the root_folder

@author: Marc Casalprim
'''


print 'Imports...'
from utils.config import flightDisksFolders
from utils.dataset import load_single_field




if __name__ == '__main__':

    folders=flightDisksFolders

    fieldsList=[]
    print "Folder name      \tfinal mceFN"
    field='bettii.RTLowPriority.mceFrameNumber'
    for folder in folders:
        d=load_single_field(folder+field,datatype='i4')
        d=d[d>50000]
        name=folder.split('/')[-2]
        print name+":\t"+str(d[-1])