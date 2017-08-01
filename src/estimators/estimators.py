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


class Estimator(object):
    '''
    Class describing an estimator.
    '''
    
    GYROS_FILENAME="gyros_dataframe"
    SC_FILENAME="sc_dataframe"
    EST_FILENAME="est_dataframe"
    QUATS_FILENAME="quats_dataframe"
    
    def __init__(self, gyros, sc):
        '''Constructor
        The dataframes must follow the following formats:
        gyros -- gyroX,gyroY,gyroZ
        sc    -- qI2G,ra_err,dec_err,roll_err
        '''
        self.gyros=gyros #dataframe whith the gyrsocopes data
        self.sc=sc #dataframe with the starcamera data
        self.est=None #resulting dataframe
        
    def plot(self):
        '''
        Plot the estimated attitude and biases
        '''
        if self.est is None:
            raise Exception("No data to plot. Please, call the estimate() method before scripts.")
        
        plotColumns(self.est[['biasX','biasY','biasZ']], '(arcsec/s)')
        
        ind=self.est.index-self.est
        self.est.index=ind
        
        plt.figure()
        ax=plt.subplot(111)
        self.est['RA'].plot(ax=ax)
        plt.plot(self.sc.index,[q.ra for q in self.sc.qI2G.values],'o')
        ax.legend(['Estimated','Starcamera'])  
        ax.set_xlabel('Time (frames)')
        ax.set_ylabel('RA (deg)')
        ymin=min(self.est['RA'])
        ymax=max(self.est['RA'])
        ax.set_ylim([ymin,ymax])

        plt.figure()
        ax=plt.subplot(111)
        self.est['DEC'].plot(ax=ax)
        plt.plot(self.sc.index,[q.dec for q in self.sc.qI2G.values],'o')
        ax.legend(['Estimated','Starcamera'])  
        ax.set_xlabel('Time (frames)')
        ax.set_ylabel('DEC (deg)')
        # recompute the ax.dataLim
        ax.relim()
        # update ax.viewLim using the new dataLim
        ax.autoscale_view()

        plt.figure()
        ax=plt.subplot(111)
        self.est['ROLL'].plot(ax=ax)
        plt.plot(self.sc.index,[q.roll for q in self.sc.qI2G.values],'o')
        ax.legend(['Estimated','Starcamera'])  
        ax.set_xlabel('Time (frames)')
        ax.set_ylabel('ROLL (deg)')
        # recompute the ax.dataLim
        ax.relim()
        # update ax.viewLim using the new dataLim
        ax.autoscale_view()

    def save(self,folder='./'):
        """Save the dataframes in pickle files"""
        self.gyros.to_pickle(folder+self.GYROS_FILENAME)
        self.sc.to_pickle(folder+self.SC_FILENAME)
        if self.est is not None: self.est.to_pickle(folder+self.EST_FILENAME)
        
    def estimate(self):
        '''Fills the self.est dataframe with the estimated data.
           self.est will have, at least, the columns RA,DEC,ROLL,biasX,biasY,biasZ
           All the subclasses will implement this "abstract" method, adding the desired parameters.
        '''
        raise NotImplementedError("Please, implement the estimate() method.")    

