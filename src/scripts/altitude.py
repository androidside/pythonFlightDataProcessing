'''
Created on Jun 22, 2017

Altitude scripts without indexing, because we dont have a valid index for GpsReadings (approximatmceFN is empty)

@author: Marc Casalprim
'''
print 'Imports...'
from utils.config import plt, flightDisksFolders
from utils.dataset import np, load_fields
from utils.field import Field,getDtypes#,getFieldsContaining,getFieldsRegex



if __name__ == '__main__':
    
    folders=flightDisksFolders
    Field.DTYPES=getDtypes(folders[0])
    
    fieldsList=[]
     
    fieldsList.append(Field('bettii.GpsReadings.altitudeMeters',indexName='bettii.GpsReadings.approximatMmceFrameNumber',label='altitude'))
    alt=None
    for folder in folders:
        d=load_fields(fieldsList, folder)
        if alt is None: alt=d['altitude']
        else: alt=np.concatenate([alt,d['altitude']])
        
    
    plt.figure(1)
    plt.plot(alt)
   
    
    plt.ylabel('Altitude (m)')
    plt.show()