import pandas as pd
from scipy.signal import periodogram

import numpy as np
from numpy import sin,cos,arctan2,arcsin
import seaborn.apionly as sns
import os
import seaborn.apionly as sns
import matplotlib as mpl
import matplotlib.pyplot as plt
import scipy.stats as stats
from itertools import combinations
import quat
from quat import Quat
from itertools import groupby


# plotting parameters
mpl.rcParams['xtick.labelsize'] = 11
mpl.rcParams['xtick.major.size'] = 5
mpl.rcParams['ytick.major.size'] = 5
mpl.rcParams['xtick.minor.size'] = 5
mpl.rcParams['ytick.minor.size'] = 5
mpl.rcParams['ytick.labelsize'] = 11
mpl.rcParams['axes.labelsize'] = 11
mpl.rcParams['legend.fontsize'] = 11
mpl.rcParams['font.size'] = 11
mpl.rcParams['font.weight'] = 100
#mpl.rcParams['lines.linewidth'] = 2
mpl.rcParams['font.family'] = 'serif'
mpl.rcParams['font.serif'] = 'Times New Roman'

red = sns.xkcd_rgb['pale red']
blue = sns.xkcd_rgb['denim blue']
lt_blue = sns.xkcd_rgb['pastel blue']
colors = [blue,'g',red]

def load_single_field(fieldname,type):
	type_str_native = ">"+type
	type_str_final = "<"+type # change endianness
	# this is a temporary fix, necessary because Steve is padding the archive for KST display.
	# if using data directly from ford, we can just write:
	field = np.fromfile(fieldname,dtype=np.dtype(type_str_native))
	
	## NOTE: this breaks theflow when consecutive MEASURED values follow each other, e.g. if the wheels stay at the same angle for a while, 
	# this would delete all repeated values even if they are actual values.
	#field = np.array([x[0] for x in groupby(np.fromfile(fieldname,dtype=np.dtype(type_str_native)))])
	field = field.astype(type_str_final)
	return field

