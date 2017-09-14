'''
Created on 28 May 2017

Plotting of the estimated biases and the diagonal values of the covariance matrix P
In addition, a plot of the diagonal values of the P rotated by the qGyros2Starcam.

See ``utils.dataset.plotCovs()`` to obtain similar results

@author: Marc Casalprim
'''
print 'Imports...'
import matplotlib
import numpy as np
import pandas as pd
from matplotlib.style import use
from utils.dataset import DataSet,plt
from utils.field import Field,getDtypes#,getFieldsContaining,getFieldsRegex



if __name__ == '__main__':
    folder = "C:/17-05-23_00_59_52/"

    
    Field.DTYPES=getDtypes(folder)
    
    fieldsList=[]

    fieldsList.append(Field('bettii.RTLowPriority.MeasurementErrorCovarianceMatrixR00',label='R00',conversion=1/4.8484e-6))
    fieldsList.append(Field('bettii.RTLowPriority.MeasurementErrorCovarianceMatrixR11',label='R11',conversion=1/4.8484e-6))
    fieldsList.append(Field('bettii.RTLowPriority.MeasurementErrorCovarianceMatrixR22',label='R22',conversion=1/4.8484e-6))
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

    fieldsList.append(Field('bettii.RTHighPriority.estimatedBiasXarcsec',label='biasX'))
    fieldsList.append(Field('bettii.RTHighPriority.estimatedBiasYarcsec',label='biasY')) 
    fieldsList.append(Field('bettii.RTHighPriority.estimatedBiasZarcsec',label='biasZ')) 

    fieldsList.append(Field('bettii.GyroReadings.angularVelocityX',label='gyroX',dtype='i4',conversion=0.0006304))
    fieldsList.append(Field('bettii.GyroReadings.angularVelocityY',label='gyroY',dtype='i4',conversion=0.0006437))
    fieldsList.append(Field('bettii.GyroReadings.angularVelocityZ',label='gyroZ',dtype='i4',conversion=0.0006324))
   
    #fieldsList.append(Field('bettii.FpgaState.state',label='state'))
    
    initial_time=5145000 #in frame number
    final_time = 5149000 #in frame number
    
    
    initial_time=1000 #in frame number
    final_time = None #in frame number
    
    ds = DataSet(folder,fieldsList=fieldsList,min=initial_time,max=final_time,verbose=True)
    
    print 'Dataframe shape:', ds.df.shape
    data=ds.df.interpolate(method='values')
    #data.index=data.index/ds.freq #index in seconds
    use('seaborn-bright')
    matplotlib.rcParams['axes.grid']=True

    
    plt.figure(1)
    data=ds.df[['biasX','biasY','biasZ']].dropna()
    ax1=plt.subplot(311,ylabel='biasX (arcsec)')
    ax2=plt.subplot(312,ylabel='biasY (arcsec)')
    ax3=plt.subplot(313,xlabel='Time (frames)',ylabel='biasZ (arcsec)')
    data['biasX'].plot(ax=ax1)
    data['biasY'].plot(ax=ax2)
    data['biasZ'].plot(ax=ax3)
    
    plt.figure(2)
    data=ds.df[['P00','P11','P22']].dropna()
    ax1=plt.subplot(311,ylabel='P00')
    ax2=plt.subplot(312,ylabel='P11')
    ax3=plt.subplot(313,xlabel='Time (frames)',ylabel='P22')
    data['P00'].plot(ax=ax1)
    data['P11'].plot(ax=ax2)
    data['P22'].plot(ax=ax3)
    
    plt.figure(3)
    data=ds.df[['P00','P01','P02','P10','P11','P12','P20','P21','P22']].dropna()
    L=len(data.P00)
    P00rot=[0]*L
    P11rot=[0]*L
    P22rot=[0]*L
    M=np.matrix([[0.693865,0,0.720106],[0,1,0],[-0.720106,0,0.693865]])
    for i in range(L):
        m=(data.iloc[i].as_matrix())
        P0=m.reshape((3,3))
        P0rot=M*P0*M.T
        D=np.sqrt(np.diag(P0rot))/4.8484e-6
        P00rot[i]=D[0];P11rot[i]=D[1];P22rot[i]=D[2];
    
    d={'P00': P00rot,'P11': P11rot,'P22': P22rot}
    data=pd.DataFrame(d,index=data.index).dropna()
    ax1=plt.subplot(311,ylabel='P00 rotated')
    ax2=plt.subplot(312,ylabel='P11 rotated')
    ax3=plt.subplot(313,xlabel='Time (frames)',ylabel='P22 rotated')
    data['P00'].plot(ax=ax1)
    data['P11'].plot(ax=ax2)
    data['P22'].plot(ax=ax3)
    
    
    plt.figure(4)
    data=ds.df[['P33','P44','P55']].dropna().apply(lambda x: np.sqrt(x)/4.8484e-6)
    ax1=plt.subplot(311,ylabel='P33')
    ax2=plt.subplot(312,ylabel='P44')
    ax3=plt.subplot(313,xlabel='Time (frames)',ylabel='P55')
    data['P33'].plot(ax=ax1)
    data['P44'].plot(ax=ax2)
    data['P55'].plot(ax=ax3)

    #print ds.df.state.drop_duplicates()
        
    plt.show()
    plt.pause(1)