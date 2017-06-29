'''
Created on 28 abr. 2017

Main script

@author: Marc Casalprim
'''
from matplotlib.pyplot import xlabel
print 'Imports...'
from matplotlib.style import use
from utils.dataset import DataSet,plt,np
from utils.field import Field,getDtypes#,getFieldsContaining,getFieldsRegex
import pandas as pd
from scipy.signal.spectral import periodogram


if __name__ == '__main__':
  
    
    folder='C:/17-05-23_19_49_39/'
    folder='F:/LocalBettiiArchive/17-06-08_22_19_34-/'
    #folder='\\\\GS66-WHITE\\LocalAuroraArchive\\17-05-18_00_15_03\\'
    #folder='C:/16-09-28_21_58_34-/'
    
    Field.DTYPES=getDtypes(folder)
    
    fieldsList=[]
     
    fieldsList.append(Field('bettii.GyroReadings.angularVelocityX',label='gyroX',dtype='i4',conversion=0.0006304))
    fieldsList.append(Field('bettii.GyroReadings.angularVelocityY',label='gyroY',dtype='i4',conversion=0.0006437))
    fieldsList.append(Field('bettii.GyroReadings.angularVelocityZ',label='gyroZ',dtype='i4',conversion=0.0006324))
   
    
    initial_time=1000 #in frame number
    final_time = 16700000 #in frame number
    

    #===========================================================================
    
    ds = DataSet(folder,fieldsList=fieldsList,min=initial_time,max=final_time,verbose=True,rpeaks=False)
    
    print 'Dataframe shape:', ds.df.shape
    data=ds.df.dropna()
    #data.index=data.index/ds.freq #index in seconds
    use('ggplot')
    
    plt.ion()
    
    gyros = ['gyroX','gyroY','gyroZ']

    ax=[]
    fig=plt.figure(1)
    fig.suptitle("Gyros PSDs [(arcsec/s)$^2$/Hz]", fontsize=15,y=1)
    ax.append(plt.subplot(311,xlabel='Frequency [Hz]', ylabel='Gyro X'))
    ax.append(plt.subplot(312,xlabel='Frequency [Hz]', ylabel='Gyro Y'))
    ax.append(plt.subplot(313,xlabel='Frequency [Hz]', ylabel='Gyro Z'))
    
    data[gyros].plot()
    
    fs=100#ds.freq/np.diff(data.index).mean();
    print "Approx dt:",np.diff(data.index).mean();
    plt.figure(3)
    plt.plot((data.index[1:]-data.index[0])/400./60.,np.diff(data.index)/400./60.)
    plt.xlabel('Time (min)')
    plt.ylabel('dt (min)')
    for i in range(len(gyros)):
        x=data[gyros[i]].interpolate('values')
        f, Pxx = periodogram(x, fs)
        ax[i].plot(f,Pxx)
        ax[i].set_ylim(min(Pxx),max(Pxx))
        ax[i].set_xlim(min(f),max(f))
    #fig.tight_layout()
    #ds.multiPSD(gyros,show=True,loglog=False,name="multiPSD_no_loglog",minMax=[1,26])

    plt.draw()
    plt.pause(1)
    
    plt.ioff()
    plt.show()