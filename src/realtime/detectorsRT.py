'''
Created on Jun 5, 2017

@author: Marc Casalprim
'''
from spyderplugins import widgets

print 'Imports...'
import matplotlib as mpl
import warnings
from matplotlib.style import use
import matplotlib.animation as animation

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


    print "Creating figures..."
    axes={}
    axes['rt']=createImagesAxes('RT Signal')
    axes['fft']=createDataAxes('FFTs',dets=[3]) #plot only detector D
    axes['interf']=createDataAxes('Interferograms',dets=[3]) #plot only detector D
    axes['intRT']=createImagesAxes('Integrated values')
    axes['power']=createImagesAxes('Power')
    
    # axes['fftcum']=createDataAxes('Integrated FFTs',dets=[3])
    
    plt.draw()

    def plotAll(i):
        global fieldsList,folder,axes,N,fftcum
        print "Reading..."
        L=1900 #number of values
        S=250 #step size (only has sense for simulation)
        data=load_fields(fieldsList, folder, nValues=L, start=S*i) #simulation
        #data=load_fields(fieldsList, folder, nValues=L) #from end
        print "Processing..."
        CDLposTarget=data['target']
        CDLmceFN=data['bettii.DelayLines.mceFrameNumber']
        masterMceFn=data['masterMceFrameNumber']
        index=getIndexRangeLastStroke(CDLposTarget, CDLmceFN, masterMceFn)
        dead_pixels=getDeadPixels(filename="C:/cygwin/home/bettii/pythonFlightDataProcessing/src/utils/dead_pixels.txt")
        det=data2matrices(data,index=index,dead=dead_pixels)
        ffts=getFFTs(det)
        print "Plotting.."
        plotData(ffts,axes['fft'])
        plotData(det,axes['interf'])
        #plotData(ffts,axes['fftcum'])
        
        plotImages(det, axes['intRT'], sum=True, cmap="Greens")
        plotImages(ffts, axes['power'], sum=True,cmap="Reds")
        plotImages(det, axes['rt'], cmap="Greys")
        
        del data
        del det
        del ffts,index
    
    #ani = animation.FuncAnimation(plt.gcf(), plotAll, 100, interval=200)
    for i in range(100):
        plotAll(i)
        plt.pause(0.2)
    
    plt.show()
    
    

