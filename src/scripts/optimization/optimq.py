'''
Created on 28 abr. 2017

Main script

@author: Marc Casalprim
'''
print 'Imports...'
import numpy as np
from scipy.linalg import expm
from utils.quat import Quat,fmin,sin,cos
from utils.dataset import DataSet,plt,sns,load_single_field,pd
from utils.field import Field,getDtypes#,getFieldsContaining,getFieldsRegex
from itertools import izip_longest

def costFunc(angles,df,i2s):
    print "Angles:",angles,
    i=i2s.loc[df.index[0]:].index[0] #index of the first starcamera solution trigger when having gyros
    q_old=i2s.qI2G.loc[i]
    df=df.loc[i:]
    i_old=df.index[0]
    q_prop=q_old
    errs=[0]*len(i2s.index)
    gyros=df[['gyroX','gyroY','gyroZ']].loc[i_old:].dropna()

    q=Quat(angles);
    M=np.matrix([[0.999999, 0.000309,-0.002822],[0.001062, 0.999995,-0.0031],[0.00129,0.002992,0.999991]]) #Arnab Matrix
    for j in range(len(gyros.index)-1):
        dt=(gyros.index[j+1]-gyros.index[j])/400.
        w=(gyros.iloc[j,:3].as_matrix())*(1/3600.*np.pi/180) #arcsec2rad conversion
        w=M.dot(w)
        wx=w[0,0];wy=w[0,1];wz=w[0,2]
        Ow=np.matrix([[0,wz,-wy,wx],[-wz,0,wx,wy],[wy,-wx,0,wz],[-wx,-wy,-wz,0]]) #Omega(omega)
        A=expm(0.5*Ow*dt)
        q_prop=Quat(A.dot(q_prop.q))
        ind=gyros.index[j]
        if ind in i2s.index:
            qdif=q_prop*(q*i2s.qI2G.loc[ind]).inv()
            err=qdif.q[0]**2+qdif.q[1]**2+qdif.q[2]**2
            errs.append(err)
    cost=np.mean(errs)
    print " Cost:",cost
    return np.mean(errs)

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
    fieldsList.append(Field('bettii.RTLowPriority.RawStarcameraRaDeg',label='roll_sc'))
    fieldsList.append(Field('bettii.RTLowPriority.RawStarcameraMceFrameNumberWhenSCTriggered',label='triggers'))
    #fieldsList.append(Field('bettii.GriffinsGalil.griffinBAngleDegrees',label='griffin_angle')) #44.114721
    fieldsList.append(Field('bettii.GyroReadings.angularVelocityX',label='gyroX',dtype='i4',conversion=-0.0006304))
    fieldsList.append(Field('bettii.GyroReadings.angularVelocityY',label='gyroY',dtype='i4',conversion=-0.0006437))
    fieldsList.append(Field('bettii.GyroReadings.angularVelocityZ',label='gyroZ',dtype='i4',conversion=0.0006324))
    

    initial_time=4000000 #in frame number
    final_time = 5100000 #in frame number
    
    initial_time=1000 #in frame number
    final_time = None #in frame number
    
    
    ds = DataSet(folder,fieldsList=fieldsList,estimator=False,starcam=False,min=initial_time,max=final_time,verbose=True)
    ds.df=ds.df.interpolate(method='values').dropna()
    ds.df=ds.df.loc[initial_time:final_time]
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
    triggers=ds.df['triggers'].drop_duplicates()
    i2s=pd.DataFrame({'qI2G': q_sc_list, 'qest':q_est_list},index=ds.df.index)
    i2s=i2s.loc[triggers.index]
    i2s.index=triggers.values
    
    angles0=[0.0003,-0.0028,-0.003]
    print "Starting optim..."
    xopt=fmin(costFunc,angles0,args=(ds.df,i2s),full_output=True,disp=True)

    print xopt
    a=1  