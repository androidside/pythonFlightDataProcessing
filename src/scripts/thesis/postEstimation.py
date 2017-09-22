'''
Created on 3 june 2017

Main script

@author: Marc Casalprim
'''
print 'Imports...'
from utils.config import os
from utils.estimator import readAndSave,openPickles
from estimators.estimators import Estimator3,Estimator6,Estimator15,pd
from utils.dataset import plt,np,plotQuaternions,plotColumns,plotCovs,plotInnovations


if __name__ == '__main__':
    folder='F:/GondolaFlightArchive/17-06-09_07_09_25/'
    ti=20389100
    tf=None#28700000
    #===========================================================================
    # folder='F:/GondolaFlightArchive/17-06-09_01_51_04/'
    # ti=18671200
    # tf=18884463
    #===========================================================================
    save_folder=folder
    img_folder=save_folder+'postflight/'
    if not os.path.exists(img_folder):
        os.makedirs(img_folder)
    
    read=True
    estimated=False
    
    use3=False
    use6=True
    use15=False
    
     
    if read: 
        gyros,sc,quats=readAndSave(folder,initial_time=ti,final_time=tf)
    else:
        gyros,sc,quats=openPickles(folder,openEst=False)
    
    #sc.index=sc.triggers.values
    if use3: kal3=Estimator3(gyros,sc)
    if use6: kalOrg=Estimator6(gyros,sc)
    if use15: kal15=Estimator15(gyros,sc)

    if not estimated:
        
        Qd=np.eye(15)
        dt=0.01
        Qd[:3,:3]=(4.848e-6*3e-2)**2*dt*np.eye(3) #dtheta
        Qd[3:6,3:6]=8e-7**2*dt*np.eye(3) #k
        Qd[6:12,6:12]=9e-6**2*dt*np.eye(6) #m
        Qd[12:15,12:15]=(4.848e-6*1e-4)**2*dt*np.eye(3) #bias

        
        
        print "Estimating 15 states Kalman filter..."
        if use15: kal15.estimate(Qd=Qd,ts=ti,te=tf,progress=True)
        Qd[3:6,3:6]=Qd[12:15,12:15] #copying bias part
        print "Estimating 6 states Kalman filter..."
        if use6: kalOrg.estimate(Qd=Qd[:6,:6],ts=ti,te=tf,progress=True)
        print "Estimating 3 states Kalman filter..."
        if use3: kal3.estimate(Qd=Qd[:3,:3],ts=ti,te=tf,progress=True)
        print "Saving..."
        if use3: kal3.est.to_pickle(save_folder+Estimator3.EST_FILENAME)
        if use6: kalOrg.est.to_pickle(save_folder+Estimator6.EST_FILENAME)
        if use15: kal15.est.to_pickle(save_folder+Estimator15.EST_FILENAME)
    else:
        print "Opening..."
        if use15: kal15.est=pd.read_pickle(save_folder+Estimator15.EST_FILENAME)
        if use3: kal3.est=pd.read_pickle(save_folder+Estimator3.EST_FILENAME)
        if use6: kalOrg.est=pd.read_pickle(save_folder+Estimator6.EST_FILENAME)
    
    print "Plotting..."
    

   
    if use6: kalOrg.est=kalOrg.est.iloc[:-1]
    if use3: kal3.est=kal3.est.iloc[:-1]
    if use15: kal15.est=kal15.est.iloc[:-1]
    
    time_label='Time (frame number)'
    if False: #convert from frame number to Palestine time
        time_label='Palestine Time'
        text=folder.split('/')[-2]
        ftime_str=text[0:8]+' '+text[9:17].replace('_',':') #foldertime
        ftime=pd.to_datetime(ftime_str,yearfirst=True)-pd.Timedelta(hours=5) #Palestine
        
        i0=19899228 #frame number referring to the start of the folder
        if use15: 
            index=(kal15.est.index-i0)/400. #time in seconds
            index=pd.to_timedelta(index,unit='s')
            time=ftime+index
            kal15.est.index=time
        if use6: 
            index=(kalOrg.est.index-i0)/400. #time in seconds
            index=pd.to_timedelta(index,unit='s')
            time=ftime+index
            kalOrg.est.index=time
        if use3: 
            index=(kal3.est.index-i0)/400. #time in seconds
            index=pd.to_timedelta(index,unit='s')
            time=ftime+index
            kal3.est.index=time
        
        index=(sc.index-i0)/400. #time in seconds
        index=pd.to_timedelta(index,unit='s')
        time=ftime+index
        sc.index=time
    styles=['b.',{'color':'g','linestyle':'None','marker':'*','ms':10}]
    if use15: 
        x=kal15.est.iloc[-1]
        m1,m2,m3,m4,m5,m6=x.m
        k1,k2,k3=x.k
        M=[[1-k1,m1,m2],[m3,1-k2,m4],[m5,m6,1-k3]]
        print np.matrix(M)
        df=pd.merge(kal15.est,sc,how='outer',left_index=True,right_index=True)
        print 'K15 Dataframe shape:', df.shape
        f=plotQuaternions(df[['qest','qI2G']],styles=styles,legend=True,labels=['Estimator','Starcamera'], time_label=time_label)
        f.savefig(img_folder+"estimator_pc_15.png")
        f=plotColumns(kal15.est[['biasX','biasY','biasZ']].apply(lambda x: x/4.848e-6), xlabel=time_label, units='(arcsec/s)',ylabels=[r'$bias_X$',r'$bias_Y$',r'$bias_Z$'])
        f.savefig(img_folder+"biases_pc_15.png") 
    if use6: 
        df=pd.merge(kalOrg.est,sc,how='outer',left_index=True,right_index=True)
        print 'K6 Dataframe shape:', df.shape
        f=plotQuaternions(df[['qest','qI2G']],styles=styles,legend=True,labels=['Estimator','Starcamera'], time_label=time_label)
        f.savefig(img_folder+"estimator_pc.png")
        f=plotColumns(kalOrg.est[['biasX','biasY','biasZ']].apply(lambda x: x/4.848e-6), xlabel=time_label, units='(arcsec/s)',ylabels=[r'$bias_X$',r'$bias_Y$',r'$bias_Z$'])
        f.savefig(img_folder+"biases_pc.png")  
    if use3: 
        df=pd.merge(kal3.est,sc,how='outer',left_index=True,right_index=True)
        print 'K3 Dataframe shape:', df.shape       
        f=plotQuaternions(df[['qest','qI2G']],styles=styles,legend=True,labels=['Estimator','Starcamera'], time_label=time_label)
        f.savefig(img_folder+"estimator_pc_3.png")
    
    Ps=pd.DataFrame()
    if use6: Ps['Kalman 6']=kalOrg.est['P']
    if use3: Ps=pd.merge(Ps,kal3.est[['P']],how='outer',left_index=True,right_index=True).dropna().rename(columns={'P':'Kalman 3'})
    if use15: Ps=pd.merge(Ps,kal15.est[['P']],how='outer',left_index=True,right_index=True).dropna().rename(columns={'P':'Kalman 15'})
    f=plotCovs(Ps,styles=['b','g','r'],legend=True, time_label=time_label,function=lambda x: np.sqrt(x)/4.848e-6,rotate=True,ylabels=[r'$\sigma_{RA}$ (arcsec)',r'$\sigma_{DEC}$ (arcsec)',r'$\sigma_{ROLL}$ (arcsec)'])
    f.savefig(img_folder+"covs_pc.png")
    
    ests=[]
    labels=[]
    if use3: 
        ests.append(kal3.est)
        labels.append('Kalman 3')
    if use6: 
        ests.append(kalOrg.est)
        labels.append('Kalman 6')
    if use15: 
        ests.append(kal15.est)
        labels.append('Kalman 15')

    styles=[{'color':'b','marker':'s','ms':3},{'color':'r','marker':'^','ms':3},{'color':'g','marker':'o','ms':3}]
    fig=plotInnovations(ests,sc, conv=lambda x: (x)*3600, units='arcsec',labels=labels, styles=styles, legend=True, sync=False)
    fig.savefig(img_folder+"errs.png")
    print "Show"
    plt.show()