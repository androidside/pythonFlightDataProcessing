'''
Created on 28 abr. 2017

Main script

@author: Marc Casalprim
'''
print 'Imports...'
import matplotlib as mpl
import pandas as pd
from matplotlib.style import use
from utils.dataset import DataSet,plt,genQuaternions
from utils.field import Field,getDtypes#,getFieldsContaining,getFieldsRegex
from utils.quat import Quat,normalize,sin,cos


if __name__ == '__main__':
    folder = "C:/17-05-28_02_18_19/"
    folder = "C:/LocalAuroraArchive/17-05-23_23_45_10/"
    folder='Z:/17-06-07_01_23_52-/'
    #folder='Z:/17-06-06_23_21_37-/'
    #folder = "\\\\GS66-WHITE\\LocalAuroraArchive\\17-05-23_23_45_07\\"
    
    #Field.DTYPES=getDtypes(folder)

    
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

    
    ds = DataSet(folder,fieldsList=fieldsList,start=0,nValues=1081500,min=10000,max=5600000,verbose=True)
    #ds = DataSet(folder,fieldsList=fieldsList,min=4500000,verbose=True)  
    #ds.readListFields(fieldsList, nValues=nValues,start=nValues*i,verbose=False) #for simulation
    ds.df=ds.df.interpolate('values')
    
    print 'Dataframe shape:', ds.df.shape
    

    print "Generating quaternions..."
    quats=genQuaternions(ds.df,norm=True)
    print "Creating Starcam dataset..."
    triggers=ds.df.triggers.drop_duplicates()  
    triggers=triggers[[(triggers.loc[mceFN]<max(triggers.index) and triggers.loc[mceFN]>min(triggers.index)) for mceFN in triggers.index]]
    sc=pd.DataFrame(quats,index=ds.df.index)
    sc=sc.loc[triggers.index]
    sc.index=triggers.values
    qGyros2Starcam=sc.qI2S.iloc[0]*sc.qI2G.iloc[0].inv() #(Quat((-0.367,0,0))*Quat((0,-44.9828,0))*Quat((0,0,-0.79))).inv()
    print "qStarcam2Gyros:",qGyros2Starcam.inv()
    print "Calculating errors..."
    q_dif_ra=[]
    q_dif_dec=[]
    q_dif_roll=[]
    q_difsc_ra=[]
    q_difsc_dec=[]
    q_difsc_roll=[]
    ind=[]
    for mceFN in sc.index:
        
        q_est=sc.qest.loc[mceFN]
        q_sc=  sc.qI2G.loc[mceFN]             
        q_dif_ra.append((q_est.ra-q_sc.ra)*3600)
        q_dif_dec.append((q_est.dec-q_sc.dec)*3600)
        q_dif_roll.append((q_est.roll-q_sc.roll)*3600)
        
        q_est=qGyros2Starcam*q_est
        q_sc=sc.qI2S.loc[mceFN]

        q_difsc_ra.append((q_est.ra-q_sc.ra)*3600)
        q_difsc_dec.append((q_est.dec-q_sc.dec)*3600)
        q_difsc_roll.append((q_est.roll-q_sc.roll)*3600)
    #triggers=ds.df['triggers'].drop_duplicates()
    error=pd.DataFrame({'ra': q_difsc_ra, 'dec':q_difsc_dec, 'roll':q_difsc_roll,'ra_est': q_dif_ra, 'dec_est':q_dif_dec, 'roll_est':q_dif_roll},index=sc.index)
    
    #initial plot
    print "Plotting..."
    
    use('classic') 
    #mpl.rcParams['toolbar'] = 'None'
    mpl.rcParams['axes.grid'] = True

    #error.index=(error.index-error.index[0])/400.

    fig=[]
    ax={}
    fig.append(plt.figure(1)) 
    ax['ra']=(plt.subplot(311,ylabel='RA (arcsec)'))
    ax['dec']=(plt.subplot(312,ylabel='DEC (arcsec)'))
    ax['roll']=(plt.subplot(313,xlabel='Time (s)',ylabel='ROLL (arcsec)'))

    
    error['ra'].plot(ax=ax['ra'])
    error['roll'].plot(ax=ax['roll'])
    error['dec'].plot(ax=ax['dec'])
    
    fig[0].suptitle('Errors SC ref. frame')
    
    fig.append(plt.figure(2)) 
    ax['ra_est']=(plt.subplot(311,ylabel='RA (arcsec)'))
    ax['dec_est']=(plt.subplot(312,ylabel='DEC (arcsec)'))
    ax['roll_est']=(plt.subplot(313,xlabel='Time (s)',ylabel='ROLL (arcsec)'))

    
    error['ra_est'].plot(ax=ax['ra_est'])
    error['roll_est'].plot(ax=ax['roll_est'])
    error['dec_est'].plot(ax=ax['dec_est'])
    
    fig[1].suptitle('Errors Gondola ref. frame')
    
    plt.figure()
    data=ds.df[['biasX','biasY','biasZ']].dropna()
    ax1=plt.subplot(311,ylabel='biasX (asec/s)')
    ax2=plt.subplot(312,ylabel='biasY (asec/s)')
    ax3=plt.subplot(313,xlabel='Time (frames)',ylabel='biasZ (asec/s)')
    data['biasX'].plot(ax=ax1)
    data['biasY'].plot(ax=ax2)
    data['biasZ'].plot(ax=ax3)
    
    
   
    plt.draw()
    fig[0].tight_layout()
    fig[1].tight_layout()
    plt.show()

    