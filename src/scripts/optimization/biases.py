'''
Created on 28 abr. 2017

Main script

@author: Marc Casalprim
'''
print 'Imports...'
import numpy as np
from scipy.linalg import expm
from utils.quat import Quat,fmin,sin,cos
from utils.dataset import DataSet,genQuaternions,sns,load_single_field,pd
from utils.field import Field,getDtypes#,getFieldsContaining,getFieldsRegex
from itertools import izip_longest

def costFunc(bias,df,i2s):
    print "Biases:",bias,
    i=i2s.loc[df.index[0]:].index[0] #index of the first starcamera solution trigger when having gyros
    q_old=i2s.qI2G.loc[i]
    df=df.loc[i:]
    i_old=df.index[0]
    q_prop=q_old
    errs=[]
    gyros=df[['gyroX','gyroY','gyroZ']].loc[i_old:].dropna()
    c=[0.00061037, -0.00354721,  0.00801496]
    cxy=c[0];cxz=c[1];cyz=c[2];
    C=np.matrix([[0.0, cxy,cxz],[-cxy, 0.0,cyz],[-cxz,-cyz,0.0]])
    M=np.eye(3)-C
    index=gyros.index.values
    gyros=gyros.as_matrix()
    for j in range(len(index)-1):
        dt=(index[j+1]-index[j])/400.
        w=(gyros[j]-bias)*(1/3600.*np.pi/180) #arcsec2rad conversion
        w=M.dot(w)
        wx=w[0,0];wy=w[0,1];wz=w[0,2]
        Ow=np.matrix([[0,wz,-wy,wx],[-wz,0,wx,wy],[wy,-wx,0,wz],[-wx,-wy,-wz,0]]) #Omega(omega)
        A=expm(0.5*Ow*dt)
        q_prop=Quat(A.dot(q_prop.q))
        ind=index[j]
        if ind in i2s.index:
            qdif=q_prop*i2s.qI2G.loc[ind].inv()
            err=qdif.q[0]**2+qdif.q[1]**2+qdif.q[2]**2
            errs.append(err)
    cost=np.mean(errs)
    print " Cost:",cost
    return cost

if __name__ == '__main__':

    #folder = "\\\\GS66-WHITE\\LocalAuroraArchive\\17-05-21_02_46_56\\"
    folder='X:/17-05-23_23_45_07/'
    
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

  
    initial_time=5763364 #in frame number
    final_time = 6840252 #in frame number
    
    
    ds = DataSet(folder,fieldsList=fieldsList,estimator=False,starcam=False,min=initial_time,max=final_time,verbose=True)
    ds.df=ds.df.interpolate(method='values').dropna()
    print 'Dataframe shape:', ds.df.shape



    print "Generating quaternions..."
    data=genQuaternions(ds.df)#, quats={'qest':['qi','qj','qk','qr'],'qI2G':['qi_sc','qj_sc','qk_sc','qr_sc']})  
    triggers=ds.df['triggers'].drop_duplicates()
    i2s=pd.DataFrame(data,index=ds.df.index)
    i2s=i2s.loc[triggers.index]
    i2s.index=triggers.values
    
    bias0=[0.01,-0.1,-0.01] #arcsec
    bias0=[ 0.00891457,  0.04355891, -0.02588394]
    print "Starting optim..."
    xopt=fmin(costFunc,bias0,args=(ds.df,i2s),full_output=True,disp=True)

    print xopt
    a=1  