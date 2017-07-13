'''
Created on 10 jul. 2017

Script for plotting thermometers data from different archives

@author: Marc Casalprim
'''
print 'Imports...'
import os
import matplotlib as mpl
from matplotlib.style import use
from utils.dataset import DataSet,plt,np,pd
from utils.field import Field,getFieldsContaining
from utils.thermometers import getTemperaturesFromRawDataFrame
from timeit import default_timer as timer

if __name__ == '__main__':

    folders=[]

    folders = []
    root_folder = 'F:/GondolaFlightArchive/'
    subdirs = next(os.walk(root_folder))[1]
    folders = [root_folder + subdir + '/' for subdir in subdirs]

    save_folder='C:/Users/bettii/thermometersPIPER/'
    img_folder=save_folder+"plots3/"
    
    DF_FILENAME='RawDataframe.pkl'
    
    folder=folders[0]
    read=False
    
    start_time = timer()
    if read:
        fieldsList=getFieldsContaining('TReadDiodeMessage.',folder)
        for field in fieldsList:
            field.indexName='TReadDiodeMessage.frameCounter'
        
        stdList=getFieldsContaining('TReadStandardMessage.',folder)
        for field in stdList:
            field.label="std_"+field.label
            field.indexName='TReadStandardMessage.frameCounter'
        
        fieldsList=fieldsList+stdList
    

                
        ds = DataSet(fieldsList=fieldsList,foldersList=folders,verbose=True,rpeaks=False)
        
        print "Converting to Palestine Time..."
        ds.df.index=ds.df.index-pd.Timedelta(hours=5) #Palestine time conversion (Archives folder names are in UTC)
        #ds.df=ds.df.ix[pd.to_datetime('06/09/2017 00:00:00'):pd.to_datetime('06/09/2017 04:00:00')] #slicing
        ds.df=ds.df.dropna(axis=1,how='all')#.interpolate(method='time')
        df=ds.df#.dropna()
        print "Elapsed time:",timer()-start_time,"seconds."
        print "Saving.."
        df.to_pickle(save_folder+DF_FILENAME)
        print "Saved."
    else:
        print "Reading..."
        df = pd.read_pickle(save_folder+DF_FILENAME)
        print "Elapsed time:",timer()-start_time,"seconds."
    
    print "Caculating temperatures..."
    rawdata=df
    df=getTemperaturesFromRawDataFrame(rawdata)
    

    use('seaborn-colorblind')
    mpl.rcParams['axes.grid']=True
    

    time_label='Palestine Time'
    
    M=1 #downsample factor
    df=df.iloc[::M]
    
    print "Generating plots.."

    print "Plotting thermometers data..."
    labels=df.columns
    N=len(labels)
    Ncpp=5 #number of curves per plot
    Np=int(np.ceil(N*1.0/Ncpp)) #number of plots
    for k in range(Np):
        fig=plt.figure()
        ax=plt.subplot(111,xlabel=time_label, ylabel='Temperature [Kelvin]')
        data=df[labels[k*Ncpp:(k+1)*Ncpp]].dropna(how='all')#.interpolate(method='time')
        data[(data>0.01) & (data<400)].plot(ax=ax,style='.',markersize=2.0)
        plt.legend(markerscale=3,numpoints=20,loc='upper left')
        fig.tight_layout()
        fig.savefig(img_folder+"thermometers_"+str(k)+".png")
    
    print "Saving CSV..."
    df.to_csv(save_folder+"thermometers3.txt",sep='\t', float_format='%.4f', index_label='Palestine time  ', date_format="%Y-%m-%d %H:%M:%S")
    print "Saved"
    
    print "Show..."
    plt.show()