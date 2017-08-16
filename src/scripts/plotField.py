'''
Created on Jun 22, 2017

Plot raw data from a field. Merging archives if we want.

@author: Marc Casalprim
'''
print 'Imports...'
import os
import matplotlib as mpl


from matplotlib.style import use

from utils.dataset import DataSet,plt,sns,np, load_single_field,pd
from utils.field import Field,getDtypes#,getFieldsContaining,getFieldsRegex


if __name__ == '__main__':

    folders=[]
    root_folder='F:/GondolaFlightArchive/'
    subdirs=next(os.walk(root_folder))[1]
    folders=[root_folder+subdir+'/' for subdir in subdirs]
    
    fieldsList=[]
    fieldsList.append(Field('bettii.GyroReadings.angularVelocityX',label='Gyro X',dtype='i4',conversion=0.0006304))
    fieldsList.append(Field('bettii.GyroReadings.angularVelocityY',label='Gyro Y',dtype='i4',conversion=0.0006437,range=2e5))
    fieldsList.append(Field('bettii.GyroReadings.angularVelocityZ',label='Gyro Z',dtype='i4',conversion=0.0006324,range=2e5))
    ds = DataSet(fieldsList=fieldsList,foldersList=folders,verbose=True,rpeaks=False)
    M = 1  # downsample factor
    ds.df = ds.df.iloc[::M]
    
    print "Converting to Palestine Time..."
    ds.df.index = ds.df.index - pd.Timedelta(hours=5)  # Palestine time conversion (Archives folder names are in UTC)
    
    print "Cropping time"
    time_start=pd.datetime(2017, 6, 8, 13)
    time_end=pd.datetime(2017, 6, 9, 10)
    ds.df = ds.df.loc[time_start:time_end]
    
    use('ggplot')
    mpl.rcParams['axes.grid'] = True
    
    img_folder = 'C:/Users/bettii/gondola_archive_plots/'
    time_label = 'Palestine Time'
    
    print "Plotting.."    
    fig=plt.figure()
    fig.suptitle("Gyroscopes", fontsize=15,y=1)
    ax=plt.subplot(111,xlabel=time_label, ylabel='Angular velocity [arcsec/s]')
    data=ds.df[['Gyro X','Gyro Y','Gyro Z']].dropna()
    data.plot(ax=ax,style=['r+','g+','b+'],markersize=1.0)
    plt.legend(markerscale=3,numpoints=20)
    fig.tight_layout()
    fig.savefig(img_folder+"gyroscopes.png")
    
    print "Show..."
    plt.show()