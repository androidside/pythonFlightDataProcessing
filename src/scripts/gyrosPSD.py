'''
Created on 28 abr. 2017

Plot of the Power Spectrum Density of the Gyroscopes

@author: Marc Casalprim
'''
print 'Imports...'
import matplotlib as mpl
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
    use('seaborn-bright')
    mpl.rcParams['axes.grid'] = True
    plt.rc('font', family='serif')
    
    gyros = ['gyroX','gyroY','gyroZ']
    
    d=data.copy()
    d.index=(data.index-data.index[0])/400.
    ax=d[gyros].plot()
    ax.set_ylabel('Angular velocity [arcsec/s]')
    ax.set_xlabel('Time [s]')
    ax.figure.tight_layout()
    
    ax=[]
    fig=plt.figure()
    fig.suptitle("Gyros PSDs [(arcsec/s)$^2$/Hz]", fontsize=15,y=1)
    ax.append(plt.subplot(311,xlabel='Frequency [Hz]', ylabel='Gyro X'))
    ax.append(plt.subplot(312,xlabel='Frequency [Hz]', ylabel='Gyro Y'))
    ax.append(plt.subplot(313,xlabel='Frequency [Hz]', ylabel='Gyro Z'))
    

    
    fs=100#ds.freq/np.diff(data.index).mean();
    print "Approx dt: %0.1f frames." % np.diff(data.index).mean();
    plt.figure(3)
    plt.plot((data.index[1:]-data.index[0])/400./60.,np.diff(data.index)/400.)
    plt.xlabel('Time (min)')
    plt.ylabel('dt (s)')
    for i in range(len(gyros)):
        x=data[gyros[i]].interpolate('values')
        f, Pxx = periodogram(x, fs)
        ax[i].loglog(f,Pxx)
        ax[i].set_ylim(1e-10,1e7)
        ax[i].set_xlim(min(f),max(f))
    plt.tight_layout()
    #ds.multiPSD(gyros,show=True,loglog=False,name="multiPSD_no_loglog",minMax=[1,26])
    
    #RMS
    ax=[]
    plt.figure()
    ax.append(plt.subplot(111,xlabel='Time [s]', ylabel='Gyro X [arcsec/s]'))
    plt.figure()
    ax.append(plt.subplot(111,xlabel='Time [s]', ylabel='Gyro Y [arcsec/s]'))
    plt.figure()
    ax.append(plt.subplot(111,xlabel='Time [s]', ylabel='Gyro Z [arcsec/s]'))
    gx={}
    styles=['b','g','r']
    for i in range(3):
        x=data[gyros[i]].interpolate('values')
        N=len(x)
        #Low pass filter @ fc Hz
        fc=5 #3hz
        ic=int(fc*1.0/fs*N)
        iu=int(0*1.0/fs*N)       
        X = fft(x, N)
        X[:ic]=0
        X[N-ic:]=0
        #x[N/2-iu:N/2+iu]=0
        x=np.real(ifft(X))
        T=2*ic #transitori
        x=x[T:N-T]
        t=(np.arange(T,N-T))/fs
        ax[i].plot(t,x,styles[i])
        ax[i].set_ylim(min(x),max(x))
        ax[i].set_xlim(min(t),max(t))

        gx[i]=x
        rms=np.sqrt(np.mean(x[:2000]**2))
        print "RMS #"+str(i)+": "+str(rms)
    plt.tight_layout()
    

    plt.show()