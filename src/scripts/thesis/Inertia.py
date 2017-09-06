'''
Created on 22 aug. 2017



@author: Marc Casalprim
'''
print 'Imports...'
import matplotlib as mpl
from matplotlib.style import use
import numpy as np
from utils.dataset import DataSet,plt,pd
from utils.field import Field,getDtypes#,getFieldsContaining,getFieldsRegex


if __name__ == '__main__':
    folder = "C:/17-04-24_19_02_57/"
    folder = "F:/LocalAuroraArchive/17-05-30_19_44_12/"

    
    Field.DTYPES=getDtypes(folder)
    
    fieldsList=[]
     
    fieldsList.append(Field('bettii.RTHighPriority.CCMGStepperSpeedManualValue',label='manual_speed')) 
    fieldsList.append(Field('bettii.PIDOutputCCMG.ut',label='ut_ccmg'))
    fieldsList.append(Field('bettii.StepperGalil.wheelsAngle',label='wheels_angle'))
    fieldsList.append(Field('bettii.GyroReadings.angularVelocityX',label='gyroX',dtype='i4',conversion=0.0006304))
    fieldsList.append(Field('bettii.GyroReadings.angularVelocityY',label='gyroY',dtype='i4',conversion=0.0006437))
    fieldsList.append(Field('bettii.GyroReadings.angularVelocityZ',label='gyroZ',dtype='i4',conversion=0.0006324))
   
 
    initial_time=4274000 #in frame number
    final_time = 4283400 #in frame number
    
    
    #===========================================================================
    # initial_time=None #in frame number
    # final_time = None #in frame number
    #===========================================================================

    
    
    ds = DataSet(folder,fieldsList=fieldsList,min=initial_time,max=final_time,verbose=True)

    print 'Dataframe shape:', ds.df.shape
    data=ds.df.interpolate(method='values').dropna()
    data.index=(data.index-data.index[0])/ds.freq #index in seconds
    t=np.array(data.index)
    dt=np.diff(t)
    M=80 #moving average window size
    theta=np.array(pd.rolling_mean(data,M).wheels_angle)*np.pi/180. #rad
    omega=np.array(pd.rolling_mean(data,M).gyroZ)/3600*np.pi/180. #rad/s
    tdot=np.diff(theta)/dt #rad/s
    wdot=np.diff(omega)/dt #rad/s2
    torque=20.8*tdot*np.cos(theta[:-1])
    N=100 #moving average torque
    torque=np.convolve(torque, np.ones((N,))/N, mode='same')
    N=100 #moving average wdot
    wdot=np.convolve(wdot, np.ones((N,))/N, mode='same')
    Jzt=torque/wdot
    mtorque=np.mean(torque[2*N:])
    mwdot=np.mean(wdot[2*N:])
    Jz=mtorque/mwdot
    #Jzt=np.convolve(Jzt, np.ones((1000,))/1000, mode='same')
    
    print"Torque: %s Nms \nWdot: %s rad/s2" % (mtorque,mwdot)
    print "Inertia Jz: %0.2f kg m^2" % Jz     
    
    use('seaborn-bright')
    mpl.rcParams['axes.grid']=True
    #plt.rc('text', usetex=True)
    plt.rc('font', family='serif')
    
    time_label='Time (s)'
    plt.figure()
    ax1=plt.subplot(211,ylabel=r'Wheels angle $\theta$ ($deg$)') 
    ax2=plt.subplot(212,xlabel=time_label,ylabel=r'Azimuth velocity $\omega$ ($rad/s$)')

    plt.figure()
    ax3=plt.subplot(211,ylabel='Torque (Nms)')   
    ax4=plt.subplot(212,xlabel=time_label,ylabel=r'Azimuth acceleration $\dot{\omega}$ ($rad/s^2$)')
        
    ax1.plot(t,theta)
    ax2.plot(t,omega)
    ax3.plot(t[:-1],torque)
    ax4.plot(t[:-1],wdot)
    
    #===========================================================================
    # plt.figure()
    # ax=plt.subplot(111,xlabel=time_label,ylabel=r'Inertia $J_z$ ($kg\ m^2$)')
    # ax.plot(t[:-1],Jzt)
    #===========================================================================
    
    #ut=data.ut_ccmg.add(data.manual_speed)
    #mdict={'ut':ut.values,'az_speed':data.gyroZ.values,'mceFN':data.index.values,'wheels_angle':data.wheels_angle.values}
    #io.savemat('C:/Users/marc/Documents/MATLAB/IDccmg_3005.mat',mdict)

    plt.show()