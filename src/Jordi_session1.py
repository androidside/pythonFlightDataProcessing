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
    #folder = "C:/17-04-24_19_02_57/"
    folder = "\\\\GS66-WHITE\\LocalAuroraArchive\\17-05-17_01_37_35\\"
    
    Field.DTYPES=getDtypes(folder)

    
    fieldsList=[]
     
    fieldsList.append(Field('bettii.PIDOutputCCMG.ut',label='ccmg_ut'))
    fieldsList.append(Field('bettii.PIDOutputCCMG.et',label='ccmg_et'))
    fieldsList.append(Field('bettii.PIDOutputMomDump.ut',label='mom_ut'))
    fieldsList.append(Field('bettii.PIDOutputMomDump.et',label='mom_et'))
    fieldsList.append(Field('bettii.PIDOutputCCMG.proportional',label='P CCMG'))   
    fieldsList.append(Field('bettii.PIDOutputCCMG.integral',label='I CCMG'))
    fieldsList.append(Field('bettii.PIDOutputCCMG.derivative',label='D CCMG'))
    fieldsList.append(Field('bettii.PIDOutputMomDump.proportional',label='P MomDump'))   
    fieldsList.append(Field('bettii.PIDOutputMomDump.integral',label='I MomDump'))
    fieldsList.append(Field('bettii.PIDOutputMomDump.derivative',label='D MomDump'))
    fieldsList.append(Field('bettii.StepperGalil.wheelsAngle',label='wheels_angle'))

    mpl.style.use('classic') 
    mpl.rcParams['toolbar'] = 'None'
    
    ds = DataSet(folder,rpeaks=True)
    fig=[]
    ax={}
    fig.append(plt.figure(1)) 
    ax['pid_ccmg1']=(plt.subplot(421,ylabel='ut'))
    ax['pid_ccmg2']=(plt.subplot(423,ylabel='et'))
    ax['pid_ccmg3']=(plt.subplot(425,ylabel='PID CCMG'))
    
    ax['pid_mom1']=(plt.subplot(422,ylabel='ut'))
    ax['pid_mom2']=(plt.subplot(424,ylabel='et'))
    ax['pid_mom3']=(plt.subplot(426,ylabel='PID MomDump'))
    
    ax['pid_wheels']=(plt.subplot(414,ylabel='wheels angle'))
    
    plt.ion()
    
    lastNValues=48000
    nValues=12000
    i=-1
    while True:
        #i=i+1
        #print 'Reading bytes from '+str(nValues*i)+' to '+str(nValues*(i+1)) 
        ds.readListFields(fieldsList, nValues=nValues,verbose=False)   
        #ds.readListFields(fieldsList, nValues=nValues,start=nValues*i,verbose=False) #for simulation
        data=ds.df.loc[max(ds.df.index)-lastNValues:,:]


        for axis in ax.values(): axis.clear()
                         
        ax['pid_ccmg1'].set_ylabel('ut')
        ax['pid_ccmg2'].set_ylabel('et')
        ax['pid_ccmg3'].set_ylabel('PID CCMG')
        
        ax['pid_mom1'].set_ylabel('ut')
        ax['pid_mom2'].set_ylabel('et')
        ax['pid_mom3'].set_ylabel('PID MomDump')
        
        ax['pid_wheels'].set_ylabel('wheels angle')
        #plotting elevation and crossElevation
        try:
            data['ccmg_ut'].dropna().plot(ax=ax['pid_ccmg1'])
            data['ccmg_et'].dropna().plot(ax=ax['pid_ccmg2'])
            data[['P CCMG','I CCMG','D CCMG']].dropna().plot(ax=ax['pid_ccmg3'])
             
            data['mom_ut'].dropna().plot(ax=ax['pid_mom1'])
            data['mom_et'].dropna().plot(ax=ax['pid_mom2'])
            data[['P MomDump','I MomDump','D MomDump']].dropna().plot(ax=ax['pid_mom3'])
            
            data['wheels_angle'].dropna().plot(ax=ax['pid_wheels'])         
            

        except Exception, err:
            print err
        
        plt.tight_layout()
        
        plt.draw()
        plt.pause(0.01)
        del ds.df
        ds.df=data #we delete some memory
    plt.show()

    