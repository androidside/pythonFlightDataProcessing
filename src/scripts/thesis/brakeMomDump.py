'''
Created on Jul 7, 2017

@author: bettii
'''
'''
Created on 28 jun. 2017

Script for scripts simultaneously data from different archives

@author: Marc Casalprim
'''
print 'Imports...'
import os
import matplotlib as mpl
from matplotlib.style import use
from utils.dataset import DataSet,plt,np,pd
from utils.field import Field
from timeit import default_timer as timer


if __name__ == '__main__':

    folder='F:/GondolaFlightArchive/17-06-09_01_51_04/'
    save_folder='C:/Users/bettii/thesis/'
    img_folder=save_folder+'plots/brake/'
    savefilename='MomDump.pkl'
    
    if not os.path.exists(img_folder):
        os.makedirs(img_folder)
    
    read=False
    if read:
        start_time = timer()
        
        fieldsList=[]
        fieldsList.append(Field('bettii.GyroReadings.angularVelocityZ',label='Gyro Z',dtype='i4',conversion=0.0006324,range=2e5))
        fieldsList.append(Field('bettii.RTHighPriority.EstimatedAzimuthVelocityArcsec',label='vaz_est',range=2e5))
        fieldsList.append(Field('bettii.StepperGalil.wheelsAngle',label='wheels_angle'))
        fieldsList.append(Field('bettii.PIDOutputMomDump.ut'))
        fieldsList.append(Field('bettii.PIDOutputMomDump.et'))
        fieldsList.append(Field('bettii.PIDOutputMomDump.derivative'))
        fieldsList.append(Field('bettii.PIDOutputMomDump.integral'))
        fieldsList.append(Field('bettii.PIDOutputMomDump.proportional'))

    
                
        ds = DataSet(fieldsList=fieldsList,folder=folder,verbose=True,min=12300000,max=19400000,timeIndex=True)
        
        print "Converting to Palestine Time..."
        ds.df.index=ds.df.index-pd.Timedelta(hours=5) #Palestine time conversion (Archives folder names are in UTC)
        df=ds.df
        
        df=df.ix[pd.to_datetime('06/08/2017 23:05:00'):]
        print "Elapsed time:",timer()-start_time,"seconds."
        print "Saving.."
        df.to_pickle(save_folder+savefilename)
        print "Saved"
    else:
        start_time = timer()
        print "Reading..."
        df = pd.read_pickle(save_folder+savefilename)
        print "Elapsed time:",timer()-start_time,"seconds."   
    
    print "Generating plots.."
    
    use('seaborn-bright')
    mpl.rcParams['axes.grid']=True
    plt.rc('font', family='serif')

    time_label='Palestine Time'
    
    M=10 #downsample factor
    df=df.iloc[::M]
        
    print "Plotting measured azimuth..."
    fig=plt.figure()
    ax=plt.subplot(111,xlabel=time_label, ylabel='Measured azimuth velocity [arcsec/s]')
    data=df['Gyro Z'].dropna()
    data.plot(ax=ax,style='b',markersize=1.0)
    fig.tight_layout()
    fig.savefig(img_folder+"vaz_gyroscope.png")
    
    print "Plotting estimated azimuth..."
    fig=plt.figure()
    ax=plt.subplot(111,xlabel=time_label, ylabel='Estimated azimuth velocity [arcsec/s]')
    data=df['vaz_est'].dropna()
    data.plot(ax=ax,style='b',markersize=1.0)
    fig.tight_layout()
    fig.savefig(img_folder+"vaz_estimated.png")
    
    print "Plotting wheels angle..."
    fig=plt.figure()
    ax=plt.subplot(111,xlabel=time_label, ylabel='Wheels angle [deg]')
    data=df['wheels_angle'].dropna()
    data.plot(ax=ax,style='b',markersize=1.0)
    fig.tight_layout()
    fig.savefig(img_folder+"wheels_angle.png")

    print "Plotting MomDump ut..."
    fig=plt.figure()
    ax=plt.subplot(111,xlabel=time_label, ylabel='Command [counts/s]')
    data=df.ut.dropna()
    data.plot(ax=ax,style='b',markersize=1.0)
    fig.tight_layout()
    fig.savefig(img_folder+"ut_rotator.png")
    
    print "Plotting MomDump et..."
    fig=plt.figure()
    ax=plt.subplot(111,xlabel=time_label, ylabel='Error')
    data=df.et.dropna()
    data.plot(ax=ax,style='r',markersize=1.0)
    fig.tight_layout()
    fig.savefig(img_folder+"et_rotator.png")
    
    print "Plotting MomDump PID..."
    fig=plt.figure()
    ax=plt.subplot(111,xlabel=time_label, ylabel='Command [counts/s]')
    data=df[['derivative','proportional','integral']].dropna()
    data.plot(ax=ax,style=['r','g','b'],markersize=1.0)
#    plt.legend(markerscale=3,numpoints=20)
    ax.set_ylim([-1300,1300])
    fig.tight_layout()
    fig.savefig(img_folder+"PID_rotator.png")

    print "Show..."
    plt.show()