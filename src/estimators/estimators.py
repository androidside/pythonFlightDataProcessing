'''
Created on 29 may. 2017

@author: Marc Casalprim
'''
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from timeit import default_timer as timer
from scipy.linalg import expm
from utils.dataset import plotColumns
from utils.quat import Quat,vec2skew

class Estimator15(object):
    '''
    classdocs
    '''


    def __init__(self, gyros, sc):
        '''
        Constructor
        '''
        self.gyros=gyros
        self.sc=sc
        self.est=None
    
    def plot(self):
        '''
        Plot the estimated attitude
        '''
        plotColumns(self.est[['biasX','biasY','biasZ']], '(arcsec/s)')
        
        plt.figure()
        ax=plt.subplot(111)
        self.est['RA'].plot(ax=ax)
        plt.plot(self.sc.index,[q.ra for q in self.sc.qI2G.values])
        ax.legend(['Estimated','Starcam'])  
        ax.set_xlabel('Time (frames)')
        ax.set_ylabel('RA (deg)')
        
        plt.figure()
        ax=plt.subplot(111)
        self.est['DEC'].plot(ax=ax)
        plt.plot(self.sc.index,[q.dec for q in self.sc.qI2G.values])
        ax.legend(['Estimated','Starcam'])  
        ax.set_xlabel('Time (frames)')
        ax.set_ylabel('DEC (deg)')
        
        plt.figure()
        ax=plt.subplot(111)
        self.est['ROLL'].plot(ax=ax)
        plt.plot(self.sc.index,[q.roll for q in self.sc.qI2G.values])
        ax.legend(['Estimated','Starcam'])  
        ax.set_xlabel('Time (frames)')
        ax.set_ylabel('ROLL (deg)')
        
    
    def estimate(self,P0=np.eye(15),b0=np.zeros(3),k0=np.zeros(3),m0=np.zeros(6),q0=None,Qd=np.eye(15),ts=None,te=None,progress=False):
        gyros=self.gyros.loc[ts:te]
        if progress: start_time = timer()
        if q0 is None:
            i=self.sc.loc[gyros.index[0]:].index[0] #index of the first starcamera solution trigger when having gyros
            q0=self.sc.qI2G.loc[i]
            gyros=gyros.loc[i:]
            sc=self.sc.loc[i:]
        else: sc=self.sc.loc[ts:te]
            
        i0=gyros.index[0]            
        q_prop=q0

        bias=b0
        k=k0
        m=m0
        props=[q_prop]
        i_prop=[i0]
        biases=[bias]
        ks=[k]
        ms=[m]
        C=np.matrix([[0.999999, 0.000309,-0.002822],[0.001062, 0.999995,-0.0031],[0.00129,0.002992,0.999991]])
        P=P0
        H=np.eye(3,15)
        dt=0.01
        L=len(gyros.index)-1
        for j in range(L):
            #Prediction
            if progress: print 'Estimating ',str(100.0*j/L)+'%'
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
            if ind in sc.index: #update!
                qmeas=sc.qI2G.loc[ind]
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
            d={'qest': props,
               'biases':biases,
               'k':ks,
               'm':ms,
               'biasX':[bias[0] for bias in biases],
               'biasY':[bias[1] for bias in biases],
               'biasZ':[bias[2] for bias in biases],
               'RA':[q.ra for q in props],
               'DEC':[q.ra for q in props],
               'ROLL':[q.roll for q in props],
               }
            self.est=pd.DataFrame(d,index=i_prop)
            if progress:
                print "Elapsed time:",timer()-start_time
                print "Data duration:",L/2400.,"minutes"