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
from utils.thermometers import ThermometerNumber,ThermometerLocationByNumber
from scipy.stats import linregress

if __name__ == '__main__':

    folders=[]

    folders = []
    root_folder = 'F:/GondolaFlightArchive/'
    subdirs = next(os.walk(root_folder))[1]
    folders = [root_folder + subdir + '/' for subdir in subdirs]

    save_folder='C:/Users/bettii/thermometersPIPER/'
    img_folder=save_folder+"plots2/"
    

    
    folder=folders[0]
    fieldsList=getFieldsContaining('TReadDiodeMessage.temperature',folder)
    


    for field in fieldsList:
        field.range=400
        field.indexName='bettii.RTLowPriority.mceFrameNumber'
            
    ds = DataSet(fieldsList=fieldsList,foldersList=folders,verbose=True,rpeaks=False)
    
    print "Converting to Palestine Time..."
    ds.df.index=ds.df.index-pd.Timedelta(hours=5) #Palestine time conversion (Archives folder names are in UTC)
    #ds.df=ds.df.ix[pd.to_datetime('06/09/2017 00:00:00'):pd.to_datetime('06/09/2017 04:00:00')] #slicing
    ds.df=ds.df.dropna(axis=1,how='all')#.interpolate(method='time')
    ds.df.dropna(inplace=True)
    
    

    use('seaborn-colorblind')
    mpl.rcParams['axes.grid']=True
    

    time_label='Palestine Time'
    
    M=1 #downsample factor
    ds.df=ds.df.iloc[::M]
    
    print "Generating plots.."

    print "Plotting thermometers data..."
    labels=ds.df.columns #sort curves by flatness
    N=len(labels)
    Ncpp=5 #number of curves per plot
    Np=int(np.ceil(N*1.0/Ncpp)) #number of plots
    for k in range(Np):
        fig=plt.figure()
        ax=plt.subplot(111,xlabel=time_label, ylabel='Temperature [Kelvin]')
        data=ds.df[labels[k*Ncpp:(k+1)*Ncpp]].dropna(how='all')#.interpolate(method='time')
        data.plot(ax=ax,style='.',markersize=2.0)
        plt.legend(markerscale=3,numpoints=20,loc='lower right')
        fig.tight_layout()
        fig.savefig(img_folder+"thermometers_"+str(k)+".png")
    
    print "Saving CSV..."
    ds.df.to_csv(save_folder+"thermometers2.txt",sep='\t', float_format='%.4f', index_label='Palestine time  ', date_format="%Y-%m-%d %H:%M:%S%f")
    print "Saved"
    
    print "Show..."
    plt.show()