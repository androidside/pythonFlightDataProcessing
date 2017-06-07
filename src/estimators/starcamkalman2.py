'''
Created on 28 abr. 2017

Main script

@author: Marc Casalprim
'''
print 'Imports...'
import matplotlib as mpl
from matplotlib.style import use
from utils.dataset import pd,DataSet,plt,np
from utils.field import Field,getDtypes#,getFieldsContaining,getFieldsRegex
from utils.quat import Quat,sin,cos


if __name__ == '__main__':
    folder = "C:/17-05-19_22_56_20/"
    #folder = "\\\\GS66-WHITE\\LocalAuroraArchive\\17-05-21_01_42_03\\"
    print "Reading formats..."
    Field.DTYPES=getDtypes(folder)

    
    fieldsList=[]
    fieldsList.append(Field('bettii.RTLowPriority.RawStarcameraDecDeg',label='dec_sc'))
    fieldsList.append(Field('bettii.RTLowPriority.RawStarcameraRollDeg',label='roll_sc'))
    fieldsList.append(Field('bettii.RTLowPriority.RawStarcameraRaDeg',label='ra_sc'))
    fieldsList.append(Field('bettii.RTLowPriority.qr'))
    fieldsList.append(Field('bettii.RTLowPriority.qi'))
    fieldsList.append(Field('bettii.RTLowPriority.qj'))
    fieldsList.append(Field('bettii.RTLowPriority.qk'))
    fieldsList.append(Field('bettii.RTLowPriority.RawStarcameraQuaternionFXPqi',label='qi_sc'))
    fieldsList.append(Field('bettii.RTLowPriority.RawStarcameraQuaternionFXPqj',label='qj_sc'))
    fieldsList.append(Field('bettii.RTLowPriority.RawStarcameraQuaternionFXPqk',label='qk_sc'))
    fieldsList.append(Field('bettii.RTLowPriority.RawStarcameraQuaternionFXPqr',label='qr_sc')) 

    use('classic') 
    #mpl.rcParams['toolbar'] = 'None'
    initial_time=10000 #in frame number
    final_time = None #in frame number
    
    ds = DataSet(folder,fieldsList=fieldsList,min=initial_time,max=final_time,nValues=10000,rpeaks=False,verbose=True)
    
    dYaw=-0.367
    dPitch=44.9828
    dRoll=-0.79
     
    qdYaw = Quat((dYaw,0,0)); #quat = Quat((ra,dec,roll)) in degrees
    qdPitch = Quat((0.0,sin(dPitch*np.pi/180./2.0),0.0,cos(dPitch*np.pi/180./2.0))) #quat = Quat((ra,dec,roll)) in degrees
    qdRoll = Quat((0,0,dRoll)) #quat = Quat((ra,dec,roll)) in degrees
    
    #qStarcam2Gyros_new =  Quat((dYaw,-dPitch,dRoll))

    qStarcam2Gyros =  qdYaw*qdPitch*qdRoll
    
    fig=[]
    ax=[]
    fig.append(plt.figure(1)) 
    ax.append(plt.subplot(311))
    ax.append(plt.subplot(312))
    ax.append(plt.subplot(313))
    fig.append(plt.figure(2)) 
    ax.append(plt.subplot(311))
    ax.append(plt.subplot(312))
    ax.append(plt.subplot(313))
    
    plt.ion()
    
    lastNValues=480000
    nValues=1200
    #data=ds.df.dropna().tail(lastNValues) #we get the last values of the dataframe
    data=ds.df#.interpolate('values')
    d={
        'ra_sc': [],
        'dec_sc': [],
        'roll_sc': [],
        'ra_est': [],
        'dec_est': [],
        'roll_est': [],
        'ra_sc_SC': [],
        'dec_sc_SC': [],
        'roll_sc_SC': [],
        'ra_est_SC': [],
        'dec_est_SC': [],
        'roll_est_SC': []}
    for mceFN in data.index:
        q_est=Quat((data.loc[mceFN][['qi','qj','qk','qr']]))
        q_sc=Quat((data.loc[mceFN][['qi_sc','qj_sc','qk_sc','qr_sc']]))
        
        d['ra_est'].append(q_est.ra)
        d['dec_est'].append(q_est.dec)
        d['roll_est'].append(q_est.roll)
        
        d['ra_sc'].append(q_sc.ra)
        d['dec_sc'].append(q_sc.dec)
        d['roll_sc'].append(q_sc.roll)
        
        q_est_sc=qStarcam2Gyros.inv()*q_est
        q_sc_sc=qStarcam2Gyros.inv()*q_sc
        
        d['ra_est_SC'].append(q_est_sc.ra)
        d['dec_est_SC'].append(q_est_sc.dec)
        d['roll_est_SC'].append(q_est_sc.roll)
        
        d['ra_sc_SC'].append(q_sc_sc.ra)
        d['dec_sc_SC'].append(q_sc_sc.dec)
        d['roll_sc_SC'].append(q_sc_sc.roll)
        
    
    qs = pd.DataFrame(d,index = data.index)
    
    for axis in ax: axis.clear()
    
    #plotting elevation and crossElevation
    if not qs.empty:
        #=======================================================================
        # qs[['dec_sc','dec_est','dec_sc_SC','dec_est_SC']].plot(ax=ax[0])
        # qs[['ra_sc','ra_est','ra_sc_SC','ra_est_SC']].plot(ax=ax[1])
        # qs[['roll_sc','roll_est','roll_sc_SC','roll_est_SC']].plot(ax=ax[2])
        #=======================================================================
        qs[['dec_sc','dec_est']].plot(ax=ax[0])
        qs[['ra_sc','ra_est']].plot(ax=ax[1])
        qs[['roll_sc','roll_est']].plot(ax=ax[2])
        qs[['dec_sc_SC','dec_est_SC']].plot(ax=ax[3])
        qs[['ra_sc_SC','ra_est_SC']].plot(ax=ax[4])
        qs[['roll_sc_SC','roll_est_SC']].plot(ax=ax[5])
    else:
        print ds.df.shape
        print data.shape
    
    ax[2].set_xlabel('Time (frames)')
     
    ax[0].set_ylabel('DEC (deg)')
    ax[1].set_ylabel('RA (deg)')
    ax[2].set_ylabel('ROLL (deg)')
    
    ax[2].set_xlabel('Time (frames)')
     
    ax[0].set_ylabel('DEC (deg)')
    ax[1].set_ylabel('RA (deg)')
    ax[2].set_ylabel('ROLL (deg)')   
    
    plt.tight_layout()
    plt.pause(0.01)
    del ds.df
    ds.df=data #we delete some memory
    plt.ioff()
    plt.show()
    a=1

    