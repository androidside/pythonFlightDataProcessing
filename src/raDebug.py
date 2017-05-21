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
    #fieldsList.append(Field('bettii.PIDOutputMomDump.et',label='mom_et'))
    ##fieldsList.append(Field('bettii.PIDOutputCCMG.et',label='ccmg_et'))
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
    fieldsList.append(Field('bettii.GriffinsGalil.griffinBAngleDegrees',label='griffin_angle')) #44.114721
    
    #target 1    
    initial_time=5145000 #in frame number
    final_time = 5149000 #in frame number
    
    #target 2
    #===========================================================================
    # initial_time=6301000 #in frame number
    # final_time = 6303000 #in frame number
    #===========================================================================
    
    initial_time=None #in frame number
    final_time = None #in frame number
    
    #array([ -0.15321407, -44.77279865,  19.87575523])
    dYaw=-0.15321407
    dPitch=44.77279865
    dRoll=-3.99
     
    qdYaw = Quat((dYaw,0,0)); #quat = Quat((ra,dec,roll)) in degrees
    qdPitch = Quat((0.0,sin(dPitch*np.pi/180./2.0),0.0,cos(dPitch*np.pi/180./2.0))) #quat = Quat((ra,dec,roll)) in degrees
    qdRoll = Quat((0,0,dRoll)) #quat = Quat((ra,dec,roll)) in degrees
    
    #qStarcam2Gyros_new =  Quat((dYaw,-dPitch,dRoll))

    qStarcam2Gyros_old =  qdYaw*qdPitch*qdRoll
    qStarcam2Gyros_mid =  qdPitch*qdYaw*qdRoll
    qStarcam2Gyros_new =  Quat((dYaw,-dPitch,dRoll))
    
    qStarcam2Gyros=[qStarcam2Gyros_old,qStarcam2Gyros_mid,qStarcam2Gyros_new]
    
    ds = DataSet(folder,fieldsList=fieldsList,estimator=False,starcam=False,min=initial_time,max=final_time,verbose=False)
    ds.df=ds.df.interpolate(method='values').dropna()
    
    q_est_list=[]    
    q_sc_list=[]
    qI2Starcam_list=[]
    qStarcam2Est_list=[]
    qGyros2Est_list=[]
    for mceFN in ds.df.index:
        q_est=Quat(normalize(ds.df.loc[mceFN][['qi','qj','qk','qr']]))
        q_sc=Quat((ds.df.loc[mceFN][['qi_sc','qj_sc','qk_sc','qr_sc']]))
        q_est_list.append(q_est)
        q_sc_list.append(q_sc)
    q_est_list=[Quat(normalize(ds.df.loc[mceFN][['qi','qj','qk','qr']])) for mceFN in ds.df.index]
    
    q_sc_list=[Quat((ds.df.loc[mceFN][['qi_sc','qj_sc','qk_sc','qr_sc']])) for mceFN in ds.df.index]
    qI2Starcam_list=[qStarcam2Gyros_old.inv()*q_sc for q_sc in q_sc_list] #my bet but who knows.. :(
    
    qStarcam2Est_list=[ q_est*qI2Starcam.inv() for q_est,qI2Starcam in izip_longest(q_est_list,qI2Starcam_list)] #q_est=qStarcam2Est*qI2Starcam

    #qStarcam2Est=qGyros2Est*qStarcam2Gyros_old
    qGyros2Est_list= [ qStarcam2Est*qStarcam2Gyros_old.inv() for qStarcam2Est in qStarcam2Est_list] #the correction the estimator is applying to the measure (any better way to do that?)
    
    q_est_corrected={'ra':[],'dec':[],'roll':[]}
    for qS2G in qStarcam2Gyros:
        q_est = [Quat((0,ds.df['griffin_angle'].iloc[i],0))*qGyros2Est_list[i]*qS2G*qI2S for i,qI2S in enumerate(qI2Starcam_list)]
        q_est_corrected['ra'].append([q.ra for i,q in enumerate(q_est)])
        q_est_corrected['dec'].append([q.dec for i,q in enumerate(q_est)])
        q_est_corrected['roll'].append([q.roll for i,q in enumerate(q_est)])
    
    d={'ra_old' : q_est_corrected['ra'][0],
       'ra_mid' : q_est_corrected['ra'][1],
       'ra_new' : q_est_corrected['ra'][2],
       'dec_old' : q_est_corrected['dec'][0],
       'dec_mid' : q_est_corrected['dec'][1],
       'dec_new' : q_est_corrected['dec'][2],
       'roll_old' : q_est_corrected['roll'][0],
       'roll_mid' : q_est_corrected['roll'][1],
       'roll_new' : q_est_corrected['roll'][2]}
    teldata= pd.DataFrame(d,index = ds.df.index).dropna()
    ds.df=pd.merge(ds.df,teldata,how='outer',left_index=True,right_index=True)
    data=ds.df.dropna()
    print 'Dataframe shape:', ds.df.shape
    
    
    matplotlib.style.use('ggplot')
    plt.ion()
    
    plt.figure(1)
    ax1=plt.subplot(211,ylabel='RA (deg)')
    ax2=plt.subplot(212,xlabel='Time (frames)',ylabel='DEC (deg)')
    
    plt.figure()
    ax3=plt.subplot(111,xlabel='Time (frames)',ylabel='ROLL (deg)')
    
    data[['ra_old','ra_mid','targetRA']].plot(ax=ax1)
    data[['dec_old','dec_mid','targetDEC']].plot(ax=ax2)
    data[['roll_old','roll_mid','roll_new']].plot(ax=ax3)
    
   
    
    
    plt.draw()

    plt.pause(0.1)
    errDEC=(data['dec_new'].subtract(data.targetDEC))
    errRA=(data['ra_new'].subtract(data.targetRA))
    print errDEC[errDEC.abs()<1e-3]
    print errRA[errRA.abs()<1e-3]
    a=1
    plt.ioff()
    plt.show()
    
