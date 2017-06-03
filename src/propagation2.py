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

    #folder = "\\\\GS66-WHITE\\LocalAuroraArchive\\17-05-21_02_46_56\\"
    #folder='C:/17-05-23_23_45_10/'
    folder = "C:/17-05-28_00_59_52/"
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
    fieldsList.append(Field('bettii.RTLowPriority.RawStarcameraRaDeg',label='roll_sc'))
    fieldsList.append(Field('bettii.RTLowPriority.RawStarcameraMceFrameNumberWhenSCTriggered',label='triggers'))
    #fieldsList.append(Field('bettii.GriffinsGalil.griffinBAngleDegrees',label='griffin_angle')) #44.114721
    fieldsList.append(Field('bettii.GyroReadings.angularVelocityX',label='gyroX',dtype='i4',conversion=-0.0006304))
    fieldsList.append(Field('bettii.GyroReadings.angularVelocityY',label='gyroY',dtype='i4',conversion=-0.0006437))
    fieldsList.append(Field('bettii.GyroReadings.angularVelocityZ',label='gyroZ',dtype='i4',conversion=0.0006324))
    

    initial_time=2000000 #in frame number
    final_time = 2010000 #in frame number
    
    #===========================================================================
    # initial_time=None #in frame number
    # final_time = None #in frame number
    #===========================================================================
    
    #===========================================================================
    # initial_time=7000000 #in frame number
    # final_time = 7010000 #in frame number
    #===========================================================================
    
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
    i=0
    for mceFN in ds.df.index:
        print str(100.0*i/len(ds.df.index))+'%'
        q_est=Quat((ds.df.loc[mceFN][['qi','qj','qk','qr']]))
        q_sc=Quat((ds.df.loc[mceFN][['qi_sc','qj_sc','qk_sc','qr_sc']]))
        q_i2s=Quat((ds.df.loc[mceFN][['ra_sc','dec_sc','roll_sc']]))
        q_est_list.append(q_est)
        q_sc_list.append(q_sc)
        qI2Starcam_list.append(q_i2s) #no other way to get the SC solution :( There is now!!
        i=i+1
    triggers=ds.df['triggers'].drop_duplicates()
    i2s=pd.DataFrame({'qI2S': qI2Starcam_list,'qI2G': q_sc_list, 'qest':q_est_list},index=ds.df.index)
    i2s=i2s.loc[triggers.index]
    i2s.index=triggers.values  

    i=i2s.loc[ds.df.index[0]:].index[0] #index of the first starcamera solution trigger when having gyros
    q_old=i2s.qI2G.loc[i]
    ds.df=ds.df.loc[i:]
    i2s=i2s.loc[i:]
    i_old=ds.df.index[0]
    
    q_prop=Quat((0,0,0,1))
    props=[q_prop]
    i_prop=[i_old]
    errs=[]
    i_err=[]
    gyros=ds.df[['gyroX','gyroY','gyroZ']].loc[i_old:].dropna()
    #===========================================================================
    # c=[0.0001,0.0001,0.0001]
    # cxy=c[0];cxz=c[1];cyz=c[2];
    # C=np.matrix([[0.0, cxy,cxz],[-cxy, 0.0,cyz],[-cxz,-cyz,0.0]])
    # M=np.eye(3)-C
    #===========================================================================
    M=np.matrix([[0.999999, 0.000309,-0.002822],[0.001062, 0.999995,-0.0031],[0.00129,0.002992,0.999991]])
    print "Propagating..."
    for j in range(len(gyros.index)-1):
        print str(100.0*j/(len(gyros.index)-1))+'%'
        dt=(gyros.index[j+1]-gyros.index[j])/400.
        w=(gyros.iloc[j,:3].as_matrix())*(1/3600.*np.pi/180) #arcsec2rad conversion
        w=M.dot(w)
        wx=w[0,0];wy=w[0,1];wz=w[0,2]
        #wx=w[0];wy=w[1];wz=w[2]
        Ow=np.matrix([[0,wz,-wy,wx],[-wz,0,wx,wy],[wy,-wx,0,wz],[-wx,-wy,-wz,0]]) #Omega(omega)
        A=scipy.linalg.expm(0.5*Ow*dt)
        q_prop=Quat(A.dot(q_prop.q))
        props.append(q_prop)
        ind=gyros.index[j]
        i_prop.append(ind)
        if ind in i2s.index:
            qdif=q_prop*i2s.qI2S.loc[ind].inv()
            err=qdif.q[0]**2+qdif.q[1]**2+qdif.q[2]**2
            errs.append(qdif)
            i_err.append(ind)

    
    print "Plotting..."
    matplotlib.style.use('classic')
    matplotlib.rcParams['axes.grid']=True
    
    fig=plt.figure()
    ax=plt.subplot(111)
    plt.plot(i_prop,[q.ra for q in props])
    plt.plot(i2s.index,[q.ra for q in i2s.qI2S.values])
    ax.legend(['Propagated','Starcam'])                         
    ax.set_xlabel('Time (frames)')
    ax.set_ylabel('RA (deg)')
        
    fig=plt.figure()
    ax=plt.subplot(111)
    plt.plot(i_prop,[q.dec for q in props])
    plt.plot(i2s.index,[q.dec for q in i2s.qI2S.values])
    ax.legend(['Propagated','Starcam'])  
    ax.set_xlabel('Time (frames)')
    ax.set_ylabel('DEC (deg)')
        
    fig=plt.figure()
    ax=plt.subplot(111)
    plt.plot(i_prop,[q.roll for q in props])
    plt.plot(i2s.index,[q.roll for q in i2s.qI2S.values])
    ax.legend(['Propagated','Starcam'])  
    ax.set_xlabel('Time (frames)')
    ax.set_ylabel('ROLL (deg)')
    
    fig=plt.figure()
    for i in range(4):
        ax=plt.subplot(2,2,i+1)
        plt.plot(i_err,[q.q[i] for q in errs])
        ax.set_ylabel('dq'+str(i))
    
    fig=plt.figure()
    ax=plt.subplot(3,1,1)
    plt.plot(i_err,[q.ra*3600 for q in errs])
    ax.set_ylabel('RA (arcsec)')
    ax=plt.subplot(3,1,2)
    plt.plot(i_err,[q.dec*3600 for q in errs])
    ax.set_ylabel('DEC (arcsec)')
    ax=plt.subplot(3,1,3)
    plt.plot(i_err,[q.roll*3600 for q in errs])
    ax.set_ylabel('ROLL (arcsec)')
    
    fig=plt.figure()
    ax=plt.subplot(3,1,1)
    plt.plot(i_err,[q.ra for q in errs])
    ax.set_ylabel('RA (deg)')
    ax=plt.subplot(3,1,2)
    plt.plot(i_err,[q.dec for q in errs])
    ax.set_ylabel('DEC (deg)')
    ax=plt.subplot(3,1,3)
    plt.plot(i_err,[q.roll for q in errs])
    ax.set_ylabel('ROLL (deg)')
    
    mq=range(4)
    for i in range(4):
        mq[i]=np.array([q.q[i] for q in errs]).mean()
    print mq
    print np.linalg.norm(mq)
    a=1  
    plt.show()