class Estimator6(Estimator):
    '''
    Class implementing the original 6 state Kalman filter.
    '''
    EST_FILENAME=Estimator.EST_FILENAME+"6"
    def estimate(self,P0=np.eye(6),b0=np.zeros(3),q0=None,Qd=np.eye(6),ts=None,te=None,progress=False):
        gyros=self.gyros.loc[ts:te]
        if progress:
            start_time = timer()
            printOn=0
            print "Initializing..."
        if q0 is None: #initializing the estimated attitude quaternion
            fig=gyros.index[0]
            fis=self.sc.index[0]
            if fig>=fis:
                isc=next((i for i,ind in enumerate(self.sc.index) if ind>fig))
                q0=self.sc.qI2G.iloc[isc-1] #nearest past starcamera solution to the gyros start assigned to the quaternion
                sc=self.sc.iloc[isc:]
            else:
                q0=self.sc.qI2G.loc[fis]
                ig=next((i for i,ind in enumerate(gyros.index) if ind>fis))
                gyros=gyros.loc[ig:]
                sc=self.sc.iloc[1:]
        else: sc=self.sc.loc[ts:te]
        nextSCindex=0
        i0=gyros.index[0]            
        q_prop=q0

        bias=b0
        L=len(gyros.index)
        props=[q_prop]*L
        i_prop=[i0]*L
        biases=[bias]*L
        Ps=[P0]*L
        
        C=np.matrix([[0.999999, 0.000309,-0.002822],[0.001062, 0.999995,-0.0031],[0.00129,0.002992,0.999991]])
        P=P0
        H=np.eye(3,6)
        dt=0.01
        
        if progress: print "Starting estimation:"
        for j in range(L-1):
            #Prediction
            dt=(gyros.index[j+1]-gyros.index[j])/400.
            w=(gyros.iloc[j,:3].as_matrix())*(1/3600.*np.pi/180)-bias #arcsec2rad conversion -bias
            w=np.asarray(C.dot(w).T).T[0]
            wx=w[0];wy=w[1];wz=w[2]
            Ow=np.matrix([[0,wz,-wy,wx],[-wz,0,wx,wy],[wy,-wx,0,wz],[-wx,-wy,-wz,0]]) #Omega(omega)
            A=expm(0.5*Ow*dt)
            q_prop=Quat(A.dot(q_prop.q))
            Theta=np.eye(3)-dt*vec2skew(w)
            Psi=-dt*np.eye(3)
            Phi=np.concatenate((np.concatenate((Theta,np.zeros((3,3)))),np.concatenate((Psi,np.eye(3)))),axis=1)
            P=Phi.dot(P.dot(Phi.T))+Qd
            
            ind=gyros.index[j]
            if nextSCindex < len(sc.index) and ind >= sc.index[nextSCindex]: #update!
                qmeas=sc.qI2G.iloc[nextSCindex]
                dq=qmeas*q_prop.inv()
                z=dq.q[:3]
                Mrot=np.matrix([[0.693865,0,0.720106],[0,1,0],[-0.720106,0,0.693865]]) #matrix used in LabView to rotate R to the Gyros ref. frame (~46 deg)
                R=np.diag(sc.iloc[nextSCindex][['ra_err','dec_err','roll_err']].tolist())**2
                R=Mrot*R*Mrot.T
                S=np.matrix(H.dot(P.dot(H.T))+R)
                K=P.dot((H.T).dot(S.I))
                x=np.asarray(K.dot(z))[0]
                dq=x[:3]
                db=x[3:]
                n=dq.dot(dq)
                if n<=1:
                    qd=Quat([dq[0],dq[1],dq[2],np.sqrt(1-n)])
                else:
                    qd=Quat(np.array([dq[0],dq[1],dq[2],1])/np.sqrt(1+n))
                q_prop=qd*q_prop

                bias=bias+db
                J=(np.eye(6)-K.dot(H))
                P=J.dot(P.dot(J.T))+K.dot(R.dot(K.T))
                nextSCindex=nextSCindex+1
                if progress: print "UPDATE! (%s/%s)" % ((nextSCindex+1),len(sc.index))
            props[j+1]=q_prop
            biases[j+1]=bias
            i_prop[j+1]=ind
            Ps[j+1]=P

            percentage=100.0*j/L
            if progress and percentage>=printOn:
                et=timer()-start_time
                print 'Estimating %0.2f%%' % percentage
                print "Elapsed time: %0.2f seconds." %et
                if percentage>0: print "Remaining time: %0.2f minutes." % (et/percentage*(100-percentage)/60)
                print "Data duration: %0.2f minutes" % (L/2400.)
                printOn=printOn+0.1
        
        d={'qest': props,
           'biases':biases,
           'biasX':[bias[0] for bias in biases],
           'biasY':[bias[1] for bias in biases],
           'biasZ':[bias[2] for bias in biases],
           'RA':[q.ra for q in props],
           'DEC':[q.dec for q in props],
           'ROLL':[q.roll for q in props],
           'P':Ps
           }
        self.est=pd.DataFrame(d,index=i_prop)
