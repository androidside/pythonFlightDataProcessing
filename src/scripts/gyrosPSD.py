'''
Created on 28 abr. 2017

Plot of the Power Spectrum Density of the Gyroscopes

@author: Marc Casalprim
'''
print 'Imports...'
from matplotlib.style import use
from utils.dataset import DataSet,plt,np
from utils.field import Field,getDtypes#,getFieldsContaining,getFieldsRegex
from scipy.signal.spectral import periodogram
from numpy.fft import fft,ifft

if __name__ == '__main__':
  
    
    folder='C:/17-05-23_19_49_39/'
    folder='F:/LocalBettiiArchive/17-06-08_22_19_34-/'
    #folder='\\\\GS66-WHITE\\LocalAuroraArchive\\17-05-18_00_15_03\\'
    folder='F:/GondolaFlightArchive/17-06-09_09_58_36/'
    
    Field.DTYPES=getDtypes(folder)
    
    fieldsList=[]
     
    fieldsList.append(Field('bettii.GyroReadings.angularVelocityX',label='gyroX',dtype='i4',conversion=0.0006304))
    fieldsList.append(Field('bettii.GyroReadings.angularVelocityY',label='gyroY',dtype='i4',conversion=0.0006437))
    fieldsList.append(Field('bettii.GyroReadings.angularVelocityZ',label='gyroZ',dtype='i4',conversion=0.0006324))
   
    
    initial_time=1100000 #in frame number
    final_time = 4020000 #in frame number
    

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
        ax[i].loglog(f,Pxx)
        ax[i].set_ylim(min(Pxx),max(Pxx))
        ax[i].set_xlim(min(f),max(f))
    plt.tight_layout()
    #ds.multiPSD(gyros,show=True,loglog=False,name="multiPSD_no_loglog",minMax=[1,26])
    
    #RMS
    ax=[]
    plt.figure()
    ax.append(plt.subplot(111,xlabel='Time [Frame Number]', ylabel='Gyro X [arcsec/s]'))
    plt.figure()
    ax.append(plt.subplot(111,xlabel='Time [Frame Number]', ylabel='Gyro X [arcsec/s]'))
    plt.figure()
    ax.append(plt.subplot(111,xlabel='Time [Frame Number]', ylabel='Gyro X [arcsec/s]'))
    gx={}
    for i in range(len(gyros)):
        x=data[gyros[i]].interpolate('values')
        N=len(x)
        f=np.array(range(N))*fs*1.0/N
        fc=3
        ic=int(fc/fs*N)       
        X = fft(x, fs)
        X[:ic]=0
        ax[i].plot(f,abs(X))
        ax[i].set_ylim(min(X),max(X))
        ax[i].set_xlim(min(f),max(f))
        x=ifft(X)
        gx[i]=x
        rms=np.sqrt(np.sum(x**2))
        print "RMS #"+str(i)+": "+str(rms)
    plt.tight_layout()
    
    plt.draw()
    plt.pause(1)
    
    plt.ioff()
    plt.show()