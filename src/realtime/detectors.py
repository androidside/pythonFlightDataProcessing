'''
Created on Jun 5, 2017

@author: Marc Casalprim
'''
from spyderplugins import widgets

print 'Imports...'
import matplotlib as mpl
import warnings
from matplotlib.style import use
from utils.dataset import load_fields,DataSet,plt,np,pd
from utils.field import Field,getDtypes,getFieldsContaining
from utils.detector import *

if __name__ == '__main__':
    #folder = "C:/17-05-17_00_36_34/"
    folder = "F:/LocalAuroraArchive/17-05-24_18_12_19/"
        
    fieldsList=getFieldsContaining("error_",folder,dtype='i8',indexName='masterMceFrameNumber')
    fieldsList.append(Field('bettii.DelayLines.CDLposTarget',label='target'))
    
    use('seaborn-bright') 
    #mpl.rcParams['toolbar'] = 'None'
    mpl.rcParams['axes.grid'] = True
    warnings.filterwarnings("ignore")
    #mpl.rcParams['axes.formatter.useoffset'] = False

    
    #===========================================================================
    # ds = DataSet(folder,fieldsList=fieldsList,nValues=1000,start=1000,verbose=True,rpeaks=False)   
    # data=ds.df.copy()
    #===========================================================================

    print "Creating figures..."
    axes={}
    axes['rt']=createImagesAxes('RT Signal')
    axes['fft']=createDataAxes('FFTs',dets=[3])
    axes['interf']=createDataAxes('Interferograms',dets=[3])
    #===========================================================================
    # axes['fftcum']=createDataAxes('Integrated FFTs',dets=[3])
    # axes['intRT']=createImagesAxes('Integrated values')
    # axes['power']=createImagesAxes('Power')
    #===========================================================================
    plt.draw()
    plt.pause(0.01)
    print "Plotting..."
    L=1000 #number of values
    S=1000 #step size (only has sense for simulation)
    for i in range(100):
        print "Reading..."
        data=load_fields(fieldsList, folder, nValues=L*(i+1), start=S*i)
        print "Processing..."
        det=data2matrices(data)
        ffts=getFFTs(det)
        print "Plotting.."
        plotData(ffts,axes['fft'])
        plotData(det,axes['interf'])
        #plotData(ffts,axes['fftcum'])
        plotImages(det, axes['rt'])
        plt.draw()
        plt.pause(1)
        #=======================================================================
        # plotImages(det, axes['rt'])
        # plotImages(det)
        #=======================================================================
        a=1
    plt.show()
    
    

