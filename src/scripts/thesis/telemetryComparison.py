'''
Created on 3 june 2017

Plot comparison between the data collected from the telemtry vs. the data in the disks

@author: Marc Casalprim
'''
print 'Imports...'
from utils.config import os,flightTelemetryFolders, flightDisksFolders, save_folder, M
from utils.dataset import DataSet, plt, pd
from utils.field import Field


if __name__ == '__main__':
    foldersD = flightDisksFolders    
    folders=flightTelemetryFolders
    
    img_folder = save_folder+'plots/telemetry_comparison/'
    
    
    fieldsList=[Field('bettii.GyroReadings.angularVelocityZ', label='Gyro Z', dtype='i4', conversion=0.0006324, range=2e5)]
    

    ds = DataSet(fieldsList=fieldsList, foldersList=folders, verbose=True, rpeaks=False)
    dsd= DataSet(fieldsList=fieldsList, foldersList=foldersD, verbose=True, rpeaks=False)
    

    ds.df = ds.df.iloc[::M]
    dsd.df = dsd.df.iloc[::M]
    
    print "Converting to Palestine Time..."
    dsd.df.index = dsd.df.index - pd.Timedelta(hours=5)  # Palestine time conversion (Archives folder names are in UTC)

    print "Cropping time"
    time_start=pd.datetime(2017, 6, 8, 18)
    time_end=pd.datetime(2017, 6, 9, 6)
    ds.df = ds.df.loc[time_start:time_end]
    dsd.df = dsd.df.loc[time_start:time_end]
    

    if not os.path.exists(img_folder):
        os.makedirs(img_folder)

    print "Generating plots.."
    
    ms=0.2 #markersize
    time_label = 'Palestine Time'
    tel_label = 'Azimuth velocity from telemetry [arcsec/s]'
    ssd_label = 'Azimuth velocity from disks [arcsec/s]'
    
    fig = plt.figure()
    ax1 = plt.subplot(111, xlabel=time_label, ylabel=tel_label)
    data = ds.df['Gyro Z'].dropna()
    data.plot(ax=ax1, style='r+', markersize=ms)
    fig.tight_layout()
    
    
    fig = plt.figure()
    ax2 = plt.subplot(111, xlabel=time_label, ylabel=ssd_label)
    data = dsd.df['Gyro Z'].dropna()
    data.plot(ax=ax2, style='b+', markersize=ms)
    fig.tight_layout()
    
    
    xmin=736488.75
    xmax=736489.25
    ax1.set_xlim(xmin,xmax)
    ax2.set_xlim(xmin,xmax)
    ax1.figure.savefig(img_folder + "gyros_tel.png")
    ax2.figure.savefig(img_folder + "gyros_ssd.png")
    
    fig = plt.figure()
    ax = plt.subplot(211, ylabel=tel_label)
    data = ds.df['Gyro Z'].dropna()
    data.plot(ax=ax, style='r+', markersize=ms)
    ax.set_xlim(xmin,xmax)
    
    ax = plt.subplot(212, xlabel=time_label, ylabel=ssd_label)
    data = dsd.df['Gyro Z'].dropna()
    data.plot(ax=ax, style='b+', markersize=ms)
    ax.set_xlim(xmin,xmax)
    fig.tight_layout()
    fig.savefig(img_folder + "gyros_comp.png")
    
    print "Show..."
    plt.show()