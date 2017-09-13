'''
Created on Jul 7, 2017

Plot, delay lines control loops

@author: Marc Casalprim
'''
print 'Imports...'
import os
from utils.dataset import DataSet,plt,pd
from utils.field import Field
from timeit import default_timer as timer


if __name__ == '__main__':

    folder='F:/GondolaFlightArchive/17-06-09_01_51_04/'
    folder='F:/GondolaFlightArchive/17-06-09_07_09_25/'
    save_folder='C:/Users/bettii/thesis/'
    img_folder=save_folder+'plots/delaylines/'
    savefilename='DelayLines.pkl'
    
    if not os.path.exists(img_folder):
        os.makedirs(img_folder)
    folders=[folder]
    read=True
    if read:
        start_time = timer()
        
        fieldsList=[]
        fieldsList.append(Field('bettii.DelayLines.CDLposTarget',range=1.5))
        fieldsList.append(Field('bettii.DelayLines.CDLposMeasurement',range=1.5))
        fieldsList.append(Field('bettii.DelayLines.CDLvelTarget'))
        fieldsList.append(Field('bettii.DelayLines.CDLvelMeasurement'))
        fieldsList.append(Field('bettii.DelayLines.CDLet'))
        fieldsList.append(Field('bettii.DelayLines.CDLut'))
        
        fieldsList.append(Field('bettii.DelayLines.WDLposTarget',range=1.5))
        fieldsList.append(Field('bettii.DelayLines.WDLposMeasurement',range=1.5))
        fieldsList.append(Field('bettii.DelayLines.WDLvelTarget'))
        fieldsList.append(Field('bettii.DelayLines.WDLvelMeasurement'))
        fieldsList.append(Field('bettii.DelayLines.WDLet'))
        fieldsList.append(Field('bettii.DelayLines.WDLut'))
    
                
        ds = DataSet(fieldsList=fieldsList,foldersList=folders,verbose=True,min=1000,max=None,timeIndex=True)
        
        print "Converting to Palestine Time..."
        ds.df.index=ds.df.index-pd.Timedelta(hours=5) #Palestine time conversion (Archives folder names are in UTC)
        df=ds.df
        
        #df=df.ix[pd.to_datetime('06/08/2017 23:05:00'):]
        print "Elapsed time:",timer()-start_time,"seconds."
        print "Saving.."
        df.to_pickle(save_folder+savefilename)
        print "Saved"
    else:
        start_time = timer()
        print "Reading..."
        df = pd.read_pickle(save_folder+savefilename)
        print "Elapsed time:",timer()-start_time,"seconds."   
    
    print "Dataframe shape:", df.shape
    print "Cropping time..."
    df=df.ix[:pd.datetime(2017,06,9,03,07)]
    print "Dataframe shape:", df.shape
    print "Generating plots.."
    

    time_label='Palestine Time'
    
    M=10 #downsample factor
    df=df.iloc[::M]
        
    for DL in ['CDL','WDL']:
        data=df[[DL+'posTarget',DL+'posMeasurement']].dropna()
        ax=data.plot()
        ax.set_xlabel(time_label)
        
        data=df[[DL+'velTarget',DL+'velMeasurement']].dropna()
        ax=data.plot()
        
        data=df[DL+'ut'].dropna()
        ax=data.plot()
        ax.set_xlabel(time_label)
        
        data=df[DL+'et'].dropna()
        ax=data.plot()
        ax.set_xlabel(time_label)
        
        

    print "Show..."
    plt.show()