'''
Created on Jul 24, 2017

@author: bettii
'''

from timeit import default_timer as timer

from utils.dataset import DataSet,extractGyrosAndStarcam,pd
from utils.field import Field
from estimators.estimators import Estimator

GYROS_FILENAME="gyros_dataframe"
SC_FILENAME="sc_dataframe"
EST_FILENAME="est_dataframe"
QUATS_FILENAME="quats_dataframe"

def readAndSave(folder):
    start_time = timer()
    fieldsList=[]     
    fieldsList.append(Field('bettii.RTLowPriority.RawStarcameraQuaternionFXPqi',label='qi_sc'))
    fieldsList.append(Field('bettii.RTLowPriority.RawStarcameraQuaternionFXPqj',label='qj_sc'))
    fieldsList.append(Field('bettii.RTLowPriority.RawStarcameraQuaternionFXPqk',label='qk_sc'))
    fieldsList.append(Field('bettii.RTLowPriority.RawStarcameraQuaternionFXPqr',label='qr_sc'))
    fieldsList.append(Field('bettii.RTLowPriority.qr'))
    fieldsList.append(Field('bettii.RTLowPriority.qi'))
    fieldsList.append(Field('bettii.RTLowPriority.qj'))
    fieldsList.append(Field('bettii.RTLowPriority.qk'))
    fieldsList.append(Field('bettii.RTLowPriority.RawStarcameraDecDeg',label='dec_sc'))
    fieldsList.append(Field('bettii.RTLowPriority.RawStarcameraRaDeg',label='ra_sc'))
    fieldsList.append(Field('bettii.RTLowPriority.RawStarcameraRollDeg',label='roll_sc'))
    fieldsList.append(Field('bettii.RTLowPriority.RawStarcameraDecError',label='dec_err'))
    fieldsList.append(Field('bettii.RTLowPriority.RawStarcameraRaError',label='ra_err'))
    fieldsList.append(Field('bettii.RTLowPriority.RawStarcameraRollError',label='roll_err'))
    fieldsList.append(Field('bettii.RTLowPriority.RawStarcameraMceFrameNumberWhenSCTriggered',label='triggers'))

    fieldsList.append(Field('bettii.GyroReadings.angularVelocityX',label='gyroX',dtype='i4',conversion=-0.0006304))
    fieldsList.append(Field('bettii.GyroReadings.angularVelocityY',label='gyroY',dtype='i4',conversion=-0.0006437))
    fieldsList.append(Field('bettii.GyroReadings.angularVelocityZ',label='gyroZ',dtype='i4',conversion=0.0006324))
    

    initial_time=1000 #in frame number
    final_time = None #in frame number

    
    ds = DataSet(folder,fieldsList=fieldsList,estimator=False,starcam=False,min=initial_time,max=final_time,verbose=True)
    #ds.df=ds.df.interpolate(method='values').dropna()

    print 'Dataframe shape:', ds.df.shape       
    gyros,sc,quats=extractGyrosAndStarcam(ds.df)
    print "Elapsed time:",timer()-start_time,"seconds."
    print "Saving.."
    gyros.to_pickle(folder+GYROS_FILENAME)
    sc.to_pickle(folder+SC_FILENAME)
    quats.to_pickle(folder+QUATS_FILENAME)
    print "Saved"
    return gyros,sc,quats

def openPickles(folder,quats=True):
    start_time = timer()
    print "Reading..."
    gyros = pd.read_pickle(folder+GYROS_FILENAME)
    print 'Gyros shape:', gyros.shape
    sc    = pd.read_pickle(folder+SC_FILENAME)
    print 'SC shape:', sc.shape
    if quats:
        quats = pd.read_pickle(folder+QUATS_FILENAME) 
        print 'Quats shape:', quats.shape
    else: quats=pd.DataFrame()
    print "Elapsed time:",timer()-start_time,"seconds."
    return gyros,sc,quats