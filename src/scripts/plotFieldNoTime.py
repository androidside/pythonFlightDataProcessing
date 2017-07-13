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
 
    field='TReadStandardMessage.frameCounter'
    fieldsList=[]
    print "Folder name      \t"+field
    data=[]
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