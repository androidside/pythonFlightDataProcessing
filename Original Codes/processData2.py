from bettiiDataProc import *
import matplotlib.pyplot as plt


gyros = ['gyroX','gyroY','gyroZ']


##400 Hz gyros mounted on truss
# folder = 'F:/AuroraArchive/16-06-07_16_23_30-/'
# ds = DataSet(folder,freq=400,folder_export='Gyros400Hz/')

# sqVel = np.sqrt(np.sum([np.mean(ds.df[val])**2 for val in gyros]))
# print sqVel,np.abs(15.-sqVel)/15.*100

# show=True
#ds.plotGyros(show=show)
# fig,axlist = plt.subplots(3,figsize=(5.9,8),dpi=120)
# for i in range(3):
	# ax = axlist[i]
	# ax.scatter(ds.df.index/400.,ds.df[gyros[i]],color=blue)
# plt.show()
# ds.multiPSD(gyros,show=show,loglog=True)
# ds.multiPSD(gyros,show=show,loglog=False,name="multiPSD_no_loglog")
# ds.multiPSD(gyros,show=show,loglog=False,name="multiPSD_no_loglog_zoom",minMax=[24,28])

# ds.scatterPlots(['gyroX','gyroY'],show=show)
# ds.scatterPlots(['gyroX','gyroZ'],show=show)
# ds.scatterPlots(['gyroY','gyroZ'],show=show)


# 400 Hz gyros mounted on truss, payload lifted
# folder = 'F:/AuroraArchive/16-06-07_17_36_27-/'
# ds = DataSet(folder,freq=400,folder_export='Gyros400Hz_lifted/')

# show=True
# ds.plotGyros(show=show)
# ds.multiPSD(gyros,show=show,loglog=True)
# ds.multiPSD(gyros,show=show,loglog=False,name="multiPSD_no_loglog")
# ds.multiPSD(gyros,show=show,loglog=False,name="multiPSD_no_loglog_zoom",minMax=[24,28])

# ds.scatterPlots(['gyroX','gyroY'],show=show)
# ds.scatterPlots(['gyroX','gyroZ'],show=show)
# ds.scatterPlots(['gyroY','gyroZ'],show=show)


## 100 Hz, gyros mounted on truss, payload lifted and tracking on (wheels not synchronized)

# folder = 'F:/AuroraArchive/16-06-07_19_35_18- Deadband = 2 FIlter Z at 5 Hz/'
# ds = DataSet(folder,freq=100,default='all',folder_export='Gyros100Hz_Tracking/')


# show=False
# ds.simplePlot('gyroZ',show=show,ylabel="Angular velocity (arcsec/s)")
# ds.simplePlot('crossEl',show=show,ylabel="Azimuthal error (arcsec)")
# ds.simplePlot('momDumpCommand',show=show,ylabel="Motor velocity (microsteps/s)")
# ds.simplePlot('CCMGCommand',show=show,ylabel="Motor velocity (microsteps/s)")
# ds.simplePlot('stepperTPA',show=show)

# ds.PSD('crossEl',show=show,name='crossEl',units='(arcsec)$^2$/Hz')
# ds.simplePlot('elevation',show=show)
# ds.PSD('elevation',show=show,name='elevation',units='(arcsec)$^2$/Hz')
# ds.multiPSD(gyros,show=show,loglog=True,units='(arcsec/s)$^2$/Hz')
# ds.multiPSD(gyros,show=show,loglog=False,name="multiPSD_no_loglog",units='(arcsec/s)$^2$/Hz')

## 100 Hz, gyros mounted on truss, payload lifted and tracking on (wheels not synchronized)

# folder = 'F:/AuroraArchive/16-06-07_19_47_55-/'
# ds = DataSet(folder,freq=100,default='all',folder_export='Gyros100Hz_Tracking2/')
# show=False
# ds.simplePlot('gyroZ',show=show,ylabel="Angular velocity (arcsec/s)")
# ds.simplePlot('crossEl',show=show,ylabel="Azimuthal error (arcsec)")
# ds.simplePlot('momDumpCommand',show=show,ylabel="Motor velocity (microsteps/s)")
# ds.simplePlot('CCMGCommand',show=show,ylabel="Motor velocity (microsteps/s)")
# ds.simplePlot('stepperTPA',show=show)

# ds.PSD('crossEl',show=show,name='crossEl',units='(arcsec)$^2$/Hz')
# ds.simplePlot('elevation',show=show)
# ds.PSD('elevation',show=show,name='elevation',units='(arcsec)$^2$/Hz')
# ds.multiPSD(gyros,show=show,loglog=True,units='(arcsec/s)$^2$/Hz')
# ds.multiPSD(gyros,show=show,loglog=False,name="multiPSD_no_loglog",units='(arcsec/s)$^2$/Hz')

