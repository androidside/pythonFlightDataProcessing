'''
Created on 28 jun. 2017

Script for scripts simultaneously data from different archives

@author: Marc Casalprim
'''
from scripts import delayLines
from matplotlib.rcsetup import validate_fontsize
print 'Imports...'
import re
from utils.config import os,flightDisksFolders,plt,save_folder,img_folder
from utils.dataset import DataSet, np, pd, paintModes
from utils.field import Field, getFieldsContaining




if __name__ == '__main__':
    folders=flightDisksFolders
    
    img_folder=save_folder+'plots/merged/' #folders where the figures will be stored
    if not os.path.exists(img_folder):
        os.makedirs(img_folder)
        
    #Flags    
    #data to read and plot
    #missing items: PID Gains, Delay Lines, Timings RT, etc.
    gyros = False
    momdump = False 
    magnetometer = False    
    thermometers = True
    currentSensors = False
    altitude = False
    timingsRT = False
    timingsFPGA = False
    griffins = False
    azimuth=False #measured and desired azimuth position and velocity
    modes = False
    
    
    titles=True #show titles on the figures
        
    fieldsList = []
    if gyros:
        fieldsList.append(Field('bettii.GyroReadings.angularVelocityX', label='Gyro X', conversion=0.0006304, range=2e5))
        fieldsList.append(Field('bettii.GyroReadings.angularVelocityY', label='Gyro Y', conversion=0.0006437, range=2e5))
        fieldsList.append(Field('bettii.GyroReadings.angularVelocityZ', label='Gyro Z', conversion=0.0006324, range=2e5))      
    
    if altitude: fieldsList.append(Field('bettii.GpsReadings.altitudeMeters', indexName='bettii.RTLowPriority.mceFrameNumber', label='altitude'))
    
    if magnetometer:
        fieldsList.append(Field('bettii.Magnetometer.AzimuthDeg', label='mAz'))
        fieldsList.append(Field('bettii.Magnetometer.PitchDeg', label='mPitch'))
        fieldsList.append(Field('bettii.Magnetometer.RollDeg', label='mRoll'))
    
    if momdump: fieldsList.append(Field('bettii.PIDOutputMomDump.ut', conversion=100*200*64)) # 100*200*64 lambda function=np.sqrt or if you want to do something more complex  function=lambda x: np.sqrt(x) +3 I can also do it in the dataframe, see below or Thesis postEstimation.py
    if thermometers:
        therm = []
#         therm.append(Field('bettii.ThermometersDemuxedCelcius.J3L28', label='Rotator', range=100))
#         therm.append(Field('bettii.ThermometersDemuxedCelcius.J4L43', label='Rotator controller', range=100))
#         therm.append(Field('bettii.ThermometersDemuxedCelcius.J4L35', label='Flight computer', range=100))  # 35
#         therm.append(Field('bettii.ThermometersDemuxedCelcius.J1L16', label='Structure points', range=100))  # 91
#         therm.append(Field('bettii.ThermometersDemuxedCelcius.J4L5', label='Right siderostat', range=100))  # 83
# For Arnab's thesis
        therm.append(Field('bettii.ThermometersDemuxedCelcius.J2L33', label='L Telescope up', range=100))  # 54
        therm.append(Field('bettii.ThermometersDemuxedCelcius.J2L29', label='L Telescope left', range=100))  # 51
        therm.append(Field('bettii.ThermometersDemuxedCelcius.J2L15', label='L Telescope right', range=100))  # 55         
        
