'''
Created on Jun 22, 2017

Prints the frame numbers that are in each Archive inside the root_folder

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
 
    fieldsList=[]
    print "Folder name      \tfinal mceFN"
    field='bettii.RTLowPriority.mceFrameNumber'
    for folder in folders:
        d=load_single_field(folder+field,datatype='i4')
        d=d[d>50000]
        name=folder.split('/')[-2]
        print name+":\t"+str(d[-1])