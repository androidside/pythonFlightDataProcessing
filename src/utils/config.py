'''
Created on Sep 12, 2017

@author: Marc Casalprim
'''
import os
import matplotlib as mpl
mpl.use('Qt4Agg') #change backend
from matplotlib.style import use
import matplotlib.pyplot as plt

#Plotting parameters
use('seaborn-colorblind')

mpl.rcParams['axes.grid']=True
plt.rc('font', family='serif')

mpl.rcParams['date.autoformatter.hour']  = '%H:%M'
mpl.rcParams['date.autoformatter.minute']  = '%H:%M:%S'

M=100 #downsampling factor

save_folder='C:/Users/bettii/flightData/'
img_folder=save_folder+'plots/' #folders where the figures will be stored by default
if not os.path.exists(save_folder):
    os.makedirs(save_folder)
if not os.path.exists(img_folder):
    os.makedirs(img_folder)

#flight data folders
root_folder='F:/GondolaFlightArchive/' #disks data
subdirs=next(os.walk(root_folder))[1]
flightDisksFolders=[root_folder+subdir+'/' for subdir in subdirs]

flightTelemetryFolders=[]
flightTelemetryFolders.append('F:/LocalBettiiArchive/17-06-08_17_07_45-/') #telemetry data
flightTelemetryFolders.append('F:/LocalBettiiArchive/17-06-08_20_43_41-/')
flightTelemetryFolders.append('F:/LocalBettiiArchive/17-06-08_20_54_26-/')
flightTelemetryFolders.append('F:/LocalBettiiArchive/17-06-08_22_09_44-/')
flightTelemetryFolders.append('F:/LocalBettiiArchive/17-06-08_22_19_34-/')
flightTelemetryFolders.append('F:/LocalBettiiArchive/17-06-09_00_27_01-/')
flightTelemetryFolders.append('F:/LocalBettiiArchive/17-06-09_01_54_43-/')
flightTelemetryFolders.append('F:/LocalBettiiArchive/17-06-09_02_12_33-/')
flightTelemetryFolders.append('F:/LocalBettiiArchive/17-06-09_02_40_53-/')
flightTelemetryFolders.append('F:/LocalBettiiArchive/17-06-09_02_59_03-/')
flightTelemetryFolders.append('F:/LocalBettiiArchive/17-06-09_04_11_03-/')

#==========================EMPTY Archives===================================
#  flightTelemetryFolders.append('F:/LocalBettiiArchive/17-06-09_04_16_13-/')
#  flightTelemetryFolders.append('F:/LocalBettiiArchive/17-06-09_04_19_53-/')
#  flightTelemetryFolders.append('F:/LocalBettiiArchive/17-06-09_04_20_34-/')
# flightTelemetryFolders.append('F:/LocalBettiiArchive/17-06-09_04_26_51-/')
# flightTelemetryFolders.append('F:/LocalBettiiArchive/17-06-09_04_28_38-/')
# flightTelemetryFolders.append('F:/LocalBettiiArchive/17-06-09_04_41_34-/')
#===========================================================================
flightTelemetryFolders.append('F:/LocalBettiiArchive/17-06-09_06_29_36-/')
