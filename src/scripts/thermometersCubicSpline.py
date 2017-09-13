'''
Created on 10 jul. 2017

Script for plotting thermometers from a single folder. Interpolating the data with cubic splines to have uniform time steps.

@author: Marc Casalprim
'''
print 'Imports...'
from utils.config import os,plt
from utils.dataset import np,pd,load_fields
from utils.field import getFieldsContaining
from utils.thermometers import ThermometerNumber,ThermometerLocationByNumber,ThermometerNumberByLocation,ThermometerName
from scipy.stats import mode
from scipy import interpolate

def filt(y):
    return y

if __name__ == '__main__':
    
    for moment in ['ground']:
    
        if moment=='sunrise':
            folder='F:/GondolaFlightArchive/17-06-09_09_58_36/' #sunrise
        elif moment=='ground':
            folder='F:/GondolaFlightArchive/17-06-08_21_36_58/' #ground
        else:        
            folder='F:/GondolaFlightArchive/17-06-09_01_51_04/'
        
        
        save_folder='C:/Users/bettii/thermometers/SteveDale/'
        img_folder=save_folder+moment+"Plots/"
        if moment != '': moment='_'+moment
        thermo_filename=save_folder+"thermo"+moment+".txt"
        thermoNumbers_filename=save_folder+"thermoNumbers"+moment+".txt"
        
        if not os.path.exists(save_folder):
            os.makedirs(save_folder)
        if not os.path.exists(img_folder):
            os.makedirs(img_folder)
    
        
        fL=getFieldsContaining('bettii.ThermometersDemuxedCelcius.J',folder) #thermometers list
        #fieldsList.append(Field('bettii.ThermometersDemuxedCelcius.J3L4'))
        
        fieldsList=[] #list that will have all the valid thermometers (that exist in ThermometerNumber dictionary)
        labels=[]
        for field in fL:
            field.range=90
            label=field.label
            if label in  ThermometerNumber.keys():
                number=ThermometerNumber[label] 
                if number in ThermometerLocationByNumber:          
                    label=ThermometerLocationByNumber[number]
                    labels.append(label)
                    field.label=label
                    fieldsList.append(field)
        
        fields=load_fields(fieldsList,folder=folder)
        time_label='Time (frameNumber)'
        fields[time_label] = fields.pop('bettii.ThermometersDemuxedCelcius.mceFrameNumber')
        
        
        #printing 'histogram' of data length
        lengths=[]
        bins={}
        for k in fields.keys():
            N=len(fields[k])
            lengths.append(N)
            if N not in bins:
                bins[N]=[]
            ref=k
            if k in ThermometerNumberByLocation:
                number=ThermometerNumberByLocation[k]      
                ref=ThermometerName[number]
            bins[N].append(ref)
        for k in bins.keys():
            print str(k)+" values: ",
            for therm in bins[k]:
                print therm+', ',
            print ''
    
        N=mode(lengths)[0][0] #the most common length is used as the length of the time to interpolate
        print "Mode: %s" % N
        time=fields[time_label]
        t0=time[0] #initial frame number
        tf=time[-1]#final frame number
        time=np.linspace(t0,tf,N) #common time
        fields[time_label]=time
        
        fieldsNew={}
        for k in fields.keys():
            y=fields[k]
            y=filt(y)
            t=np.linspace(t0,tf,len(y)) #time
            tck = interpolate.splrep(t, y, s=0) #we prepare the interpolation
            ynew = interpolate.splev(time, tck, der=0) #we query at the common time
            if k!=time_label: fieldsNew[k]=ynew
    
        df=pd.DataFrame(fieldsNew,index=time)
        labels=df.columns
        
    
    
        
        M=1 #downsample factor overriden
        df=df.iloc[::M]
        
        print "Generating plots.."
    
        print "Plotting thermometers data..."
        N=len(labels)
        Ncpp=5 #number of curves per plot
        Np=int(np.ceil(N*1.0/Ncpp)) #number of plots
        labels=sorted(labels)
        for k in range(Np):
            fig=plt.figure()
            ax=plt.subplot(111,xlabel=time_label, ylabel='Temperature [Celsius]')
            data=df[labels[k*Ncpp:(k+1)*Ncpp]].dropna(how='all').interpolate(method='time')
            data.plot(ax=ax,style='.',markersize=2.0)
            ax.legend(markerscale=3,numpoints=20,loc=0)
            fig.tight_layout()
            fig.savefig(img_folder+"thermometers_"+str(k)+".png")
        
        print "Saving CSV..."
        df.to_csv(thermo_filename,sep='\t', float_format='%.3f', index_label=time_label, date_format="%Y-%m-%d %H:%M:%S")
        #changing column labels, to print the thermometers by Name on the CSV file
        cols=labels
        for i,label in enumerate(labels):
            number=ThermometerNumberByLocation[label]      
            col=ThermometerName[number]
            cols[i]=col
        df.columns=cols
        df.to_csv(thermoNumbers_filename,sep='\t', float_format='%.3f', index_label=time_label, date_format="%Y-%m-%d %H:%M:%S")
        print "Saved"
        text=folder.split('/')[-2]
        ftime_str=text[0:8]+' '+text[9:17].replace('_',':') #foldertime
        ftime=pd.to_datetime(ftime_str,yearfirst=True)-pd.to_timedelta(5,unit='H')
        dt=(time[1]-time[0])/400.
        print "Delta time: %.2f seconds" % dt
        ds=((tf-t0)/400./60)
        print "Data span: %.2f minutes" % ds
        print ftime
        print ftime+pd.to_timedelta(dt,unit='m')
    print "Show..."
    plt.show()