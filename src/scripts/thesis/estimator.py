'''
Created on 23 May 2017

Plotting of:
Estimator-SC errors in SC ref. frame
Estimator-SC errors in Gondola ref. frame
Biases


@author: Marc Casalprim
'''
print 'Imports...'
import matplotlib as mpl
import pandas as pd
from matplotlib.style import use
from utils.dataset import DataSet,plt,genQuaternions,plotQuaternions,\
    filterQuats,extractGyrosAndStarcam,filterArray
from utils.field import Field#,getFieldsContaining,getFieldsRegex


if __name__ == '__main__':
    folder='F:/GondolaFlightArchive/17-06-09_01_51_04/'
    folder='F:/GondolaFlightArchive/17-06-09_07_09_25/'
    
    text=folder.split('/')[-2]
    ftime_str=text[0:8]+' '+text[9:17].replace('_',':') #foldertime
    ftime=pd.to_datetime(ftime_str,yearfirst=True)
    
    est_filename=folder+'est.pkl'
    sc_filename=folder+'sc.pkl'
    gyros_filename=folder+'gyr.pkl'
    org_filename=folder+'org.pkl'
    
    read=False
    
    SCLabels=['qI2S','qI2G']
    if read:
        fieldsList=[]
         
        fieldsList.append(Field('bettii.RTLowPriority.RawStarcameraQuaternionFXPqi',label='qi_sc'))
        fieldsList.append(Field('bettii.RTLowPriority.RawStarcameraQuaternionFXPqj',label='qj_sc'))
        fieldsList.append(Field('bettii.RTLowPriority.RawStarcameraQuaternionFXPqk',label='qk_sc'))
        fieldsList.append(Field('bettii.RTLowPriority.RawStarcameraQuaternionFXPqr',label='qr_sc'))
        fieldsList.append(Field('bettii.RTLowPriority.RawStarcameraDecDeg',label='dec_sc'))
        fieldsList.append(Field('bettii.RTLowPriority.RawStarcameraRaDeg',label='ra_sc'))
        fieldsList.append(Field('bettii.RTLowPriority.RawStarcameraRollDeg',label='roll_sc'))
        fieldsList.append(Field('bettii.RTLowPriority.RawStarcameraDecError',label='dec_err'))
        fieldsList.append(Field('bettii.RTLowPriority.RawStarcameraRaError',label='ra_err'))
        fieldsList.append(Field('bettii.RTLowPriority.RawStarcameraRollError',label='roll_err'))
        fieldsList.append(Field('bettii.RTLowPriority.qr'))
        fieldsList.append(Field('bettii.RTLowPriority.qi'))
        fieldsList.append(Field('bettii.RTLowPriority.qj'))
        fieldsList.append(Field('bettii.RTLowPriority.qk'))
        fieldsList.append(Field('bettii.RTLowPriority.RawStarcameraMceFrameNumberWhenSCTriggered',label='triggers'))
        
        fieldsList.append(Field('bettii.RTHighPriority.estimatedBiasXarcsec',label='biasX'))
        fieldsList.append(Field('bettii.RTHighPriority.estimatedBiasYarcsec',label='biasY'))
        fieldsList.append(Field('bettii.RTHighPriority.estimatedBiasZarcsec',label='biasZ'))
        
        fieldsList.append(Field('bettii.GyroReadings.angularVelocityX',label='gyroX',dtype='i4',conversion=-0.0006304))
        fieldsList.append(Field('bettii.GyroReadings.angularVelocityY',label='gyroY',dtype='i4',conversion=-0.0006437))
        fieldsList.append(Field('bettii.GyroReadings.angularVelocityZ',label='gyroZ',dtype='i4',conversion=0.0006324))
    
        ti=19061609
        tf=None#22880065
        ds = DataSet(folder,fieldsList=fieldsList,min=ti,max=tf,verbose=True)
    
        ds.df=ds.df.interpolate('values')
        print 'Dataframe shape:', ds.df.shape
        gyros,sc,est=extractGyrosAndStarcam(ds.df)
        

        print "Saving..."
        est.to_pickle(est_filename)
        gyros.to_pickle(gyros_filename)
        sc.to_pickle(sc_filename)
        ds.df.to_pickle(org_filename)
    else:
        print "Opening..."
        est=pd.read_pickle(est_filename)
        sc=pd.read_pickle(sc_filename)
    
    print 'SC   Dataframe shape:', sc.shape
    print 'Est. Dataframe shape:', est.shape
    df=pd.merge(est.iloc[1:-1],sc,how='outer',left_index=True,right_index=True)
    print 'Dataframe shape:', df.shape
    if True:
        print "Time conversion ..."
        index=(df.index-df.index[0])/400. #time in seconds
        index=pd.to_timedelta(index,unit='s')
        time=ftime+index-pd.Timedelta(hours=5) #Palestine
        df.index=time
        #=======================================================================
        # print "Cropping time"
        # ftime=pd.datetime(2017, 6, 9, 1, 51,4)
        # time_start=pd.datetime(2017, 6, 9, 4, 51)
        # time_end=pd.datetime(2017, 6, 9, 12)
        # df = df.loc[time_start:time_end]
        # dt=df.index[0]-ftime
        # df.index=df.index-pd.Timedelta(hours=8)
        #=======================================================================
    print 'Dataframe shape:', df.shape
    
    print "Plotting..."
   
    use('seaborn-bright')
    mpl.rcParams['axes.grid'] = True
    plt.rc('font', family='serif')
    
    styles=['b.',{'color':'g','linestyle':'None','marker':'*','ms':10}]
    sc=df[SCLabels].dropna()
    xmin=736489.01118224463
    xmax=736489.07284310518
    tmin=None#pd.datetime(2017, 6, 9, 0, 15, 44)
    tmax=None#pd.datetime(2017, 6, 9, 1, 44, 04)
    xlim=None#[xmin,xmax]
    plotQuaternions(df[['qest','qI2G']].loc[tmin:tmax],styles=styles,legend=True,labels=['Estimator','Starcamera'],xlim=xlim)
    #plotQuaternions(sc[['qI2G','qI2S']],legend=True,styles=['g*','b+'])
    a=1
    print "Show"
    plt.show()


    