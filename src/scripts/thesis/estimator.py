'''
Created on 28 Aug 2017

Generates the data and stores it in a pickle.
There is a lot of filtering involved in the estimator data


@author: Marc Casalprim
'''
print 'Imports...'
import matplotlib as mpl
import pandas as pd
from matplotlib.style import use
from utils.dataset import DataSet,plt,extractGyrosAndStarcam
from utils.field import Field,getDtypes#,getFieldsContaining,getFieldsRegex
from utils.quat import Quat,normalize,sin,cos


if __name__ == '__main__':
    folder='D:/GondolaFlightArchive/17-06-09_01_51_04/'
    
    fieldsList=[]
     
    fieldsList.append(Field('bettii.RTLowPriority.RawStarcameraQuaternionFXPqi',label='qi_sc'))
    fieldsList.append(Field('bettii.RTLowPriority.RawStarcameraQuaternionFXPqj',label='qj_sc'))
    fieldsList.append(Field('bettii.RTLowPriority.RawStarcameraQuaternionFXPqk',label='qk_sc'))
    fieldsList.append(Field('bettii.RTLowPriority.RawStarcameraQuaternionFXPqr',label='qr_sc'))
    fieldsList.append(Field('bettii.RTLowPriority.RawStarcameraDecDeg',label='dec_sc'))
    fieldsList.append(Field('bettii.RTLowPriority.RawStarcameraRaDeg',label='ra_sc'))
    fieldsList.append(Field('bettii.RTLowPriority.RawStarcameraRollDeg',label='roll_sc'))
    fieldsList.append(Field('bettii.RTLowPriority.qr'))
    fieldsList.append(Field('bettii.RTLowPriority.qi'))
    fieldsList.append(Field('bettii.RTLowPriority.qj'))
    fieldsList.append(Field('bettii.RTLowPriority.qk'))
    fieldsList.append(Field('bettii.RTLowPriority.RawStarcameraMceFrameNumberWhenSCTriggered',label='triggers'))
    
    fieldsList.append(Field('bettii.RTHighPriority.estimatedBiasXarcsec',label='biasX'))
    fieldsList.append(Field('bettii.RTHighPriority.estimatedBiasYarcsec',label='biasY'))
    fieldsList.append(Field('bettii.RTHighPriority.estimatedBiasZarcsec',label='biasZ'))

    
    ds = DataSet(folder,fieldsList=fieldsList,min=19061609,max=19712791,verbose=True)

    ds.df=ds.df.interpolate('values')
    
    print 'Dataframe shape:', ds.df.shape
    

    _,sc,quats=extractGyrosAndStarcam(ds.df,labels_gyros=None,label_scerrors=None)
    qGyros2Starcam=sc.qI2S.iloc[0]*sc.qI2G.iloc[0].inv() #(Quat((-0.367,0,0))*Quat((0,-44.9828,0))*Quat((0,0,-0.79))).inv()
    print "qStarcam2Gyros:",qGyros2Starcam.inv()
    
    #initial plot
    print "Plotting..."
    
    use('classic') 
    #mpl.rcParams['toolbar'] = 'None'
    mpl.rcParams['axes.grid'] = True

    SCstyle='go'
    ESTstyle='b+'
    
    fig=plt.figure()
    ax=plt.subplot(311)
    plt.plot(ds.df.index,[q.ra for q in quats['qest']],ESTstyle)
    plt.plot(sc.index,[q.ra for q in sc.qI2G.values],SCstyle)
    ax.legend(['Estimated','Starcamera'])  
    ax.set_xlabel('Time (frames)')
    ax.set_ylabel('RA (deg)')
    
    ax=plt.subplot(312)
    plt.plot(ds.df.index,[q.dec for q in quats['qest']],ESTstyle)
    plt.plot(sc.index,[q.dec for q in sc.qI2G.values],SCstyle)
    ax.legend(['Estimated','Starcamera'])  
    ax.set_xlabel('Time (frames)')
    ax.set_ylabel('DEC (deg)')
    
    ax=plt.subplot(313)
    plt.plot(ds.df.index,[q.roll for q in quats['qest']],ESTstyle)
    plt.plot(sc.index,[q.roll for q in sc.qI2G.values],SCstyle)
    ax.legend(['Estimated','Starcamera'])  
    ax.set_xlabel('Time (frames)')
    ax.set_ylabel('ROLL (deg)')
    
    fig.suptitle('Gondola ref. frame')
    
    fig=plt.figure()
    ax=plt.subplot(311)
    plt.plot(ds.df.index,[(qGyros2Starcam*q).ra for q in quats['qest']],ESTstyle)
    plt.plot(sc.index,[q.ra for q in sc.qI2S.values],SCstyle)
    ax.legend(['Estimated','Starcamera'])  
    ax.set_xlabel('Time (frames)')
    ax.set_ylabel('RA (deg)')
    
    ax=plt.subplot(312)
    plt.plot(ds.df.index,[(qGyros2Starcam*q).dec for q in quats['qest']],ESTstyle)
    plt.plot(sc.index,[q.dec for q in sc.qI2S.values],SCstyle)
    ax.legend(['Estimated','Starcamera'])  
    ax.set_xlabel('Time (frames)')
    ax.set_ylabel('DEC (deg)')
    
    ax=plt.subplot(313)
    plt.plot(ds.df.index,[(qGyros2Starcam*q).roll for q in quats['qest']],ESTstyle)
    plt.plot(sc.index,[q.roll for q in sc.qI2S.values],SCstyle)
    ax.legend(['Estimated','Starcamera'])  
    ax.set_xlabel('Time (frames)')
    ax.set_ylabel('ROLL (deg)')
    
    fig.suptitle('SC ref. frame')

    for i in sc.index:
        qI2S=sc.loc[i].qI2S
        qI2G=sc.loc[i].qI2G
        qS2G=qI2G*qI2S.inv()
        print "qS2G: "+str(qS2G)
    
    plt.show()

    