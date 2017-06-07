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
    folder = "\\\\GS66-WHITE\\LocalAuroraArchive\\17-05-19_20_57_10\\"
    
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
    ds.readListFields(fieldsList, nValues=1000,verbose=True)   
    #ds.readListFields(fieldsList, nValues=nValues,start=nValues*i,verbose=False) #for simulation
    data=ds.df
    #initial plot
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
    

    
    data['ccmg_ut'].plot(ax=ax['pid_ccmg1'])
    data['ccmg_et'].plot(ax=ax['pid_ccmg2'])
    data[['P CCMG','I CCMG','D CCMG']].plot(ax=ax['pid_ccmg3'])
    
    data['mom_ut'].plot(ax=ax['pid_mom1'])
    data['mom_et'].plot(ax=ax['pid_mom2'])
    data[['P MomDump','I MomDump','D MomDump']].plot(ax=ax['pid_mom3'])
    
    data['wheels_angle'].plot(ax=ax['pid_wheels'])  
    
    m={} #map axes to columns
    for a in ax.keys(): m[a]=[l.get_label() for l in ax[a].get_lines()]
    
    plt.ion()
     
    plt.draw()
    fig[0].tight_layout()
    lastNValues=4000
    nValues=1200
    i=-1
    while True:
        #i=i+1
        #print 'Reading bytes from '+str(nValues*i)+' to '+str(nValues*(i+1)) 
        ds.readListFields(fieldsList, nValues=nValues,verbose=False)   
        #i=i+1;ds.readListFields(fieldsList, nValues=nValues,start=nValues*i,verbose=False) #for simulation
        data=ds.df.loc[max(ds.df.index)-lastNValues:,:]

        #plotting elevation and crossElevation
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

        except Exception, err:
            print err      

        del ds.df
        ds.df=data #we delete some memory
        plt.draw()
        #fig[0].tight_layout()
        plt.pause(0.1)
    plt.show()

    