'''
Created on 23 May 2017

Plotting of:
Estimator-SC errors in SC ref. frame
Estimator-SC errors in Gondola ref. frame
Biases


@author: Marc Casalprim
'''
print 'Imports...'
import matplotlib as mpl
import pandas as pd
from matplotlib.style import use
from utils.dataset import DataSet,plt,extractGyrosAndStarcam
from utils.field import Field,getDtypes#,getFieldsContaining,getFieldsRegex
from utils.quat import Quat,normalize,sin,cos


if __name__ == '__main__':
    folder='F:/GondolaFlightArchive/17-06-09_01_51_04/'
    
    fieldsList=[]
    
    fieldsList.append(Field('bettii.RTHighPriority.TelescopeRaDeg',  label='RA (deg)'))
    fieldsList.append(Field('bettii.RTHighPriority.TelescopeDecDeg', label='DEC (deg)'))


    
    ds = DataSet(folder,fieldsList=fieldsList,min=19361609,max=19712791,verbose=True)

    ds.df=ds.df.interpolate('values')
    
    print 'Dataframe shape:', ds.df.shape
    
    print ds.df
    
    print "Saving CSV..."
    ds.df.to_csv(folder+"telescopeRADEC.txt",sep='\t', float_format='%.25f', index_label='mceFrameNumber', date_format="%Y-%m-%d %H:%M:%S")
    print "Saved"

    plt.show()

    