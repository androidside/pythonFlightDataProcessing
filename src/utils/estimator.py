'''
Created on Jul 24, 2017

Defines two functions that are useful when dealing with the estimators.
readAndSave reads the infromation and stores it in pickle files.
openPickle opens the saved pickles.
In this way we read and generate all the useful dataframes just once, saving time.

@author: Marc Casalprim
'''

from timeit import default_timer as timer

from utils.dataset import DataSet,extractGyrosAndStarcam,pd
from utils.field import Field
from estimators.estimators import Estimator

GYROS_FILENAME="gyros_dataframe"
SC_FILENAME="sc_dataframe"
EST_FILENAME="est_dataframe"
QUATS_FILENAME="quats_dataframe"
ORG_FILENAME="org_dataframe"

def readAndSave(folder,initial_time=1000,final_time = None):
    '''Reads the information relevant to the estimator and creates different dataframes. It uses ``extractGyrosAndStarcam()``.
    The generated dataframes are stored in pickle files.
    
    columns of gyros: ['gyroX', 'gyroY', 'gyroZ']
    columns of sc: ['qI2G','qI2S','triggers']
    columns of est: ['qest','biasX','biasY','biasZ','P']
    
    :param folder: folder where the fields are located and the files will be stored
    :param initial_time: mce frame number where we start
    :param final_time: mce frame number where we end (if None, until the end of the files)
    :return: gyros,sc,est
    :rtype: (pandas.Dataframe,pandas.Dataframe,pandas.Dataframe)   
    '''
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
    
    fieldsList.append(Field('bettii.RTLowPriority.covarianceMatrix00',label='P00'))
    fieldsList.append(Field('bettii.RTLowPriority.covarianceMatrix01',label='P01'))
    fieldsList.append(Field('bettii.RTLowPriority.covarianceMatrix02',label='P02'))
    fieldsList.append(Field('bettii.RTLowPriority.covarianceMatrix10',label='P10'))
    fieldsList.append(Field('bettii.RTLowPriority.covarianceMatrix11',label='P11'))
    fieldsList.append(Field('bettii.RTLowPriority.covarianceMatrix12',label='P12'))
    fieldsList.append(Field('bettii.RTLowPriority.covarianceMatrix20',label='P20'))
    fieldsList.append(Field('bettii.RTLowPriority.covarianceMatrix21',label='P21'))
    fieldsList.append(Field('bettii.RTLowPriority.covarianceMatrix22',label='P22'))
    fieldsList.append(Field('bettii.RTLowPriority.covarianceMatrix33',label='P33'))
    fieldsList.append(Field('bettii.RTLowPriority.covarianceMatrix44',label='P44'))
    fieldsList.append(Field('bettii.RTLowPriority.covarianceMatrix55',label='P55'))
    
    for field in fieldsList:
        field.range=1e3
    
    fieldsList.append(Field('bettii.RTLowPriority.RawStarcameraMceFrameNumberWhenSCTriggered',label='triggers'))
    fieldsList.append(Field('bettii.RTHighPriority.estimatedBiasXarcsec',label='biasX'))
    fieldsList.append(Field('bettii.RTHighPriority.estimatedBiasYarcsec',label='biasY')) 
    fieldsList.append(Field('bettii.RTHighPriority.estimatedBiasZarcsec',label='biasZ'))
    fieldsList.append(Field('bettii.RTHighPriority.StarCameraTriggerStatus',label='tstatus',range=400))
    
    fieldsList.append(Field('bettii.GyroReadings.angularVelocityX',label='gyroX',dtype='i4',conversion=-0.0006304))
    fieldsList.append(Field('bettii.GyroReadings.angularVelocityY',label='gyroY',dtype='i4',conversion=-0.0006437))
    fieldsList.append(Field('bettii.GyroReadings.angularVelocityZ',label='gyroZ',dtype='i4',conversion=0.0006324))
    

    
    ds = DataSet(folder,fieldsList=fieldsList,estimator=False,starcam=False,min=initial_time,max=final_time,verbose=True)
    #ds.df=ds.df.interpolate(method='values').dropna()

    print 'Dataframe shape:', ds.df.shape       
    gyros,sc,est=extractGyrosAndStarcam(ds.df)
    print "Elapsed time:",timer()-start_time,"seconds."
    print 'SC     Dataframe shape:', sc.shape
    print 'Gyros. Dataframe shape:', gyros.shape
    print 'Est  Dataframe shape:', est.shape
    print "Saving.."
    gyros.to_pickle(folder+GYROS_FILENAME)
    sc.to_pickle(folder+SC_FILENAME)
    est.to_pickle(folder+EST_FILENAME)
    ds.df.to_pickle(folder+ORG_FILENAME)
    print "Saved"
    return gyros,sc,est

def openPickles(folder,openEst=True):
    '''Reads the information relevant to the estimator and creates different dataframes. It uses ``extractGyrosAndStarcam()``.
    The generated dataframes are stored in pickle files.
    
    columns of gyros: ['gyroX', 'gyroY', 'gyroZ']
    columns of sc: ['qI2G','qI2S','triggers']
    columns of est: ['qest','biasX','biasY','biasZ','P']
    
    :param folder: folder where the files are located
    :param openEst: open estimator dataframe? (if False, saves time and est will be a empty dataframe)
    :return: gyros,sc,est
    :rtype: (pandas.Dataframe,pandas.Dataframe,pandas.Dataframe)   
    '''
    start_time = timer()
    print "Reading..."
    gyros = pd.read_pickle(folder+GYROS_FILENAME)
    print 'Gyros shape:', gyros.shape
    sc    = pd.read_pickle(folder+SC_FILENAME)
    print 'SC shape:', sc.shape
    if openEst:
        est = pd.read_pickle(folder+EST_FILENAME) 
        print 'Quats shape:', est.shape
    else: est=pd.DataFrame()
    print "Elapsed time:",timer()-start_time,"seconds."
    return gyros,sc,est