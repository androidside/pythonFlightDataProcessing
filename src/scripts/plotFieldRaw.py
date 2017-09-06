'''
Created on Jun 22, 2017

Plot raw data from a field. Merging archives if we want.

@author: Marc Casalprim
'''

print 'Imports...'
import os
import matplotlib as mpl


from matplotlib.style import use

from utils.dataset import plt, load_single_field
from utils.field import Field


if __name__ == '__main__':
    telemetry=True
    folders=[]
    if not telemetry:
        root_folder='F:/GondolaFlightArchive/'
        subdirs=next(os.walk(root_folder))[1]
        folders=[root_folder+subdir+'/' for subdir in subdirs]
    else:
        folders.append('F:/LocalBettiiArchive/17-06-08_17_07_45-/')
        folders.append('F:/LocalBettiiArchive/17-06-08_20_43_41-/')
        folders.append('F:/LocalBettiiArchive/17-06-08_20_54_26-/')
        folders.append('F:/LocalBettiiArchive/17-06-08_22_09_44-/')
        folders.append('F:/LocalBettiiArchive/17-06-08_22_19_34-/')
        folders.append('F:/LocalBettiiArchive/17-06-09_00_27_01-/')
        folders.append('F:/LocalBettiiArchive/17-06-09_01_54_43-/')
        folders.append('F:/LocalBettiiArchive/17-06-09_02_12_33-/')
        folders.append('F:/LocalBettiiArchive/17-06-09_02_40_53-/')
        folders.append('F:/LocalBettiiArchive/17-06-09_02_59_03-/')
        folders.append('F:/LocalBettiiArchive/17-06-09_04_11_03-/')
        
        #==========================EMPTY Archives===================================
        #  folders.append('F:/LocalBettiiArchive/17-06-09_04_16_13-/')
        #  folders.append('F:/LocalBettiiArchive/17-06-09_04_19_53-/')
        #  folders.append('F:/LocalBettiiArchive/17-06-09_04_20_34-/')
        # folders.append('F:/LocalBettiiArchive/17-06-09_04_26_51-/')
        # folders.append('F:/LocalBettiiArchive/17-06-09_04_28_38-/')
        # folders.append('F:/LocalBettiiArchive/17-06-09_04_41_34-/')
        #===========================================================================
        folders.append('F:/LocalBettiiArchive/17-06-09_06_29_36-/')
    field='bettii.RTLowPriority.RawStarcameraMceFrameNumberWhenSCTriggered'
    time_field='bettii.RTLowPriority.mceFrameNumber'

    print "Folder name      \t"+field
    data=[]
    time=[]
    for folder in folders:
        d=load_single_field(folder+field,datatype=Field.DTYPES[field])
        t=load_single_field(folder+time_field,datatype=Field.DTYPES[time_field])
        data=data+list(d)
        time=time+list(t)
        name=folder.split('/')[-2]
        print name+":\t"+str(len(d))+" raw values. "+str(len(t))+' FN values.'
    
    print "Plotting.."
    use('ggplot')
    mpl.rcParams['axes.grid'] = True
    plt.plot(time,data)
    plt.ylabel(field)
    plt.xlabel(time_field)
    print "Show.."
    plt.show()