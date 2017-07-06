'''
Created on 2 May 2017

Real Time plots of crossElevation,elevation and target and telescope RA,DEC

@author: Marc Casalprim
'''
print 'Imports...'
from matplotlib.style import use
from utils.dataset import DataSet,plt
from utils.field import Field



if __name__ == '__main__':
    #folder = "C:/17-04-24_19_02_57/"
    #folder = "\\\\GS66-WHITE\\LocalAuroraArchive\\17-05-02_18_01_58\\"
    
    folder='C:/16-09-28_21_58_34-/'
    
    fieldsList=[]
     
    fieldsList.append(Field('bettii.RTHighPriority.crossElevation'))
    fieldsList.append(Field('bettii.RTHighPriority.elevation'))
    fieldsList.append(Field('bettii.RTHighPriority.TelescopeDecDeg'))
    fieldsList.append(Field('bettii.RTHighPriority.TelescopeRaDeg'))
    fieldsList.append(Field('bettii.RTHighPriority.targetDEC'))
    fieldsList.append(Field('bettii.RTHighPriority.targetRA'))
      
    use('ggplot') 
    
    initial_time=None #in frame number
    final_time = None #in frame number
    
    ds = DataSet(folder,min=initial_time,max=final_time,rpeaks=True)

    print 'Dataframe shape:', ds.df.shape
    fig=[]
    ax=[]
    fig.append(plt.figure(1)) 
    ax.append(plt.subplot(211,xlabel='Time (frames)',ylabel='DEC (deg)'))
    ax.append(plt.subplot(212,xlabel='Time (frames)',ylabel='RA (deg)'))
    fig.append(plt.figure(2))
    ax.append(plt.subplot(211,xlabel='Time (frames)',ylabel='DEC error (deg)'))
    ax.append(plt.subplot(212,xlabel='Time (frames)',ylabel='RA error (deg)'))
    fig.append(plt.figure(3))
    ax.append(plt.subplot(221,xlabel='Time (frames)',ylabel='elevation (arcsec)'))
    ax.append(plt.subplot(223,xlabel='Time (frames)',ylabel='crossElevation (arcsec)'))
    ax.append(plt.subplot(122,xlabel='crossElevation (arcsec)',ylabel='Elevation (arcsec)'))
    
    plt.ion()
    
    lastNValues=2000
    nValues=500
    for i in range(10000):
        
        #print 'Reading bytes from '+str(nValues*i)+' to '+str(nValues*(i+1))    
        ds.readListFields(fieldsList, nValues=nValues, start=nValues*i,verbose=False)
        data=ds.df.dropna().loc[max(ds.df.index)-lastNValues:,:]
        #data=ds.df.dropna().tail(lastNValues) #we get the last values of the dataframe
        
        #data.index=data.index/ds.freq #index in seconds


        for axis in ax: axis.clear()
        
        #print 'Plotting last '+str(lastNValues)+' values.'
        #plotting RA and DEC target vs estimated
        data[['targetDEC','TelescopeDecDeg']].plot(ax=ax[0])
        data[['targetRA','TelescopeRaDeg']].plot(ax=ax[1])       
        
        #plotting RA and DEC estimated-target  estimated
        
        errDEC=(data.TelescopeDecDeg.subtract(data.targetDEC))
        errDEC.plot(ax=ax[2])
        errRA=(data.TelescopeRaDeg.subtract(data.targetRA))
        errRA.plot(ax=ax[3])
        
        #plotting elevation and crossElevation
        
        data['elevation'].plot(ax=ax[4])
        data['crossElevation'].plot(ax=ax[5])
        data.plot(ax=ax[6],x='crossElevation',y='elevation',legend=None)
        
        for axis in ax[:6]: axis.set_xlabel('Time (frames)')
         
        ax[0].set_ylabel('DEC (deg)')
        ax[1].set_ylabel('RA (deg)')
        ax[2].set_ylabel('DEC error (deg)')
        ax[3].set_ylabel('RA error (deg)')
        ax[4].set_ylabel('elevation (arcsec)')
        ax[5].set_ylabel('crossElevation (arcsec)')
        ax[6].set_ylabel('Elevation (arcsec)')       
        ax[6].set_xlabel('crossElevation(arcsec)')        
        
        #plt.draw()
        plt.pause(0.01)
        del ds.df
        ds.df=data #we delete some memory
    plt.show()

    