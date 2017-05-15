'''
Created on 28 abr. 2017

Main script

@author: Marc Casalprim
'''
print 'Imports...'
import matplotlib
from utils.dataset import DataSet,plt,sns
from utils.field import Field,getDtypes#,getFieldsContaining,getFieldsRegex



if __name__ == '__main__':
    #folder = "C:/17-04-24_19_02_57/"
    folder = "\\\\GS66-WHITE\\LocalAuroraArchive\\17-05-15_02_09_25\\"
    
    Field.DTYPES=getDtypes(folder)

    
    fieldsList=[]
     
    fieldsList.append(Field('bettii.RTLowPriority.RawStarcameraDecDeg',label='dec_sc'))
    fieldsList.append(Field('bettii.RTLowPriority.RawStarcameraRollDeg',label='roll_sc'))
    fieldsList.append(Field('bettii.RTLowPriority.RawStarcameraRaDeg',label='ra_sc'))  
    matplotlib.style.use('ggplot') 
    
    initial_time=None #in frame number
    final_time = None #in frame number
    
    ds = DataSet(folder,min=initial_time,max=final_time,rpeaks=True)
    fig=[]
    ax=[]
    fig.append(plt.figure(1)) 
    ax.append(plt.subplot(311,xlabel='Time (frames)',ylabel='DEC (deg)'))
    ax.append(plt.subplot(312,xlabel='Time (frames)',ylabel='RA (deg)'))
    ax.append(plt.subplot(313,xlabel='Time (frames)',ylabel='ROLL (deg)'))
    
    plt.ion()
    
    lastNValues=48000
    nValues=12000
    for i in range(10000):
        
        #print 'Reading bytes from '+str(nValues*i)+' to '+str(nValues*(i+1))    
        ds.readListFields(fieldsList, nValues=nValues,verbose=False)
        data=ds.df.dropna().loc[max(ds.df.index)-lastNValues:,:]
        #data=ds.df.dropna().tail(lastNValues) #we get the last values of the dataframe
        
        #data.index=data.index/ds.freq #index in seconds


        for axis in ax: axis.clear()
  
        #plotting elevation and crossElevation
        
        data['dec_sc'].plot(ax=ax[0])
        data['ra_sc'].plot(ax=ax[1])
        data['roll_sc'].plot(ax=ax[2])
        
        for axis in ax[:3]: axis.set_xlabel('Time (frames)')
         
        ax[0].set_ylabel('DEC (deg)')
        ax[1].set_ylabel('RA (deg)')
        ax[2].set_ylabel('ROLL (deg)')      
        
        #plt.draw()
        plt.pause(0.01)
        del ds.df
        ds.df=data #we delete some memory
    plt.show()

    