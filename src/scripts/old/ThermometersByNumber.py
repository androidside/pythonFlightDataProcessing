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
from utils.thermometers import ThermometerNumber


if __name__ == '__main__':

    folders=[]
    root_folder='F:/GondolaFlightArchive/'
    subdirs=next(os.walk(root_folder))[1]
    folders=[root_folder+subdir+'/' for subdir in subdirs]

    save_folder='C:/Users/bettii/thermometers/'
    img_folder=save_folder+"plotsByNumber/"
    

    
    folder=folders[0]
    fieldsList=getFieldsContaining('bettii.ThermometersDemuxedCelcius.J',folder)
    


    for field in fieldsList:
        field.range=90
        label=field.label
        if label in  ThermometerNumber.keys():
            number=ThermometerNumber[label]          
            label=number         
        field.label=label
            
    ds = DataSet(fieldsList=fieldsList,foldersList=folders,verbose=True,rpeaks=False)
    
    print "Converting to Palestine Time..."
    ds.df.index=ds.df.index-pd.Timedelta(hours=5) #Palestine time conversion (Archives folder names are in UTC)

    ds.df=ds.df.dropna(axis=1,how='all').interpolate(method='time')
    ds.df.dropna(inplace=True)
    
    Ngroups=20
    group={}
    for i in range(Ngroups):
        group[i]=[]
    for number in ds.df.columns:
        if number in ThermometerNumber.values():
            j=number*Ngroups/100
            group[j].append(number)
    
    use('seaborn-bright')
    mpl.rcParams['axes.grid']=True
    

    time_label='Palestine Time'
    
    M=1 #downsample factor
    ds.df=ds.df.iloc[::M]
    
    print "Generating plots.."

    print "Plotting thermometers data..."
    for i in group.keys():
        #if group[i] in ds.df.columns:
        fig=plt.figure()
        ax=plt.subplot(111,xlabel=time_label, ylabel='Temperature [Celsius]')
        data=ds.df[group[i]].dropna(how='all').interpolate(method='time')
        data.plot(ax=ax,style='.',markersize=2.0)
        plt.legend(markerscale=3,numpoints=20)
        fig.tight_layout()
        fig.savefig(img_folder+"thermometers_"+'-'.join(str(x) for x in group[i])+".png")
    
    print "Saving CSV..."
    ds.df.to_csv(save_folder+"thermometersByNumber.txt",sep='\t', float_format='%.2f', index_label='Palestine time  ', date_format="%Y-%m-%d %H:%M:%S")
    print "Saved"
    
    print "Show..."
    plt.show()