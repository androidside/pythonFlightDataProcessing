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
    filterQuats,extractDuplicates
from utils.field import Field#,getFieldsContaining,getFieldsRegex


if __name__ == '__main__':
    folder='D:/GondolaFlightArchive/17-06-09_01_51_04/'
    filename=folder+'estimator.pkl'
    read=True
    
    if read:
        fieldsList=[]
         
        fieldsList.append(Field('bettii.RTLowPriority.RawStarcameraQuaternionFXPqi',label='qi_sc'))
        fieldsList.append(Field('bettii.RTLowPriority.RawStarcameraQuaternionFXPqj',label='qj_sc'))
        fieldsList.append(Field('bettii.RTLowPriority.RawStarcameraQuaternionFXPqk',label='qk_sc'))
        fieldsList.append(Field('bettii.RTLowPriority.RawStarcameraQuaternionFXPqr',label='qr_sc'))
        fieldsList.append(Field('bettii.RTLowPriority.RawStarcameraDecDeg',label='dec_sc'))
        fieldsList.append(Field('bettii.RTLowPriority.RawStarcameraRaDeg',label='ra_sc'))
        fieldsList.append(Field('bettii.RTLowPriority.RawStarcameraRollDeg',label='roll_sc'))
        fieldsList.append(Field('bettii.RTLowPriority.qr'))
        fieldsList.append(Field('bettii.RTLowPriority.qi'))
        fieldsList.append(Field('bettii.RTLowPriority.qj'))
        fieldsList.append(Field('bettii.RTLowPriority.qk'))
        fieldsList.append(Field('bettii.RTLowPriority.RawStarcameraMceFrameNumberWhenSCTriggered',label='triggers'))
        
        fieldsList.append(Field('bettii.RTHighPriority.estimatedBiasXarcsec',label='biasX'))
        fieldsList.append(Field('bettii.RTHighPriority.estimatedBiasYarcsec',label='biasY'))
        fieldsList.append(Field('bettii.RTHighPriority.estimatedBiasZarcsec',label='biasZ'))
    
        m=19061609
        ds = DataSet(folder,fieldsList=fieldsList,min=1000,max=None,verbose=True)
    
        ds.df=ds.df.interpolate('values')
        print 'Dataframe shape:', ds.df.shape
        
        print "Generating quaternions"
        quats=genQuaternions(ds.df,norm=True)
        est=pd.DataFrame(quats,index=ds.df.index)
        print "Filtering"
        est=filterQuats(est)
        print 'Dataframe shape:', est.shape
        
        print "Dropping duplicates..."
        sc=extractDuplicates(est[['qI2G','qI2S']])
        print 'Dataframe shape:', sc.shape

        df=pd.merge(est[['qest']],sc,how='outer',left_index=True,right_index=True)
        #time conversion
        text=folder.split('/')[-2]
        ftime_str=text[0:8]+' '+text[9:17].replace('_',':') #foldertime
        ftime=pd.to_datetime(ftime_str,yearfirst=True)
        index=(df.index-df.index[0])/400. #time in seconds
        index=pd.to_timedelta(index,unit='s')
        time=ftime+index-pd.Timedelta(hours=5)
        df.index=time
        print "Saving..."
        df.to_pickle(filename)
    else:
        print "Opening..."
        df=pd.read_pickle(filename)
    print 'Dataframe shape:', df.shape
    styles=['g*','b+']
    
    use('seaborn-bright')
    mpl.rcParams['axes.grid'] = True
    
    plotQuaternions(df[['qI2G','qest']],styles=styles,legend=True,labels=['Starcamera','Estimator'])
    plotQuaternions(df[['qI2S']],styles=styles)
    plt.show()


    