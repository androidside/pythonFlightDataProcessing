'''
Created on 28 abr. 2017

Main script

@author: Marc Casalprim
'''
print 'Imports...'
import matplotlib
import numpy as np
import scipy
from utils.quat import Quat,normalize,sin,cos
from utils.dataset import DataSet,plt,sns,load_single_field,pd
from utils.field import Field,getDtypes#,getFieldsContaining,getFieldsRegex
from itertools import izip_longest


if __name__ == '__main__':

    
    folder='C:/16-09-28_21_58_34-/'
    folder = "\\\\GS66-WHITE\\LocalAuroraArchive\\17-05-21_02_46_56\\"
    folder='C:/17-05-23_19_49_39/'
    Field.DTYPES=getDtypes(folder)
    
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
    fieldsList.append(Field('bettii.RTLowPriority.RawStarcameraMceFrameNumberWhenSCTriggered',label='triggers'))
    #fieldsList.append(Field('bettii.GriffinsGalil.griffinBAngleDegrees',label='griffin_angle')) #44.114721
    fieldsList.append(Field('bettii.GyroReadings.angularVelocityX',label='gyroX',dtype='i4',conversion=-0.0006304))
    fieldsList.append(Field('bettii.GyroReadings.angularVelocityY',label='gyroY',dtype='i4',conversion=-0.0006437))
    fieldsList.append(Field('bettii.GyroReadings.angularVelocityZ',label='gyroZ',dtype='i4',conversion=0.0006324))
    

    initial_time=4000000 #in frame number
    final_time = 5100000 #in frame number
    
    initial_time=1150000 #in frame number
    final_time = 1200000 #in frame number
    
    #array([ -0.15321407, -44.77279865,  19.87575523])
    dYaw=-0.367
    dPitch=44.9828
    dRoll=-0.79
     
    qdYaw = Quat((dYaw,0,0)); #quat = Quat((ra,dec,roll)) in degrees
    qdPitch = Quat((0.0,sin(dPitch*np.pi/180./2.0),0.0,cos(dPitch*np.pi/180./2.0))) #quat = Quat((ra,dec,roll)) in degrees
    qdRoll = Quat((0,0,dRoll)) #quat = Quat((ra,dec,roll)) in degrees
    
    #qStarcam2Gyros_new =  Quat((dYaw,-dPitch,dRoll))

    qStarcam2Gyros_old =  qdYaw*qdPitch*qdRoll
    qStarcam2Gyros_mid =  qdPitch*qdYaw*qdRoll
    qStarcam2Gyros_new =  Quat((dYaw,-dPitch,dRoll))
    
    qStarcam2Gyros=qStarcam2Gyros_old#[qStarcam2Gyros_old,qStarcam2Gyros_mid,qStarcam2Gyros_new]
    
    ds = DataSet(folder,fieldsList=fieldsList,estimator=False,starcam=False,min=initial_time,max=final_time,verbose=True)
    ds.df=ds.df.interpolate(method='values').dropna()
    ds.df=ds.df.loc[initial_time:final_time]
    print 'Dataframe shape:', ds.df.shape
    
    q_est_list=[]    
    q_sc_list=[]
    qI2Starcam_list=[]
    qStarcam2Est_list=[]
    qGyros2Est_list=[]
    qI2Starcam_list=[]
    print "Generating quaternions..."
    for mceFN in ds.df.index:
        q_est=Quat((ds.df.loc[mceFN][['qi','qj','qk','qr']]))
        q_sc=Quat((ds.df.loc[mceFN][['qi_sc','qj_sc','qk_sc','qr_sc']]))
        q_est_list.append(q_est)
        q_sc_list.append(q_sc)
        qI2Starcam_list.append(qStarcam2Gyros.inv()*q_sc) #no other way to get the SC solution :(
    triggers=ds.df['triggers'].drop_duplicates()
    i2s=pd.DataFrame({'qI2S': qI2Starcam_list,'qI2G': q_sc_list, 'qest':q_est_list},index=ds.df.index)
    i2s=i2s.loc[triggers.index]
    i2s.index=triggers.values  

    q_old=q_est_list[0]
    i_old=ds.df.index[0]
    q_prop=q_old
    props=[q_prop]
    i_prop=[i_old]
    
    gyros=ds.df[['gyroX','gyroY','gyroZ']].loc[i_old:].dropna()
    C=np.eye(4)
    print "Propagating..."
    for j in range(len(gyros.index)-1):
        dt=(gyros.index[j+1]-gyros.index[j])/400.
        bias=[0, 0, 0]#-0.04,-0.17,0.04] #in arcsec
        w=(gyros.iloc[j,:3].as_matrix()-bias)*(1/3600.*np.pi/180) #arcsec2rad conversion
        wx=w[0];wy=w[1];wz=w[2]
        Ow=np.matrix([[0,wz,-wy,wx],[-wz,0,wx,wy],[wy,-wx,0,wz],[-wx,-wy,-wz,0]]) #Omega(omega)
        A=scipy.linalg.expm(0.5*Ow*dt)
        C=A.dot(C)
        q_prop=Quat(A.dot(q_prop.q))
        props.append(q_prop)
        i_prop.append(gyros.index[j+1])

    
    print "Plotting..."
    matplotlib.style.use('classic')
    matplotlib.rcParams['axes.grid']=True
    
    fig=plt.figure()
    ax=plt.subplot(111)
    plt.plot(i_prop,[q.ra for q in props])
    plt.plot(i2s.index,[q.ra for q in i2s.qI2G.values])
    plt.plot(ds.df.index,[q.ra for q in q_est_list])
    plt.plot(ds.df.index,[q.ra for q in q_sc_list])
    ax.legend(['Propagated','Starcamera','Estimated','SC'])                         
    ax.set_xlabel('Time (frames)')
    ax.set_ylabel('RA (deg)')
        
    fig=plt.figure()
    ax=plt.subplot(111)
    plt.plot(i_prop,[q.dec for q in props])
    plt.plot(i2s.index,[q.dec for q in i2s.qI2G.values])
    plt.plot(ds.df.index,[q.dec for q in q_est_list])
    plt.plot(ds.df.index,[q.dec for q in q_sc_list])
    ax.legend(['Propagated','Starcamera','Estimated','SC'])  
    ax.set_xlabel('Time (frames)')
    ax.set_ylabel('DEC (deg)')
        
    fig=plt.figure()
    ax=plt.subplot(111)
    plt.plot(i_prop,[q.roll for q in props])
    plt.plot(i2s.index,[q.roll for q in i2s.qI2G.values])
    plt.plot(ds.df.index,[q.roll for q in q_est_list])
    plt.plot(ds.df.index,[q.roll for q in q_sc_list])
    ax.legend(['Propagated','Starcamera','Estimated','SC'])  
    ax.set_xlabel('Time (frames)')
    ax.set_ylabel('ROLL (deg)')
    plt.show()
    a=1
    
