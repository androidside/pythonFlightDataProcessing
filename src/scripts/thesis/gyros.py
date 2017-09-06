'''
Created on 28 abr. 2017

Plot of the Power Spectrum Density of the Gyroscopes

@author: Marc Casalprim
'''
print 'Imports...'
import matplotlib as mpl
from matplotlib.style import use
from utils.dataset import DataSet,plt,pd
from utils.field import Field,getDtypes#,getFieldsContaining,getFieldsRegex
from scipy.signal.spectral import periodogram
from numpy.fft import fft,ifft

if __name__ == '__main__':
  
    
    folder='C:/17-05-23_19_49_39/'
    folder='F:/LocalBettiiArchive/17-06-08_22_19_34-/'
    #folder='\\\\GS66-WHITE\\LocalAuroraArchive\\17-05-18_00_15_03\\'
    folder='F:/GondolaFlightArchive/17-06-09_09_58_36/'
    folder='F:/GondolaFlightArchive/17-06-09_07_09_25/'
    Field.DTYPES=getDtypes(folder)
    
    fieldsList=[]
    gyros = ['Gyro X','Gyro Y','Gyro Z'] 
    fieldsList.append(Field('bettii.GyroReadings.angularVelocityX',label=gyros[0],dtype='i4',conversion=0.0006304, range=2e5))
    fieldsList.append(Field('bettii.GyroReadings.angularVelocityY',label=gyros[1],dtype='i4',conversion=0.0006437, range=2e5))
    fieldsList.append(Field('bettii.GyroReadings.angularVelocityZ',label=gyros[2],dtype='i4',conversion=0.0006324, range=2e5))
    
    initial_time=1100000 #in frame number
    final_time = 4020000 #in frame number
    
    initial_time=19061609 #in frame number
    final_time = None #in frame number

    #===========================================================================
    
    ds = DataSet(folder=folder,fieldsList=fieldsList,min=initial_time,max=final_time,verbose=True,rpeaks=False,timeIndex=False)
    
    ds.df.to_pickle(folder+'gyros.pkl')
    
    print 'Dataframe shape:', ds.df.shape

    print "Converting to Palestine Time..."
    ds.df.index = ds.df.index - pd.Timedelta(hours=5)  # Palestine time conversion (Archives folder names are in UTC)
    
    use('seaborn-bright')
    mpl.rcParams['axes.grid'] = True
    plt.rc('font', family='serif')
    
    fig = plt.figure()
    ax = plt.subplot(111, xlabel='Palestine Time', ylabel='Angular velocity [arcsec/s]')
    data = ds.df[gyros].dropna()
    data.plot(ax=ax, style=['r+', 'g+', 'b+'], markersize=1.0)
    plt.legend(markerscale=3, numpoints=20)
    fig.tight_layout()
    

    plt.show()