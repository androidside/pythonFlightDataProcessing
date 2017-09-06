'''
Created on 3 june 2017

Main script

@author: Marc Casalprim
'''

print 'Imports...'
import os
import matplotlib as mpl
from matplotlib.style import use
from utils.dataset import DataSet, plt, np, pd
from utils.field import Field, getFieldsContaining


if __name__ == '__main__':
    foldersD = []
    root_folder = 'F:/GondolaFlightArchive/'
    subdirs = next(os.walk(root_folder))[1]
    foldersD = [root_folder + subdir + '/' for subdir in subdirs]
    
    folders=[]
    folders.append('F:/LocalBettiiArchive/17-06-08_17_07_45-/')
    folders.append('F:/LocalBettiiArchive/17-06-08_20_43_41-/')
    folders.append('F:/LocalBettiiArchive/17-06-08_20_54_26-/')
    folders.append('F:/LocalBettiiArchive/17-06-08_22_09_44-/')
    folders.append('F:/LocalBettiiArchive/17-06-08_22_19_34-/')
    folders.append('F:/LocalBettiiArchive/17-06-09_00_27_01-/')
    folders.append('F:/LocalBettiiArchive/17-06-09_01_54_43-/')
    folders.append('F:/LocalBettiiArchive/17-06-09_02_12_33-/')
    folders.append('F:/LocalBettiiArchive/17-06-09_02_40_53-/')
    folders.append('F:/LocalBettiiArchive/17-06-09_02_59_03-/')
    folders.append('F:/LocalBettiiArchive/17-06-09_04_11_03-/')
    
    #==========================EMPTY Archives===================================
    #  folders.append('F:/LocalBettiiArchive/17-06-09_04_16_13-/')
    #  folders.append('F:/LocalBettiiArchive/17-06-09_04_19_53-/')
    #  folders.append('F:/LocalBettiiArchive/17-06-09_04_20_34-/')
    # folders.append('F:/LocalBettiiArchive/17-06-09_04_26_51-/')
    # folders.append('F:/LocalBettiiArchive/17-06-09_04_28_38-/')
    # folders.append('F:/LocalBettiiArchive/17-06-09_04_41_34-/')
    #===========================================================================
    folders.append('F:/LocalBettiiArchive/17-06-09_06_29_36-/')
    
    fieldsList=[Field('bettii.GyroReadings.angularVelocityZ', label='Gyro Z', dtype='i4', conversion=0.0006324, range=2e5)]
    

    read=True
    estimated=False
    
    ds = DataSet(fieldsList=fieldsList, foldersList=folders, verbose=True, rpeaks=False)
    dsd= DataSet(fieldsList=fieldsList, foldersList=foldersD, verbose=True, rpeaks=False)
    
    M = 1  # downsample factor
    ds.df = ds.df.iloc[::M]
    dsd.df = dsd.df.iloc[::M]
    print "Converting to Palestine Time..."
    dsd.df.index = dsd.df.index - pd.Timedelta(hours=5)  # Palestine time conversion (Archives folder names are in UTC)

    print "Cropping time"
    time_start=pd.datetime(2017, 6, 8, 18)
    time_end=pd.datetime(2017, 6, 9, 6)
    ds.df = ds.df.loc[time_start:time_end]
    dsd.df = dsd.df.loc[time_start:time_end]
    
    use('seaborn-bright')
    mpl.rcParams['axes.grid'] = True
    plt.rc('font', family='serif')
    img_folder = 'C:/Users/bettii/thesis/plots/telemetry_comparison/'

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