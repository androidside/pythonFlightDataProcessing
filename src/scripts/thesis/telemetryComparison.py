'''
Created on 3 june 2017

Main script

@author: Marc Casalprim
'''
from bokeh.io import save
print 'Imports...'

import numpy as np

from matplotlib.style import use
from matplotlib import rcParams

from utils.estimator import readAndSave,openPickles
from estimators.estimators import Estimator15,Estimator6,plt,pd


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
    
    save_folder=folder
    read=True
    estimated=False
    
    if read: 
        gyros,sc,quats=readAndSave(folder)
    else:
        gyros,sc,quats=openPickles(folder,quats=True)
    kal15=Estimator15(gyros,sc)
    kalOrg=Estimator6(gyros,sc)
    if not estimated:
        print "Estimating 15 states Kalman filter..."
        ts=17369088
        Qd=0.003*np.eye(15)
        kal15.estimate(Qd=Qd,ts=ts,te=ts+600*400,progress=True)

        print "Estimating 6 states Kalman filter..."
        Qd=0.003*np.eye(6)
        kalOrg.estimate(Qd=Qd,ts=ts,te=ts+600*400,progress=True)
        print "Saving..."
        kal15.est.to_pickle(save_folder+Estimator15.EST_FILENAME)
        kalOrg.est.to_pickle(save_folder+Estimator6.EST_FILENAME)
    else:
        print "Opening.."
        kal15.est=pd.read_pickle(save_folder+Estimator15.EST_FILENAME)
        kalOrg.est=pd.read_pickle(save_folder+Estimator6.EST_FILENAME)
    print "Plotting..."
    use('classic')
    rcParams['axes.grid']=True
    
    kal15.plot()
    kalOrg.plot()
    
    a=1  
    plt.show()