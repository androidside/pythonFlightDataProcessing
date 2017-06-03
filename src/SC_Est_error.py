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
    folder = "C:/17-05-23_23_45_10/"
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
    use('classic') 
    mpl.rcParams['toolbar'] = 'None'
    mpl.rcParams['axes.grid'] = True
    
    ds = DataSet(folder,rpeaks=True)
    ds.readListFields(fieldsList,verbose=True,rpeaks=False)   
    #ds.readListFields(fieldsList, nValues=nValues,start=nValues*i,verbose=False) #for simulation
    ds.df=ds.df.loc[6800000::400]
    
    q_dif_ra=[]
    q_dif_dec=[]
    q_dif_roll=[]
    print "Generating quaternions..."
    
    for mceFN in ds.df.index:
        q_est=Quat((ds.df.loc[mceFN][['qi','qj','qk','qr']]))
        q_sc=Quat((ds.df.loc[mceFN][['qi_sc','qj_sc','qk_sc','qr_sc']]))
        qdif=q_est*q_sc.inv()
        q_dif_ra.append(qdif.ra/3600.)
        q_dif_dec.append(qdif.dec/3600.)
        q_dif_roll.append(qdif.roll/3600.)
    #triggers=ds.df['triggers'].drop_duplicates()
    data=pd.DataFrame({'ra': q_dif_ra, 'dec':q_dif_dec, 'roll':q_dif_roll},index=ds.df.index)
    
    #initial plot
    print "Plotting..."
    fig=[]
    ax={}
    fig.append(plt.figure(1)) 
    ax['ra']=(plt.subplot(311,ylabel='RA (arcsec)'))
    ax['dec']=(plt.subplot(312,ylabel='DEC (arcsec)'))
    ax['roll']=(plt.subplot(313,xlabel='Time (frames)',ylabel='ROLL (arcsec)'))

    
    data['ra'].plot(ax=ax['ra'])
    data['roll'].plot(ax=ax['roll'])
    data['dec'].plot(ax=ax['dec'])
    
    m={} #map axes to columns
    for a in ax.keys(): m[a]=[l.get_label() for l in ax[a].get_lines()]
     
    plt.draw()
    fig[0].tight_layout()
    plt.show()

    