'''
Created on 28 abr. 2017

Main script

@author: Marc Casalprim
'''
print 'Imports...'
from utils.dataset import DataSet,plt
from utils.field import Field,getDtypes#,getFieldsContaining,getFieldsRegex



if __name__ == '__main__':
    folder = "C:/17-05-17_00_36_34/"
    folder = "\\\\GS66-WHITE\\LocalAuroraArchive\\17-05-24_00_40_24\\"
    
    Field.DTYPES=getDtypes(folder)

    
    fieldsList=[]
     
    fieldsList.append(Field('bettii.RTHighPriority.TelescopeRaDeg',label='tra'))
    fieldsList.append(Field('bettii.RTHighPriority.TelescopeDecDeg',label='tdec'))
    fieldsList.append(Field('bettii.RTHighPriority.GondolaRaDeg',label='gra'))
    fieldsList.append(Field('bettii.RTHighPriority.GondolaDecDeg',label='gdec'))
    fieldsList.append(Field('bettii.RTLowPriority.RawStarcameraRaDeg',label='sra'))
    fieldsList.append(Field('bettii.RTLowPriority.RawStarcameraDecDeg',label='sdec'))

    fieldsList.append(Field('bettii.GriffinsGalil.griffinAAngleDegrees',label='gangle'))

    
    ds = DataSet(folder,rpeaks=True)
    ds.readListFields(fieldsList, nValues=1000,verbose=True)   
    #ds.readListFields(fieldsList, nValues=nValues,start=nValues*i,verbose=False) #for simulation
    data=ds.df
    #initial plot
    fig=[]
    ax={}
    fig.append(plt.figure(1)) 
    ax['sra']=(plt.subplot(231,ylabel='RA (deg)'))
    ax['sdec']=(plt.subplot(234,xlabel='Time (frames)',ylabel='DEC (deg)'))
    ax['gra']=(plt.subplot(232))
    ax['gdec']=(plt.subplot(235,xlabel='Time (frames)'))
    ax['tra']=(plt.subplot(233))
    ax['tdec']=(plt.subplot(236,xlabel='Time (frames)'))
    fig.append(plt.figure(2))
    ax['gangle']=(plt.subplot(111,xlabel='Time (frames)',ylabel='Griffin A Angle (deg)'))
    
    ax['sra'].set_title('StarCamera')
    ax['gra'].set_title('Gondola')
    ax['tra'].set_title('Telescope')
    
    for a in ax.values(): a.get_yaxis().get_major_formatter().set_useOffset(False)

    
    data['tra'].plot(ax=ax['tra'])
    data['tdec'].plot(ax=ax['tdec'])
    data['gra'].plot(ax=ax['gra'])
    data['gdec'].plot(ax=ax['gdec'])
    data['sra'].plot(ax=ax['sra'])
    data['sdec'].plot(ax=ax['sdec'])
    data['gangle'].plot(ax=ax['gangle'])
    
    m={} #map axes to columns
    for a in ax.keys(): m[a]=[l.get_label() for l in ax[a].get_lines()]
    
    #plt.ion()
     
    plt.draw()
    fig[0].tight_layout()
    lastNValues=4000
    nValues=1200
    i=-1
    while True:
        #i=i+1
        #print 'Reading bytes from '+str(nValues*i)+' to '+str(nValues*(i+1)) 
        ds.readListFields(fieldsList, nValues=nValues,verbose=False,rpeaks=True)   
        #i=i+1;ds.readListFields(fieldsList, nValues=nValues,start=nValues*i,verbose=False) #for simulation
        data=ds.df.loc[max(ds.df.index)-lastNValues:,:]

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

    