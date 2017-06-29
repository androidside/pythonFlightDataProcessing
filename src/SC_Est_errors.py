'''
Created on 28 abr. 2017

Main script

@author: Marc Casalprim
'''
print 'Imports...'
import matplotlib as mpl
import pandas as pd
from matplotlib.style import use
from utils.dataset import DataSet,plt
from utils.field import Field,getDtypes#,getFieldsContaining,getFieldsRegex
from utils.quat import Quat,normalize,sin,cos


if __name__ == '__main__':
    folder = "C:/17-05-28_02_18_19/"
    folder = "C:\LocalAuroraArchive\17-05-23_23_45_10"
    #folder = "\\\\GS66-WHITE\\LocalAuroraArchive\\17-05-23_23_45_07\\"
    
    Field.DTYPES=getDtypes(folder)

    
    fieldsList=[]
     
    fieldsList.append(Field('bettii.RTLowPriority.RawStarcameraQuaternionFXPqi',label='qi_sc'))
    fieldsList.append(Field('bettii.RTLowPriority.RawStarcameraQuaternionFXPqj',label='qj_sc'))
    fieldsList.append(Field('bettii.RTLowPriority.RawStarcameraQuaternionFXPqk',label='qk_sc'))
    fieldsList.append(Field('bettii.RTLowPriority.RawStarcameraQuaternionFXPqr',label='qr_sc'))
    fieldsList.append(Field('bettii.RTLowPriority.qr'))
    fieldsList.append(Field('bettii.RTLowPriority.qi'))
    fieldsList.append(Field('bettii.RTLowPriority.qj'))
    fieldsList.append(Field('bettii.RTLowPriority.qk'))
    fieldsList.append(Field('bettii.RTLowPriority.RawStarcameraMceFrameNumberWhenSCTriggered',label='triggers'))
    
    fieldsList.append(Field('bettii.RTHighPriority.estimatedBiasXarcsec',label='bias_x'))
    fieldsList.append(Field('bettii.RTHighPriority.estimatedBiasYarcsec',label='bias_y'))
    fieldsList.append(Field('bettii.RTHighPriority.estimatedBiasZarcsec',label='bias_z'))

    
    ds = DataSet(folder,rpeaks=True)
    ds.readListFields(fieldsList,verbose=True,rpeaks=False)   
    #ds.readListFields(fieldsList, nValues=nValues,start=nValues*i,verbose=False) #for simulation
    ds.df=ds.df.interpolate('values')
    
    print 'Dataframe shape:', ds.df.shape
    
    sc=pd.DataFrame({'t': ds.df.triggers.values},index=ds.df.triggers).drop_duplicates()
    data=pd.merge(ds.df,sc,how='outer',left_index=True,right_index=True).interpolate('values')
    q_dif_ra=[]
    q_dif_dec=[]
    q_dif_roll=[]
    q_difsc_ra=[]
    q_difsc_dec=[]
    q_difsc_roll=[]
    ind=[]
    print "Generating quaternions..."
    triggerFN=0
    qrot=(Quat((-0.367,0,0))*Quat((0,-44.9828,0))*Quat((0,0,-0.79))).inv()
    for mceFN in ds.df.triggers.drop_duplicates().index:
            triggerFN=ds.df.triggers.loc[mceFN]
            if triggerFN < max(ds.df.index) and triggerFN > min(ds.df.index):
                q_est=Quat((data.loc[triggerFN][['qi','qj','qk','qr']]))
                q_sc=Quat((ds.df.loc[mceFN][['qi_sc','qj_sc','qk_sc','qr_sc']]))
                
                q_dif_ra.append((q_est.ra-q_sc.ra)*3600)
                q_dif_dec.append((q_est.dec-q_sc.dec)*3600)
                q_dif_roll.append((q_est.roll-q_sc.roll)*3600)
                
                q_est=qrot*q_est
                q_sc=qrot*q_sc

                q_difsc_ra.append((q_est.ra-q_sc.ra)*3600)
                q_difsc_dec.append((q_est.dec-q_sc.dec)*3600)
                q_difsc_roll.append((q_est.roll-q_sc.roll)*3600)
                ind.append(triggerFN)
    #triggers=ds.df['triggers'].drop_duplicates()
    error=pd.DataFrame({'ra': q_difsc_ra, 'dec':q_difsc_dec, 'roll':q_difsc_roll,'ra_est': q_dif_ra, 'dec_est':q_dif_dec, 'roll_est':q_dif_roll},index=ind)
    
    #initial plot
    print "Plotting..."
    
    use('classic') 
    #mpl.rcParams['toolbar'] = 'None'
    mpl.rcParams['axes.grid'] = True

    error.index=error.index/400.

    fig=[]
    ax={}
    fig.append(plt.figure(1)) 
    ax['ra']=(plt.subplot(311,ylabel='RA (arcsec)'))
    ax['dec']=(plt.subplot(312,ylabel='DEC (arcsec)'))
    ax['roll']=(plt.subplot(313,xlabel='Time (s)',ylabel='ROLL (arcsec)'))

    
    error['ra'].plot(ax=ax['ra'])
    error['roll'].plot(ax=ax['roll'])
    error['dec'].plot(ax=ax['dec'])
    
    fig[0].suptitle('Errors 45deg elevation')
    
    fig.append(plt.figure(2)) 
    ax['ra_est']=(plt.subplot(311,ylabel='RA (arcsec)'))
    ax['dec_est']=(plt.subplot(312,ylabel='DEC (arcsec)'))
    ax['roll_est']=(plt.subplot(313,xlabel='Time (s)',ylabel='ROLL (arcsec)'))

    
    error['ra_est'].plot(ax=ax['ra_est'])
    error['roll_est'].plot(ax=ax['roll_est'])
    error['dec_est'].plot(ax=ax['dec_est'])
    
    fig[1].suptitle('Errors 0deg elevation')
    
    plt.figure()
    ds.df['bias_x'].dropna().plot()
    plt.figure()
     
    ds.df['bias_y'].dropna().plot()
    plt.figure()
    ds.df['bias_z'].dropna().plot() 
    
    
   
    plt.draw()
    fig[0].tight_layout()
    plt.show()

    