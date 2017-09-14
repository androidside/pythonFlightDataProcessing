'''
Created on 17 may 2017

RT plottin gof the estimated biases.

@author: Marc Casalprim
'''
print 'Imports...'
from utils.dataset import DataSet,plt
from utils.field import Field,getDtypes#,getFieldsContaining,getFieldsRegex



if __name__ == '__main__':
    folder = "C:/17-05-17_00_36_34/"
    folder = "\\\\GS66-WHITE\\LocalAuroraArchive\\17-05-24_00_50_03\\"
    
    Field.DTYPES=getDtypes(folder)

    
    fieldsList=[]
     
    fieldsList.append(Field('bettii.RTHighPriority.estimatedBiasXarcsec',label='bx'))
    fieldsList.append(Field('bettii.RTHighPriority.estimatedBiasYarcsec',label='by'))
    fieldsList.append(Field('bettii.RTHighPriority.estimatedBiasZarcsec',label='bz'))

    
    ds = DataSet(folder,rpeaks=True)
    ds.readListFields(fieldsList, nValues=1000,verbose=True,rpeaks=False)   
    #ds.readListFields(fieldsList, nValues=nValues,start=nValues*i,verbose=False) #for simulation
    data=ds.df
    #initial plot
    fig=[]
    ax={}
    fig.append(plt.figure(1)) 
    ax['x']=(plt.subplot(311,ylabel='bias X (arcsec)'))
    ax['y']=(plt.subplot(312,ylabel='bias Y (arcsec)'))
    ax['z']=(plt.subplot(313,xlabel='Time (frames)',ylabel='bias Z (arcsec)'))

    
    data['bx'].plot(ax=ax['x'])
    data['by'].plot(ax=ax['y'])
    data['bz'].plot(ax=ax['z'])
    
    
    #for a in ax.values(): a.get_yaxis().get_major_formatter().set_useOffset(False)

    
    m={} #map axes to columns
    for a in ax.keys(): m[a]=[l.get_label() for l in ax[a].get_lines()]
    
    #plt.ion()
     
    plt.draw()
    fig[0].tight_layout()
    lastNValues=40000
    nValues=1200
    i=-1
    while True:
        #i=i+1
        #print 'Reading bytes from '+str(nValues*i)+' to '+str(nValues*(i+1)) 
        ds.readListFields(fieldsList, nValues=nValues,verbose=False,rpeaks=False)   
        #i=i+1;ds.readListFields(fieldsList, nValues=nValues,start=nValues*i,verbose=False) #for simulation
        #if lastN
        st=max(ds.df.index)-lastNValues #starting time for the x axis
        data=ds.df.loc[st:,:]

        #scripts elevation and crossElevation
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
        plt.pause(0.1)
    plt.show()

    