#         therm.append(Field('bettii.ThermometersDemuxedCelcius.J4L3', label='R Telescope up', range=100))  # 63
#         therm.append(Field('bettii.ThermometersDemuxedCelcius.J2L33', label='L Telescope up', range=100))  # 54

        therm.append(Field('bettii.ThermometersDemuxedCelcius.J4L3', label='R Telescope up', range=100))  # 63
        therm.append(Field('bettii.ThermometersDemuxedCelcius.J4L11', label='R Telescope right', range=100))  # 63
        therm.append(Field('bettii.ThermometersDemuxedCelcius.J4L7', label='R Telescope left', range=100))  # 63

        
        fieldsList.append(Field('bettii.GyroReadings.temperatureDegF_X', label='Temp. Gyro X', range=100, conversion=0.01))
        fieldsList.append(Field('bettii.GyroReadings.temperatureDegF_Y', label='Temp. Gyro Y', range=100,conversion=0.01))
        fieldsList.append(Field('bettii.GyroReadings.temperatureDegF_Z', label='Temp. Gyro Z',range=100, conversion=0.01))
        therm_labels = [field.label for field in therm]
        fieldsList = fieldsList + therm
    if currentSensors:
        folder = folders[0]
        l1 = getFieldsContaining('bettii.currentReadout.currentReadout_UPBOne', folder)
        l2 = getFieldsContaining('bettii.currentReadout.currentReadout_UPBTwo', folder)
        lv=[]
        lv.append(Field('bettii.currentReadout.voltageReadout_UPBOne_5VChannel', label='5V line UPB1', range=10))
        lv.append(Field('bettii.currentReadout.voltageReadout_UPBTwo_5VChannel', label='5V line UPB2', range=10))
        for field in l1:
            number=re.findall(r'\d+', field.label)[0] #find regular expression (r) that contains a number (\d) even if its surrounded by characters (+). It returns a vector so take the first value, #\d means digit, and + means "one or more"
            if 'negative' in field.label: l1.remove(field)#number='-'+number
            field.label=number+'V line UPB1'
        currentsUPB1_labels = [field.label for field in l1]
        for field in l2:
            number=re.findall(r'\d+', field.label)[0] #find regular expression (r) that contains a number (\d) even if its surrounded by characters (+). It returns a vector so take the first value, #\d means digit, and + means "one or more"
            field.label=number+'V line UPB2'
        currentsUPB2_labels = [field.label for field in l2]       
        voltages_labels = [field.label for field in lv]
        for field in l1 + l2 + lv:
            field.range = 10
        fieldsList = fieldsList + l1 + l2 + lv
    if timingsRT:
        timingsRT = []
        timingsRT.append(Field('bettii.RTHighPriority.TimingRTLoopDuration', label='TimingRTLoopDuration',range=20000))
        timingsRT.append(Field('bettii.RTHighPriority.TimingRTCounterOver10ms', label='TimingRTCounterOver10ms',range=20000))
#         timingsRT.append(Field('bettii.RTLowPriority.TimingRTBetweenLoops', label='TimingRTBetweenLoops',range=20000))
#         timingsRT.append(Field('bettii.RTLowPriority.TimingRTFPGAInOut', label='TimingRTFPGAInOut',range=20000))
#         timingsRT.append(Field('bettii.RTLowPriority.TimingRTGenerateGyroVel', label='TimingRTGenerateGyroVel',range=20000))
#         timingsRT.append(Field('bettii.RTLowPriority.TimingRTPropagateTrueSC', label='TimingRTPropagateTrueSC',range=20000))
#         timingsRT.append(Field('bettii.RTLowPriority.TimingRTGenerateSC', label='TimingRTGenerateSC',range=20000))
#         timingsRT.append(Field('bettii.RTLowPriority.TimingRTEKFPropagate', label='TimingRTEKFPropagate',range=20000))
        timingsRT.append(Field('bettii.RTLowPriority.TimingRTEKFUpdate', label='TimingRTEKFUpdate',range=20000))
#         timingsRT.append(Field('bettii.RTLowPriority.TimingRTRotateTarget', label='TimingRTRotateTarget',range=20000))
#         timingsRT.append(Field('bettii.RTLowPriority.TimingRTPlotGyroVelocities', label='TimingRTPlotGyroVelocities',range=20000))
#         timingsRT.append(Field('bettii.RTLowPriority.TimingRTModeManager', label='TimingRTModeManager',range=20000))
#         timingsRT.append(Field('bettii.RTLowPriority.TimingRTPlotSetpoints', label='TimingRTPlotSetpoints',range=20000))
#         timingsRT.append(Field('bettii.RTLowPriority.TimingRTMatrices', label='TimingRTMatrices',range=20000))
#         timingsRT.append(Field('bettii.RTLowPriority.TimingRTPlotsRaDec', label='TimingRTPlotsRaDec',range=20000))
#         timingsRT.append(Field('bettii.RTLowPriority.TimingRTSendToAurora', label='TimingRTSendToAurora',range=20000))
        timingsRT_labels = [field.label for field in timingsRT]
        fieldsList = fieldsList + timingsRT
        
    if timingsFPGA:
        timingsFPGA = []
