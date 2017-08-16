'''
Created on Jun 22, 2017

Plot raw data from a field. Merging archives if we want.

@author: Marc Casalprim
'''

print 'Imports...'
import os
import matplotlib as mpl


from matplotlib.style import use

from utils.dataset import DataSet,plt,sns,np, load_single_field
from utils.field import Field,getDtypes#,getFieldsContaining,getFieldsRegex


if __name__ == '__main__':

    folders=[]
    root_folder='F:/GondolaFlightArchive/'
    subdirs=next(os.walk(root_folder))[1]
    folders=[root_folder+subdir+'/' for subdir in subdirs]
 
    field='bettii.GyroReadings.angularVelocityX'
    time_field='bettii.GyroReadings.mceFrameNumber'

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