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

    folder = "C:/LocalAuroraArchive/17-05-30_19_44_12/"
    #Flags    
    #data to read and plot
    ccmg = True
    momdump = True
    steppergalil=False
    gyros=False
    azimuth=False #measured and desired azimuth position and velocity
    radec = False #telescopeRaDec, GondolaRaDec, StarcameraRaDec
    griffins = False    
    
    titles=True #show titles on the figures
    
    fieldsList = []    
    if ccmg:
        fieldsList.append(Field('bettii.PIDOutputCCMG.ut',label='ccmg_ut'))
        fieldsList.append(Field('bettii.PIDOutputCCMG.et',label='ccmg_et'))
        fieldsList.append(Field('bettii.PIDOutputCCMG.proportional',label='P CCMG'))   #To remove very highbalues
        fieldsList.append(Field('bettii.PIDOutputCCMG.integral',label='I CCMG'))
        fieldsList.append(Field('bettii.PIDOutputCCMG.derivative',label='D CCMG'))                
    if momdump:
        fieldsList.append(Field('bettii.PIDOutputMomDump.ut',label='mom_ut'))
        fieldsList.append(Field('bettii.PIDOutputMomDump.et',label='mom_et'))
        fieldsList.append(Field('bettii.PIDOutputMomDump.proportional',label='P MomDump'))   
        fieldsList.append(Field('bettii.PIDOutputMomDump.integral',label='I MomDump'))
        fieldsList.append(Field('bettii.PIDOutputMomDump.derivative',label='D MomDump'))        
    if steppergalil: fieldsList.append(Field('bettii.StepperGalil.wheelsAngle',label='wheels_angle'))        
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
    
    ds = DataSet(fieldsList=fieldsList, folder=folder, verbose=True, rpeaks=False,timeIndex=True)
    #optional Filter
    filterDataframe(ds.df, 3, 0.9)#N remove peaks inferior at 3 samples, with 0.9 advances 10% 
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


         
         
    #===========================================================================
    # if momdump:
    # if steppergalil:
    # if gyros:
    #     
    #    
    # if azimuth:
    # if radec:
    # if griffins:
    #===========================================================================

    print "Show..."
    plt.show()