class DataSet():
	def __init__(self,folder,freq=100,default = 'gyros',min=None,max=None,folder_export = None,estimator=False,starcam=False,droplist = []):
		'''
		return a Pandas data frame indexed on the mceFramenumber
		Start loading the gyros by default
		'''
		time = load_single_field(folder+'bettii.GyroReadings.mceFrameNumber','i8')
		gyroX = load_single_field(folder+'bettii.GyroReadings.angularVelocityX','i4')*0.0006304
		gyroY = load_single_field(folder+'bettii.GyroReadings.angularVelocityY','i4')*0.0006437
		gyroZ = load_single_field(folder+'bettii.GyroReadings.angularVelocityZ','i4')*0.0006324
		gyroXF = load_single_field(folder+'bettii.GyroReadings.angularVelocityFilteredX','i4')*0.0006304
		gyroYF = load_single_field(folder+'bettii.GyroReadings.angularVelocityFilteredY','i4')*0.0006437
		gyroZF = load_single_field(folder+'bettii.GyroReadings.angularVelocityFilteredZ','i4')*0.0006324
		gyroXT = load_single_field(folder+'bettii.GyroReadings.temperatureDegF_X','i4')
		gyroYT = load_single_field(folder+'bettii.GyroReadings.temperatureDegF_Y','i4')
		gyroZT = load_single_field(folder+'bettii.GyroReadings.temperatureDegF_X','i4')
		timeRTHighPriority = load_single_field(folder+'bettii.RTHighPriority.mceFrameNumber','i8')
		timeRTLowPriority = load_single_field(folder+'bettii.RTLowPriority.mceFrameNumber','i8')
		crossEl = load_single_field(folder+'bettii.RTHighPriority.crossElevation','f8')
		elevation = load_single_field(folder+'bettii.RTHighPriority.Elevation','f8')
		telRA = load_single_field(folder+'bettii.RTHighPriority.TelescopeRaDeg','f8')
		telDec = load_single_field(folder+'bettii.RTHighPriority.TelescopeDecDeg','f8')
		#plt.plot(telRA,telDec)
		print(len(timeRTHighPriority))
		print(len(crossEl))
		print(len(elevation))
		plt.plot(crossEl,elevation)
		plt.show()
		criticals = {'crossEl':crossEl,
					'elevation':elevation}
		gyros = {'gyroX':gyroX,
				'gyroY': gyroY,
				'gyroZ':gyroZ}
		gyros_T = {'gyroXT':gyroXT,
				'gyroYT': gyroYT,
				'gyroZT':gyroZT}
		# gyros_F = {'gyroXF':gyroXF,
				# 'gyroYF': gyroYF,
				# 'gyroZF':gyroZF}
		timeDivider = 1
		df_tmp = pd.DataFrame(gyros,index=time/timeDivider)
		df_tmp.drop_duplicates(inplace=True)
		#df_crit = pd.DataFrame(criticals,index=timeRTHighPriority/timeDivider)
		#df_tmp = pd.merge(df_tmp,df_crit,how='inner',left_index=True,right_index=True)
		#plt.plot(crossEl,elevation)
		#plt.show()
		#print df_tmp
		#df_temp = pd.DataFrame(gyros_T,index=time/timeDivider)
		#df_tmp =  pd.merge(df_tmp,df_temp,how='inner',left_index=True,right_index=True)
		#df_filt = pd.DataFrame(gyros_F,index=time/timeDivider)
		#df_tmp =  pd.merge(df_tmp,df_filt,how='inner',left_index=True,right_index=True)
		if default != 'gyros':
			momDumpTime = load_single_field(folder+'bettii.PIDOutputMomDump.mceFrameNumber','i8')
			momDumpCommand = load_single_field(folder+'bettii.PIDOutputMomDump.ut','f4')
			CCMGTime = load_single_field(folder+'bettii.PIDOutputCCMG.mceFrameNumber','i8')
			CCMGCommand = load_single_field(folder+'bettii.PIDOutputCCMG.ut','f4')
			momDump = {'momDumpCommand':momDumpCommand}
			CCMG = {'CCMGCommand':CCMGCommand}
			stepperTime = load_single_field(folder+'bettii.StepperGalil.mceFrameNumber','i8')
			stepperWheelsAngle = load_single_field(folder+'bettii.StepperGalil.wheelsAngle','f4')
			stepper = {'CCMGWheelsAngle':stepperWheelsAngle}
			print stepperTime,stepperWheelsAngle
			df_tmp2 = pd.DataFrame(criticals,index=timeRTHighPriority/timeDivider)
			df_tmp2.drop_duplicates(inplace=True)
			df_tmp3 = pd.DataFrame(momDump,index=momDumpTime/timeDivider)
			df_tmp3.drop_duplicates(inplace=True)
			df_tmp4 = pd.DataFrame(CCMG,index=CCMGTime/timeDivider)
			df_tmp4.drop_duplicates(inplace=True)
			#df_tmp5 = pd.DataFrame(stepper,index=stepperTime/timeDivider)
			df_tmp = pd.merge(df_tmp,df_tmp2,how='inner',left_index=True,right_index=True)
			df_tmp = pd.merge(df_tmp,df_tmp3,how='inner',left_index=True,right_index=True)
			df_tmp = pd.merge(df_tmp,df_tmp4,how='inner',left_index=True,right_index=True)
			print df_tmp
			#df_tmp = pd.merge(df_tmp,df_tmp5,how='inner',left_index=True,right_index=True)
		#df_tmp.to_csv('.csv')
		if estimator:
			#covariance matrix
			Cov00 = np.sqrt(load_single_field(folder+'bettii.RTLowPriority.MeasurementErrorCovarianceMatrixR00','f8'))/4.8484e-6
			Cov11 = np.sqrt(load_single_field(folder+'bettii.RTLowPriority.MeasurementErrorCovarianceMatrixR11','f8'))/4.8484e-6
			Cov22 = np.sqrt(load_single_field(folder+'bettii.RTLowPriority.MeasurementErrorCovarianceMatrixR22','f8'))/4.8484e-6

			#estimator (show only diagonal values)
			Q00 = np.sqrt(load_single_field(folder+'bettii.RTLowPriority.covarianceMatrix00','f8'))/4.8484e-6
			Q11 = np.sqrt(load_single_field(folder+'bettii.RTLowPriority.covarianceMatrix11','f8'))/4.8484e-6
			Q22 = np.sqrt(load_single_field(folder+'bettii.RTLowPriority.covarianceMatrix22','f8'))/4.8484e-6
			Q33 = np.sqrt(load_single_field(folder+'bettii.RTLowPriority.covarianceMatrix33','f8'))/4.8484e-6
			Q44 = np.sqrt(load_single_field(folder+'bettii.RTLowPriority.covarianceMatrix44','f8'))/4.8484e-6
			Q55 = np.sqrt(load_single_field(folder+'bettii.RTLowPriority.covarianceMatrix55','f8'))/4.8484e-6

			#bias
			biasX = load_single_field(folder+'bettii.RTHighPriority.estimatedBiasXarcsec','f8')
			biasY = load_single_field(folder+'bettii.RTHighPriority.estimatedBiasYarcsec','f8')
			biasZ = load_single_field(folder+'bettii.RTHighPriority.estimatedBiasZarcsec','f8')
			
			# trigger pulses (aligned with mceFrameNmber); this tells us how long the exposure time was, in number of frames (400Hz)
			#position given by the star camera corresponds should be compared to the estimated position at the 
			# at the location of the trigger (the index of this pulse) + half the amount of this pulse's value
			starcam_trigger_pulses =load_single_field(folder+'bettii.RTHighPriority.StarCameraTriggerStatus','i8')

			# estimator
			qr_list = load_single_field(folder+'bettii.RTLowPriority.qr','f8')
			qi_list = load_single_field(folder+'bettii.RTLowPriority.qi','f8')
			qj_list = load_single_field(folder+'bettii.RTLowPriority.qj','f8')
			qk_list = load_single_field(folder+'bettii.RTLowPriority.qk','f8')
			estimated_quatlist = [Quat(quat.normalize((qi_list[i],qj_list[i],qk_list[i],qr_list[i]))) for i in range(len(qr_list))]
			est_ra = [q.ra*3600. for q in estimated_quatlist]
			est_dec = [q.dec*3600. for q in estimated_quatlist]
			est_roll = [q.roll*3600. for q in estimated_quatlist]

			estimatorData = {'Cov00':Cov00,'Cov11':Cov11,'Cov22':Cov22,
							'Q00':Q00,'Q11':Q11,'Q22':Q22,'Q33':Q33,'Q44':Q44,'Q55':Q55,
							'ra':est_ra,'dec':est_dec,'roll':est_roll,
							}
			biasData = {'biasX':biasX,'biasY':biasY,'biasZ':biasZ}
			df_estimator = pd.DataFrame(estimatorData,index = timeRTLowPriority/timeDivider)
			df_estimator.drop_duplicates(inplace=True)
			print df_estimator
			df_bias = pd.DataFrame(biasData,index = timeRTHighPriority/timeDivider)
			df_bias.drop_duplicates(inplace=True)
			df_tmp = pd.merge(df_tmp,df_estimator,how='inner',left_index=True,right_index=True)
			df_tmp = pd.merge(df_tmp,df_bias,how='inner',left_index=True,right_index=True)
		
		if starcam:
			### star camera loading
			# Load star camera trigger number
			# this is the mceFrameNumber at which the starcamera trigger occurred, and which is processed by the starFinder
			starcam_trigger = load_single_field(folder+'bettii.RTLowPriority.RawStarcameraMceFrameNumberWhenSCTriggered','i8')
			
			meas_qr_list = load_single_field(folder+'bettii.RTLowPriority.StarCameraRotatedqr','f8')
			meas_qi_list = load_single_field(folder+'bettii.RTLowPriority.StarCameraRotatedqi','f8')
			meas_qj_list = load_single_field(folder+'bettii.RTLowPriority.StarCameraRotatedqj','f8')
			meas_qk_list = load_single_field(folder+'bettii.RTLowPriority.StarCameraRotatedqk','f8')

			starcamsol = {'triggers': starcam_trigger,
						'meas_qr': meas_qr_list,
						'meas_qi': meas_qi_list,
						'meas_qj': meas_qj_list,
						'meas_qk': meas_qk_list,
						}
			print starcam_trigger
			print len(starcam_trigger)
			df_solution = pd.DataFrame(starcamsol,index = timeRTLowPriority/timeDivider)
			df_solution.drop_duplicates(inplace=True)
			df_solution = df_solution.loc[np.abs(df_solution['meas_qr'])>1e-10]
			df_solution = df_solution.loc[np.abs(df_solution['meas_qr'])<=1.0]
			df_solution = df_solution.loc[np.abs(df_solution['meas_qi'])<=1.0]
			df_solution = df_solution.loc[np.abs(df_solution['meas_qj'])<=1.0]
			df_solution = df_solution.loc[np.abs(df_solution['meas_qk'])<=1.0]
			df_solution = df_solution.drop_duplicates(subset='triggers') # only keeps the unique values for triggers
			
			# convert to ra/dec/roll
			#print df_solution.iloc[5][['meas_qi','meas_qj','meas_qk','meas_qr']]
			measured_quatlist = [Quat(quat.normalize(df_solution.loc[mceFN][['meas_qi','meas_qj','meas_qk','meas_qr']])) for mceFN in df_solution.index]
			meas_ra_calc = [q.ra*3600. for q in measured_quatlist]
			meas_dec_calc = [q.dec*3600. for q in measured_quatlist]
			meas_roll_calc = [q.roll*3600. for q in measured_quatlist]
			
			meas_radecroll = {'ra_sc':meas_ra_calc,
							'dec_sc':meas_dec_calc,
							'roll_sc':meas_roll_calc,
							}
			df_solution = pd.merge(df_solution,pd.DataFrame(meas_radecroll,index=df_solution.index),how='inner',left_index=True,right_index=True)
			df_solution = df_solution.drop(['meas_qi','meas_qj','meas_qk','meas_qr'],1)
			
			
			# sort out the triggers and bad data lines
			self.pulses = pd.DataFrame({'duration': starcam_trigger_pulses},index = timeRTLowPriority/timeDivider)
			(self.pulses).drop_duplicates(inplace=True)
			durations = self.pulses.loc[df_solution['triggers']]
			durations = pd.DataFrame(durations,index = durations.index)
			self.df_solution = pd.merge(df_solution,durations,how='inner',left_on='triggers',right_index=True)
			self.df_solution = self.df_solution.dropna(axis=0)
			self.df_solution['trigger_center'] = self.df_solution['triggers']+np.round(self.df_solution['duration']/8)*4
			
			# what are the estimated values?
			#estval = df_estimator.loc[self.df_solution['trigger_center']] # times 4 and divided by 2
			#values = pd.DataFrame(estval.loc[:,['ra','dec','roll']],index=self.df_solution.index)
			#print estval.loc[:,['ra','dec','roll']],values
			self.df_solution = pd.merge(self.df_solution,df_estimator[['ra','dec','roll']],how='inner',left_on='trigger_center',right_index=True)
			#self.df_solution[['ra','dec','roll']] = estval.loc[:,['ra','dec','roll']]
			#print self.df_solution
			
		df_tmp = df_tmp.dropna(axis=0)
		df_tmp = df_tmp.drop(droplist)
		if min == None and max==None:
			self.df = df_tmp
		elif min == None and max!=None:
			self.df = df_tmp.loc[:max*400,:]
		elif max == None and min!=None:
			self.df = df_tmp.loc[min*400:,:]
		else:
			self.df = df_tmp.loc[min*400:max*400,:]
		self.freq = freq
		self.length = len(self.df)
		self.folder = folder.split('/')[-1]
		if folder_export == None: self.folder_export = self.folder
		else: self.folder_export = folder_export
		#print self.df[['meas_qr','meas_qi','meas_qj','meas_qk']] #.iloc[-1]
		#print self.df #.iloc[-1]
		#print self.df_solution
		
		
		
		
		
	def simplePlot(self,val,minMax = [],ylabel="",ax_key=None,save=True,show=False,realTime=True,name=None):
		print "Loading %s data..." %val
		if ax_key==None: fig,ax = plt.subplots(figsize=(5.9,4),dpi=120)
		else: ax = ax_key
		data = self.df[val]
		ax.set_xlabel("Time (s)")
		ax.set_ylabel(ylabel)
		ax.grid(True)
		if realTime: ax.plot(self.df.index/400.,data,label=val,color=blue)
		else: ax.plot(self.df.index,data,label=val,color=blue)
		if minMax != []:
			ax.set_xlim = minMax
		ax.legend(loc='best')
		if ax_key==None:
			fig.tight_layout()
			if save: 
				if name==None: fig.savefig(self.folder_export+"simplePlot_%s.png" % val,dpi=300)
				else: fig.savefig(self.folder_export+name+"_%s.png" % val,dpi=300)
			if show: plt.show()
			#plt.close(fig)
		print "Done."
	def simple2DPlot(self,field1,field2,minMax = [],xlabel="",ylabel="",ax_key=None,save=True,show=False,realTime=True,name=None,kde = False):
		print "Loading data..."
		if ax_key==None: fig,ax = plt.subplots(figsize=(5.9,4),dpi=120)
		else: ax = ax_key
		data1 = self.df[field1]
		data2 = self.df[field2]
		ax.set_xlabel(xlabel)
		ax.set_ylabel(ylabel)
		ax.grid(True)
		ax.scatter(data1,data2,color=blue,alpha=0.4)
		if kde:
			sns.kdeplot(data1,data2,ax=ax)
		ax.set_xlabel(xlabel)
		ax.set_ylabel(ylabel)
		ax.grid(True)
		if ax_key==None:
			fig.tight_layout()
			if save: 
				if name==None: fig.savefig(self.folder_export+"simple2DPlot_%s_%s.png" % (field1,field2),dpi=300)
				else: fig.savefig(self.folder_export+name+"_%s_%s.png" % (field1,field2),dpi=300)
			if show: plt.show()
			plt.close(fig)
		print "Done."

	def plotGyros(self,minMax = [],ylabel="",save=True,show=False,realTime=True,name=None):
		print "Plotting Gyros"
		mylist = ['gyroX','gyroY','gyroZ']
		fig,axlist = plt.subplots(3,figsize=(5.9,8),dpi=120)
		for i in range(3):
			ax = axlist[i]
			self.simplePlot(mylist[i],ylabel = mylist[i] + " (arcsec/s)",ax_key=ax,save=save,show=False,name=None)
		fig.tight_layout()
		if save:
			if name==None: fig.savefig(self.folder_export+"gyros%d.png" % self.freq,dpi=300)
			else: fig.savefig(self.folder_export+name+"_%d.png" % self.freq,dpi=300)
		if show: plt.show()
		plt.close(fig)
	def plotBiases(self,minMax = [],ylabel="",save=True,show=False,realTime=True,name=None):
		print "Plotting biases"
		mylist = ['biasX','biasY','biasZ']
		fig,axlist = plt.subplots(3,figsize=(5.9,8),dpi=120)
		for i in range(3):
			ax = axlist[i]
			self.simplePlot(mylist[i],ylabel = mylist[i] + " (arcsec/s)",ax_key=ax,save=save,show=False,name=None)
			if minMax != []:
				ax.set_xlim = minMax
		fig.tight_layout()
		if save:
			if name==None: fig.savefig(self.folder_export+"biases%d.png" % self.freq,dpi=300)
			else: fig.savefig(self.folder_export+name+"_%d.png" % self.freq,dpi=300)
		if show: plt.show()
		plt.close(fig)
	def plotQdiag(self,minMax = [],ylabel="",save=True,show=False,realTime=True,name=None):
		print "Plotting covariance"
		mylist = ['Q00','Q11','Q22']
		fig,axlist = plt.subplots(3,figsize=(5.9,8),dpi=120)
		for i in range(3):
			ax = axlist[i]
			self.simplePlot(mylist[i],ylabel = mylist[i]  + " (arcsec)",ax_key=ax,save=save,show=False,name=None)
			if minMax != []:
				ax.set_xlim = minMax

		fig.tight_layout()
		if save:
			if name==None: fig.savefig(self.folder_export+"covar%d.png" % self.freq,dpi=300)
			else: fig.savefig(self.folder_export+name+"_%d.png" % self.freq,dpi=300)
		if show: plt.show()
		plt.close(fig)
	
	def integralPlot(self,val,minMax = [],ylabel="",save=True,show=False,realTime=True,name=None):
		print "Loading %s data..." %val
		fig,ax = plt.subplots(figsize=(5.9,4),dpi=120)
		data = np.cumsum(self.df[val])/np.float(self.freq)
		ax.set_xlabel("Time (s)")
		ax.set_ylabel(ylabel)
		ax.grid(True)
		if realTime: ax.plot(self.df.index/400.,data,label=val,color=blue)
		else: ax.plot(self.df.index,data,label=val,color=blue)
		if minMax != []:
			ax.set_xlim = minMax
		ax.legend(loc='best')
		fig.tight_layout()
		if save: 
			if name==None: fig.savefig(self.folder_export+"integralPlot_%s.png" % val,dpi=300)
			else: fig.savefig(self.folder_export+name+"_%s.png" % val,dpi=300)
		if show: plt.show()
		plt.close(fig)
		print "Done."

		
	def PSD(self,column,show=False,save=True,loglog=True,ax_key=None,minPlot=None,name=None,minMax=[],units = '(arcsec/s)$^2$/Hz'):
		print "Loading gyro data..."
		data = self.df[column]
		if ax_key==None: fig,ax = plt.subplots(figsize=(5.9,4),dpi=120)
		else: ax = ax_key
		print "Calculating power spectral density..."
		f, Pxx_den = periodogram(data, self.freq)

		if loglog: ax.loglog(f,Pxx_den,color=blue,label=column)
		else:ax.plot(f,Pxx_den,color=blue,label=column)
		ax.set_xlabel('Frequency [Hz]')
		ax.set_ylabel('Power spectral density ['+units+']')
		if minPlot !=None and minMax==[]: ax.set_xlim([minPlot,max(f)])
		elif minMax!=[]: ax.set_xlim(minMax)
		ax.set_ylim([1e-8,max(Pxx_den)])
		ax.legend(loc='best')
		ax.grid(True)
		if ax_key==None:
			fig.tight_layout()
			if save:
				if name==None: fig.savefig(self.folder_export+"PSD%d.png" % self.freq,dpi=300)
				else: fig.savefig(self.folder_export+name+"_%d.png" % self.freq,dpi=300)
			if show: plt.show()
			plt.close(fig)
		print "Done."

	def multiPSD(self,columns,show=False,save=True,loglog=False,name=None,minMax=[],units='(arcsec/s)$^2$/Hz'):
		print "Plotting multiple PSDs"
		fig,axlist = plt.subplots(len(columns),figsize=(5.9,8),dpi=120)
		for i in range(len(columns)):
			ax = axlist[i]
			self.PSD(columns[i],save=False,loglog=loglog,ax_key=ax,minPlot=0.001,minMax=minMax,units=units)
			if minMax != []:
				ax.set_xlim = minMax
		fig.tight_layout()
		if save:
			if name==None: fig.savefig(self.folder_export+"multiPSD%d.png" % self.freq,dpi=300)
			else: fig.savefig(self.folder_export+name+"_%d.png" % self.freq,dpi=300)
		if show: plt.show()
		plt.close(fig)
		

	def qqplot(self,column,show=False,ax_key=None,save=True):
		print "QQ plot..."
		data = self.df[column]
		if ax_key==None: fig,ax = plt.subplots(figsize=(5.9,4),dpi=120)
		else: ax=ax_key
		(osm,osr),(slope, intercept, r) = stats.probplot(data)
		ax.scatter(osm, osr, color=blue)
		ax.plot(osm, slope*osm + intercept, color=red)
		ax.set_xlabel('Quantiles')
		ax.set_ylabel('Ordered Values')
		# Add R^2 value to the plot as text
		xmin = min(osm)
		xmax = max(osm)
		ymin = min(data)
		ymax = max(data)
		posx = xmin + 0.70 * (xmax - xmin)
		posy = ymin + 0.01 * (ymax - ymin)
		ax.text(posx, posy, "$R^2=%1.10f$" % r)
		if ax_key==None:
			fig.tight_layout()
			if save:fig.savefig(self.folder_export+"qqplot_%s.png" % name,dpi=300)
			if show: plt.show()
			plt.close(fig)
		print "Done."

	def kde(self,column,show=False,ax_key=None,save=True):
		print "Kernel estimation..."
		data = self.df[column]
		if ax_key==None: fig,ax = plt.subplots(figsize=(5.9,4),dpi=120)
		else: ax=ax_key
		kernel = stats.gaussian_kde(data)
		print "Calculating histogram of dataset..."
		hist, bin_edges = np.histogram(data, bins =50,density=True)
		print "Plotting..."
		ax.bar(bin_edges[:-1], hist, width = np.diff(bin_edges),color=blue,alpha=0.7)
		ax.set_xlim(min(bin_edges), max(bin_edges))
		xaxis = np.linspace(min(bin_edges),max(bin_edges),200)
		ax.set_xlabel('Angular velocity bins (arcsec/s)')
		ax.set_ylabel('Probability density')
		ax.plot(xaxis,kernel(xaxis),color=red,lw=2)
		if ax_key==None:
			fig.tight_layout()
			if save:fig.savefig(self.folder_export+"hist_%s.png" % name,dpi=300)
			if show: plt.show()
			plt.close(fig)
		print "Done."

	def scatterPlots(self,collist,ax_key=None,show=False,save=True,name=None):
		print 'Making scatter plots'
		pairList = list(combinations(collist,2))
		N = len(pairList)
		#nsqr = np.sqrt(N)
		#N = np.ceil(nsqrt)
		if ax_key==None: fig,ax = plt.subplots(figsize=(5.9,5.9),dpi=120)
		else: ax=ax_key
		for i in range(len(pairList)):
			pair = pairList[i]
			ax.scatter(self.df[pair[0]],self.df[pair[1]],color = colors[i],label=pair[0]+","+pair[1],alpha=0.9,edgecolor=None,facecolor=None,linewidth=0.1)
		ax.legend()
		ax.grid()
		if ax_key==None:
			fig.tight_layout()
			if save:
				if name==None: fig.savefig(self.folder_export+"scatterPlots"+"".join([col for col in collist])+".png",dpi=300)
				else: fig.savefig(self.folder_export+name+".png",dpi=300)
			if show: plt.show()
			plt.close(fig)
	
	def plotEstVsMeas(self,ax_key=None,show=False,save=True,name=None):
		if ax_key==None: fig,ax = plt.subplots(figsize = (5.9,5.9))
		else: ax=ax_key
		print "Plotting estimated attitude"
		ax.scatter(self.df['ra']/3600.,self.df['dec'],color=red,label='Estimated attitude')
		print "Plotting Star camera measurements"
		ax.scatter(self.df_solution['ra_sc']/3600.,self.df_solution['dec_sc'],color=blue,s=20,label='Star camera measurement')
		print "Plotting distance between star camera measurement and estimated attitude"
		blues = sns.color_palette("Blues_d",len(self.df_solution))
		for i in range(len(self.df_solution)):
			ax.plot(np.array([self.df_solution.iloc[i]['ra_sc']/3600.,self.df_solution.iloc[i]['ra']/3600.]),np.array([self.df_solution.iloc[i]['dec_sc'],self.df_solution.iloc[i]['dec']]),color=blues[i],lw=1)
		ax.set_xlabel("RA (deg)")
		ax.set_ylabel("DEC (arcsec)")
		#ax.set_xlim([225,244])
		ax.grid(True)
		ax.legend(loc = 'best')
		if ax_key==None:
			fig.tight_layout()
			if save:
				if name==None:  fig.savefig(self.folder_export+"EstVsMeas.png",dpi=300)
				else: fig.savefig(self.folder_export+name+".png",dpi=300)
			if show: plt.show()
			plt.close(fig)
