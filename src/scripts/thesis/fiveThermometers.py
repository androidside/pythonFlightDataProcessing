'''
Created on 10 jul. 2017

Script for plotting thermometers data from different archives

@author: Marc Casalprim
'''

print 'Imports...'
from utils.config import os,flightDisksFolders, save_folder
from utils.dataset import DataSet,plt,np,pd
from utils.field import Field
from utils.thermometers import ThermometerNumber,ThermometerLocationByNumber

if __name__ == '__main__':

    folders=flightDisksFolders

    img_folder=save_folder+'plots/thermometers/'
    if not os.path.exists(img_folder):
        os.makedirs(img_folder)
    

    
    folder=folders[0]
    fieldsList=[]#getFieldsContaining('bettii.ThermometersDemuxedCelcius.J',folder)
    fieldsList.append(Field('bettii.ThermometersDemuxedCelcius.J3L10'))
    fieldsList.append(Field('bettii.ThermometersDemuxedCelcius.J4L35'))
    fieldsList.append(Field('bettii.ThermometersDemuxedCelcius.J4L31'))
    fieldsList.append(Field('bettii.ThermometersDemuxedCelcius.J2L13'))
    fieldsList.append(Field('bettii.ThermometersDemuxedCelcius.J2L47'))

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
    print ds.df.shape

    labels=ds.df.columns   

    time_label='Time'
    
    M=1 #downsample factor
    ds.df=ds.df.iloc[::M]
    
    print ds.df.shape
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
        plt.legend(loc=0,markerscale=3,numpoints=20)
        fig.tight_layout()
        fig.savefig(img_folder+"thermometers_"+str(k)+".png")
    
    print "Saving CSV..."
    ds.df.to_csv(save_folder+"thermometersByNumber.txt",sep='\t', float_format='%.2f', index_label='Palestine time  ', date_format="%Y-%m-%d %H:%M:%S")
    print "Saved"
    
    print "Show..."
    plt.show()