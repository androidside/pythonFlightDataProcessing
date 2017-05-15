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

    
    folder='C:/16-09-28_21_58_34-/'
    
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
    
    #target 1    
    initial_time=5147500 #in frame number
    final_time = 5153400 #in frame number
    
    #target 2
    #===========================================================================
    # initial_time=6301000 #in frame number
    # final_time = 6303000 #in frame number
    #===========================================================================
    
    #===========================================================================
    # initial_time=None #in frame number
    # final_time = None #in frame number
    #===========================================================================
    
    #array([ -0.15321407, -44.77279865,  19.87575523])
    dYaw=-0.15321407
    dPitch=44.77279865
    dRoll=-3.99
     
    qdYaw = Quat((dYaw,0,0)); #quat = Quat((ra,dec,roll)) in degrees
    qdPitch = Quat((0.0,sin(dPitch*np.pi/180./2.0),0.0,cos(dPitch*np.pi/180./2.0))) #quat = Quat((ra,dec,roll)) in degrees
    qdRoll = Quat((0,0,dRoll)) #quat = Quat((ra,dec,roll)) in degrees
    
    #qStarcam2Gyros_new =  Quat((dYaw,-dPitch,dRoll))
    qStarcam2Gyros_new =  Quat((dYaw,-dPitch,0))*qdRoll
    qStarcam2Gyros_old =  qdYaw*qdPitch*qdRoll
    
    ds = DataSet(folder,fieldsList=fieldsList,estimator=False,starcam=False,min=initial_time,max=final_time,verbose=False)
    ds.df=ds.df.interpolate(method='values').dropna()
    q_est_list=[Quat(normalize(ds.df.loc[mceFN][['qi','qj','qk','qr']])) for mceFN in ds.df.index]
    
    q_sc_list=[Quat((ds.df.loc[mceFN][['qi_sc','qj_sc','qk_sc','qr_sc']])) for mceFN in ds.df.index]
    qI2Starcam_list=[qStarcam2Gyros_old.inv()*q_sc for q_sc in q_sc_list]
    
    qStarcam2Est_list=[ q_est*qI2Starcam.inv() for q_est,qI2Starcam in izip_longest(q_est_list,qI2Starcam_list)] #q_est=qStarcam2Est*qI2Starcam
    
    
    #qStarcam2Est=qGyros2Est*qStarcam2Gyros_old
    qGyros2Est_list= [ qStarcam2Est*qStarcam2Gyros_old.inv() for qStarcam2Est in qStarcam2Est_list] #the correction the estimator is applying to the measure (any better way to do that?)
    
    q_est_new_list = [ qGyros2Est*qStarcam2Gyros_new*qI2Starcam for qGyros2Est,qI2Starcam in izip_longest(qGyros2Est_list,qI2Starcam_list)]
    q_sc_new_list = [ qStarcam2Gyros_new*qI2Starcam for qI2Starcam in qI2Starcam_list]
    q_tel_new_list = [Quat((0,griffin_angle,0))*q_est_new for q_est_new,griffin_angle in izip_longest(q_est_new_list,ds.df['griffin_angle'])]
    q_tel2_new_list = [Quat((0,griffin_angle,0))*q_sc_new for q_sc_new,griffin_angle in izip_longest(q_sc_new_list,ds.df['griffin_angle'])]
    
    #q_tel_new_list=q_tel2_new_list
    
    d={'TelRA corrected' : [q.ra for q in q_tel_new_list],
       'TelDEC corrected' : [q.dec for q in q_tel_new_list],
       'tel_roll' : [q.roll for q in q_tel_new_list],
       'ra_s2e' : [q.ra for q in qStarcam2Est_list],
       'dec_s2e' : [q.dec for q in qStarcam2Est_list],
       'roll_s2e' : [q.roll for q in qStarcam2Est_list]}
    
    teldata= pd.DataFrame(d,index = ds.df.index)
    ds.df=pd.merge(ds.df,teldata,how='outer',left_index=True,right_index=True)

    data=ds.df.dropna()
    
         
    print 'Dataframe shape:', ds.df.shape
    
    
    matplotlib.style.use('ggplot')
    
    plt.ion()
    
    plt.figure(1)
    ax1=plt.subplot(211,xlabel='Time (frames)',ylabel='DEC (deg)')
    ax2=plt.subplot(212,xlabel='Time (frames)',ylabel='RA (deg)')
    
    data[['targetDEC','TelescopeDecDeg','TelDEC corrected']].plot(ax=ax1)
    data[['targetRA','TelescopeRaDeg','TelRA corrected']].plot(ax=ax2)
    
    plt.figure(2)
    ax1=plt.subplot(211,xlabel='Time (frames)',ylabel='DEC (deg)')
    ax2=plt.subplot(212,xlabel='Time (frames)',ylabel='RA (deg)')
    
    data['ra_s2e'].plot(ax=ax1)
    data['dec_s2e'].plot(ax=ax2)
    
    
    plt.draw()

    plt.pause(0.1)
    errDEC=(data['TelDEC corrected'].subtract(data.targetDEC))
    errRA=(data['TelRA corrected'].subtract(data.targetRA))
    print errDEC[errDEC.abs()<1e-3]
    print errRA[errRA.abs()<1e-3]
    a=1
    plt.ioff()
    plt.show()
    