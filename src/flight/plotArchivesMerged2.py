'''
Created on Jun 22, 2017

@author: bettii
'''
'''
Created on 28 abr. 2017

Main script

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
    #folders.append('F:/LocalBettiiArchive/17-06-09_06_29_36-/')

    
    
    gyros=False
    momdump=False
    magnetometer=False
    thermometers=True
    currents=False
    altitude=False
    
    fieldsList=[]
    if gyros:
        fieldsList.append(Field('bettii.GyroReadings.angularVelocityX',label='Gyro X',dtype='i4',conversion=0.0006304))
        fieldsList.append(Field('bettii.GyroReadings.angularVelocityY',label='Gyro Y',dtype='i4',conversion=0.0006437,range=2e5))
        fieldsList.append(Field('bettii.GyroReadings.angularVelocityZ',label='Gyro Z',dtype='i4',conversion=0.0006324,range=2e5))
    
    if altitude: fieldsList.append(Field('bettii.GpsReadings.altitudeMeters',indexName='bettii.RTLowPriority.mceFrameNumber',label='altitude'))
    
    if magnetometer:
        fieldsList.append(Field('bettii.Magnetometer.AzimuthDeg',label='mAz',function =  lambda x: np.unwrap(x*np.pi/180.-np.pi)*180/np.pi+180))
        fieldsList.append(Field('bettii.Magnetometer.PitchDeg',label='mPitch'))
        fieldsList.append(Field('bettii.Magnetometer.RollDeg',label='mRoll'))
    
    if momdump: fieldsList.append(Field('bettii.PIDOutputMomDump.ut'))
    if thermometers:
        fieldsList.append(Field('bettii.ThermometersDemuxedCelcius.J3L28',label='Momentum dump'))
        fieldsList.append(Field('bettii.ThermometersDemuxedCelcius.J3L12',label='Top Dewar'))
        fieldsList.append(Field('bettii.ThermometersDemuxedCelcius.J1L14',label='Siderostat Left'))
    ds = DataSet(fieldsList=fieldsList,foldersList=folders,verbose=True,rpeaks=False)
    
    

    data=ds.df
    use('ggplot')
    mpl.rcParams['axes.grid']=True
    
    if gyros:
        fig=plt.figure(1)
        fig.suptitle("Gyroscopes", fontsize=15,y=1)
        ax=plt.subplot(111,xlabel='Time', ylabel='Angular velocity [arcsec/s]')
        data=ds.df[['Gyro X','Gyro Y','Gyro Z']].dropna()
        data.plot(ax=ax,style=['r+','g+','b+'],markersize=1.0)
        fig.tight_layout()
    
    if magnetometer:
        fig=plt.figure(2)
        fig.suptitle("Magnetometer", fontsize=15,y=1)
        ax=plt.subplot(211,xlabel='Time', ylabel='Azimuth [deg]')
        ax2=plt.subplot(212,xlabel='Time', ylabel='Pitch [deg]')
        data=ds.df[['mAz','mPitch','mRoll']].dropna()
        data.mAz.plot(ax=ax,style='.')
        data.mPitch.plot(ax=ax2,style='.')
        fig.tight_layout()
    
    if momdump:
        fig=plt.figure(3)
        fig.suptitle("Momentum dump", fontsize=15,y=1)
        ax=plt.subplot(111,xlabel='Time', ylabel='Command [counts/s]')
        data=ds.df.ut.dropna()
        data.plot(ax=ax,style='b+',markersize=1.0)
        fig.tight_layout()
    
    if thermometers:
        fig=plt.figure(4)
        fig.suptitle("Thermometers", fontsize=15,y=0.999)
        ax=plt.subplot(111,xlabel='Time', ylabel='Temperature [Celsius]')
        data=ds.df[['Top Dewar','Siderostat Left','Momentum dump']].dropna(how='all').interpolate(method='time')
        data.plot(ax=ax,style=['r','g','b'],markersize=1.0)
        fig.tight_layout()
    
    if altitude:
        fig=plt.figure(5)
        ax=plt.subplot(111,xlabel='Time', ylabel='Altitude [m]')
        data=ds.df.altitude.dropna()
        data.plot(ax=ax,style='b')
        fig.tight_layout()
    
    if currents:
        fig=plt.figure(6)
        ax=plt.subplot(111,xlabel='Time', ylabel='Altitude [m]')
        data=ds.df.altitude.dropna()
        data.plot(ax=ax,style='b')
        fig.tight_layout()
    
    
    a=1
    plt.show()