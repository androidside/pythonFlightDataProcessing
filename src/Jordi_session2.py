'''
Created on 28 abr. 2017

Main script

@author: Marc Casalprim
'''
print 'Imports...'
import matplotlib as mpl
from matplotlib.style import use
from utils.dataset import DataSet,plt
from utils.field import Field,getDtypes#,getFieldsContaining,getFieldsRegex



if __name__ == '__main__':
    folder = "C:/17-05-17_00_36_34/"
    folder = "\\\\GS66-WHITE\\LocalAuroraArchive\\17-05-23_23_25_41\\"
    
    Field.DTYPES=getDtypes(folder)

    
    fieldsList=[]
     
    fieldsList.append(Field('bettii.PIDInputCCMG.positionTarget',label='ptarget'))
    fieldsList.append(Field('bettii.PIDInputCCMG.positionMeasurement',label='pmeas'))
    fieldsList.append(Field('bettii.PIDInputCCMG.velocityTarget',label='vtarget'))
    fieldsList.append(Field('bettii.PIDInputCCMG.velocityMeasurement',label='vmeas'))

    fieldsList.append(Field('bettii.GyroReadings.angularVelocityX',label='gyroX',dtype='i4',conversion=0.0006304))
    fieldsList.append(Field('bettii.GyroReadings.angularVelocityY',label='gyroY',dtype='i4',conversion=0.0006437))
    fieldsList.append(Field('bettii.GyroReadings.angularVelocityZ',label='gyroZ',dtype='i4',conversion=0.0006324))
    use('classic') 
    mpl.rcParams['toolbar'] = 'None'
    mpl.rcParams['axes.grid'] = True
    
    ds = DataSet(folder,rpeaks=True)
    ds.readListFields(fieldsList, nValues=1000,verbose=True)   
    #ds.readListFields(fieldsList, nValues=nValues,start=nValues*i,verbose=False) #for simulation
    data=ds.df
    #initial plot
    fig=[]
    ax={}
    fig.append(plt.figure(1)) 
    ax['gx']=(plt.subplot(311,ylabel='Gyro X'))
    ax['gy']=(plt.subplot(312,ylabel='Gyro Y'))
    ax['gz']=(plt.subplot(313,ylabel='Gyro Z'))
    fig.append(plt.figure(2))
    ax['ptarget']=(plt.subplot(221,ylabel='Position'))
    ax['pmeas']=(plt.subplot(222))
    ax['vtarget']=(plt.subplot(223,xlabel='Time (frames)',ylabel='Velocity')) 
    ax['vmeas']=(plt.subplot(224,xlabel='Time (frames)'))
    
    ax['ptarget'].set_title('Target')
    ax['pmeas'].set_title('Measurement')

    
    data['gyroX'].plot(ax=ax['gx'])
    data['gyroY'].plot(ax=ax['gy'])
    data['gyroZ'].plot(ax=ax['gz'])
    data['ptarget'].plot(ax=ax['ptarget'])
    data['pmeas'].plot(ax=ax['pmeas'])
    data['vtarget'].plot(ax=ax['vtarget'])
    data['vmeas'].plot(ax=ax['vmeas'])
    
    m={} #map axes to columns
    for a in ax.keys(): m[a]=[l.get_label() for l in ax[a].get_lines()]
     
    plt.draw()
    fig[0].tight_layout()
    fig[1].tight_layout()
    lastNValues=30000
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
        fig[0].tight_layout()
        fig[1].tight_layout()
        plt.pause(0.1)
    plt.show()

    