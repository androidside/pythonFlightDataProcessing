'''
Created on 21 May 2017

Real Time scripts of the Starcamera solutions and Estimated attitudes in the Gyroscopes reference frame.

@author: Marc Casalprim
'''
print 'Imports...'
import matplotlib as mpl
from matplotlib.style import use
from utils.dataset import pd,DataSet,plt,np
from utils.field import Field,getDtypes#,getFieldsContaining,getFieldsRegex
from utils.quat import Quat,sin,cos


if __name__ == '__main__':
    folder = "C:/17-05-16_03_06_46/"
    folder = "\\\\GS66-WHITE\\LocalAuroraArchive\\17-05-21_01_42_03\\"
    Field.DTYPES=getDtypes(folder)

    
    fieldsList=[]
    fieldsList.append(Field('bettii.RTLowPriority.qr'))
    fieldsList.append(Field('bettii.RTLowPriority.qi'))
    fieldsList.append(Field('bettii.RTLowPriority.qj'))
    fieldsList.append(Field('bettii.RTLowPriority.qk'))
    fieldsList.append(Field('bettii.RTLowPriority.RawStarcameraQuaternionFXPqi',label='qi_sc'))
    fieldsList.append(Field('bettii.RTLowPriority.RawStarcameraQuaternionFXPqj',label='qj_sc'))
    fieldsList.append(Field('bettii.RTLowPriority.RawStarcameraQuaternionFXPqk',label='qk_sc'))
    fieldsList.append(Field('bettii.RTLowPriority.RawStarcameraQuaternionFXPqr',label='qr_sc')) 

    use('classic') 
    mpl.rcParams['toolbar'] = 'None'
    initial_time=None #in frame number
    final_time = None #in frame number
    
    ds = DataSet(folder,fieldsList=fieldsList,min=initial_time,max=final_time,nValues=480000,rpeaks=False)

    
    fig=[]
    ax=[]
    fig.append(plt.figure(1)) 
    ax.append(plt.subplot(311))
    ax.append(plt.subplot(312))
    ax.append(plt.subplot(313))
    
    plt.ion()
    
    lastNValues=480000
    nValues=1200
    for i in range(10000):
        
        #print 'Reading bytes from '+str(nValues*i)+' to '+str(nValues*(i+1))    
        ds.readListFields(fieldsList, nValues=nValues,verbose=False,rpeaks=False)
        data=ds.df.loc[max(ds.df.index)-lastNValues:,:].interpolate('values')
        #data=ds.df.dropna().tail(lastNValues) #we get the last values of the dataframe

        d={
            'ra_sc': [],
            'dec_sc': [],
            'roll_sc': [],
            'ra_est': [],
            'dec_est': [],
            'roll_est': []}
        for mceFN in data.index:
            q_est=Quat((data.loc[mceFN][['qi','qj','qk','qr']]))
            q_sc=Quat((data.loc[mceFN][['qi_sc','qj_sc','qk_sc','qr_sc']]))
            
            d['ra_est'].append(q_est.ra)
            d['dec_est'].append(q_est.dec)
            d['roll_est'].append(q_est.roll)
            
            d['ra_sc'].append(q_sc.ra)
            d['dec_sc'].append(q_sc.dec)
            d['roll_sc'].append(q_sc.roll)
            

        qs = pd.DataFrame(d,index = data.index)

        for axis in ax: axis.clear()
  
        #scripts elevation and crossElevation
        if not qs.empty:
            qs[['dec_sc','dec_est']].plot(ax=ax[0])
            qs[['ra_sc','ra_est']].plot(ax=ax[1])
            qs[['roll_sc','roll_est']].plot(ax=ax[2])
        else:
            print ds.df.shape
            print data.shape
        
        ax[2].set_xlabel('Time (frames)')
         
        ax[0].set_ylabel('DEC (deg)')
        ax[1].set_ylabel('RA (deg)')
        ax[2].set_ylabel('ROLL (deg)')      
        
        plt.tight_layout()
        plt.pause(0.01)
        del ds.df
        ds.df=data #we delete some memory
    plt.show()

    