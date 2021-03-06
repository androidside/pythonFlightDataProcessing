'''
Created on 3 june 2017

Main script

@author: Marc Casalprim
'''
print 'Imports...'

import numpy as np

from utils.config import plt
from utils.estimator import readAndSave,openPickles
from estimators.estimators import Estimator15,Estimator6,pd


if __name__ == '__main__':
    folder="F:/GondolaFlightArchive/17-06-09_01_51_04/"
    folder = 'A:/BettiiDataAnalysis/gondolaArchive/flightArchive/all/17-06-09_01_51_04/'      #disks data
    save_folder=folder
    
    read=False
    estimated=True
    
    if read: 
        gyros,sc,quats=readAndSave(folder)
    else:
        gyros,sc,quats=openPickles(folder,openEst=True)
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
    
    kal15.plot()
    kalOrg.plot()
    
    a=1  
    plt.show()