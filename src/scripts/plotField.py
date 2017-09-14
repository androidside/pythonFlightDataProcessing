'''
Created on Jun 22, 2017

Plot data from a field, using DataSet class. Merging archives if we want.

@author: Marc Casalprim
'''
print 'Imports...'
from utils.config import flightDisksFolders,plt
from utils.dataset import DataSet,pd,plotColumns
from utils.field import Field


if __name__ == '__main__':

    folders=flightDisksFolders
    
    fieldsList=[]
    fieldsList.append(Field('bettii.GyroReadings.angularVelocityX',label='Gyro X',conversion=0.0006304))
    fieldsList.append(Field('bettii.GyroReadings.angularVelocityY',label='Gyro Y',conversion=0.0006437,range=2e5))
    fieldsList.append(Field('bettii.GyroReadings.angularVelocityZ',label='Gyro Z',conversion=0.0006324,range=2e5))
    ds = DataSet(fieldsList=fieldsList,foldersList=folders,verbose=True,rpeaks=False)
    
    M=100
    ds.df = ds.df.iloc[::M] #Downsample
    
    print "Converting to Palestine Time..."
    ds.df.index = ds.df.index - pd.Timedelta(hours=5)  # Palestine time conversion (Archives folder names are in UTC)
    
    print "Cropping time"
    time_start=pd.datetime(2017, 6, 8, 13)
    time_end=pd.datetime(2017, 6, 9, 10)
    ds.df = ds.df.loc[time_start:time_end]
    
    time_label = 'Palestine Time'
    
    print "Plotting.."
    plotColumns(ds.df,xlabel=time_label)

    plotColumns(ds.df,xlabel=time_label,ylabels=['Angular velocity'],ncols=0)
    
    print "Show..."
    plt.show()