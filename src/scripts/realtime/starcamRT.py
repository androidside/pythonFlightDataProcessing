'''
Created on 16 may 2017

Real Time script scripts Starcamera solutions in the Gyroscopes reference frame, using three different rotation orders.

@author: Marc Casalprim
'''
from test._mock_backport import inplace
print 'Imports...'
import matplotlib as mpl
from utils.dataset import pd,DataSet,plt,np
from utils.field import Field,getDtypes#,getFieldsContaining,getFieldsRegex
from utils.quat import Quat,sin,cos


if __name__ == '__main__':
    folder = "C:/17-05-16_03_06_46/"
    folder = "\\\\GS66-WHITE\\LocalAuroraArchive\\17-05-17_00_36_34\\"
    Field.DTYPES=getDtypes(folder)

    
    fieldsList=[]
     
    fieldsList.append(Field('bettii.RTLowPriority.RawStarcameraDecDeg',label='dec_sc'))
    fieldsList.append(Field('bettii.RTLowPriority.RawStarcameraRollDeg',label='roll_sc'))
    fieldsList.append(Field('bettii.RTLowPriority.RawStarcameraRaDeg',label='ra_sc'))  
    mpl.style.use('classic') 
    mpl.rcParams['toolbar'] = 'None'
    initial_time=None #in frame number
    final_time = None #in frame number
    
    ds = DataSet(folder,min=initial_time,max=final_time,rpeaks=True)
    
    dYaw = -0.367
    dPitch = 44.9828
    dRoll = -0.79
    qdYaw = Quat((dYaw,0,0)); #quat = Quat((ra,dec,roll)) in degrees
    qdPitch = Quat((0.0,sin(dPitch*np.pi/180./2.0),0.0,cos(dPitch*np.pi/180./2.0))) #quat = Quat((ra,dec,roll)) in degreesq
    qdRoll = Quat((0,0,dRoll)) #quat = Quat((ra,dec,roll)) in degrees
    qStarcam2Gyros_old=qdYaw*qdPitch*qdRoll
    qStarcam2Gyros_mid=qdPitch*qdYaw*qdRoll
    qStarcam2Gyros_new=qdRoll*qdPitch*qdYaw
    
    
    fig=[]
    ax=[]
    fig.append(plt.figure(1)) 
    ax.append(plt.subplot(311))
    ax.append(plt.subplot(312))
    ax.append(plt.subplot(313))
    
    plt.ion()
    
    lastNValues=48000
    nValues=12000
    for i in range(10000):
        
        #print 'Reading bytes from '+str(nValues*i)+' to '+str(nValues*(i+1))    
        ds.readListFields(fieldsList, nValues=nValues,verbose=False)
        data=ds.df.dropna().loc[max(ds.df.index)-lastNValues:,:]
        #data=ds.df.dropna().tail(lastNValues) #we get the last values of the dataframe
        
        d={
            'ra_old': [],
            'dec_old': [],
            'roll_old': [],
            'ra_mid': [],
            'dec_mid': [],
            'roll_mid': [],
            'ra_new': [],
            'dec_new': [],
            'roll_new': []}
        
        for mceFN in data.index:
            qI2Starcam=Quat((data.loc[mceFN][['ra_sc','dec_sc','roll_sc']]))
            #data.index=data.index/ds.freq #index in seconds
            
            q_old=qStarcam2Gyros_old*qI2Starcam
            q_mid=qStarcam2Gyros_mid*qI2Starcam
            q_new=qStarcam2Gyros_new*qI2Starcam
            
            d['ra_old'].append(q_old.ra)
            d['dec_old'].append(q_old.dec)
            d['roll_old'].append(q_old.roll)
            
            d['ra_mid'].append(q_mid.ra)
            d['dec_mid'].append(q_mid.dec)
            d['roll_mid'].append(q_mid.roll)
            
            d['ra_new'].append(q_new.ra)
            d['dec_new'].append(q_new.dec)
            d['roll_new'].append(q_new.roll)

        qs = pd.DataFrame(d,index = data.index)

        for axis in ax: axis.clear()
        
        qs[['dec_old','dec_mid','dec_new']].plot(ax=ax[0])
        qs[['ra_old','ra_mid','ra_new']].plot(ax=ax[1])
        qs[['roll_old','roll_mid','roll_new']].plot(ax=ax[2])
        
        ax[2].set_xlabel('Time (frames)')
         
        ax[0].set_ylabel('DEC (deg)')
        ax[1].set_ylabel('RA (deg)')
        ax[2].set_ylabel('ROLL (deg)')      
        
        plt.tight_layout()
        plt.pause(0.01)
        del ds.df
        ds.df=data #we delete some memory
    plt.show()

    