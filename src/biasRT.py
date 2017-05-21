'''
Created on 28 abr. 2017

Main script

@author: Marc Casalprim
'''
print 'Imports...'
import matplotlib as mpl
from utils.dataset import DataSet,plt,sns
from utils.field import Field,getDtypes#,getFieldsContaining,getFieldsRegex



if __name__ == '__main__':
    folder = "C:/17-05-17_00_36_34/"
    #folder = "\\\\GS66-WHITE\\LocalAuroraArchive\\17-05-17_00_36_34\\"
    
    Field.DTYPES=getDtypes(folder)

    
    fieldsList=[]
     
    fieldsList.append(Field('bettii.RTHighPriority.estimatedBiasXarcsec',label='bias_x'))
    fieldsList.append(Field('bettii.RTHighPriority.estimatedBiasYarcsec',label='bias_y'))
    fieldsList.append(Field('bettii.RTHighPriority.estimatedBiasZarcsec',label='bias_z'))

    mpl.style.use('classic') 
    #mpl.rcParams['toolbar'] = 'None'
    
    ds = DataSet(folder,rpeaks=True)
    fig=[]
    ax={}
    fig.append(plt.figure(1)) 
    ax['bias_x']=(plt.subplot(311))
    ax['bias_y']=(plt.subplot(312))
    ax['bias_z']=(plt.subplot(313))
    
    plt.ion()
    
    lastNValues=900000
    nValues=lastNValues
    i=-1
    while True:
        #i=i+1
        #print 'Reading bytes from '+str(nValues*i)+' to '+str(nValues*(i+1)) 
        ds.readListFields(fieldsList, nValues=nValues,verbose=True,rpeaks=False)   
        #ds.readListFields(fieldsList, nValues=nValues,start=nValues*i,verbose=False) #for simulation
        data=ds.df.loc[max(ds.df.index)-lastNValues:,:]


        for axis in ax.values(): axis.clear()
                         
        ax['bias_x'].set_ylabel('bias X')
        ax['bias_y'].set_ylabel('bias Y')
        ax['bias_z'].set_ylabel('bias Z')
        
        #plotting elevation and crossElevation
        try:
            data['bias_x'].dropna().plot(ax=ax['bias_x'])
            data['bias_y'].dropna().plot(ax=ax['bias_y'])
            data['bias_z'].dropna().plot(ax=ax['bias_z']) 
            

        except Exception, err:
            print err
        
        plt.tight_layout()
        
        plt.draw()
        plt.pause(0.01)
        del ds.df
        ds.df=data #we delete some memory
        break
    
    plt.ioff()
    plt.show()
    