'''Code to debug the delay in the estimated target RA,DEC crossings seen on Fort Summer.

Solved! Bad converesion from arcseconds to degrees in LabView
'''
print 'Imports...'


import pandas as pd
from numpy import sin,cos,arctan2,pi,sqrt
from utils.quat import Quat
from utils.dataset import DataSet,plt, genQuaternions
from utils.field import Field,getDtypes#,getFieldsContaining,getFieldsRegex



if __name__ == '__main__':
    #folder = "C:/17-04-24_19_02_57/"
    #folder = "\\\\GS66-WHITE\\LocalAuroraArchive\\17-05-02_18_01_58\\"
    
    
    folder='X:/16-09-28_21_58_34-/'
    
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
    fieldsList.append(Field('bettii.RTLowPriority.qr'))
    fieldsList.append(Field('bettii.RTLowPriority.qi'))
    fieldsList.append(Field('bettii.RTLowPriority.qj'))
    fieldsList.append(Field('bettii.RTLowPriority.qk'))
    fieldsList.append(Field('bettii.GriffinsGalil.griffinBAngleDegrees'))
    fieldsList.append(Field('bettii.RTHighPriority.estimatedBiasXarcsec',label='biasX'))
    fieldsList.append(Field('bettii.RTHighPriority.estimatedBiasYarcsec',label='biasY')) 
    fieldsList.append(Field('bettii.RTHighPriority.estimatedBiasZarcsec',label='biasZ')) 
    #fieldsList.append(Field('bettii.PIDOutputCCMG.et',label='et_ccmg'))
   
    fieldsList.append(Field('bettii.RTHighPriority.EstimatorErrorRespectLastSCAzArcsec',label='err_az'))
    fieldsList.append(Field('bettii.RTHighPriority.EstimatorErrorRespectLastSCElArcsec',label='err_el'))
    fieldsList.append(Field('bettii.RTHighPriority.EstimatorErrorRespectLastSCRollArcsec',label='err_roll'))
    #fieldsList = getFieldsContaining('CCMG',folder)   
    
    #fieldsList = getFieldsRegex('bettii.[U-Z]+',folder)
    
    #target 1   
    initial_time=5145000 #in frame number
    final_time = 5149000 #in frame number
    
    #target 2
    initial_time=6301000 #in frame number
    final_time = 6303000 #in frame number
    
    initial_time=5350000 #in frame number
    final_time = 5600000 #in frame number
    
    #ds = DataSet(folder,fieldsList=fieldsList,starcam=True,min=initial_time,max=final_time,verbose=True)
    ds = DataSet(folder,fieldsList=fieldsList,start=0,nValues=1081500,min=initial_time,max=final_time,verbose=True)
    ds.df=ds.df.interpolate(method='values')
    print "Removing peaks.."
    ds.df=ds.df.loc[(ds.df[['TelescopeDecDeg']].abs()>=17).any(1)] #remove all decs less than 1
    ds.df=ds.df.loc[(ds.df[['TelescopeRaDeg']].abs()>=170).any(1)]
    ds.df=ds.df.loc[(ds.df[['targetDEC']].abs()>=17).any(1)]

    print 'Dataframe shape:', ds.df.shape
    
    print "Generating quaternions..."
    quats=genQuaternions(ds.df,quats={'qest':['qi','qj','qk','qr']})
    print "Calculating telescope..."
    targetRA=ds.df.targetRA.iloc[0]*pi/180
    targetDEC=ds.df.targetDEC.iloc[0]*pi/180
    #targetRA to Cartesian
    x=cos(targetRA)*cos(targetDEC)
    y=sin(targetRA)*cos(targetDEC)
    z=sin(targetDEC)
    targetqV=Quat([x,y,z,0])
    quats['qtelRA']=[]
    quats['qtelDEC']=[]
    quats['el']=[]
    quats['xel']=[]
    for i,qest in enumerate(quats['qest']):
        angle=ds.df.griffinBAngleDegrees.iloc[i]
        tra=ds.df.TelescopeRaDeg.iloc[i]
        tdec=ds.df.TelescopeDecDeg.iloc[i]
        qG2T=Quat((0,angle,0))
        qI2T=qG2T*qest
        qV=qI2T*targetqV*(qI2T.inv())
        v=qV.q[:3]
        xel=arctan2(v[1],v[0])
        el=arctan2(v[2],sqrt(v[0]**2+v[1]**2))
        quats['qtelRA'].append(qI2T.ra+360)
        quats['qtelDEC'].append(qI2T.dec)
        quats['el'].append(el*180/pi*3600)
        quats['xel'].append(xel*180/pi*3600)
    
    teldata= pd.DataFrame(quats,index = ds.df.index)
    ds.df=pd.merge(ds.df,teldata,how='outer',left_index=True,right_index=True)
    
    print "Plotting..."
    
    #scripts RA and DEC target vs estimated
    plt.figure(1)
    data = ds.df.dropna()
    ax1=plt.subplot(211,xlabel='Time (frames)',ylabel='DEC (deg)')
    ax2=plt.subplot(212,xlabel='Time (frames)',ylabel='RA (deg)')
    
    data[['targetDEC','TelescopeDecDeg','qtelDEC']].plot(ax=ax1)
    data[['targetRA','TelescopeRaDeg','qtelRA']].plot(ax=ax2)

    #scripts RA and DEC estimated-target  estimated
    plt.figure(2)
    ax3=plt.subplot(211,xlabel='Time (frames)',ylabel='DEC error (deg)')
    ax4=plt.subplot(212,xlabel='Time (frames)',ylabel='RA error (deg)')
    errDEC=(data.TelescopeDecDeg.subtract(data.targetDEC))
    errDEC.plot(ax=ax3)
    errRA=(data.TelescopeRaDeg.subtract(data.targetRA))
    errRA.plot(ax=ax4)
    
    errDECnew=(data.qtelDEC.subtract(data.targetDEC))
    errRAnew=(data.qtelRA.subtract(data.targetRA))
    
    #scripts elevation and crossElevation
    plt.figure(3)
    ax5=plt.subplot(221,xlabel='Time (frames)',ylabel='elevation (arcsec)')
    ax6=plt.subplot(223,xlabel='Time (frames)',ylabel='crossElevation (arcsec)')
    ax7=plt.subplot(122,xlabel='CrossElevation (arcsec)',ylabel='Elevation (arcsec)')
    data[['elevation','el']].plot(ax=ax5)
    data[['crossElevation','xel']].plot(ax=ax6)
    data.plot(ax=ax7,x='crossElevation',y='elevation',legend=None)
    ax7.set_xlabel('CrossElevation(arcsec)')
    crossxEl=data['crossElevation'].abs().argmin()
    
    plt.figure(4)
    data=ds.df[['biasX','biasY','biasZ']].dropna()
    ax8=plt.subplot(311,ylabel='biasX (arcsec)')
    ax9=plt.subplot(312,ylabel='biasY (arcsec)')
    ax10=plt.subplot(313,xlabel='Time (frames)',ylabel='biasZ (arcsec)')
    data['biasX'].plot(ax=ax8)
    data['biasY'].plot(ax=ax9)
    data['biasZ'].plot(ax=ax10)
    
    
    plt.figure(6)
    data=ds.df[['err_az','err_el','err_roll']].dropna()
    ax11=plt.subplot(311,ylabel='Error Az (arcsec)')
    ax12=plt.subplot(312,ylabel='Error El (arcsec)')
    ax13=plt.subplot(313,xlabel='Time (frames)',ylabel='Error Roll (arcsec)')
    data['err_az'].plot(ax=ax11)
    data['err_el'].plot(ax=ax12)
    data['err_roll'].plot(ax=ax13)
    
     
    crossDEC=errDEC.abs().argmin()
    crossRA=errRA.abs().argmin()
    crossDECnew=errDECnew.abs().argmin()
    crossRAnew=errRAnew.abs().argmin()

    
    ax1.axvline(x=crossDEC,color='g')
    ax2.axvline(x=crossRA,color='g')
    ax1.axvline(x=crossDECnew,color='r')
    ax2.axvline(x=crossRAnew,color='r')
    ax6.axvline(x=crossxEl)
    
    
    
    print "Min Err. DEC:",crossDEC
    print "Min Err. RA:",crossRA

    print "Gap:",(crossDEC-crossRA)/400.,"seconds"
    
    print "Min Err. DEC:",crossDECnew
    print "Min Err. RA:",crossRAnew

    print "Gap:",(crossDECnew-crossRAnew)/400.,"seconds"
    print "0 crossElevation:",crossxEl

    
    #===========================================================================
    # print errDEC.loc[crossRA:crossDEC]
    # print errRA.loc[crossRA:crossDEC]
    #===========================================================================
    
    
    a=1    
    plt.show()
    plt.pause(1)