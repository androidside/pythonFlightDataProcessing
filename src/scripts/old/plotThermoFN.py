'''
Created on Jun 22, 2017

Plot raw data from a field. Merging archives if we want.

@author: Marc Casalprim
'''

print 'Imports...'
import os

from utils.dataset import DataSet,plt,np,pd, load_single_field
from utils.field import Field,getDtypes#,getFieldsContaining,getFieldsRegex


if __name__ == '__main__':

    folders=[]
    root_folder='D:/GondolaFlightArchive/'
    subdirs=next(os.walk(root_folder))[1]
    folders=[root_folder+subdir+'/' for subdir in subdirs]
 
    field='bettii.ThermometersDemuxedCelcius.J3L4'
    index='bettii.ThermometersDemuxedCelcius.mceFrameNumber'
    fieldsList=[]
    print "Folder name      \t"+field
    data=[];frames=[];frames2=[]
    cut={}
    for folder in folders[:-3]:
        d=load_single_field(folder+field,datatype=Field.DTYPES[field])
        i=load_single_field(folder+index,datatype=Field.DTYPES[index])
        data=data+list(d)
        frames=frames+list(i)
        L=len(d)
        frames2=frames2+list(np.linspace(i[0],i[-1],L))
        cut[folder]=i[-1]
        name=folder.split('/')[-2]
        print name+":\t%s temp values\t%s frame numbers." % (L,len(i))
        
    df=pd.DataFrame({'C6':data},index=frames2)
    print "Saving..."
    df.to_csv(root_folder+"C6.txt",sep='\t', float_format='%.2f', index_label='Frame Number  ')

    print "Plotting.."
    plt.plot(frames2,data)
    for c in cut.values():
        plt.axvline(x=c,color='k')
    plt.suptitle(field)
    plt.xlabel('Frame Number')
    plt.ylabel('Temperature [Celsius]')
    plt.savefig(root_folder+'C6.png')
    print "Show.."
    plt.show()