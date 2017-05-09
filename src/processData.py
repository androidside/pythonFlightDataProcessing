'''
Created on 28 abr. 2017

Main script

@author: Marc Casalprim
'''
print 'Imports...'
import matplotlib
from utils.dataset import DataSet,plt,sns
from utils.field import Field#,getFieldsContaining,getFieldsRegex



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
      
    #===========================================================================
    # fieldsList.append(Field('bettii.GyroReadings.angularVelocityX',label='gyroX',dtype='i4',conversion=0.0006304))
    # fieldsList.append(Field('bettii.GyroReadings.angularVelocityY',label='gyroY',dtype='i4',conversion=0.0006437))
    # fieldsList.append(Field('bettii.GyroReadings.angularVelocityZ',label='gyroZ',dtype='i4',conversion=0.0006324))
    #===========================================================================
   
    #fieldsList = getFieldsContaining('CCMG',folder)   
    
    #fieldsList = getFieldsRegex('bettii.[U-Z]+',folder)
    
    #target 1
    
    initial_time=5147000 #in frame number
    final_time = 5149000 #in frame number
    
    #target 2
    #===========================================================================
    # initial_time=6301000 #in frame number
    # final_time = 6303000 #in frame number
    #===========================================================================
    
    #===========================================================================
    # initial_time=None #in frame number
    # final_time = None #in frame number
    #===========================================================================
    
    ds = DataSet(folder,fieldsList=fieldsList,min=initial_time,max=final_time,verbose=True)
    
    print 'Dataframe shape:', ds.df.shape
    data=ds.df.dropna()
    #data.index=data.index/ds.freq #index in seconds
    matplotlib.style.use('ggplot')
    #plotting RA and DEC target vs estimated
    plt.figure(1)
    ax1=plt.subplot(211,xlabel='Time (frames)',ylabel='DEC (deg)')
    ax2=plt.subplot(212,xlabel='Time (frames)',ylabel='RA (deg)')
    
    data[['targetDEC','TelescopeDecDeg']].plot(ax=ax1)
    data[['targetRA','TelescopeRaDeg']].plot(ax=ax2)
    
    #plotting RA and DEC estimated-target  estimated
    plt.figure(2)
    ax1=plt.subplot(211,xlabel='Time (frames)',ylabel='DEC error (deg)')
    ax2=plt.subplot(212,xlabel='Time (frames)',ylabel='RA error (deg)')
    errDEC=(data.TelescopeDecDeg.subtract(data.targetDEC))
    errDEC.plot(ax=ax1)
    errRA=(data.TelescopeRaDeg.subtract(data.targetRA))
    errRA.plot(ax=ax2)

    
    #plotting elevation and crossElevation
    plt.figure(3)
    ax1=plt.subplot(221,xlabel='Time (frames)',ylabel='elevation (arcsec)')
    ax2=plt.subplot(223,xlabel='Time (frames)',ylabel='crossElevation (arcsec)')
    ax3=plt.subplot(122,xlabel='CrossElevation (arcsec)',ylabel='Elevation (arcsec)')
    data['elevation'].plot(ax=ax1)
    data['crossElevation'].plot(ax=ax2)
    data.plot(ax=ax3,x='crossElevation',y='elevation',legend=None)
    ax3.set_xlabel('CrossElevation(arcsec)')
    


    
    #===========================================================================
    # f=ds.simplePlot('AI0')
    # 
    # g=ds.multiPSD(['AI0','AI2','AI7'])
    #===========================================================================
    
    #print 'Plotting scatter plot...'
    #g = sns.pairplot(ds.df.dropna())
 
    #===========================================================================
    # print ds.df['crossElevation'].dropna()
    # print ds.df['gyroX']
    # f=ds.simplePlot('crossElevation')
    # i=ds.simplePlot('gyroX')
    # data = ds.df[['elevation','crossElevation','TelescopeDecDeg']].dropna()
    #  
    # sns.set(style="ticks", color_codes=True)
    #  
    # plt.figure()    
    # h=sns.tsplot(data.elevation,color='blue')
    #===========================================================================
 
     
    #plt.draw()
    #print ds.df
    #ds.simplePlot('elevation')
    #===========================================================================
    # gyros = ['gyroX','gyroY','gyroZ']
    # 
    # ds.plotGyros(show=show)
    # fig,axlist = plt.subplots(3,figsize=(5.9,8),dpi=120)
    # for i in range(3):
    #     ax = axlist[i]
    #     ax.scatter(ds.df.index/400.,ds.df[gyros[i]],color=blue)
    # plt.show()
    # ds.multiPSD(gyros,show=show,loglog=True)
    # ds.multiPSD(gyros,show=show,loglog=False,name="multiPSD_no_loglog")
    # ds.multiPSD(gyros,show=show,loglog=False,name="multiPSD_no_loglog_zoom",minMax=[24,28])
    # 
    # ds.scatterPlots(['gyroX','gyroY'],show=show)
    # ds.scatterPlots(['gyroX','gyroZ'],show=show)
    # ds.scatterPlots(['gyroY','gyroZ'],show=show)
    #===========================================================================
    plt.show()
#===============================================================================
#     
#     ind=ds.df.index
# us=[i*2500 for i in ds.df.index]
# dic={'year': [2017] * len(us), 'month': [04] * len(us), 'day': [24] * len(us), 'us': us}
# dfdt=ds.df.set_index(pd.to_datetime(pd.DataFrame(dic)).values)
# rs=dfdt.resample('1ms')
#===============================================================================
    