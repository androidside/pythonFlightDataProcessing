'''
Created on 3 june 2017

Main script

@author: Marc Casalprim
'''
print 'Imports...'

import numpy as np

from matplotlib.style import use
from matplotlib import rcParams

from utils.dataset import DataSet,plt,genQuaternions,pd
from utils.field import Field,getDtypes
from estimators import Estimator15


if __name__ == '__main__':

    #folder = "\\\\GS66-WHITE\\LocalAuroraArchive\\17-05-21_02_46_56\\"
    folder='F:/LocalAuroraArchive/17-06-01_21_53_20/'
    
    fieldsList=[]     
    fieldsList.append(Field('bettii.RTLowPriority.RawStarcameraQuaternionFXPqi',label='qi_sc'))
    fieldsList.append(Field('bettii.RTLowPriority.RawStarcameraQuaternionFXPqj',label='qj_sc'))
    fieldsList.append(Field('bettii.RTLowPriority.RawStarcameraQuaternionFXPqk',label='qk_sc'))
    fieldsList.append(Field('bettii.RTLowPriority.RawStarcameraQuaternionFXPqr',label='qr_sc'))
    fieldsList.append(Field('bettii.RTLowPriority.qr'))
    fieldsList.append(Field('bettii.RTLowPriority.qi'))
    fieldsList.append(Field('bettii.RTLowPriority.qj'))
    fieldsList.append(Field('bettii.RTLowPriority.qk'))
    fieldsList.append(Field('bettii.RTLowPriority.RawStarcameraDecDeg',label='dec_sc'))
    fieldsList.append(Field('bettii.RTLowPriority.RawStarcameraRaDeg',label='ra_sc'))
    fieldsList.append(Field('bettii.RTLowPriority.RawStarcameraRollDeg',label='roll_sc'))
    fieldsList.append(Field('bettii.RTLowPriority.RawStarcameraDecError',label='dec_err'))
    fieldsList.append(Field('bettii.RTLowPriority.RawStarcameraRaError',label='ra_err'))
    fieldsList.append(Field('bettii.RTLowPriority.RawStarcameraRollError',label='roll_err'))
    fieldsList.append(Field('bettii.RTLowPriority.RawStarcameraMceFrameNumberWhenSCTriggered',label='triggers'))
    #fieldsList.append(Field('bettii.GriffinsGalil.griffinBAngleDegrees',label='griffin_angle')) #44.114721
    fieldsList.append(Field('bettii.GyroReadings.angularVelocityX',label='gyroX',dtype='i4',conversion=-0.0006304))
    fieldsList.append(Field('bettii.GyroReadings.angularVelocityY',label='gyroY',dtype='i4',conversion=-0.0006437))
    fieldsList.append(Field('bettii.GyroReadings.angularVelocityZ',label='gyroZ',dtype='i4',conversion=0.0006324))
    

    initial_time=100 #in frame number
    final_time = None #in frame number

    
    ds = DataSet(folder,fieldsList=fieldsList,estimator=False,starcam=False,min=initial_time,max=final_time,verbose=True)
    ds.df=ds.df.interpolate(method='values').dropna()

    print 'Dataframe shape:', ds.df.shape

    print "Generating quaternions..."
    quats=genQuaternions(ds.df)
    print "Creating Starcam dataframe..."
    triggers=ds.df.triggers.drop_duplicates()  
    triggers=triggers[[(triggers.loc[mceFN]<max(triggers.index) and triggers.loc[mceFN]>min(triggers.index)) for mceFN in triggers.index]]
    sc=pd.DataFrame(quats,index=ds.df.index)
    sc=sc.loc[triggers.index]
    sc.index=triggers.values  
    print 'Done'
    
    gyros=ds.df[['gyroX','gyroY','gyroZ']]
    kal15=Estimator15(gyros,sc)
    
    print "Estimating..."
    Qd=0.03*np.pi/180.*np.eye(15)
    kal15.estimate(Qd=Qd,progress=True)
    
    print "Plotting..."
    use('classic')
    rcParams['axes.grid']=True
    
    kal15.plot()
    
    a=1  
    plt.show()