#         timingsFPGA.append(Field('bettii.TimingSensorsLoop.betweenLoops', label='TimingSensorsLoopbetweenLoops',range=20000))
#         timingsFPGA.append(Field('bettii.TimingSensorsLoop.triggerGyro', label='TimingSensorsLooptriggerGyro',range=20000))
#         timingsFPGA.append(Field('bettii.TimingSensorsLoop.writeStarcamOptions', label='TimingSensorsLoopwriteStarcamOptions',range=20000))
#         timingsFPGA.append(Field('bettii.TimingSensorsLoop.readGyroStarcamTipTilts', label='TimingSensorsLoopreadGyroStarcamTipTilts',range=20000))
#         timingsFPGA.append(Field('bettii.TimingSensorsLoop.writeToIndicator', label='TimingSensorsLoopwriteToIndicator',range=20000))
#         timingsFPGA.append(Field('bettii.TimingSensorsLoop.notifyRTMain', label='TimingSensorsLoopnotifyRTMain',range=20000))
#         timingsFPGA.append(Field('bettii.TimingSensorsLoop.totalLoopTime', label='TimingSensorsLooptotalLoopTime',range=20000))
        
        
#         timingsFPGA.append(Field('bettii.TimingApplyPIDLoop.betweenapplyPIDLoops', label='ApplyPIDLoopbetweenapplyPIDLoops',range=20000))
#         timingsFPGA.append(Field('bettii.TimingApplyPIDLoop.writeTipTiltsandMCEmemoryItems', label='ApplyPIDLoopwriteTipTiltsandMCEmemoryItems',range=20000))
#         timingsFPGA.append(Field('bettii.TimingApplyPIDLoop.readControls', label='ApplyPIDLoopreadControls',range=20000))
#         timingsFPGA.append(Field('bettii.TimingApplyPIDLoop.checkLimits', label='ApplyPIDLoopcheckLimits',range=20000))
#         timingsFPGA.append(Field('bettii.TimingApplyPIDLoop.readGains', label='ApplyPIDLoopreadGains',range=20000))
#         timingsFPGA.append(Field('bettii.TimingApplyPIDLoop.calculatePIDs', label='ApplyPIDLoopcalculatePIDs',range=20000))
        timingsFPGA.append(Field('bettii.TimingApplyPIDLoop.commandAndReadoutGalils', label='ApplyPIDLoopcommandAndReadoutGalils',range=20000))
