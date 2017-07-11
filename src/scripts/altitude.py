'''
Created on Jun 22, 2017

Altitude scripts without indexing, because we dont have a valid index for GpsReadings (approximatmceFN is empty)

@author: Marc Casalprim
'''
from scipy.optimize.optimize import fmin
print 'Imports...'

import matplotlib as mpl
import pandas as pd
from numpy import sin,cos,arctan2,pi,sqrt
from matplotlib.style import use
from utils.quat import Quat
from utils.dataset import DataSet,plt,sns,np, load_fields
from utils.field import Field,getDtypes#,getFieldsContaining,getFieldsRegex



if __name__ == '__main__':

    folders=[]
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

    
    
    Field.DTYPES=getDtypes(folders[0])
    
    fieldsList=[]
     
    fieldsList.append(Field('bettii.GpsReadings.altitudeMeters',indexName='bettii.GpsReadings.approximatMmceFrameNumber',label='altitude'))
    alt=None
    for folder in folders:
        d=load_fields(fieldsList, folder)
        if alt is None: alt=d['altitude']
        else: alt=np.concatenate([alt,d['altitude']])
        
    
    use('classic')
    mpl.rcParams['axes.grid']=True
    
    plt.figure(1)
    plt.plot(alt)
   
    
    plt.ylabel('Altitude (m)')
    plt.show()