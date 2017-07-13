'''
Created on 28 jun. 2017

Script for scripts simultaneously data from different archives

@author: Marc Casalprim
'''
print 'Imports...'
import os
import matplotlib as mpl
from matplotlib.style import use
from utils.dataset import DataSet, plt, np, pd
from utils.field import Field, getFieldsContaining



if __name__ == '__main__':

    folders = []
    root_folder = 'F:/GondolaFlightArchive/'
    subdirs = next(os.walk(root_folder))[1]
    folders = [root_folder + subdir + '/' for subdir in subdirs]

        
    gyros = False
    momdump = True
    magnetometer = False
    thermometers = False
    currentSensors = False
    altitude = False
    
    
    fieldsList = []
    if gyros:
        fieldsList.append(Field('bettii.GyroReadings.angularVelocityX', label='Gyro X', dtype='i4', conversion=0.0006304))
        fieldsList.append(Field('bettii.GyroReadings.angularVelocityY', label='Gyro Y', dtype='i4', conversion=0.0006437, range=2e5))
        fieldsList.append(Field('bettii.GyroReadings.angularVelocityZ', label='Gyro Z', dtype='i4', conversion=0.0006324, range=2e5))
      
    
    if altitude: fieldsList.append(Field('bettii.GpsReadings.altitudeMeters', indexName='bettii.RTLowPriority.mceFrameNumber', label='altitude'))
    
    if magnetometer:
        fieldsList.append(Field('bettii.Magnetometer.AzimuthDeg', label='mAz'))
        fieldsList.append(Field('bettii.Magnetometer.PitchDeg', label='mPitch'))
        fieldsList.append(Field('bettii.Magnetometer.RollDeg', label='mRoll'))
    
    if momdump: fieldsList.append(Field('bettii.PIDOutputMomDump.ut'))
    if thermometers:
        therm = []
        therm.append(Field('bettii.ThermometersDemuxedCelcius.J3L28', label='Rotator', range=100))
        therm.append(Field('bettii.ThermometersDemuxedCelcius.J4L43', label='Rotator controller', range=100))
        therm.append(Field('bettii.ThermometersDemuxedCelcius.J4L35', label='Flight computer', range=100))  # 35
        therm.append(Field('bettii.ThermometersDemuxedCelcius.J1L16', label='Structure points', range=100))  # 91
        therm.append(Field('bettii.ThermometersDemuxedCelcius.J4L5', label='Right siderostat', range=100))  # 83
        fieldsList.append(Field('bettii.GyroReadings.temperatureDegF_X', label='Temp. Gyro X', conversion=0.01))
        fieldsList.append(Field('bettii.GyroReadings.temperatureDegF_Y', label='Temp. Gyro Y', conversion=0.01))
        fieldsList.append(Field('bettii.GyroReadings.temperatureDegF_Z', label='Temp. Gyro Z', conversion=0.01))
        therm_labels = [field.label for field in therm]
        fieldsList = fieldsList + therm
    if currentSensors:
        folder = folders[0]
        l1 = getFieldsContaining('bettii.currentReadout.currentReadout_UPBOne', folder)
        l2 = getFieldsContaining('bettii.currentReadout.currentReadout_UPBTwo', folder)
        lv = getFieldsContaining('bettii.currentReadout.voltage', folder)
        currentsUPB1_labels = [field.label for field in l1]
        currentsUPB2_labels = [field.label for field in l2]
        voltages_labels = [field.label for field in lv]
        for field in l1 + l2 + lv:
            field.range = 10
        fieldsList = fieldsList + l1 + l2 + lv
          
    ds = DataSet(fieldsList=fieldsList, foldersList=folders, verbose=True, rpeaks=False)
    
    M = 100  # downsample factor
    ds.df = ds.df.iloc[::M]
    
    print "Converting to Palestine Time..."
    ds.df.index = ds.df.index - pd.Timedelta(hours=5)  # Palestine time conversion (Archives folder names are in UTC)

    use('ggplot')
    mpl.rcParams['axes.grid'] = True
    
    img_folder = 'C:/Users/bettii/gondola_archive_plots/'
    time_label = 'Palestine Time'
    

    
    print "Generating plots.."
    
    if gyros:
        print "Plotting gyroscopes data..."
        fig = plt.figure()
        fig.suptitle("Gyroscopes", fontsize=15, y=1)
        ax = plt.subplot(111, xlabel=time_label, ylabel='Angular velocity [arcsec/s]')
        data = ds.df[['Gyro X', 'Gyro Y', 'Gyro Z']].dropna()
        data.plot(ax=ax, style=['r+', 'g+', 'b+'], markersize=1.0)
        plt.legend(markerscale=3, numpoints=20)
        fig.tight_layout()
        fig.savefig(img_folder + "gyroscopes.png")
        

    
    if magnetometer:
        print "Plotting magnetometer data..."
        fig = plt.figure()
        fig.suptitle("Magnetometer", fontsize=15, y=1)
        ax = plt.subplot(211, xlabel=time_label, ylabel='Azimuth [deg]')
        ax2 = plt.subplot(212, xlabel=time_label, ylabel='Pitch [deg]')
        data = ds.df[['mAz', 'mPitch', 'mRoll']].dropna()
        data.mAz.plot(ax=ax, style='.')
        data.mPitch.plot(ax=ax2, style='.')
        fig.tight_layout()
        fig.savefig(img_folder + "magnetometer.png")
        
        print "Unwrapping azimuth..."
        y = (data.mAz.values - 180) * np.pi / 180
        az = np.unwrap(y) * 180 / np.pi

        fig = plt.figure()
        fig.suptitle("Magnetometer unwrapped", fontsize=15, y=1)
        ax = plt.subplot(211, xlabel=time_label, ylabel='Azimuth [deg]')
        ax2 = plt.subplot(212, xlabel=time_label, ylabel='Pitch [deg]')
        pd.Series(az, index=data.index).plot(ax=ax, style='.')
        data.mPitch.plot(ax=ax2, style='.')
        fig.tight_layout()
        fig.savefig(img_folder + "magnetometer_unwrapped.png")
        
        
        print "Plotting polar magnetometer"
        fig = plt.figure()
        data = ds.df.mAz.dropna()
        fig.suptitle("Magnetometer Azimuth", fontsize=15, y=1)
        t = data.index.astype(np.int64) // 10 ** 9  # in seconds
        t = t - t[0]  # reorigin
        plt.polar(az * np.pi / 180., t ** 0.7, ms=0.3)
        fig.tight_layout()
        fig.savefig(img_folder + "magnetometer_polar.png")
    
    if momdump:
        print "Plotting rotator data..."
        fig = plt.figure()
        fig.suptitle("Rotator output", fontsize=15, y=1)
        ax = plt.subplot(111, xlabel=time_label, ylabel='Command [counts/s]')
        data = ds.df.ut.dropna()
        data.plot(ax=ax, style='b+', markersize=1.0)
        fig.tight_layout()
        fig.savefig(img_folder + "rotator.png")
    if thermometers:
        print "Plotting thermometers data..."
        fig = plt.figure()
        fig.suptitle("Thermometers", fontsize=15, y=0.999)
        ax = plt.subplot(111, xlabel=time_label, ylabel='Temperature [Celsius]')
        data = ds.df[therm_labels].dropna(how='all').interpolate(method='time')
        data.plot(ax=ax, style='.', markersize=2.0)
        plt.legend(markerscale=3, numpoints=20)
        fig.tight_layout()
        fig.savefig(img_folder + "thermometers.png")
        
        fig = plt.figure()
        fig.suptitle("Gyroscopes Temperatures", fontsize=15, y=1)
        ax = plt.subplot(111, xlabel=time_label, ylabel='Temperature [Celsius]')
        data = ds.df[['Temp. Gyro X', 'Temp. Gyro Y', 'Temp. Gyro Z']].dropna()
        data.plot(ax=ax, style=['r+', 'g+', 'b+'], markersize=1.0)
        plt.legend(markerscale=3, numpoints=20)
        fig.tight_layout()
        fig.savefig(img_folder + "gyroscopes_temps.png", dpi=300)
    if altitude:
        print "Plotting altitude data..."
        fig = plt.figure()
        ax = plt.subplot(111, xlabel=time_label, ylabel='Altitude [m]')
        data = ds.df.altitude.dropna()
        data.plot(ax=ax, style='b')
        fig.tight_layout()
        fig.savefig(img_folder + "altitude.png")
    
    if currentSensors:
        print "Plotting current sensors data..."
        fig = plt.figure()
        ax = plt.subplot(111, xlabel=time_label, ylabel='Current [A]')
        data = ds.df[currentsUPB1_labels].dropna()
        data.plot(ax=ax, style='.', ms=3.0)
        plt.legend(markerscale=3, numpoints=20)
        fig.tight_layout()
        fig.savefig(img_folder + "currentsUPB1.png")
        
        fig = plt.figure()
        ax = plt.subplot(111, xlabel=time_label, ylabel='Current [A]')
        data = ds.df[currentsUPB2_labels].dropna()
        data.plot(ax=ax, style='.', ms=3.0)
        plt.legend(markerscale=3, numpoints=20)
        fig.tight_layout()
        fig.savefig(img_folder + "currentsUPB2.png")
        
        fig = plt.figure()
        ax = plt.subplot(111, xlabel=time_label, ylabel='Voltage [V]')
        data = ds.df[voltages_labels].dropna()
        data.plot(ax=ax, style='.', ms=3.0)
        plt.legend(markerscale=3, numpoints=20)
        fig.tight_layout()
        fig.savefig(img_folder + "voltages5V.png")
    print "Show..."
    plt.show()