#         timingsFPGA.append(Field('bettii.TimingApplyPIDLoop.writeToIndicator', label='ApplyPIDLoopwriteToIndicator',range=20000))
        timingsFPGA.append(Field('bettii.TimingApplyPIDLoop.applyPIDLoopDuration', label='ApplyPIDLoopapplyPIDLoopDuration',range=20000))
        
        timingsFPGA_labels = [field.label for field in timingsFPGA]
        fieldsList = fieldsList + timingsFPGA
        
    if griffins:
        fieldsList.append(Field('bettii.GriffinsGalil.TPA', label='TPA', range=1e9))
        fieldsList.append(Field('bettii.GriffinsGalil.TPB', label='TPB', range=1e9))
        fieldsList.append(Field('bettii.GriffinsGalil.TPC', label='TPC', range=1e9))
        fieldsList.append(Field('bettii.GriffinsGalil.griffinAAngleDegrees', label='griffinAAngleDegrees', range=1e3))
        fieldsList.append(Field('bettii.GriffinsGalil.griffinBAngleDegrees', label='griffinBAngleDegrees', range=1e3))
        fieldsList.append(Field('bettii.GriffinsGalil.griffinCAngleDegrees', label='griffinCAngleDegrees', range=1e3))
      #  fieldsList.append(Field('bettii.RTHighPriority.Elevation', label='Elevation', conversion=0.000277777778, range=1e8))          
       
    if azimuth:        
        fieldsList.append(Field('bettii.PIDInputCCMG.positionTarget',label='ptarget'))
        fieldsList.append(Field('bettii.PIDInputCCMG.positionMeasurement',label='pmeas'))
        fieldsList.append(Field('bettii.PIDInputCCMG.velocityTarget',label='vtarget'))
        fieldsList.append(Field('bettii.PIDInputCCMG.velocityMeasurement',label='vmeas'))
        fieldsList.append(Field('bettii.RTHighPriority.targetRA',label='targetra'))
        fieldsList.append(Field('bettii.RTHighPriority.targetDEC',label='targetdec'))
        fieldsList.append(Field('bettii.RTLowPriority.SlewParametersAccelarcsecss',label='SlewParametersAccelarcsecss'))
        fieldsList.append(Field('bettii.RTLowPriority.SlewParametersVsetpointsarcsecs',label='SlewParametersVsetpointsarcsecs'))
        fieldsList.append(Field('bettii.RTLowPriority.SlewParametersPDarcsec',label='SlewParametersPDarcsec'))
        fieldsList.append(Field('bettii.RTLowPriority.SlewParametersAzTargetInitial',label='SlewParametersAzTargetInitial'))
        fieldsList.append(Field('bettii.RTLowPriority.SlewParametersAzTargetInitial',label='SlewParametersTotalDistanceToCover'))
        fieldsList.append(Field('bettii.RTLowPriority.SlewParametersAzTargetInitial',label='SlewParametersDecceleration'))     
    if modes:
        fieldsList.append(Field('bettii.FpgaState.state',label='modes',range=6))
        
    ds = DataSet(fieldsList=fieldsList, foldersList=folders, verbose=True, rpeaks=False, timeIndex=True)
    #ds.df = ds.df.iloc[:-1000]
    M = 1 # downsample factor
    ds.df = ds.df.iloc[:-100:M] #ie: ds.df.iloc[:-1000:M] do not plot the last 1000 samples (fn are too high)  (from:to:step)
    
    print 'Converting to Palestine Time...'
    ds.df.index = ds.df.index - pd.Timedelta(hours=5)  # Palestine time conversion (Archives folder names are in UTC)

    time_label = 'Palestine Time'
    
    print "Generating plots.."
    
    
    if gyros:
        print "Plotting gyroscopes data..."
        fig = plt.figure()
        if titles: fig.suptitle("Gyroscopes", fontsize=15, y=1)
        ax = plt.subplot(111, xlabel=time_label, ylabel='Angular velocity [arcsec/s]')
        data = ds.df[['Gyro X', 'Gyro Y', 'Gyro Z']].dropna()
        data.plot(ax=ax, style=['r+', 'g+', 'b+'], markersize=2.0)
        plt.xlabel(time_label, fontsize = 18)
        plt.ylabel('Angular velocity [arcsec/s]', fontsize = 28)
        plt.yticks(fontsize=26)
        plt.xticks(fontsize=26)
        plt.legend(markerscale=3, numpoints=20, fontsize = 30)
        fig.tight_layout()
        fig.savefig(img_folder + "gyroscopes.png")
        
        if modes:
            modes=ds.df.modes.dropna()
            modes.plot()
            print "Painting.."
            paintModes(ax,modes)
            print "Show"   
            plt.show() 
            
    if magnetometer:
        print "Plotting magnetometer data..."
        fig = plt.figure()
        if titles: fig.suptitle("Magnetometer", fontsize=15, y=1)
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
        if titles: fig.suptitle("Magnetometer unwrapped", fontsize=15, y=1)
        ax = plt.subplot(211, xlabel=time_label, ylabel='Azimuth [deg]')
        ax2 = plt.subplot(212, xlabel=time_label, ylabel='Pitch [deg]')
        pd.Series(az, index=data.index).plot(ax=ax, style='.')
        data.mPitch.plot(ax=ax2, style='.')
        fig.tight_layout()
        fig.savefig(img_folder + "magnetometer_unwrapped.png")
        
        fig = plt.figure()
        ax = plt.subplot(111, xlabel=time_label, ylabel='Azimuth [deg]')
        data.mAz.plot(ax=ax, style='.')
        fig.tight_layout()
        fig.savefig(img_folder + "mAz.png")
        
        fig = plt.figure()
        ax = plt.subplot(111, xlabel=time_label, ylabel='Pitch [deg]')
        data.mPitch.plot(ax=ax, style='.')
        fig.tight_layout()
        fig.savefig(img_folder + "mPitch.png")
        
        fig = plt.figure()
        ax = plt.subplot(111, xlabel=time_label, ylabel='Azimuth [deg]')
        pd.Series(az, index=data.index).plot(ax=ax, style='.')
        fig.tight_layout()
        fig.savefig(img_folder + "mAz_unwrapped.png")
        
        print "Plotting polar magnetometer"
        fig = plt.figure()
        data = ds.df.mAz.dropna()
        if titles: fig.suptitle("Magnetometer Azimuth", fontsize=15, y=1)
        t = data.index.astype(np.int64) // 10 ** 9  # in seconds
        t = t - t[0]  # reorigin
        plt.polar(az * np.pi / 180., t ** 0.7, ms=0.3)
        fig.tight_layout()
        fig.savefig(img_folder + "magnetometer_polar.png")
    
    if momdump:
        print "Plotting rotator data..."
        fig = plt.figure()
        if titles: fig.suptitle("Rotator output", fontsize=15, y=1)
        ax = plt.subplot(111, xlabel=time_label, ylabel='Command [rev/s]')
        data = ds.df.ut.dropna() #.apply(lambda x: np.sqrt(x) +3)
        data.plot(ax=ax, style='b+', markersize=1.0)
        fig.tight_layout()
        fig.savefig(img_folder + "rotator.png")
    if thermometers:
        print "Plotting thermometers data..."
        fig = plt.figure()
