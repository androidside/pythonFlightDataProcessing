'''
Created on 28 abr. 2017

Main script

@author: Marc Casalprim
'''
print 'Imports...'
import matplotlib
import numpy as np
from utils.quat import Quat,normalize,sin,cos
from utils.dataset import DataSet,plt,sns,load_single_field
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
    fieldsList.append(Field('bettii.RTHighPriority.GondolaRaDeg'))
    fieldsList.append(Field('bettii.RTHighPriority.GondolaRaDeg'))
    fieldsList.append(Field('bettii.RTLowPriority.qr'))
    fieldsList.append(Field('bettii.RTLowPriority.qi'))
    fieldsList.append(Field('bettii.RTLowPriority.qj'))
    fieldsList.append(Field('bettii.RTLowPriority.qk'))
    fieldsList.append(Field('bettii.RTLowPriority.RawStarcameraQuaternionFXPqi',label='qi_sc'))
    fieldsList.append(Field('bettii.RTLowPriority.RawStarcameraQuaternionFXPqj',label='qj_sc'))
    fieldsList.append(Field('bettii.RTLowPriority.RawStarcameraQuaternionFXPqk',label='qk_sc'))
    fieldsList.append(Field('bettii.RTLowPriority.RawStarcameraQuaternionFXPqr',label='qr_sc'))
     
    fieldsList.append(Field('bettii.RTLowPriority.RawStarcameraDecDeg',label='dec_sc'))
    fieldsList.append(Field('bettii.RTLowPriority.RawStarcameraRollDeg',label='roll_sc'))
    fieldsList.append(Field('bettii.RTLowPriority.RawStarcameraRaDeg',label='ra_sc'))
    fieldsList.append(Field('bettii.RTLowPriority.RawStarcameraAzDeg',label='az_sc',conversion=1))
    fieldsList.append(Field('bettii.RTLowPriority.RawStarcameraElDeg',label='el_sc',conversion=1))
    
    #===========================================================================
    # fieldsList.append(Field('bettii.RTHighPriority.SCAnglesInertialGondolaRefFrameArcsecDec',label='dec_sc',conversion=1/3600.))
    # fieldsList.append(Field('bettii.RTHighPriority.SCAnglesInertialGondolaRefFrameArcsecRa',label='ra_sc',conversion=1/3600.))
    # fieldsList.append(Field('bettii.RTHighPriority.SCAnglesInertialGondolaRefFrameArcsecRoll',label='roll_sc',conversion=1/3600.))
    #===========================================================================
    
    #fieldsList.append(Field('bettii.GriffinsGalil.griffinAAngleDegrees',label='griffin_angle')) #44.114721
    griffin_angle=44.114721
    
    
    #===========================================================================
    # fieldsList.append(Field('bettii.GyroReadings.angularVelocityX',label='gyroX',dtype='i4',conversion=0.0006304))
    # fieldsList.append(Field('bettii.GyroReadings.angularVelocityY',label='gyroY',dtype='i4',conversion=0.0006437))
    # fieldsList.append(Field('bettii.GyroReadings.angularVelocityZ',label='gyroZ',dtype='i4',conversion=0.0006324))
    #===========================================================================
   
    #fieldsList = getFieldsContaining('CCMG',folder)   
    
    #fieldsList = getFieldsRegex('bettii.[U-Z]+',folder)
    
    #target 1    
    initial_time=5145000 #in frame number
    final_time = 5149000 #in frame number
    
    #===========================================================================
    # initial_time=None #in frame number
    # final_time = None #in frame number
    #===========================================================================
    
    
    ds = DataSet(folder,fieldsList=fieldsList,estimator=False,starcam=False,min=initial_time,max=final_time,verbose=False)
    
    print 'Dataframe shape:', ds.df.shape
    t=5145804 #interesting time
    d=ds.df.loc[t]

    qI2Starcam=Quat(d[['ra_sc','dec_sc','roll_sc']])
    q=Quat(d[['qi_sc','qj_sc','qk_sc','qr_sc']]) #meas_q qI2Gyros
    
    #array([ -0.15321407, -44.77279865,  19.87575523])
    dYaw=-0.15321407
    dPitch=44.77279865
    dRoll=19.87575523#-3.99
    errRoll=0.1
     
    qdYaw = Quat((dYaw,0,0)); #quat = Quat((ra,dec,roll)) in degrees
    qdPitch = Quat((0.0,sin(dPitch*np.pi/180./2.0),0.0,cos(dPitch*np.pi/180./2.0))) #quat = Quat((ra,dec,roll)) in degrees
    qdRoll = Quat((0,0,dRoll+errRoll)) #quat = Quat((ra,dec,roll)) in degrees
    
    qStarcam2Gyros =  (qdYaw*(qdPitch*qdRoll))
    
    S2C=np.array([ 18.45660617, -41.54825556,  26.86634329]) #ra,dec,roll converted from dYaw,-dPitch,dRoll == array([ -0.15321407, -44.77279865,  19.87575523])
    qStarcam2Gyros2 =  Quat(S2C+(0,0,errRoll))     #
    
    qI2Gyros =  qStarcam2Gyros*qI2Starcam
    qI2Gyros2 =  qStarcam2Gyros2*qI2Starcam
    
    qGyros2Tel = Quat((0,griffin_angle,0))
    
    q_est=Quat(d[['qi','qj','qk','qr']])
    #q_meas = d['meas_q'];

    print 'qI2Starcam: ', qI2Starcam.equatorial
    print 'qStarcam2Gyros: ', qStarcam2Gyros.equatorial
    print 'qStarcam2Gyros2: ', qStarcam2Gyros2.equatorial
    print
    print 'q_estimator :', q_est.equatorial
    print
    print 'Without error in roll:'
    print 'qI2Gyros : ', ((qdYaw*(qdPitch*Quat((0,0,dRoll))))*qI2Starcam).equatorial
    print 'qI2Gyros2: ', (Quat(S2C)*qI2Starcam).equatorial
    print
    print 'With error in roll:',errRoll,'deg'
    print 'qI2Gyros : ', qI2Gyros.equatorial
    print 'qI2Gyros2: ', qI2Gyros2.equatorial
    print
    print 'qGyros2Tel: ', qGyros2Tel.equatorial
    print
    print 'qI2Tel :',(qGyros2Tel*qI2Gyros).equatorial
    print 'qI2Tel2:',(qGyros2Tel*qI2Gyros2).equatorial
    print 'qI2Tel_est:',(qGyros2Tel*q_est).equatorial
    print 'TelescopeRa, TelescopeDec :',d['TelescopeRaDeg'],d['TelescopeDecDeg']
    print 'TargetRa, TargetDec :',d['targetRA'],d['targetDEC']
    
    
    a=1
    



    
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
#===============================================================================
#     
#     ind=ds.df.index
# us=[i*2500 for i in ds.df.index]
# dic={'year': [2017] * len(us), 'month': [04] * len(us), 'day': [24] * len(us), 'us': us}
# dfdt=ds.df.set_index(pd.to_datetime(pd.DataFrame(dic)).values)
# rs=dfdt.resample('1ms')
#===============================================================================
#===============================================================================
# from scipy.optimize import fmin   
# def costFunc(x):
#     ra,dec,roll=x
#     qY = Quat((ra,0,0))
#     qP = Quat((0,dec,0))
#     qR = Quat((0,0,roll))
#     Q=qY*(qP*qR)
#     dif=Q.equatorial-np.array([ 18.45660617, -41.54825556,  26.86634329])
#     return np.sqrt(np.dot(dif, dif))
# 
# xo=np.array([18,-40,26])
# xopt=fmin(costFunc,xo)
#===============================================================================