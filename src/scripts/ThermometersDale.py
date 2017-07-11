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

def flatness(x):
    slope, intercept, r_value, p_value, std_err = linregress(range(len(x)),x)
    return std_err

if __name__ == '__main__':

    folders=[]
    root_folder='F:/GondolaFlightArchive/'
    subdirs=next(os.walk(root_folder))[1]
    folders=[root_folder+subdir+'/' for subdir in subdirs]

    save_folder='C:/Users/bettii/thermometers/'
    img_folder=save_folder+"Dale/set1/"
    

    
    folder=folders[0]
    fieldsList=getFieldsContaining('bettii.ThermometersDemuxedCelcius.J',folder)
    

    labels=[]
    for field in fieldsList:
        field.range=90
        label=field.label
        if label in  ThermometerNumber.keys():
            number=ThermometerNumber[label] 
            if number in ThermometerLocationByNumber:          
                label=ThermometerLocationByNumber[number]
                labels.append(label)
        field.label=label
   
    ds = DataSet(fieldsList=fieldsList,foldersList=folders,verbose=True,rpeaks=False)
    
    print "Converting to Palestine Time..."
    ds.df.index=ds.df.index-pd.Timedelta(hours=5) #Palestine time conversion (Archives folder names are in UTC)
    #ds.df=ds.df.ix[pd.to_datetime('06/09/2017 06:00:00'):] #slicing
    ds.df=ds.df[labels].dropna(axis=1,how='all').interpolate(method='time')
    ds.df.dropna(inplace=True)

    labels=ds.df.columns
      
    use('seaborn-colorblind')
    mpl.rcParams['axes.grid']=True
    

    time_label='Palestine Time'
    
    M=1 #downsample factor
    ds.df=ds.df.iloc[::M]
    
    print "Generating plots.."

    print "Plotting thermometers data..."
    N=len(labels)
    Ncpp=5 #number of curves per plot
    Np=int(np.ceil(N*1.0/Ncpp)) #number of plots
    labels=sorted(labels)
    for k in range(Np):
        fig=plt.figure()
        ax=plt.subplot(111,xlabel=time_label, ylabel='Temperature [Celsius]')
        data=ds.df[labels[k*Ncpp:(k+1)*Ncpp]].dropna(how='all').interpolate(method='time')
        data.plot(ax=ax,style='.',markersize=2.0)
        plt.legend(markerscale=3,numpoints=20)
        fig.tight_layout()
        fig.savefig(img_folder+"thermometers_"+str(k)+".png")
    
    print "Saving CSV..."
    ds.df.to_csv(save_folder+"thermometersByNumber.txt",sep='\t', float_format='%.2f', index_label='Palestine time  ', date_format="%Y-%m-%d %H:%M:%S")
    print "Saved"
    
    print "Show..."
    plt.show()