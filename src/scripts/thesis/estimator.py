'''
Created on 3 june 2017

Main script

@author: Marc Casalprim
'''
print 'Imports...'

from timeit import default_timer as timer

import numpy as np

from matplotlib.style import use
from matplotlib import rcParams

from utils.estimator import readAndSave,openPickles
from estimators.estimators import Estimator3,Estimator6,Estimator15,plt,pd
from utils.dataset import plotQuaternions,plotColumns,plotCovs,plotInnovations


if __name__ == '__main__':
    folder='F:/GondolaFlightArchive/17-06-09_07_09_25/'
    save_folder='C:/Users/bettii/thesis/plots/postflight/'
    
    read=False #read again the files?
    estimated=True
    
    ti=20389100
    tf=None#28700000
    if read: 
        gyros,sc,quats=readAndSave(folder,initial_time=ti,final_time=None)
    else:
        gyros,sc,quats=openPickles(folder,quats=False)
    

    kal3=Estimator3(gyros,sc)

    if not estimated:
        dt=0.01
        Qd=(4.848e-6*0.3)**2*dt*np.eye(3) #dtheta

        print "Estimating 3 states Kalman filter..."
        kal3.estimate(Qd=Qd[:3,:3],ts=ti,te=tf,progress=True)
        print "Saving..."
        kal3.est.to_pickle(save_folder+Estimator3.EST_FILENAME)
    else:
        print "Opening..."
        kal3.est=pd.read_pickle(save_folder+Estimator3.EST_FILENAME)
    
    print "Plotting..."
    use('seaborn-bright')
    rcParams['axes.grid']=True
    plt.rc('font', family='serif')
    
   
    kal3.est=kal3.est.iloc[:-1]
    
    time_label='Time (frame number)'
    if False: #convert from frame number to Palestine time
        time_label='Palestine Time'
        text=folder.split('/')[-2]
        ftime_str=text[0:8]+' '+text[9:17].replace('_',':') #foldertime
        ftime=pd.to_datetime(ftime_str,yearfirst=True)-pd.Timedelta(hours=5) #Palestine
        
        i0=19899228 #frame number referring to the start of the folder
        
        index=(kal3.est.index-i0)/400. #time in seconds
        index=pd.to_timedelta(index,unit='s')
        time=ftime+index
        kal3.est.index=time
        
        index=(sc.index-i0)/400. #time in seconds
        index=pd.to_timedelta(index,unit='s')
        time=ftime+index
        sc.index=time
    
    #===========================================================================
    # df=pd.merge(kal3.est,sc,how='outer',left_index=True,right_index=True)
    # print 'Dataframe shape:', df.shape
    # styles=['b.',{'color':'g','linestyle':'None','marker':'*','ms':10}]
    # f=plotQuaternions(df[['qest','qI2G']],styles=styles,legend=True,labels=['Estimator','Starcamera'], time_label=time_label)
    # f.savefig(save_folder+"estimator_pc_3_opt.png")
    # 
    # Ps=pd.DataFrame()
    # Ps['Kalman 3']=kal3.est['P']
    # f=plotCovs(Ps,styles=['b','g','r'],legend=True, time_label=time_label,function=lambda x: np.sqrt(x)/4.848e-6,rotate=True,ylabels=[r'$\sigma_{RA}$ (arcsec)',r'$\sigma_{DEC}$ (arcsec)',r'$\sigma_{ROLL}$ (arcsec)'])
    # f.savefig(save_folder+"covs_pc.png")
    #===========================================================================
    
    
    ests=[kal3.est]
    labels=['Kalman 3']
    styles=['b','r','g']
    fig=plotInnovations(ests,sc, time_label=time_label, labels=labels, styles=styles, legend=True)
    fig.savefig(save_folder+"errs.png")
    
    print "Show"
    plt.show()