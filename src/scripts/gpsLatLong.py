'''GPS Latitude and Longitude. We dont have a valid index for GpsReadings (approximatmceFN is empty).
'''
print 'Imports...'
from utils.config import plt, flightDisksFolders
from utils.dataset import pd,DataSet
from utils.field import Field,getDtypes#,getFieldsContaining,getFieldsRegex



if __name__ == '__main__':
    
    folders=flightDisksFolders
    Field.DTYPES=getDtypes(folders[0])
    
    fieldsList=[]
    fieldsList.append(Field('bettii.GpsReadings.latitudeDegrees',indexName='bettii.RTLowPriority.mceFrameNumber',label='lat',range=360)) 
    fieldsList.append(Field('bettii.GpsReadings.longitudeDegrees',indexName='bettii.RTLowPriority.mceFrameNumber',label='long',range=360))
    

    ds = DataSet(fieldsList=fieldsList,foldersList=folders,verbose=True,rpeaks=False)
    
    ds.df.dropna(inplace=True)
    
    print "Shape: ", ds.df.shape  
    
    M=1
    ds.df = ds.df.iloc[::M] #Downsample
    
    print "Converting to Palestine Time..."
    ds.df.index = ds.df.index - pd.Timedelta(hours=5)  # Palestine time conversion (Archives folder names are in UTC)
    
    print "Plot..."
    time_label='Time (approx.)'
    lat_label='Latitude (deg)'
    long_label='Longitude (deg)'
    ax1=plt.subplot(2,2,1)
    ax2=plt.subplot(2,2,3)
    ax3=plt.subplot(1,2,2)
    
    ax1.set_xlabel(time_label)
    ax1.set_ylabel(lat_label)
    ax2.set_xlabel(time_label)
    ax2.set_ylabel(long_label)
    ax3.set_xlabel(long_label)
    ax3.set_ylabel(lat_label)
    
    ax1.plot(ds.df.index,ds.df.lat,'b+',linestyle='-')
    ax2.plot(ds.df.index,ds.df.long,'b+',linestyle='-')
    ax3.plot(ds.df.long,ds.df.lat,'b+',linestyle='-')    

    print "Show"
    plt.show()