## Estimated biases from new starcam
folder = 'F:/AuroraArchive/16-06-10_00_43_55-EstimateBiasesNewStarcam/'
#ds = DataSet(folder,freq=100,folder_export='BiasEstimation/',default='all',estimator=True,min=111,max=112,droplist = [44516])

#folder = 'F:/AuroraArchive/16-06-10_01_05_44-Tracking run/'
#folder = 'F:/AuroraArchive/16-06-09_21_56_10-/'
#folder = 'F:/AuroraArchive/16-06-07_16_23_30-/'


# ds = DataSet(folder,freq=100,folder_export='BiasEstimation/',default='all',estimator=True,min=50)

# show=True
# ds.df.where(ds.df>0)
# print ds.df.loc(index=44516)

# ds.plotGyros(show=show,save=False)
# ds.multiPSD(gyros,show=show,loglog=True)

# ds.plotBiases(show=show,save=False)
# ds.plotQdiag(show=show,save=False)

# ds.simplePlot('crossEl',show=show,ylabel="Angular distance from target (arcsec)",save=False)

# means = ds.df[gyros].mean(axis=0)
# print means
# print np.sqrt(np.sum(ds.df[gyros].mean(axis=0)**2))
# print means*-9.439/means[2]
# elev = -39.0*np.pi/180.
# azimuth = (-50.3)*np.pi/180. #from north
# Qelev = Quat((0.0,np.sin(elev/2.),0.0,np.cos(elev/2.)))
# Qaz = Quat((np.sin(azimuth/2.),0.0,0.0,np.cos(azimuth/2.)))
# Qtot = Qaz*Qelev
# vec = Quat((0,0,1.,0))
# rotVec =  (Qtot * (vec * (Qtot.inv()))).q*15.0
# print "Z axis is supposed to be",rotVec[0],"and is",-means[2]
# print "Y axis is supposed to be",rotVec[1],"and is",-means[0]
# print "X axis is supposed to be",rotVec[2],"and is",means[1]
# gyrosF = ['gyroXF','gyroYF','gyroZF']

# sumsq = np.sum(ds.df[gyrosF]**2,axis=1)
# print np.mean(np.sqrt(sumsq))
# plt.plot(np.sqrt(sumsq))
# plt.show()



#folder = 'F:/AuroraArchive/16-06-09_22_25_08-/'
#ds = DataSet(folder,freq=100,folder_export='BiasEstimation/',default='all',estimator=True,starcam=True)

# folder = 'F:/AuroraArchive/16-06-09_21_56_10-/'
# ds = DataSet(folder,freq=100,folder_export='BiasEstimation/',default='all',estimator=True,starcam=True)

#folder = 'F:/AuroraArchive/16-06-09_18_07_49-Point and Slew-Nice-Indoors/'
# folder = 'F:/AuroraArchive/16-06-10_00_43_55-EstimateBiasesNewStarcam/'
# ds = DataSet(folder,freq=100,folder_export='BiasEstimation/',default='all',estimator=True,starcam=True)
show=True


#folder = 'F:/AuroraArchive/16-06-10_01_15_33-/'
#ds = DataSet(folder,freq=100,folder_export='BiasEstimation/',default='all',estimator=True,starcam=True,min=3300)
# folder = 'F:/AuroraArchive/16-06-10_01_05_44-Tracking run/' #(not very good run, diverges after 2400)
# ds = DataSet(folder,freq=100,folder_export='BiasEstimation/',default='all',estimator=True,starcam=True,max=2400)
#print ds.df_solution.loc[np.abs(ds.df_solution['starcam_trigger_pulses'])<500].max()
#ds.plotGyros(show=show,save=False)
#ds.simple2DPlot('crossEl','elevation',show=show,save=True,kde=True,xlabel='Cross-elevation error (arcsec)',ylabel='Elevation error (arcsec)')
# ds.simplePlot('crossEl',show=show,ylabel="Angular distance from target (arcsec)",save=False)
# ds.plotEstVsMeas(show=show)
# ds.plotBiases(show=show,save=False)
# ds.multiPSD(gyros,show=show,loglog=True)

# mapped network drive
folder = "Y:/16-09-15_00_49_26-/"
ds = DataSet(folder,freq=100,folder_export='',default='all',estimator=True,starcam=False,min=0)
#ds.simple2DPlot('crossEl','elevation',show=show,save=True,kde=True,xlabel='Cross-elevation error (arcsec)',ylabel='Elevation error (arcsec)')

#folder = "Y:/16-03-27_23_48_45-/"
#ds = DataSet(folder,freq=100,folder_export='',default='all',estimator=True,starcam=True,min=0)
#ds.simple2DPlot('crossEl','elevation',show=show,save=True,kde=True,xlabel='Cross-elevation error (arcsec)',ylabel='Elevation error (arcsec)')
