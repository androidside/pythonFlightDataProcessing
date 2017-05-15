'''
Created on 28 abr. 2017

Main script

@author: Marc Casalprim
'''
print 'Imports...'
import matplotlib
import numpy as np
from utils.quat import Quat,normalize,sin,cos
from utils.dataset import DataSet,plt,sns,load_single_field
from utils.field import Field,getDtypes#,getFieldsContaining,getFieldsRegex



if __name__ == '__main__':
    #folder = "C:/17-04-24_19_02_57/"
    #folder = "\\\\GS66-WHITE\\LocalAuroraArchive\\17-05-02_18_01_58\\"
    
    folder='C:/16-09-28_21_58_34-/'
    #folder='C:/17-05-12_21_13_14/'
    
    Field.DTYPES=getDtypes(folder)
    
    fieldsList=[]
     
    fieldsList.append(Field('bettii.RTHighPriority.crossElevation'))
    fieldsList.append(Field('bettii.RTHighPriority.elevation'))
    fieldsList.append(Field('bettii.RTHighPriority.TelescopeDecDeg'))
    fieldsList.append(Field('bettii.RTHighPriority.TelescopeRaDeg'))
    fieldsList.append(Field('bettii.RTHighPriority.targetDEC'))
    fieldsList.append(Field('bettii.RTHighPriority.targetRA'))
    fieldsList.append(Field('bettii.RTHighPriority.GondolaDecDeg'))
    fieldsList.append(Field('bettii.RTHighPriority.GondolaRaDeg'))
    fieldsList.append(Field('bettii.RTHighPriority.GondolaRaDeg'))
    fieldsList.append(Field('bettii.RTHighPriority.GondolaRaDeg'))
    fieldsList.append(Field('bettii.RTLowPriority.qr'))
    fieldsList.append(Field('bettii.RTLowPriority.qi'))
    fieldsList.append(Field('bettii.RTLowPriority.qj'))
    fieldsList.append(Field('bettii.RTLowPriority.qk'))
    fieldsList.append(Field('bettii.RTLowPriority.RawStarcameraQuaternionFXPqi',label='qi_sc'))
    fieldsList.append(Field('bettii.RTLowPriority.RawStarcameraQuaternionFXPqj',label='qj_sc'))
    fieldsList.append(Field('bettii.RTLowPriority.RawStarcameraQuaternionFXPqk',label='qk_sc'))
    fieldsList.append(Field('bettii.RTLowPriority.RawStarcameraQuaternionFXPqr',label='qr_sc'))
     
    fieldsList.append(Field('bettii.RTLowPriority.RawStarcameraDecDeg',label='dec_sc'))
    fieldsList.append(Field('bettii.RTLowPriority.RawStarcameraRollDeg',label='roll_sc'))
    fieldsList.append(Field('bettii.RTLowPriority.RawStarcameraRaDeg',label='ra_sc'))
    fieldsList.append(Field('bettii.RTLowPriority.RawStarcameraAzDeg',label='az_sc',conversion=1))
    fieldsList.append(Field('bettii.RTLowPriority.RawStarcameraElDeg',label='el_sc',conversion=1))
    
    #===========================================================================
    # fieldsList.append(Field('bettii.RTHighPriority.SCAnglesInertialGondolaRefFrameArcsecDec',label='dec_sc',conversion=1/3600.))
    # fieldsList.append(Field('bettii.RTHighPriority.SCAnglesInertialGondolaRefFrameArcsecRa',label='ra_sc',conversion=1/3600.))
    # fieldsList.append(Field('bettii.RTHighPriority.SCAnglesInertialGondolaRefFrameArcsecRoll',label='roll_sc',conversion=1/3600.))
    #===========================================================================
    
    fieldsList.append(Field('bettii.GriffinsGalil.griffinBAngleDegrees',label='griffin_angle')) #44.114721
    griffin_angle=44.114721
    
    
    #===========================================================================
    # fieldsList.append(Field('bettii.GyroReadings.angularVelocityX',label='gyroX',dtype='i4',conversion=0.0006304))
    # fieldsList.append(Field('bettii.GyroReadings.angularVelocityY',label='gyroY',dtype='i4',conversion=0.0006437))
    # fieldsList.append(Field('bettii.GyroReadings.angularVelocityZ',label='gyroZ',dtype='i4',conversion=0.0006324))
    #===========================================================================
   
    #fieldsList = getFieldsContaining('CCMG',folder)   
    
    #fieldsList = getFieldsRegex('bettii.[U-Z]+',folder)
    
    #target 1    
    initial_time=5145000 #in frame number
    final_time = 5149000 #in frame number
    
    #===========================================================================
    # initial_time=None #in frame number
    # final_time = None #in frame number
    #===========================================================================
    
    
    ds = DataSet(folder,fieldsList=fieldsList,estimator=False,starcam=False,min=initial_time,max=final_time,verbose=False)
    
    print 'Dataframe shape:', ds.df.shape
    t=5145804 #interesting time
    d=ds.df.loc[t].dropna()

    qI2Starcam=Quat(d[['ra_sc','dec_sc','roll_sc']])
    q_sc=Quat(d[['qi_sc','qj_sc','qk_sc','qr_sc']]) #meas_q qI2Gyros
    
    #array([ -0.15321407, -44.77279865,  19.87575523])
    dYaw=-0.15321407
    dPitch=44.77279865
    dRoll=-3.99
    errRoll=4#19.87575523+3.99
     
    qdYaw = Quat((dYaw,0,0)); #quat = Quat((ra,dec,roll)) in degrees
    qdPitch = Quat((0.0,sin(dPitch*np.pi/180./2.0),0.0,cos(dPitch*np.pi/180./2.0))) #quat = Quat((ra,dec,roll)) in degrees
    qdRoll = Quat((0,0,dRoll+errRoll)) #quat = Quat((ra,dec,roll)) in degrees

    qStarcam2Gyros =  Quat((-dYaw,dPitch,-(dRoll+errRoll))) #
    

    qI2Gyros =  qStarcam2Gyros*qI2Starcam
    
    qGyros2Tel = Quat((0,griffin_angle,0))
    
    q_est=Quat(d[['qi','qj','qk','qr']])
    #q_sc = d['meas_q'];

    print 'qI2Starcam: ', qI2Starcam.equatorial
    print 'qStarcam2Gyros: ', qStarcam2Gyros.equatorial
    print
    print 'q_est :', q_est.equatorial
    print 'q_sc  :', q_sc.equatorial
    print
    print 'Without error in roll:'
    print 'qI2Gyros: ', (Quat((-dYaw,dPitch,-dRoll)).inv()*qI2Starcam).equatorial
    print
    print 'With error in roll:',errRoll,'deg'
    print 'qI2Gyros : ', qI2Gyros.equatorial
    print
    print 'qGyros2Tel: ', qGyros2Tel.equatorial
    print
    print 'qI2Tel :',(qGyros2Tel*qI2Gyros).equatorial
    print 'qI2Tel_sc :',(qGyros2Tel*q_sc).equatorial
    print 'qI2Tel_est:',(qGyros2Tel*q_est).equatorial
    print 'Telescope RA DEC :',d['TelescopeRaDeg'],d['TelescopeDecDeg']
    print 'Target RA DEC :',d['targetRA'],d['targetDEC']
    
    
    a=1
    
