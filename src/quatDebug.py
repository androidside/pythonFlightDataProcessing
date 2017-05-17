'''
Created on 28 abr. 2017

Main script

@author: Marc Casalprim
'''
print 'Imports...'
import matplotlib
import numpy as np
from utils.quat import Quat,normalize,sin,cos
from utils.dataset import DataSet,plt,sns,load_single_field,pd
from utils.field import Field,getDtypes#,getFieldsContaining,getFieldsRegex
from itertools import izip_longest


if __name__ == '__main__':

    
    folder='C:/17-05-16_03_06_46/'
    
    print "Getting data types..."
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
    fieldsList.append(Field('bettii.RTLowPriority.RawStarcameraMceFrameNumberWhenSCTriggered',label='triggers'))
    
    #===========================================================================
    # fieldsList.append(Field('bettii.RTHighPriority.SCAnglesInertialGondolaRefFrameArcsecDec',label='dec_sc',conversion=1/3600.))
    # fieldsList.append(Field('bettii.RTHighPriority.SCAnglesInertialGondolaRefFrameArcsecRa',label='ra_sc',conversion=1/3600.))
    # fieldsList.append(Field('bettii.RTHighPriority.SCAnglesInertialGondolaRefFrameArcsecRoll',label='roll_sc',conversion=1/3600.))
    #===========================================================================
    
    fieldsList.append(Field('bettii.GriffinsGalil.griffinBAngleDegrees',label='griffin_angle')) #44.114721
    
    
    #===========================================================================
    # fieldsList.append(Field('bettii.GyroReadings.angularVelocityX',label='gyroX',dtype='i4',conversion=0.0006304))
    # fieldsList.append(Field('bettii.GyroReadings.angularVelocityY',label='gyroY',dtype='i4',conversion=0.0006437))
    # fieldsList.append(Field('bettii.GyroReadings.angularVelocityZ',label='gyroZ',dtype='i4',conversion=0.0006324))
    #===========================================================================
   
    #fieldsList = getFieldsContaining('CCMG',folder)   
    
    #fieldsList = getFieldsRegex('bettii.[U-Z]+',folder)
    
  
    #target 2
    #===========================================================================
    # initial_time=6301000 #in frame number
    # final_time = 6303000 #in frame number
    #===========================================================================
    #2975744
    initial_time=2975744 #in frame number
    final_time = 2976744 #in frame number
    
    #array([ -0.15321407, -44.77279865,  19.87575523])
    dYaw=-0.367
    dPitch=44.9828
    dRoll=-0.79
     
    qdYaw = Quat((dYaw,0,0)); #quat = Quat((ra,dec,roll)) in degrees
    qdPitch = Quat((0.0,sin(dPitch*np.pi/180./2.0),0.0,cos(dPitch*np.pi/180./2.0))) #quat = Quat((ra,dec,roll)) in degreesq
    qdRoll = Quat((0,0,dRoll)) #quat = Quat((ra,dec,roll)) in degrees
    
    #qStarcam2Gyros_new =  Quat((dYaw,-dPitch,dRoll))
    qStarcam2Gyros_new =  Quat((dYaw,-dPitch,dRoll))
    qStarcam2Gyros_old =  qdYaw*qdPitch*qdRoll
    
    ds = DataSet(folder,fieldsList=fieldsList,estimator=False,starcam=False,min=initial_time,max=final_time,verbose=True)
    ds.df=ds.df.interpolate(method='values').dropna()
    
    L=len(ds.df.index)
    
    print L," values"
    
    
    q_est_list=[0]*L
    q_sc_list=[0]*L
    qI2Starcam_list=[0]*L
    qStarcam2Gyros_list=[0]*L
    qStarcam2Est_list=[0]*L
    "Generating quaternions..."
    for i in range(L):
        mceFN=ds.df.index[i]
        q_est_list[i]=Quat((ds.df.loc[mceFN][['qi','qj','qk','qr']]))
        q_sc_list[i]=Quat((ds.df.loc[mceFN][['qi_sc','qj_sc','qk_sc','qr_sc']]))
        qI2Starcam_list[i]=qStarcam2Gyros_old.inv()*q_sc_list[i]
        #qStarcam2Gyros_list[i]=q_sc_list[i]*qI2Starcam_list[i].inv() #when we have the good roll in the telemetries!!
        qStarcam2Est_list[i]=q_est_list[i]*qI2Starcam_list[i].inv() #q_est=qStarcam2Est*qI2Starcam
        if (i*100/L %10)==0: print 'quat', i,'of',L,",", i*100./L,'%'


    #q_tel_new_list=q_tel2_new_list
    
    d={'q_est' : q_est_list,
       'q_sc' : q_sc_list,
       'qI2Starcam' : qI2Starcam_list,
       'qStarcam2Gyros' : qStarcam2Gyros_list,
       'qStarcam2Est' : qStarcam2Est_list }
    
    teldata= pd.DataFrame(d,index = ds.df.index)
    ds.df=pd.merge(ds.df,teldata,how='outer',left_index=True,right_index=True)

    data=ds.df.dropna()      
    print 'Dataframe shape:', ds.df.shape
    

    errDEC=(data['TelescopeDecDeg'].subtract(data.targetDEC))
    errRA=(data['TelescopeRaDeg'].subtract(data.targetRA))
    print errDEC[errDEC.abs()<1e-3]
    print errRA[errRA.abs()<1e-3]
    
