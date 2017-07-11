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
    
  
    gyros = ['gyroX','gyroY','gyroZ']

    data[gyros].plot()
    
    fs=100.#ds.freq/np.diff(data.index).mean(); 
    #RMS
    ax=[]
    plt.figure()
    ax.append(plt.subplot(111, ylabel='Gyro X [arcsec/s]'))
    plt.figure()
    ax.append(plt.subplot(111, ylabel='Gyro Y [arcsec/s]'))
    plt.figure()
    ax.append(plt.subplot(111, ylabel='Gyro Z [arcsec/s]'))
    gx={}
    for i in range(len(gyros)):
        x=data[gyros[i]].interpolate('values')
        N=len(x)
        f=np.array(range(N))*fs/N
        fc=3 #in Hz
        ic=int(fc/fs*N)       
        X = fft(x)
        X[:ic]=0
        X[N-ic:N]=0
        x=ifft(X)
        tr=1000 #number of smaples for the transition time of the ifft
        x=np.real(x[tr:N-tr])
        gx[i]=x
        ax[i].plot(x)
        ax[i].figure.tight_layout()

        rms=np.sqrt(np.mean(x**2))
        print "RMS "+gyros[i]+": "+str(rms)+" arcsec/s"
    
    plt.show()