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
    #folder = "\\\\GS66-WHITE\\LocalAuroraArchive\\17-05-02_18_01_58\\"
    
    
    folder='C:/16-09-28_21_58_34-/'
    
    Field.DTYPES=getDtypes(folder)
    
    fieldsList=[]
     
    fieldsList.append(Field('bettii.RTHighPriority.crossElevation'))
    fieldsList.append(Field('bettii.RTHighPriority.elevation'))
    fieldsList.append(Field('bettii.RTHighPriority.TelescopeDecDeg'))
    fieldsList.append(Field('bettii.RTHighPriority.TelescopeRaDeg'))
    fieldsList.append(Field('bettii.RTHighPriority.targetDEC'))
    fieldsList.append(Field('bettii.RTHighPriority.targetRA'))
    fieldsList.append(Field('bettii.RTHighPriority.GondolaDecDeg'))
    fieldsList.append(Field('bettii.RTHighPriority.GondolaRaDeg'))
    fieldsList.append(Field('bettii.GriffinsGalil.griffinAAngleDegrees'))
    fieldsList.append(Field('bettii.RTHighPriority.estimatedBiasXarcsec',label='biasX'))
    fieldsList.append(Field('bettii.RTHighPriority.estimatedBiasYarcsec',label='biasY')) 
    fieldsList.append(Field('bettii.RTHighPriority.estimatedBiasZarcsec',label='biasZ')) 
    fieldsList.append(Field('bettii.PIDOutputCCMG.et',label='et_ccmg'))
    fieldsList.append(Field('bettii.GyroReadings.angularVelocityX',label='gyroX',dtype='i4',conversion=0.0006304))
    fieldsList.append(Field('bettii.GyroReadings.angularVelocityY',label='gyroY',dtype='i4',conversion=0.0006437))
    fieldsList.append(Field('bettii.GyroReadings.angularVelocityZ',label='gyroZ',dtype='i4',conversion=0.0006324))
   
    fieldsList.append(Field('bettii.RTHighPriority.EstimatorErrorRespectLastSCAzArcsec',label='err_az'))
    fieldsList.append(Field('bettii.RTHighPriority.EstimatorErrorRespectLastSCElArcsec',label='err_el'))
    fieldsList.append(Field('bettii.RTHighPriority.EstimatorErrorRespectLastSCRollArcsec',label='err_roll'))
    #fieldsList = getFieldsContaining('CCMG',folder)   
    
    #fieldsList = getFieldsRegex('bettii.[U-Z]+',folder)
    
    #target 1
    
    #===========================================================================
    # initial_time=None #in frame number
    # final_time = None #in frame number
    #===========================================================================
    
    initial_time=5145000 #in frame number
    final_time = 5149000 #in frame number
    
    #target 2
    
    #===========================================================================
    # initial_time=6301000 #in frame number
    # final_time = 6303000 #in frame number
    #===========================================================================
    
    initial_time=1000 #in frame number
    final_time = None #in frame number
    
    ds = DataSet(folder,fieldsList=fieldsList,starcam=True,min=initial_time,max=final_time,verbose=True)
    
    print 'Dataframe shape:', ds.df.shape
    data=ds.df.interpolate(method='values')
    #data.index=data.index/ds.freq #index in seconds
    matplotlib.style.use('classic')
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
    
    plt.figure(4)
    data=ds.df[['biasX','biasY','biasZ']].dropna()
    ax1=plt.subplot(311,ylabel='biasX (arcsec)')
    ax2=plt.subplot(312,ylabel='biasY (arcsec)')
    ax3=plt.subplot(313,xlabel='Time (frames)',ylabel='biasZ (arcsec)')
    data['biasX'].plot(ax=ax1)
    data['biasY'].plot(ax=ax2)
    data['biasZ'].plot(ax=ax3)
    
    plt.figure(5)
    data=ds.df['et_ccmg'].dropna()
    ax1=plt.subplot(111,ylabel='CCMG et')
    data.plot(ax=ax1)
    
    plt.figure(6)
    data=ds.df[['err_az','err_el','err_roll']].dropna()
    ax1=plt.subplot(311,ylabel='Error Az (arcsec)')
    ax2=plt.subplot(312,ylabel='Error El (arcsec)')
    ax3=plt.subplot(313,xlabel='Time (frames)',ylabel='Error Roll (arcsec)')
    data['err_az'].plot(ax=ax1)
    data['err_el'].plot(ax=ax2)
    data['err_roll'].plot(ax=ax3)


    
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

     

    print errRA[errRA.abs()<1e-3]
    print errDEC[errDEC.abs()<1e-3]
        
    plt.show()
    plt.pause(1)