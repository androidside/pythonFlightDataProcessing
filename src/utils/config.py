'''
Module that configures the :mod:`matplotlib` module.
It also contains some common variables that are useful for the scripts:

    * ``save_folder`` folder where the txt and pickle files can be saved
    * ``img_folder`` folder where the figures can be saved    
    * ``flightDisksFolders`` List of Aurora archive folders (full path) where there is the SSDs information.
    * ``flightTelemetryFolders`` List of Aurora archive folders (full path) where there is the information from the telemetry (Rubble)."

'''
import os
import matplotlib as mpl
mpl.use('Qt4Agg') #change matplotlib backend
from matplotlib.style import use
import matplotlib.pyplot as plt

#Plotting parameters
use('seaborn-bright') #style

mpl.rcParams['axes.grid']=True
#plt.rc('font', family='serif') #Serif font, more Latex-like
mpl.rcParams['date.autoformatter.hour']  = '%H:%M' #format of the date axes when the autoformatter decides it should be in hour precision
#mpl.rcParams['date.autoformatter.hour']  = '%H:%M' 
mpl.rcParams['date.autoformatter.minute']  = '%H:%M:%S' #format of the date axes when the autoformatter decides it should be in minute precision

#Useful variables
save_folder='C:/Users/bettii/flightData/' #folders where the files will be stored by default
img_folder=save_folder+'plots/' #folders where the figures will be stored by default
#check if the folders exist. If not, make them.
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