#         if titles: fig.suptitle("Thermometers", fontsize=15, y=0.999)
        ax = plt.subplot(111, xlabel=time_label, ylabel='Temperature [Celsius]')
        plt.xlabel(time_label, fontsize = 50)
        plt.ylabel('Temperature [Celsius]', fontsize = 50)
        plt.yticks(fontsize=38)
        plt.xticks(fontsize=38)
        data = ds.df[therm_labels].dropna(how='all').interpolate(method='time')
        data.plot(ax=ax, style='.', markersize=5.0)
        plt.legend(markerscale=3, numpoints=20, fontsize = 38)
        fig.tight_layout()
        fig.savefig(img_folder + "thermometers.png")
        
        fig = plt.figure()
        if titles: fig.suptitle("Gyroscopes Temperatures", fontsize=15, y=1)
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
        data.plot(ax=ax, style='b.',markersize=3)
        fig.tight_layout()
        fig.savefig(img_folder + "altitude.png")
    
    if currentSensors:
        print "Plotting current sensors data..."
        fig = plt.figure()
        ax = plt.subplot(111, xlabel=time_label, ylabel='Current [A]')
        data = ds.df[currentsUPB1_labels].dropna()
        data.plot(ax=ax, style='.', ms=3.0)
        plt.legend(loc=0,markerscale=3, numpoints=20)
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
    
    if timingsRT:
        print "Plotting timings RT data..."
        for label in timingsRT_labels:
            fig = plt.figure()
            if titles: fig.suptitle(label, fontsize=38, y=1)
            ax = plt.subplot(111, xlabel=time_label, ylabel='Time (microsec)')
            plt.xlabel(time_label, fontsize = 38)
            plt.ylabel('Time (microsec)', fontsize = 38)
            plt.yticks(fontsize=36)
            plt.xticks(fontsize=36)            
            data = ds.df[label].dropna() #.apply(lambda x: np.sqrt(x) +3)
            data = data[data > 0]
            data.plot(ax=ax, style='b+', markersize=2.0)
            fig.tight_layout()
            fig.savefig(img_folder + label+".png")
            
    if timingsFPGA:
        print "Plotting timings FPGA data..."
        for label in timingsFPGA_labels:
            fig = plt.figure()
            if titles: fig.suptitle(label, fontsize=38, y=1)
            ax = plt.subplot(111, xlabel=time_label, ylabel='Time (microsec)')
            plt.xlabel(time_label, fontsize = 38)
            plt.ylabel('Time (microsec)', fontsize = 38)
            plt.yticks(fontsize=26)
            plt.xticks(fontsize=26)
            data = ds.df[label].dropna() #.apply(lambda x: np.sqrt(x) +3)
            data = data[data > 0]
            data.plot(ax=ax, style='g+', markersize=2.0)
            fig.tight_layout()
            fig.savefig(img_folder + label+".png")
        
