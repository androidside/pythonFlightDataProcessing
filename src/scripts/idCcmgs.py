'''
Created on 30 may. 2017

Generates a dataset including CCMGinput, wheelsAngle and Gyros and saves it on a .mat file.
Useful for model identification, or finding the Inertia value in MatLab.

@author: Marc Casalprim
'''
print 'Imports...'
import numpy as np
from utils.dataset import DataSet,plt
from utils.field import Field,getDtypes#,getFieldsContaining,getFieldsRegex
from scipy import io


if __name__ == '__main__':
    folder = "C:/17-04-24_19_02_57/"
    folder = "\\\\GS66-WHITE\\LocalAuroraArchive\\17-05-16_03_06_46\\"
    
    
    folder='C:/17-05-30_19_44_12/'
    
    Field.DTYPES=getDtypes(folder)
    
    fieldsList=[]
     
    fieldsList.append(Field('bettii.RTHighPriority.CCMGStepperSpeedManualValue',label='manual_speed')) 
    fieldsList.append(Field('bettii.PIDOutputCCMG.ut',label='ut_ccmg'))
    fieldsList.append(Field('bettii.StepperGalil.wheelsAngle',label='wheels_angle'))
    fieldsList.append(Field('bettii.GyroReadings.angularVelocityX',label='gyroX',dtype='i4',conversion=0.0006304))
    fieldsList.append(Field('bettii.GyroReadings.angularVelocityY',label='gyroY',dtype='i4',conversion=0.0006437))
    fieldsList.append(Field('bettii.GyroReadings.angularVelocityZ',label='gyroZ',dtype='i4',conversion=0.0006324))
   
 
    initial_time=4274000 #in frame number
    final_time = 4283400 #in frame number
    
    #===========================================================================
    # initial_time=None #in frame number
    # final_time = None #in frame number
    #===========================================================================

    
    
    ds = DataSet(folder,fieldsList=fieldsList,min=initial_time,max=final_time,verbose=True)

    print 'Dataframe shape:', ds.df.shape
    data=ds.df.interpolate(method='values').dropna()
    #data.index=data.index/ds.freq #index in seconds
    ds.df=ds.df[np.abs(ds.df['ut_ccmg'].values)<= 3e4]
    ds.df=ds.df[np.abs(ds.df['manual_speed'].values)<= 3e4]

    #scripts RA and DEC target vs estimated
    plt.ion()
    plt.figure(1)
    ax1=plt.subplot(211,xlabel='Time (frames)',ylabel='Jog Speed')
    ax2=plt.subplot(212,xlabel='Time (frames)',ylabel='Azimuth velocity (arcsec/s)')
    ut=data.ut_ccmg.add(data.manual_speed)
    ut.plot(ax=ax1)
    data['gyroZ'].plot(ax=ax2)
    mdict={'ut':ut.values,'az_speed':data.gyroZ.values,'mceFN':data.index.values,'wheels_angle':data.wheels_angle.values}
    io.savemat('C:/Users/marc/Documents/MATLAB/IDccmg_3005.mat',mdict)
    plt.ioff()
    plt.show()
    plt.pause(1)