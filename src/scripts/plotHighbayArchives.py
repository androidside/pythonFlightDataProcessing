'''
Created on Jun 22, 2017

Plot data from a field, using DataSet class. Merging archives if we want.

@author: Jordi Vila Vila
'''
print 'Imports...'
from utils.config import flightDisksFolders,plt,save_folder,img_folder
from utils.dataset import DataSet,pd,plotColumns, filterDataframe
from utils.field import Field


if __name__ == '__main__':
    folder = 'A:/2ndcopy/LocalAuroraArchive/17-05-30_19_44_12/'
    #folder = "C:/LocalAuroraArchive/17-05-30_19_44_12/"
    #Flags    
    #data to read and plot
    ccmg = True
    momdump = True
    wheelsangle=True
    gyros=True
    azimuth=True #measured and desired azimuth position and velocity
    radec = True #telescopeRaDec, GondolaRaDec, StarcameraRaDec
    griffins = True    
    
    titles=True #show titles on the figures
    
    fieldsList = []    
    if ccmg:
        fieldsList.append(Field('bettii.PIDOutputCCMG.ut',label='ccmg_ut'))
        fieldsList.append(Field('bettii.PIDOutputCCMG.et',label='ccmg_et'))
        fieldsList.append(Field('bettii.PIDOutputCCMG.proportional',label='P CCMG', range=1e6))   #range =3e6 To remove very highbalues
        fieldsList.append(Field('bettii.PIDOutputCCMG.integral',label='I CCMG'))
        fieldsList.append(Field('bettii.PIDOutputCCMG.derivative',label='D CCMG'))                
    if momdump:
        fieldsList.append(Field('bettii.PIDOutputMomDump.ut',label='mom_ut'))
        fieldsList.append(Field('bettii.PIDOutputMomDump.et',label='mom_et'))
        fieldsList.append(Field('bettii.PIDOutputMomDump.proportional',label='P MomDump'))   
        fieldsList.append(Field('bettii.PIDOutputMomDump.integral',label='I MomDump'))
        fieldsList.append(Field('bettii.PIDOutputMomDump.derivative',label='D MomDump'))        
    if wheelsangle: fieldsList.append(Field('bettii.StepperGalil.wheelsAngle',label='wheels_angle'))        
    if gyros:
        fieldsList.append(Field('bettii.GyroReadings.angularVelocityX',label='gyroX',dtype='i4',conversion=0.0006304))
        fieldsList.append(Field('bettii.GyroReadings.angularVelocityY',label='gyroY',dtype='i4',conversion=0.0006437))
        fieldsList.append(Field('bettii.GyroReadings.angularVelocityZ',label='gyroZ',dtype='i4',conversion=0.0006324))
        fieldsList.append(Field('bettii.RTLowPriority.estimatedGyroXarcsec',label='estimatedgyroX',dtype='i4'))#No need to put i4 anymore
        fieldsList.append(Field('bettii.RTLowPriority.estimatedGyroYarcsec',label='estimatedgyroY',dtype='i4'))
        fieldsList.append(Field('bettii.RTLowPriority.estimatedGyroZarcsec',label='estimatedgyroZ',dtype='i4'))            
    if azimuth:        
        fieldsList.append(Field('bettii.PIDInputCCMG.positionTarget',label='ptarget'))
        fieldsList.append(Field('bettii.PIDInputCCMG.positionMeasurement',label='pmeas'))
        fieldsList.append(Field('bettii.PIDInputCCMG.velocityTarget',label='vtarget'))
        fieldsList.append(Field('bettii.PIDInputCCMG.velocityMeasurement',label='vmeas'))
        fieldsList.append(Field('bettii.RTHighPriority.targetRA',label='targetra'))
        fieldsList.append(Field('bettii.RTHighPriority.targetDEC',label='targetdec'))        
    if radec:
        fieldsList.append(Field('bettii.RTHighPriority.TelescopeRaDeg',label='tra'))
        fieldsList.append(Field('bettii.RTHighPriority.TelescopeDecDeg',label='tdec'))
        fieldsList.append(Field('bettii.RTHighPriority.GondolaRaDeg',label='gra'))
        fieldsList.append(Field('bettii.RTHighPriority.GondolaDecDeg',label='gdec'))
        fieldsList.append(Field('bettii.RTLowPriority.RawStarcameraRaDeg',label='sra'))
        fieldsList.append(Field('bettii.RTLowPriority.RawStarcameraDecDeg',label='sdec'))        
    if griffins:
         fieldsList.append(Field('bettii.GriffinsGalil.griffinAAngleDegrees',label='gangle'))
    
    ds = DataSet(fieldsList=fieldsList, folder=folder, verbose=True, rpeaks=True,timeIndex=True)
    #optional Filter
    #filterDataframe(ds.df, 3, 0.9)#N remove peaks inferior at 3 samples, with 0.9 advances 10% 
    M=1
    data = ds.df.iloc[::M] #ie: ds.df.iloc[:-1000:M] do not plot the last 1000 samples (fn are too high). M downsample
    time_label = 'Palestine Time'
    print "Generating plots.."

    if ccmg: 
        print "Plotting CCMG data..."
        fig = plt.figure()
        if titles: fig.suptitle("CCMG PID contributions", fontsize=15, y=1)
        ax = plt.subplot(111, xlabel=time_label, ylabel='CCMG PID contributions')
        data = ds.df[['P CCMG', 'I CCMG', 'D CCMG']].dropna()
        data.plot(ax=ax, style=['r', 'g', 'b'], markersize=1.0)
        plt.legend(markerscale=3, numpoints=20)
        fig.tight_layout()
        fig.savefig(img_folder + "CCMGContributions.png")
        
        fig = plt.figure()
        if titles: fig.suptitle("CCMG e(t)", fontsize=15, y=1)
        ax = plt.subplot(111, xlabel=time_label, ylabel='Error [arcsec]')
        data = ds.df.ccmg_et.dropna() #.apply(lambda x: np.sqrt(x) +3)
        data.plot(ax=ax, style='b', markersize=1.0)
        fig.tight_layout()
        fig.savefig(img_folder + "ccmg_et.png")
        
        fig = plt.figure()
        if titles: fig.suptitle("CCMG u(t)", fontsize=15, y=1)
        ax = plt.subplot(111, xlabel=time_label, ylabel='Command')
        data = ds.df.ccmg_ut.dropna() #.apply(lambda x: np.sqrt(x) +3)
        data.plot(ax=ax, style='b', markersize=1.0)
        fig.tight_layout()
        fig.savefig(img_folder + "ccmg_ut.png")
    
    if momdump:
        print "Plotting Momentum Dump data..."
        fig = plt.figure()
        if titles: fig.suptitle("Mom.Dump PID contributions", fontsize=15, y=1)
        ax = plt.subplot(111, xlabel=time_label, ylabel='Mom.Dump PID contributions')
        data = ds.df[['P MomDump', 'I MomDump', 'D MomDump']].dropna()
        data.plot(ax=ax, style=['r', 'g', 'b'], markersize=1.0)
        plt.legend(markerscale=3, numpoints=20)
        fig.tight_layout()
        fig.savefig(img_folder + "MomDumpContributions.png")
        
        fig = plt.figure()
        if titles: fig.suptitle("MomDump e(t)", fontsize=15, y=1)
        ax = plt.subplot(111, xlabel=time_label, ylabel='Error [arcsec]')
        data = ds.df.mom_et.dropna() #.apply(lambda x: np.sqrt(x) +3)
        data.plot(ax=ax, style='b', markersize=1.0)
        fig.tight_layout()
        fig.savefig(img_folder + "momdump_et.png")
        
        fig = plt.figure()
        if titles: fig.suptitle("MomDump u(t)", fontsize=15, y=1)
        ax = plt.subplot(111, xlabel=time_label, ylabel='Command')
        data = ds.df.mom_ut.dropna() #.apply(lambda x: np.sqrt(x) +3)
        data.plot(ax=ax, style='b', markersize=1.0)
        fig.tight_layout()
        fig.savefig(img_folder + "mom_ut.png")
    
    if wheelsangle:
        fig = plt.figure()
        if titles: fig.suptitle("Wheels Angle", fontsize=15, y=1)
        ax = plt.subplot(111, xlabel=time_label, ylabel='Angle Degrees')
        data = ds.df.wheels_angle.dropna() #.apply(lambda x: np.sqrt(x) +3)
        data.plot(ax=ax, style='b', markersize=1.0)
        fig.tight_layout()
        fig.savefig(img_folder + "wheelsangle.png")
    
    if gyros:
        print "Plotting gyroscopes data..."
        fig = plt.figure()
        if titles: fig.suptitle("Gyroscopes Raw", fontsize=15, y=1)
        ax1 = plt.subplot(311, xlabel=time_label, ylabel='Raw gyro X [arcsec/s]')
        data = ds.df.gyroX.dropna()
        data.plot(ax=ax1, style=['r'], markersize=1.0)
        ax2 = plt.subplot(312, xlabel=time_label, ylabel='Raw gyro Y [arcsec/s]',sharex=ax1)
        data = ds.df.gyroY.dropna()
        data.plot(ax=ax2, style=['g'], markersize=1.0)
        ax3 = plt.subplot(313, xlabel=time_label, ylabel='Raw gyro Z [arcsec/s]',sharex=ax1)
        data = ds.df.gyroZ.dropna()
        data.plot(ax=ax3, style=['b'], markersize=1.0)        
        fig.tight_layout()
        fig.savefig(img_folder + "gyroscopesraw.png")
        
        fig = plt.figure()
        if titles: fig.suptitle("Gyroscopes Estimated", fontsize=15, y=1)
        ax1 = plt.subplot(311, xlabel=time_label, ylabel='Estimated gyro X [arcsec/s]')
        data = ds.df.estimatedgyroX.dropna()
        data.plot(ax=ax1, style=['r'], markersize=1.0)
        ax2 = plt.subplot(312, xlabel=time_label, ylabel='Estimated gyro Y [arcsec/s]',sharex=ax1)
        data = ds.df.estimatedgyroY.dropna()
        data.plot(ax=ax2, style=['g'], markersize=1.0)
        ax3 = plt.subplot(313, xlabel=time_label, ylabel='Estimated gyro Z [arcsec/s]',sharex=ax1)
        data = ds.df.estimatedgyroZ.dropna()
        data.plot(ax=ax3, style=['b'], markersize=1.0)        
        fig.tight_layout()
        fig.savefig(img_folder + "gyroscopesestimated.png")
    
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
         
    if radec:
        fig = plt.figure()
        if titles: fig.suptitle("Telescope Ra & Dec", fontsize=15, y=1)
        ax1 = plt.subplot(211, xlabel=time_label, ylabel='Telescope Ra')
        data = ds.df[['tra','tdec']].dropna() #.apply(lambda x: np.sqrt(x) +3)
        data = data.loc[(data.abs() >= 1).any(1)]  # remove rows were all fields have a value <1. #.any(1) any row (data with the same fn)
        #data=filterDataframe(data, 3, 0.9)#N remove peaks inferior at 3 samples, with 0.9 advances 10% 
        data.tra.plot(ax=ax1, style='b', markersize=1.0)
        ax2 = plt.subplot(212, xlabel=time_label, ylabel='Telescope Dec',sharex=ax1)
        data.tdec.plot(ax=ax2, style='b', markersize=1.0)
        fig.tight_layout()
        fig.savefig(img_folder + "Telescope Ra&Dec.png")
             
        fig = plt.figure()
        if titles: fig.suptitle("Gondola Ra & Dec", fontsize=15, y=1)
        ax1 = plt.subplot(211, xlabel=time_label, ylabel='Gondola Ra')
        data = ds.df[['gra','gdec']].dropna() #.apply(lambda x: np.sqrt(x) +3)
        data = data.loc[(data.abs() >= 1).any(1)]  # remove rows were all fields have a value <1. #.any(1) any row (data with the same fn)
        #data=filterDataframe(data, 3, 0.9)#N remove peaks inferior at 3 samples, with 0.9 advances 10% 
        data.gra.plot(ax=ax1, style='b', markersize=1.0)
        ax2 = plt.subplot(212, xlabel=time_label, ylabel='Gondola Dec',sharex=ax1)
        data.gdec.plot(ax=ax2, style='b', markersize=1.0)
        fig.tight_layout()
        fig.savefig(img_folder + "Telescope Ra&Dec.png")
        
        fig = plt.figure()
        if titles: fig.suptitle("Star Camera Ra & Dec", fontsize=15, y=1)
        ax1 = plt.subplot(211, xlabel=time_label, ylabel='Star Camera Ra')
        data = ds.df[['sra','sdec']].dropna() #.apply(lambda x: np.sqrt(x) +3)
        data = data.loc[(data.abs() >= 1).any(1)]  # remove rows were all fields have a value <1. #.any(1) any row (data with the same fn)
        #data=filterDataframe(data, 3, 0.9)#N remove peaks inferior at 3 samples, with 0.9 advances 10% 
        data.sra.plot(ax=ax1, style='b', markersize=1.0)
        ax2 = plt.subplot(212, xlabel=time_label, ylabel='Star Camera Dec',sharex=ax1)
        data.sdec.plot(ax=ax2, style='b', markersize=1.0)
        fig.tight_layout()
        fig.savefig(img_folder + "Star Camera Ra&Dec.png")
        
        
         
    #===========================================================================
    # 
    # if griffins:
    #===========================================================================

    print "Show..."
    plt.show()