class Estimator15(Estimator):
    '''
    Class implementing the 15 state Kalman filter.
    '''
    EST_FILENAME=Estimator.EST_FILENAME+"15" 
    def estimate(self,P0=np.eye(15),b0=np.zeros(3),k0=np.zeros(3),m0=np.zeros(6),q0=None,Qd=np.eye(15),ts=None,te=None,progress=False):
        gyros=self.gyros.loc[ts:te]
        if progress:
            start_time = timer()
            printOn=0
            print "Initializing..."
        if q0 is None: #initializing the estimated attitude quaternion
            fig=gyros.index[0]
            fis=self.sc.index[0]
            if fig>=fis:
                isc=next((i for i,ind in enumerate(self.sc.index) if ind>fig))
                q0=self.sc.qI2G.iloc[isc-1] #nearest past starcamera solution to the gyros start assigned to the quaternion
                sc=self.sc.iloc[isc:]
            else:
                q0=self.sc.qI2G.loc[fis]
                ig=next((i for i,ind in enumerate(gyros.index) if ind>fis))
                gyros=gyros.loc[ig:]
                sc=self.sc.iloc[1:]
        else: sc=self.sc.loc[ts:te]
        nextSCindex=0
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
        Ps=[P0]
        C=np.matrix([[0.999999, 0.000309,-0.002822],[0.001062, 0.999995,-0.0031],[0.00129,0.002992,0.999991]])
        P=P0
        H=np.eye(3,15)
        dt=0.01
        L=len(gyros.index)-1
        for j in range(L):
            #Prediction
            dt=(gyros.index[j+1]-gyros.index[j])/400.
            w=(gyros.iloc[j,:3].as_matrix())*(1/3600.*np.pi/180)-bias #arcsec2rad conversion -bias
            M=np.matrix([[1-k[0],-m[0],-m[1]], [-m[2],1-k[1],-m[3]], [-m[4],-m[5],1-k[2]]]) #M=I-dM   dM=kdiag+[m]
            w=np.asarray(M.dot(C.dot(w).T)).T[0]
            wx=w[0];wy=w[1];wz=w[2]
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
            if nextSCindex < len(sc.index) and ind >= sc.index[nextSCindex]: #update!
                qmeas=sc.qI2G.iloc[nextSCindex]
                dq=qmeas*q_prop.inv()
                z=dq.q[:3]
                Mrot=np.matrix([[0.693865,0,0.720106],[0,1,0],[-0.720106,0,0.693865]]) #matrix used in LabView to rotate R to the Gyros ref. frame (~46 deg)
                R=np.diag(sc.iloc[nextSCindex][['ra_err','dec_err','roll_err']].tolist())**2 #we should read that from starcam
                R=Mrot*R*Mrot.T
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
                nextSCindex=nextSCindex+1
                if progress: print "UPDATE! (%s/%s)" % ((nextSCindex+1),len(sc.index))
            props.append(q_prop)
            ks.append(k)
            ms.append(m)
            biases.append(bias)
            Ps.append(P)
            i_prop.append(ind)
            
            percentage=100.0*j/L
            if progress and percentage>=printOn:
                et=timer()-start_time
                print 'Estimating %0.2f%%' % percentage
                print "Elapsed time: %0.2f seconds." %et
                if percentage>0: print "Remaining time: %0.2f minutes." % (et/percentage*(100-percentage)/60)
                print "Data duration: %0.2f minutes" % (L/2400.)
                printOn=printOn+0.1
        d={'qest': props,
           'biases':biases,
           'k':ks,
           'm':ms,
           'biasX':[bias[0] for bias in biases],
           'biasY':[bias[1] for bias in biases],
           'biasZ':[bias[2] for bias in biases],
           'RA':[q.ra for q in props],
           'DEC':[q.dec for q in props],
           'ROLL':[q.roll for q in props],
           'P':Ps
           }
        self.est=pd.DataFrame(d,index=i_prop)