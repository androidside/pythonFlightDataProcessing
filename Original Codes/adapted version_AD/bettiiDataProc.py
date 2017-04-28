import pandas as pd
from scipy.signal import periodogram

import numpy as np
from numpy import sin,cos,arctan2,arcsin
#import seaborn.apionly as sns
import os
import matplotlib as mpl
import matplotlib.pyplot as plt
import scipy.stats as stats
from itertools import combinations
#import quat
#from quat import Quat

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

#red = sns.xkcd_rgb['pale red']
#blue = sns.xkcd_rgb['denim blue']
#lt_blue = sns.xkcd_rgb['pastel blue']
#colors = [blue,'g',red]

def load_single_field(fieldname,type):
	type_str_native = ">"+type
	type_str_final = "<"+type # change endianness
	field = np.fromfile(fieldname,dtype=np.dtype(type_str_native))
	field = field.astype(type_str_final)
	return field

class DataSet():
	def __init__(self,folder,freq=100,default = 'gyros',min=None,max=None,folder_export = None,estimator=False,starcam=False,droplist = []):
		'''
		return a Pandas data frame indexed on the mceFramenumber
		Start loading the gyros by default
		'''
		timeLowPriority = load_single_field(folder+'bettii.RTLowPriority.RawStarcameraMceFrameNumberWhenSCTriggered','i8')
		SCnumMatch = load_single_field(folder+'bettii.RTLowPriority.RawStarcameraNumMatched','i4')
		f = open('RTlowPr.txt', 'w')
		for i in range(1, len(timeLowPriority)):
			if (timeLowPriority[i] != timeLowPriority[i-1]):
				#print(str(timeRTHighPriority[i])+ " " + str(timeRTHighPriority[i-1]))
				f.write(str(timeLowPriority[i]) + " " + str(SCnumMatch[i]) + "\n")		
		f.close()

		timeRTHighPriority = load_single_field(folder+'bettii.RTHighPriority.mceFrameNumber','i8')
		crossEl = load_single_field(folder+'bettii.RTHighPriority.crossElevation','f8')
		elevation = load_single_field(folder+'bettii.RTHighPriority.Elevation','f8')
		TelRA = load_single_field(folder+'bettii.RTHighPriority.TelescopeRaDeg','f8')
		TelDec = load_single_field(folder+'bettii.RTHighPriority.TelescopeDecDeg','f8')
		compAz = load_single_field(folder+'bettii.RTHighPriority.computedEstimatorAzimuth','f8')
		compEl = load_single_field(folder+'bettii.RTHighPriority.computedEstimatorElevation','f8')
		TarRA = load_single_field(folder+'bettii.RTHighPriority.targetRA','f8')
		TarDec = load_single_field(folder+'bettii.RTHighPriority.targetDEC','f8')
		gonRA = load_single_field(folder+'bettii.RTHighPriority.GondolaRaDeg','f8')
		gonDec = load_single_field(folder+'bettii.RTHighPriority.GondolaDecDeg','f8')
		SCtrigsts = load_single_field(folder+'bettii.RTHighPriority.StarCameraTriggerStatus','i4')
		print(len(timeRTHighPriority))		
		print(len(TelRA))
		print(len(TelDec))
		print(len(SCtrigsts))
		print(SCtrigsts[2000])
		#f = open('RThighPr4.txt', 'w')
		#for i in range(1, len(compAz)):
		#	if (timeRTHighPriority[i] != timeRTHighPriority[i-1]):
		#		#print(str(timeRTHighPriority[i])+ " " + str(timeRTHighPriority[i-1]))
		#		f.write(str(timeRTHighPriority[i]) + " " + str(TelRA[i]) + " " + str(TelDec[i]) + " " + str(TarRA[i]) + " " + str(TarDec[i]) + " " +str(gonRA[i]) + " " + str(gonDec[i]) + " " + str(SCtrigsts[i]) + "\n")		
		#f.close()
		
		SCsolReq = load_single_field(folder+'bettii.RTHighPriority.SCSolutionsRequested','i4')
		SCsolFnd = load_single_field(folder+'bettii.RTHighPriority.SCSolutionsFound','i4')
		SCloopsS = load_single_field(folder+'bettii.RTHighPriority.SCLoopsSinceLastSolution','i4')
		SCloopsB = load_single_field(folder+'bettii.RTHighPriority.SCLoopsBetweenSCsolutions','i4')
		f = open('RThighSC.txt', 'w')
		for i in range(1, len(SCsolReq)):
			if (timeRTHighPriority[i] != timeRTHighPriority[i-1]):
				#print(str(timeRTHighPriority[i])+ " " + str(timeRTHighPriority[i-1]))
				f.write(str(timeRTHighPriority[i]) + " " + str(SCsolReq[i]) + " " + str(SCsolFnd[i]) +" " +str(SCloopsS[i])+ " " + str(SCloopsB[i]) + "\n")
		f.close()
				
		GPSh = load_single_field(folder+'bettii.GpsReadings.hourUTC','i4')
		GPSm = load_single_field(folder+'bettii.GpsReadings.minuteUTC','i4')
		GPSs = load_single_field(folder+'bettii.GpsReadings.secondUTC','f4')
		GPSlati = load_single_field(folder+'bettii.GpsReadings.latitudeDegrees','f4')
		GPSlongi = load_single_field(folder+'bettii.GpsReadings.longitudeDegrees','f4')
		timeGPS = load_single_field(folder+'bettii.GpsReadings.approximatMmceFrameNumber','i8')
		#f = open('GPSdata2.txt', 'w')
		#print(len(timeGPS))		
		#print(len(GPSs))
		#print(len(GPSm))
		#for i in range(len(GPSs)):	
		#	f.write(str(GPSh[i]) + " " + str(GPSm[i]) + " " + str(GPSs[i]) + " " + str(GPSlati[i]) + " " + str(GPSlongi[i]) + "\n")		
		#f.close()
		
		timeMag = load_single_field(folder+'bettii.Magnetometer.mceFrameNumber','i8')
		timeaccMag = load_single_field(folder+'bettii.Magnetometer.mceFrameNumberWhenMeasured','i8')
		timeLST = load_single_field(folder+'bettii.Magnetometer.TimeLST','f4')
		MagAz = load_single_field(folder+'bettii.Magnetometer.AzimuthDeg','f4')
		#print(len(timeMag))		
		#print(len(timeaccMag))
		#print(len(MagAz))
		#print(MagAz[100000])
		#print(MagAz[900000])
				
		#f = open('Magdata.txt', 'w')
		#for i in range(1, len(timeMag)):	
		#	if (timeMag[i] != timeMag[i-1]):
		#		f.write(str(timeMag[i]) + " " + str(timeaccMag[i]) + " " +str(timeLST[i]) + " " + str(MagAz[i]) + "\n")		
		#f.close()


		timeGG = load_single_field(folder+'bettii.GriffinsGalil.mceFrameNumber','i8')

		TPA = load_single_field(folder+'bettii.GriffinsGalil.TPA','i4')
		TPB = load_single_field(folder+'bettii.GriffinsGalil.TPB','i4')
		TPC = load_single_field(folder+'bettii.GriffinsGalil.TPC','i4')
		GGA = load_single_field(folder+'bettii.GriffinsGalil.griffinAAngleDegrees','f8')
		GGB = load_single_field(folder+'bettii.GriffinsGalil.griffinBAngleDegrees','f8')
		GGC = load_single_field(folder+'bettii.GriffinsGalil.griffinCAngleDegrees','f8')
		#f = open('GGdata.txt', 'w')
		#for i in range(1, len(timeGG)):	
		#	if (timeGG[i] != timeGG[i-1]):
		#		f.write(str(timeGG[i]) + " " + str(GGA[i]) + " " +str(GGB[i]) + " " + str(GGC[i]) + " " + str(TPA[i]) + " " +str(TPB[i]) + " " + str(TPC[i]) +"\n")		
		#f.close()

	
