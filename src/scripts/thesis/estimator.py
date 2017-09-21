'''
Created on 3 june 2017

Main script

@author: Marc Casalprim
'''
print 'Imports...'
from utils.estimator import readAndSave,openPickles
from estimators.estimators import Estimator6
from utils.dataset import plt,pd,np,plotQuaternions,plotCovs,plotInnovations
from utils.config import save_folder,img_folder


if __name__ == '__main__':
    folder='F:/GondolaFlightArchive/17-06-09_07_09_25/'
    
    
    read=True #read again the files?
    estimated=True
    
    ti=20389100
    tf=None#28700000
    if read: 
        gyros,sc,est=readAndSave(folder,initial_time=ti,final_time=None)
    else:
        gyros,sc,est=openPickles(folder,ests=True)
    

    kal3=Estimator6(gyros,sc)
    kal3.est=est
    
    print "Plotting..."
    
   
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
    
    df=pd.merge(kal3.est,sc,how='outer',left_index=True,right_index=True)
    print 'Dataframe shape:', df.shape
    styles=['b.',{'color':'g','linestyle':'None','marker':'*','ms':10}]
    f=plotQuaternions(df[['qest','qI2G']],styles=styles,legend=True,labels=['Estimator','Starcamera'], time_label=time_label)
    f.savefig(save_folder+"estimator.png")
     
    Ps=pd.DataFrame()
    Ps['Kalman 3']=kal3.est['P']
    f=plotCovs(Ps,styles=['b','g','r'],legend=True, time_label=time_label,function=lambda x: np.sqrt(abs(x))/4.848e-6,rotate=True,ylabels=[r'$\sigma_{RA}$ (arcsec)',r'$\sigma_{DEC}$ (arcsec)',r'$\sigma_{ROLL}$ (arcsec)'])
    f.savefig(save_folder+"covs_estimator.png")
    
    
    ests=[kal3.est]
    labels=['Kalman 3']
    styles=['b','r','g']
    fig=plotInnovations(ests,sc, time_label=time_label, labels=labels, styles=styles, legend=True)
    fig.savefig(save_folder+"errs.png")
    
    print "Show"
    plt.show()