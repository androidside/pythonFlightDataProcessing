'''
Created on 17 May 2017

Real Time scripts of the error between the SC and Estimator.

@author: Marc Casalprim
'''
print 'Imports...'
from utils.dataset import DataSet,plt,pd
from utils.field import Field,getDtypes
from utils.quat import Quat
from utils.config import flightDisksFolders,plt,save_folder,img_folder



if __name__ == '__main__':
    folder = "C:/17-05-17_00_36_34/"
    folder = "\\\\GS66-WHITE\\LocalAuroraArchive\\17-05-24_02_06_18\\"
    
    
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
    
    ds = DataSet(folder,rpeaks=True)
    ds.readListFields(fieldsList, nValues=3000,verbose=True,rpeaks=False)   
    #ds.readListFields(fieldsList, nValues=nValues,start=nValues*i,verbose=False) #for simulation
    
    q_dif_ra=[]
    q_dif_dec=[]
    q_dif_roll=[]
    print "Generating quaternions..."
    for mceFN in ds.df.index:
        q_est=Quat((ds.df.loc[mceFN][['qi','qj','qk','qr']]))
        q_sc=Quat((ds.df.loc[mceFN][['qi_sc','qj_sc','qk_sc','qr_sc']]))
        qdif=q_est*q_sc.inv()
        q_dif_ra.append(qdif.ra*3600.)
        q_dif_dec.append(qdif.dec*3600.)
        q_dif_roll.append(qdif.roll*3600.)
    #triggers=ds.df['triggers'].drop_duplicates()
    data=pd.DataFrame({'ra': q_dif_ra, 'dec':q_dif_dec, 'roll':q_dif_roll},index=ds.df.index)
    
    #initial plot
    fig=[]
    ax={}
    fig.append(plt.figure(1)) 
    ax['ra']=(plt.subplot(311,ylabel='RA (arcsec)'))
    ax['dec']=(plt.subplot(312,ylabel='DEC (arcsec)'))
    ax['roll']=(plt.subplot(313,xlabel='Time (frames)',ylabel='ROLL (arcsec)'))
    
    fig.append(plt.figure(2))
    ax3=(plt.subplot(111,xlabel='RA (arcsec)',ylabel='DEC (arcsec)'))
    
    data['ra'].plot(ax=ax['ra'])
    data['roll'].plot(ax=ax['roll'])
    data['dec'].plot(ax=ax['dec'])
    data['dec'].plot(ax=ax3)
    
    m={} #map axes to columns
    for a in ax.keys(): m[a]=[l.get_label() for l in ax[a].get_lines()]
     
    plt.draw()
    fig[0].tight_layout()
    lastNValues=30000
    nValues=3000
    i=-1
    print "Plotting.."
    while True:
        #i=i+1
        #print 'Reading bytes from '+str(nValues*i)+' to '+str(nValues*(i+1)) 
        ds.readListFields(fieldsList, nValues=nValues,verbose=False,rpeaks=False)   
        #i=i+1;ds.readListFields(fieldsList, nValues=nValues,start=nValues*i,verbose=False) #for simulation
        data=ds.df.loc[max(ds.df.index)-lastNValues:,:]
        q_dif_ra=[]
        q_dif_dec=[]
        q_dif_roll=[]
        #print "Generating quaternions..."
        for mceFN in ds.df.index:
            q_est=Quat((ds.df.loc[mceFN][['qi','qj','qk','qr']]))
            q_sc=Quat((ds.df.loc[mceFN][['qi_sc','qj_sc','qk_sc','qr_sc']]))
            qdif=q_est*q_sc.inv()
            q_dif_ra.append(qdif.ra*3600.)
            q_dif_dec.append(qdif.dec*3600.)
            q_dif_roll.append(qdif.roll*3600.)
        data=pd.DataFrame({'ra': q_dif_ra, 'dec':q_dif_dec, 'roll':q_dif_roll},index=ds.df.index)
        try:
            x=data.index
            xlims=(min(x),max(x))
            for key in ax.keys():
                columns=m[key]
                axis=ax[key]
                lines=axis.get_lines()
                ylims=[+1e30,-1e30]
                for k in range(len(lines)) :
                    line=lines[k]
                    column=columns[k]
                    y=data[column].dropna()
                    x=y.index
                    y=y.values
                    line.set_data(x,y)
                    ylims[0]=min(min(y),ylims[0])
                    ylims[1]=max(max(y),ylims[1])
                axis.set_xlim(xlims)
                axis.set_ylim(ylims)
                #axis.autoscale()
            line=ax3.get_lines()[0]
            x=data.ra.values
            y=data.dec.values
            line.set_data(x,y)
            ax3.set_xlim(min(x),max(x))
            ax3.set_ylim(min(y),max(y))
        except Exception, err:
            print err      

        del ds.df
        ds.df=data #we delete some memory
        plt.draw()
        fig[0].tight_layout()
        plt.pause(0.1)
    plt.show()

    