'''
Created on 28 abr. 2017

Main script

@author: Marc Casalprim
'''
print 'Imports...'
import matplotlib
import numpy as np
from matplotlib.style import use
from scipy.linalg import expm
from utils.quat import Quat,vec2skew,sin,cos
from utils.dataset import DataSet,plt,sns,load_single_field,pd
from utils.field import Field,getDtypes#,getFieldsContaining,getFieldsRegex
from itertools import izip_longest


if __name__ == '__main__':

    #folder = "\\\\GS66-WHITE\\LocalAuroraArchive\\17-05-21_02_46_56\\"
    folder='C:/17-05-23_23_45_10/'
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
    L=len(ds.df.index)
    q_est_list=[0]*L   
    q_sc_list=[0]*L
    q_i2s_list=[0]*L
    print "Generating quaternions..."
    for i in range(L):
        mceFN=ds.df.index[i]
        q_est=Quat((ds.df.loc[mceFN][['qi','qj','qk','qr']]))
        q_sc=Quat((ds.df.loc[mceFN][['qi_sc','qj_sc','qk_sc','qr_sc']]))
        q_i2s=Quat((ds.df.loc[mceFN][['ra_sc','dec_sc','roll_sc']]))
        q_est_list[i]=(q_est)
        q_sc_list[i]=(q_sc)
        q_i2s_list[i]=(q_i2s)
    print "Creating Starcam dataset..."
    triggers=ds.df['triggers'].drop_duplicates()
    i2s=pd.DataFrame({'qI2S': q_i2s_list,'qI2G': q_sc_list, 'qest':q_est_list},index=ds.df.index)
    i2s=i2s.loc[triggers.index]
    i2s.index=triggers.values  

    i=i2s.loc[ds.df.index[0]:].index[0] #index of the first starcamera solution trigger when having gyros
    q_old=i2s.qI2G.loc[i]
    ds.df=ds.df.loc[i:]
    i2s=i2s.loc[i:]
    i_old=ds.df.index[0]
    
    q_prop=q_old
    props=[q_prop]
    i_prop=[i_old]

    gyros=ds.df[['gyroX','gyroY','gyroZ']].loc[i_old:].dropna()

    C=np.matrix([[0.999999, 0.000309,-0.002822],[0.001062, 0.999995,-0.0031],[0.00129,0.002992,0.999991]])
    P=np.eye(15)
    H=np.eye(3,15)
    dt=0.01
    sg=0.1
    sb=0.1
    Q11=sg*dt*np.eye(3)
    Q12=-sb*(dt**2)/2*np.eye(3)
    Q22=sb*dt*np.eye(3)
    #Qd=0.001*np.concatenate((np.concatenate((Q11,Q12.T)),np.concatenate((Q12,Q22))),axis=1)
    Qd=sb*dt*np.eye(15)
    Qd[:3,:3]=Q11
    Qd[3:6,:3]=Q12
    Qd[:3,3:6]=Q12
    Qd[3:6,3:6]=Q22
    Qd=0.1*Qd
    k=np.array([0,0,0])
    m=np.array([0,0,0,0,0,0])
    bias=np.array([0,0,0])   # in arcsec/s
    biases=[bias]
    ks=[k]
    ms=[m]
    print "Estimating..."
    for j in range(len(gyros.index)-1):
        #Prediction
        print str(100.0*j/(len(gyros.index)-1))+'%'
        dt=(gyros.index[j+1]-gyros.index[j])/400.
        w=(gyros.iloc[j,:3].as_matrix())*(1/3600.*np.pi/180)-bias #arcsec2rad conversion -bias
        M=np.matrix([[1-k[0],-m[0],-m[1]], [-m[2],1-k[1],-m[3]], [-m[4],-m[5],1-k[2]]]) #M=I-dM   dM=kdiag+[m]
        w=np.asarray(M.dot(C.dot(w).T)).T[0]
        wx=w[0];wy=w[1];wz=w[2]
        #wx=w[0];wy=w[1];wz=w[2]
        Ow=np.matrix([[0,wz,-wy,wx],[-wz,0,wx,wy],[wy,-wx,0,wz],[-wx,-wy,-wz,0]]) #Omega(omega)
        A=expm(0.5*Ow*dt)
        q_prop=Quat(A.dot(q_prop.q))
        Theta=np.eye(3)-dt*vec2skew(w)
        Ok=np.diag(w)
        Om=np.zeros((3,6)); Om[0,0]=wy;Om[1,2]=wx;Om[2,4]=wx; Om[0,1]=wz;Om[1,3]=wz;Om[2,5]=wy;
        Psi=-dt*np.concatenate((Ok,Om,np.eye(3)),axis=1)
        Phi=np.concatenate((np.concatenate((Theta,np.zeros((12,3)))),np.concatenate((Psi,np.eye(12)))),axis=1)
        P=Phi.dot(P.dot(Phi.T))+Qd
        
        ind=gyros.index[j]
        if ind in i2s.index: #update!
            qmeas=i2s.qI2G.loc[ind]
            dq=qmeas*q_prop.inv()
            z=dq.q[:3]
            R=0.01*np.eye(3) #we should read that from starcam
            S=np.matrix(H.dot(P.dot(H.T))+R)
            K=P.dot((H.T).dot(S.I))
            x=np.asarray(K.dot(z))[0]
            dq=x[:3]
            dk=x[3:6]
            dm=x[6:12]
            db=x[12:]
            n=dq.dot(dq)
            if n<=1:
                qd=Quat([dq[0],dq[1],dq[2],np.sqrt(1-n)])
            else:
                qd=Quat(np.array([dq[0],dq[1],dq[2],1])/np.sqrt(1+n))
            q_prop=qd*q_prop
            k=k+dk
            m=m+dm
            bias=bias+db
            J=(np.eye(15)-K.dot(H))
        P=J.dot(P.dot(J.T))+K.dot(R.dot(K.T))
        props.append(q_prop)
        ks.append(k)
        ms.append(m)
        biases.append(bias)
        i_prop.append(ind)
        #print bias
    
    print "Plotting..."
    use('classic')
    matplotlib.rcParams['axes.grid']=True
    
    fig=plt.figure()
    ax=plt.subplot(111)
    plt.plot(i_prop,[q.ra for q in props])
    plt.plot(i2s.index,[q.ra for q in i2s.qI2G.values])
    plt.plot(i2s.index,[q.ra for q in i2s.qest.values])
    ax.legend(['Propagated','Starcam','Estimated'])                         
    ax.set_xlabel('Time (frames)')
    ax.set_ylabel('RA (deg)')
        
    fig=plt.figure()
    ax=plt.subplot(111)
    plt.plot(i_prop,[q.dec for q in props])
    plt.plot(i2s.index,[q.dec for q in i2s.qI2G.values])
    plt.plot(i2s.index,[q.dec for q in i2s.qest.values])
    ax.legend(['Propagated','Starcam','Estimated'])  
    ax.set_xlabel('Time (frames)')
    ax.set_ylabel('DEC (deg)')
        
    fig=plt.figure()
    ax=plt.subplot(111)
    plt.plot(i_prop,[q.roll for q in props])
    plt.plot(i2s.index,[q.roll for q in i2s.qI2G.values])
    plt.plot(i2s.index,[q.roll for q in i2s.qest.values])
    ax.legend(['Propagated','Starcam','Estimated']) 
    ax.set_xlabel('Time (frames)')
    ax.set_ylabel('ROLL (deg)')
    
    fig=plt.figure()
    ax=plt.subplot(311)
    plt.plot(i_prop,[b[0]*180*3600/np.pi for b in biases])
    ax.set_ylabel('biasX (arcsec/s)')
    ax=plt.subplot(312)
    plt.plot(i_prop,[b[1]*180*3600/np.pi for b in biases])
    ax.set_ylabel('biasY (arcsec/s)')
    ax=plt.subplot(313)
    plt.plot(i_prop,[b[2]*180*3600/np.pi for b in biases])
    ax.set_ylabel('biasZ (arcsec/s)')
    ax.set_xlabel('Time (frames)')
    
    a=1  
    plt.show()