#         fig = plt.figure()
#         if titles: fig.suptitle("TimingRTCounterOver10ms", fontsize=15, y=1)
#         ax = plt.subplot(111, xlabel=time_label, ylabel='Time (microsec)')
#         data = ds.df.TimingRTCounterOver10ms.dropna() #.apply(lambda x: np.sqrt(x) +3)
#         data = data[data> 0]
#         data.plot(ax=ax, style='b+', markersize=1.0)
#         fig.tight_layout()
#         fig.savefig(img_folder + "TimingRTCounterOver10ms.png")
#         
#         
#         print "Plotting thermometers data..."
#         fig = plt.figure()
#         if titles: fig.suptitle("Thermometers", fontsize=15, y=0.999)
#         ax = plt.subplot(111, xlabel=time_label, ylabel='Temperature [Celsius]')
#         data = ds.df[therm_labels].dropna(how='all').interpolate(method='time')
#         data.plot(ax=ax, style='.', markersize=2.0)
#         plt.legend(markerscale=3, numpoints=20)
#         fig.tight_layout()
#         fig.savefig(img_folder + "thermometers.png")
        
    if griffins:
        print "Plotting griffins data..."
        fig = plt.figure()
        if titles: fig.suptitle("Griffins Absolute Position Encoder", fontsize=15, y=1)
        ax = plt.subplot(111, xlabel=time_label, ylabel='Griffins Absolute Position')
        data = ds.df[['TPA', 'TPB', 'TPC']].dropna()
        data.plot(ax=ax, style=['r+', 'g+', 'b+'], markersize=1.0)
        plt.legend(markerscale=3, numpoints=20)
        fig.tight_layout()
        fig.savefig(img_folder + "TPA_TPB_TPC.png")
        
        fig = plt.figure()
        if titles: fig.suptitle("Griffins Angle Degree", fontsize=15, y=1)
        ax = plt.subplot(111, xlabel=time_label, ylabel='Griffins Absolute Angle')
        data = ds.df[['griffinAAngleDegrees', 'griffinBAngleDegrees', 'griffinCAngleDegrees']].dropna()
        data.plot(ax=ax, style=['r+', 'g+', 'b+','y+'], markersize=1.0)
        plt.legend(markerscale=3, numpoints=20)
        fig.tight_layout()
        fig.savefig(img_folder + "GriffinsAngle.png")
        
    if azimuth:
        print "Plotting azimuth data..."
        fig = plt.figure()
        if titles: fig.suptitle("Position Target vs Measured", fontsize=15, y=1)
        ax = plt.subplot(111, xlabel=time_label, ylabel='Position [arcsec]')
        data = ds.df[['ptarget', 'pmeas']].dropna()
        data.plot(ax=ax, style=['r', 'g'], markersize=1.0)
        plt.legend(markerscale=3, numpoints=20)
        fig.tight_layout()
        fig.savefig(img_folder + "position.png")
        
        fig = plt.figure()
        if titles: fig.suptitle("Velocity Target vs Measured", fontsize=15, y=1)
        ax = plt.subplot(111, xlabel=time_label, ylabel='Velocity [arcsec/s]')
        data = ds.df[['vtarget', 'vmeas']].dropna()
        data.plot(ax=ax, style=['r', 'g'], markersize=1.0)
        plt.legend(markerscale=3, numpoints=20)
        fig.tight_layout()
        fig.savefig(img_folder + "velocity.png")
        
        fig = plt.figure()
        if titles: fig.suptitle("Target Ra & Dec", fontsize=15, y=1)
        ax1 = plt.subplot(211, xlabel=time_label, ylabel='Target Ra')
        data = ds.df.targetra.dropna() #.apply(lambda x: np.sqrt(x) +3)
        data.plot(ax=ax1, style='b', markersize=1.0)
        ax2 = plt.subplot(212, xlabel=time_label, ylabel='Target Dec',sharex=ax1)
        data = ds.df.targetdec.dropna() #.apply(lambda x: np.sqrt(x) +3)
        data.plot(ax=ax2, style='b', markersize=1.0)
        fig.tight_layout()
        fig.savefig(img_folder + "Target Ra&Dec.png")
        
        fig = plt.figure()
        if titles: fig.suptitle("Slew Parameters", fontsize=15, y=1)
        ax = plt.subplot(111, xlabel=time_label, ylabel='Value')
        data = ds.df[['SlewParametersAccelarcsecss', 'SlewParametersVsetpointsarcsecs', 'SlewParametersPDarcsec', 'SlewParametersAzTargetInitial',
                      'SlewParametersTotalDistanceToCover', 'SlewParametersDecceleration']].dropna()
        data.plot(ax=ax, style=['r', 'c', 'm', 'y', 'k', 'w'], markersize=1.0)
        plt.legend(markerscale=3, numpoints=20)
        fig.tight_layout()
        fig.savefig(img_folder + "slewParameters.png")
        
    
    print "Show..."
    plt.show()
