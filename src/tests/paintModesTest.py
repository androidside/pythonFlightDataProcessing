'''
Created on Sep 22, 2017
'''
print 'Imports...'
from utils.config import flightDisksFolders,plt,save_folder,img_folder
from utils.dataset import DataSet,pd,plotColumns, filterDataframe, paintModes
from utils.field import Field

if __name__ == '__main__':
    folder = "C:/LocalAuroraArchive/17-05-30_19_44_12/"
    fieldsList=[]
    fieldsList.append(Field('bettii.PIDOutputCCMG.ut',label='ccmg_ut'))
    fieldsList.append(Field('bettii.PIDOutputCCMG.et',label='ccmg_et'))
    fieldsList.append(Field('bettii.PIDOutputCCMG.proportional',label='P CCMG',range=3e6))
    fieldsList.append(Field('bettii.PIDOutputCCMG.integral',label='I CCMG'))
    fieldsList.append(Field('bettii.PIDOutputCCMG.derivative',label='D CCMG'))
    fieldsList.append(Field('bettii.FpgaState.state',label='modes',range=6))
    
    ds = DataSet(fieldsList=fieldsList, folder=folder, verbose=True, rpeaks=False,timeIndex=True)
    time_label = 'Palestine Time'
    print "Plotting.."
    fig = plt.figure()
    fig.suptitle("CCMG PID contributions", fontsize=15, y=1)
    ax = plt.subplot(111, xlabel=time_label, ylabel='CCMG PID contributions')
    data = ds.df[['P CCMG', 'I CCMG', 'D CCMG']].dropna()
    data.plot(ax=ax, style=['r', 'g', 'b'], markersize=1.0)
    plt.legend(markerscale=3, numpoints=20)
    fig.tight_layout()
    plt.figure()
    modes=ds.df.modes.dropna()
    modes.plot()
    print "Painting.."
    paintModes(ax,modes)
    print "Show"
    plt.show()
    