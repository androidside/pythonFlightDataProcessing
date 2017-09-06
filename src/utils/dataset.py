'''
Created on 28 abr. 2017

Based on Maxime's files.
The DataSet class is very similar, but using 'outer' merges

@author: Marc Casalprim
'''
import os
import pandas as pd
import numpy as np
import seaborn.apionly as sns
import matplotlib.pyplot as plt
import scipy.stats as stats
from scipy.signal import find_peaks_cwt
from scipy.signal.spectral import periodogram
from quat import Quat,normalize
from utils.thermometers import unwrapCounter

red = sns.xkcd_rgb['pale red']
blue = sns.xkcd_rgb['denim blue']
lt_blue = sns.xkcd_rgb['pastel blue']
colors = [blue,'g',red]

def load_single_field(fieldname,datatype,nValues=None,start=None):
    """Return np.array from the file fieldname interpreting datatype (eg. 'i4')"""
    type_str_native = ">"+datatype
    type_str_final = "<"+datatype # change endianness
    
    if nValues is None:
        field = np.fromfile(fieldname,dtype=np.dtype(type_str_native))
    else:
        bpv=int(datatype[-1]) #bytes per value
        f = open(fieldname, "rb")
        try:
            if start is None:
                nBytes=nValues*bpv 
                f.seek(-nBytes, os.SEEK_END)
            else:
                nBytes=start*bpv
                f.seek(nBytes, os.SEEK_SET)
    
        
            field = np.fromfile(f,dtype=np.dtype(type_str_native),count=nValues)
        finally:
            f.close()

    field = field.astype(type_str_final)
    return field
def load_fields(fieldsList,folder=None,nValues=None,start=None):
    """Return dictionary of np.array keyed by the field's label"""
    df={}
    for field in fieldsList:
        df[field.label]=load_single_field(folder+field.fieldName,field.dtype,nValues=nValues,start=start)
        if field.indexName not in df: df[field.indexName]=load_single_field(folder+field.indexName,field.indexType,nValues=nValues,start=start)
    return df
        
def genQuaternions(dataframe,quats={'qest':['qi','qj','qk','qr'],'qI2G':['qi_sc','qj_sc','qk_sc','qr_sc'],'qI2S':['ra_sc','dec_sc','roll_sc']},norm=False,filter=False):
    """Generates a dictionary of lists of utils.quat.Quat objects using the columns of dataframe defined on the quats dictionary."""
    lists={}
    matrices={}
    for key in quats.keys() :
        lists[key]=[]
        matrices[key]=dataframe[quats[key]].as_matrix()


    for i in range(len(dataframe.index)):
        for key in quats.keys() :
            v=matrices[key][i]
            q=Quat(v)
            if filter:
                if len(v)==4:
                    if abs(q)>1.5 or abs(q)<0.7:
                        q=np.nan
                else:
                    if np.mean(abs(v[:2]))<0.01:
                        q=np.nan
            if norm and not filter and isinstance(q, Quat): q=q.normalize()
            lists[key].append(q)
     
    return lists

def extractGyrosAndStarcam(dataframe,labels_gyros=['gyroX','gyroY','gyroZ'],label_triggers='triggers',label_scerrors=['ra_err','dec_err','roll_err']):
    """Returns two dataframes with the Groscopes and Starcamera data respectively. Synchronizes the Starcamera with the triggers. Useful for the Estimator classes."""
    SClabels=['qI2G','qI2S']

    print "Creating Starcam dataframe..."
    triggers=dataframe[label_triggers].drop_duplicates()
    L=1e300
    while (L-len(triggers))>0:
        L=len(triggers)
        triggers=triggers[[(triggers.loc[mceFN]<max(triggers.index) and triggers.loc[mceFN]>(min(triggers.index)-10000)) for mceFN in triggers.index]]
    subdf=dataframe.loc[triggers.index].drop_duplicates(subset=['dec_sc','ra_sc','roll_sc']).dropna()
    index=triggers.loc[subdf.index].index#values #here we can index the sc dataframe with the triggers (using .values instead of .index)
    sc=pd.DataFrame(genQuaternions(subdf,norm=True,filter=True),index=index)[SClabels].dropna()
    if label_scerrors is not None: sc[label_scerrors]=dataframe[label_scerrors].loc[sc.index]
    sc[label_triggers]=triggers.loc[subdf.index]
    print "Number of solutions: %s"%len(sc)
    print "Generating estimator quaternions..."
    quats=pd.DataFrame(genQuaternions(dataframe,quats={'qest':['qi','qj','qk','qr']},norm=True),index=dataframe.index)
    print "Filtering..."
    quats=filterQuats(quats)
    

 
    if labels_gyros is not None: gyros=dataframe[labels_gyros].dropna().interpolate(method='values')
    else: gyros=None
    #print 'Done'  
    return gyros,sc,quats
    
class DataSet():
        
    def __init__(self,folder=None,freq=400.,min=None,max=None,folder_export = None, nValues=None, start=None, verbose=False, rpeaks=False,estimator=False,starcam=False,fieldsList=[],foldersList=[],droplist = [],timeIndex=False):
        '''
        return a DataSet object containing df, a Pandas data frame indexed on the mceFramenumber
        Loads a list of fields fieldsList, the estimator data or the starcamera data dpeending on the correct parameters
        Keyword arguments:
        folder -- folder where the fields in fieldsList are located
        freq   -- frequency of the mce (default 400Hz)
        min    -- minimum mceFN value
        max    -- maximum mceFN value
        folder_export -- folder where the plots will be saved
        nValues -- number of values to read from the files (if None, all the file is read)
        start  -- value from where we start to read (if None, we count nValues from the end)
        verbose -- Print progress of the dataframe generation
        rpeaks -- Remove rows were all fields have values less than 1 (typical error when using telemetry archives)
        estimator -- read estimator data?
        starcam -- read starcam data?
        fieldsList -- list of utils.field.Field objects, representing the fields to store on the dataframe.
        foldersList -- list of folders, data will be merged
        droplist -- list of columns to drop before returning DataSet object
        '''
        
        self.folder = folder
        self.times=dict() #dict storing np.arrays of the different indexes, to avoid loading them every time               
        self.df = pd.DataFrame()
        self.freq = freq
        self.min=min
        self.max=max
        if len(foldersList)<2:
            if len(foldersList)==1: self.folder=foldersList[0]
            self.readListFields(fieldsList,rpeaks=rpeaks,nValues=nValues,start=start,verbose=verbose,timeIndex=timeIndex)
        else:
            self.folder=foldersList[0]
            self.readMultipleFolders(fieldsList,foldersList,rpeaks=rpeaks, verbose=verbose,timeIndex=True)
        
        if estimator:
            self.readEstimator()
        if starcam:
            self.readStarcamera()
        
        if not self.df.empty:
            self.df = self.df.dropna(axis=0,how='all')
            self.df = self.df.drop(droplist)
            if rpeaks: #remove peaks
                self.df=self.df.loc[(self.df.abs()>=1).any(1)]  #remove rows were all fields have a value <1           
            #self.df = self.df.loc[self.min:self.max,:]
                
        if folder_export == None: self.folder_export = self.folder.split('/')[-1]
        else: self.folder_export = folder_export
        
    def readListFields(self,fieldsList,folder=None,rpeaks=True, verbose=False, nValues=None,start=None,timeIndex=False):
        if folder is None: folder=self.folder
        i=0
        if verbose: print 'Reading list of '+str(len(fieldsList))+' fields.'
        for field in fieldsList:
            i=i+1
            if verbose: print str(100*i/len(fieldsList))+'%', 
            self.readField(field, folder=folder,rpeaks=rpeaks,verbose=verbose,nValues=nValues,start=start)
        if verbose: print ''
        self.df = self.df.dropna(axis=0,how='all').sort_index()
        self.df = self.df.loc[self.min:self.max,:]
        if timeIndex and len(self.df.index)>0:
            text=folder.split('/')[-2]
            ftime_str=text[0:8]+' '+text[9:17].replace('_',':') #foldertime
            ftime=pd.to_datetime(ftime_str,yearfirst=True)
            index=(self.df.index-self.df.index[0])/self.freq #time in seconds
            index=pd.to_timedelta(index,unit='s')
            time=ftime+index
            self.df.index=time
        if rpeaks: #remove peaks
            self.df=self.df.loc[(self.df.abs()>=1).any(1)]  #remove rows were all fields have a value <1
    def readField(self,field,folder=None,rpeaks=True,verbose=False,nValues=None,start=None,timeIndex=False):
        if folder is None: folder=self.folder
        
        try:
            field_data = field.function(load_single_field(folder+field.fieldName,field.dtype,nValues=nValues,start=start))*field.conversion
            Lraw=len(field_data)
            timeName=field.indexName
            timeType=field.indexType
            if nValues is None:
                if timeName in self.times.keys(): time=self.times[timeName]
                else:
                    if verbose: print 'Time reference '+timeName+' not loaded in local dataset yet. Adding...',
                    time = load_single_field(folder+timeName,timeType)
                    self.times[timeName]=time
            elif start is None:
                    if verbose: print 'Time reference '+timeName+' not loaded in local dataset yet. Adding...',
                    time = load_single_field(folder+timeName,timeType,nValues=nValues) #reading last nValues from the end
                    self.times[timeName]=time
            else:
                if timeName in self.times.keys():
                    d=(start+nValues)-len(self.times[timeName]) #number of values we need
                    if d>0:
                        if verbose: print 'Expanding time index '+timeName+' in local dataset...'
                        time = load_single_field(folder+timeName,timeType,nValues=d,start=len(self.times[timeName]))
                        self.times[timeName]= np.concatenate((self.times[timeName],time))                    
                else:
                    if verbose: print 'Time reference '+timeName+' not loaded in local dataset yet. Adding...'
                    time = load_single_field(folder+timeName,timeType,nValues=start+nValues,start=0)
                    self.times[timeName]=time
                
                time=(self.times[timeName])[start:start+nValues]
            
            label=field.label
            
            if label in self.df.keys() and len(self.df[label].as_matrix())==len(field_data):
                if verbose: print label+' already in dataframe.'
            else:
                indmin=50000 #minimum index, frame number
                if field.fieldName=='bettii.GpsReadings.altitudeMeters' or 'PiperThermo' in field.fieldName: #its PIPER or GPS data (theres no mceframenumber)
                    time=self.times['bettii.RTLowPriority.mceFrameNumber'] #get another mceFN vector of this archive
                    L=len(field_data)
                    time=time[time>indmin]
                    DT=(time[-1]-time[0])
                    time=np.round(np.linspace(time[0], time[0]+DT, L))
                if "TRead" in field.fieldName: #its TRead message (using frame counter)
                    time=(unwrapCounter(time)+indmin)*400 #time has to be TRead[...].frameCounter
                if field.indexName=='bettii.ThermometersDemuxedCelcius.mceFrameNumber': #its a thermometer
                    field_data=field_data[field_data!=0]
                    L=len(field_data)
                    time=time[time>indmin]
                    time=np.linspace(time[0], time[-1], L) #we expand the time (i dont understand the logic of the thermomemeters mceframenumber)
                L=min(len(field_data),len(time))
                df_tmp = pd.DataFrame({label:field_data[:L]},index=time[:L]).sort_index() #create temporal dataframe
                df_tmp = df_tmp[~df_tmp.index.duplicated(keep='first')] #remove values with duplicated index
                df_tmp=df_tmp[np.abs(df_tmp[label].as_matrix())<= field.range] #keep only the ones that are within fields range.
                df_tmp=df_tmp[df_tmp.index>indmin] #keep only meaningful index (a FN less than indmin is impossible)
                if False and not df_tmp.empty:
                    z=(np.abs(df_tmp.index)-np.mean(df_tmp.index))/np.std(df_tmp.index)
                    df_tmp=df_tmp[z<2] #keep only meaningful index (drop outliers >2sigmas), seems dangerous but there are always bad mceFN that mess the entire plot
                if timeIndex and len(df_tmp.index)>0:
                    text=folder.split('/')[-2]
                    ftime_str=text[0:8]+' '+text[9:17].replace('_',':').replace('-','') #foldertime
                    ftime=pd.to_datetime(ftime_str,yearfirst=True)
                    index=(df_tmp.index-df_tmp.index[0])/self.freq #time in seconds
                    index=pd.to_timedelta(index,unit='s')
                    time=ftime+index
                    df_tmp.index=time
                if self.df.empty: self.df = df_tmp
                elif label in self.df: self.df = self.df.combine_first(df_tmp)
                else: self.df =        pd.merge(self.df,df_tmp,how='outer',left_index=True,right_index=True) 
                if verbose: print field.fieldName+' read. '+str(Lraw)+' raw values. '+str(len(df_tmp))+' deduplicated values.'
        except Exception as e:
            raise
            print 'ERROR reading '+field.fieldName+':', e
    
    def readMultipleFolders(self,fieldsList,foldersList,rpeaks=False, verbose=False,timeIndex=True):
        """Stores in self.df a new pd.DatFrame object containing
        the fieldsList data from all the folders in foldersList.
        The indexing of the DataFrame is a DatetimeIndex by default
        (timeIndex=True), using the date and time of the folder name."""
        i=0
        dftmp=pd.DataFrame() #temporal dataframe where all the data is being merged
        for folder in foldersList:
            if verbose: print 'Reading list of '+str(len(fieldsList))+' fields from folder '+folder+'.'
            self.times=dict()
            self.df=pd.DataFrame() #reset of self.df, that way we can use readField method
            for field in fieldsList:
                i=i+1
                if verbose: print str(100*i/len(foldersList)/len(fieldsList))+'%', 
                self.readField(field, folder=folder,rpeaks=rpeaks,verbose=verbose,timeIndex=False)
            if verbose: print ''
            self.df = self.df.dropna(axis=0,how='all')
            #if True, change mceFN indexing to a DatetimeIndex
            #Using folder name as the time for the first mce frame
            if timeIndex and len(self.df.index)>0:
                text=folder.split('/')[-2]
                ftime_str=text[0:8]+' '+text[9:17].replace('_',':') #foldertime
                ftime=pd.to_datetime(ftime_str,yearfirst=True)
                index=(self.df.index-self.df.index[0])/self.freq #time in seconds
                index=pd.to_timedelta(index,unit='s')
                time=ftime+index
                self.df.index=time
            if dftmp.empty: dftmp = self.df
            else: dftmp = dftmp.combine_first(self.df)
            
        self.df=dftmp
    def readEstimator(self,folder=None,timeDivider=1):
        if folder is None: folder=self.folder
        #covariance matrix
        Cov00 = np.sqrt(load_single_field(folder+'bettii.RTLowPriority.MeasurementErrorCovarianceMatrixR00','f8'))/4.8484e-6
        Cov11 = np.sqrt(load_single_field(folder+'bettii.RTLowPriority.MeasurementErrorCovarianceMatrixR11','f8'))/4.8484e-6
        Cov22 = np.sqrt(load_single_field(folder+'bettii.RTLowPriority.MeasurementErrorCovarianceMatrixR22','f8'))/4.8484e-6

        #estimator (show only diagonal values)
        Q00 = np.sqrt(load_single_field(folder+'bettii.RTLowPriority.covarianceMatrix00','f8'))/4.8484e-6
        Q11 = np.sqrt(load_single_field(folder+'bettii.RTLowPriority.covarianceMatrix11','f8'))/4.8484e-6
        Q22 = np.sqrt(load_single_field(folder+'bettii.RTLowPriority.covarianceMatrix22','f8'))/4.8484e-6
        Q33 = np.sqrt(load_single_field(folder+'bettii.RTLowPriority.covarianceMatrix33','f8'))/4.8484e-6
        Q44 = np.sqrt(load_single_field(folder+'bettii.RTLowPriority.covarianceMatrix44','f8'))/4.8484e-6
        Q55 = np.sqrt(load_single_field(folder+'bettii.RTLowPriority.covarianceMatrix55','f8'))/4.8484e-6

        #bias
        biasX = load_single_field(folder+'bettii.RTHighPriority.estimatedBiasXarcsec','f8')
        biasY = load_single_field(folder+'bettii.RTHighPriority.estimatedBiasYarcsec','f8')
        biasZ = load_single_field(folder+'bettii.RTHighPriority.estimatedBiasZarcsec','f8')
        
        self.times['bettii.RTLowPriority.mceFrameNumber'] = load_single_field(folder+'bettii.RTLowPriority.mceFrameNumber','i8')

        # estimator
        qr_list = load_single_field(folder+'bettii.RTLowPriority.qr','f8')
        qi_list = load_single_field(folder+'bettii.RTLowPriority.qi','f8')
        qj_list = load_single_field(folder+'bettii.RTLowPriority.qj','f8')
        qk_list = load_single_field(folder+'bettii.RTLowPriority.qk','f8')
        estimated_quatlist = [Quat(normalize((qi_list[i],qj_list[i],qk_list[i],qr_list[i]))) for i in range(len(qr_list))]
        est_ra = [q.ra*3600. for q in estimated_quatlist]
        est_dec = [q.dec*3600. for q in estimated_quatlist]
        est_roll = [q.roll*3600. for q in estimated_quatlist]

        estimatorData = {'Cov00':Cov00,'Cov11':Cov11,'Cov22':Cov22,
                        'Q00':Q00,'Q11':Q11,'Q22':Q22,'Q33':Q33,'Q44':Q44,'Q55':Q55,
                        'ra':est_ra,'dec':est_dec,'roll':est_roll,'est_q':estimated_quatlist
                        }
        biasData = {'biasX':biasX,'biasY':biasY,'biasZ':biasZ}
        df_estimator = pd.DataFrame(estimatorData,index = self.times['bettii.RTLowPriority.mceFrameNumber']/timeDivider)
        df_estimator.drop_duplicates(inplace=True)

        df_bias = pd.DataFrame(biasData,index = self.times['bettii.RTHighPriority.mceFrameNumber']/timeDivider)
        df_bias.drop_duplicates(inplace=True)
        df_tmp = pd.merge(self.df,df_estimator,how='outer',left_index=True,right_index=True)
        self.df = pd.merge(df_tmp,df_bias,how='outer',left_index=True,right_index=True)
    
    def readStarcamera(self,folder=None,timeDivider=1):
        if folder is None: folder=self.folder
        ### star camera loading
        # Load star camera trigger number
        # this is the mceFrameNumber at which the starcamera trigger occurred, and which is processed by the starFinder
        starcam_trigger = load_single_field(folder+'bettii.RTLowPriority.RawStarcameraMceFrameNumberWhenSCTriggered','i8')
        
        self.times['bettii.RTLowPriority.mceFrameNumber'] = load_single_field(folder+'bettii.RTLowPriority.mceFrameNumber','i8')
        
        meas_qr_list = load_single_field(folder+'bettii.RTLowPriority.StarCameraRotatedqr','f8')
        meas_qi_list = load_single_field(folder+'bettii.RTLowPriority.StarCameraRotatedqi','f8')
        meas_qj_list = load_single_field(folder+'bettii.RTLowPriority.StarCameraRotatedqj','f8')
        meas_qk_list = load_single_field(folder+'bettii.RTLowPriority.StarCameraRotatedqk','f8')

        starcamsol = {'triggers': starcam_trigger,
                    'meas_qr': meas_qr_list,
                    'meas_qi': meas_qi_list,
                    'meas_qj': meas_qj_list,
                    'meas_qk': meas_qk_list,
                    }
        df_solution = pd.DataFrame(starcamsol,index = self.times['bettii.RTLowPriority.mceFrameNumber']/timeDivider)
        df_solution.drop_duplicates(inplace=True)
        df_solution = df_solution.loc[np.abs(df_solution['meas_qr'])>1e-10]
        df_solution = df_solution.loc[np.abs(df_solution['meas_qr'])<=1.0]
        df_solution = df_solution.loc[np.abs(df_solution['meas_qi'])<=1.0]
        df_solution = df_solution.loc[np.abs(df_solution['meas_qj'])<=1.0]
        df_solution = df_solution.loc[np.abs(df_solution['meas_qk'])<=1.0]
        df_solution = df_solution.drop_duplicates(subset='triggers') # only keeps the unique values for triggers
        
        # convert to ra/dec/roll
        #print df_solution.iloc[5][['meas_qi','meas_qj','meas_qk','meas_qr']]
        measured_quatlist = [Quat(normalize(df_solution.loc[mceFN][['meas_qi','meas_qj','meas_qk','meas_qr']])) for mceFN in df_solution.index]
        meas_ra_calc = [q.ra*3600. for q in measured_quatlist]
        meas_dec_calc = [q.dec*3600. for q in measured_quatlist]
        meas_roll_calc = [q.roll*3600. for q in measured_quatlist]
        
        meas_radecroll = {'ra_sc':meas_ra_calc,
                        'dec_sc':meas_dec_calc,
                        'roll_sc':meas_roll_calc,
                        'q_sc': measured_quatlist
                        }
        df_solution = pd.merge(df_solution,pd.DataFrame(meas_radecroll,index=df_solution.index),how='inner',left_index=True,right_index=True)
        df_solution = df_solution.drop(['meas_qi','meas_qj','meas_qk','meas_qr'],1)
        
        self.df = pd.merge(self.df,df_solution,how='outer',left_index=True,right_index=True)

    def simplePlot(self,val,minMax = [],ylabel="",origin=0,ax_key=None,save=False,draw=True,realTime=True,name=None,color=sns.xkcd_rgb['denim blue']):
        print "simplePlot, Loading %s data..." %val
        if ax_key==None: fig,ax = plt.subplots(figsize=(5.9,4),dpi=120)
        else: ax = ax_key
        data = self.df[val].dropna()
        ax.set_xlabel("Time (s)")
        ax.set_ylabel(ylabel)
        ax.grid(True)
        if realTime: ax.plot(data.index/self.freq-origin,data,label=val,color=color)
        else: ax.plot(data.index-origin,data,label=val,color=color)
        if minMax != []:
            ax.set_xlim = minMax
        ax.legend(loc='best')
        if ax_key==None:
            fig.tight_layout()
            if save: 
                if name==None: fig.savefig(self.folder_export+"simplePlot_%s.png" % val,dpi=300)
                else: fig.savefig(self.folder_export+name+"_%s.png" % val,dpi=300)
            if draw: plt.draw()
            #plt.close(fig)
        print "Done."
    def simple2DPlot(self,field1,field2,minMax = [],xlabel="",ylabel="",ax_key=None,save=False,draw=True,realTime=True,name=None,kde = False,color=sns.xkcd_rgb['denim blue']):
        print "simple2DPlot, Loading data..."
        if ax_key==None: fig,ax = plt.subplots(figsize=(5.9,4),dpi=120)
        else: ax = ax_key
        data=self.df[[field1,field2]].dropna()
        data1 = data[field1]
        data2 = data[field2]
        ax.set_xlabel(xlabel)
        ax.set_ylabel(ylabel)
        ax.grid(True)
        ax.scatter(data1,data2,color=color,alpha=0.4)
        if kde:
            sns.kdeplot(data1,data2,ax=ax)
        ax.set_xlabel(xlabel)
        ax.set_ylabel(ylabel)
        ax.grid(True)
        if ax_key==None:
            fig.tight_layout()
            if save: 
                if name==None: fig.savefig(self.folder_export+"simple2DPlot_%s_%s.png" % (field1,field2),dpi=300)
                else: fig.savefig(self.folder_export+name+"_%s_%s.png" % (field1,field2),dpi=300)
            if draw: plt.draw()
            #plt.close(fig)
        print "Done."
    
    def integralPlot(self,val,minMax = [],ylabel="",save=False,show=True,realTime=True,name=None):
        print "Loading %s data..." %val
        fig,ax = plt.subplots(figsize=(5.9,4),dpi=120)
        data = np.cumsum(self.df[val])/np.float(self.freq)
        ax.set_xlabel("Time (s)")
        ax.set_ylabel(ylabel)
        ax.grid(True)
        if realTime: ax.plot(self.df.index/400.,data,label=val,color=blue)
        else: ax.plot(self.df.index,data,label=val,color=blue)
        if minMax != []:
            ax.set_xlim = minMax
        ax.legend(loc='best')
        fig.tight_layout()
        if save: 
            if name==None: fig.savefig(self.folder_export+"integralPlot_%s.png" % val,dpi=300)
            else: fig.savefig(self.folder_export+name+"_%s.png" % val,dpi=300)
        if show: plt.draw()
        #plt.close(fig)
        print "Done."

        
    def PSD(self,column,draw=True,save=False,loglog=True,ax_key=None,minPlot=None,name=None,minMax=[],units = '(arcsec/s)$^2$/Hz'):
        print "PSD, Loading data..."
        data = self.df[column].dropna()
        if ax_key==None: fig,ax = plt.subplots(figsize=(5.9,4),dpi=120)
        else: ax = ax_key
        print "Calculating power spectral density..."
        f, Pxx_den = periodogram(data, self.freq)
        if loglog: ax.loglog(f,Pxx_den,label=column)
        else:ax.plot(f,Pxx_den,label=column)
        ax.set_xlabel('Frequency [Hz]')
        ax.set_ylabel('PSD ['+units+']')
        if minPlot !=None and minMax==[]: ax.set_xlim([minPlot,max(f)])
        elif minMax!=[]: ax.set_xlim(minMax)
        ax.set_ylim([min(Pxx_den),max(Pxx_den)])
        ax.legend(loc='best')
        ax.grid(True)
        if ax_key==None:
            fig.tight_layout()
            if save:
                if name==None: fig.savefig(self.folder_export+"PSD%d.png" % self.freq,dpi=300)
                else: fig.savefig(self.folder_export+name+"_%d.png" % self.freq,dpi=300)
            if draw: plt.draw()
            #plt.close(fig)
        print "Done."

    def multiPSD(self,columns,show=True,save=False,loglog=False,name=None,minMax=[],units='(arcsec/s)$^2$/Hz'):
        print "Plotting multiple PSDs"
        fig,axlist = plt.subplots(len(columns),figsize=(5.9,8),dpi=120)
        for i in range(len(columns)):
            ax = axlist[i]
            self.PSD(columns[i],save=False,loglog=loglog,ax_key=ax,minPlot=0.001,minMax=minMax,units=units)
            if minMax != []:
                ax.set_xlim = minMax
        fig.tight_layout()
        if save:
            if name==None: fig.savefig(self.folder_export+"multiPSD%d.png" % self.freq,dpi=300)
            else: fig.savefig(self.folder_export+name+"_%d.png" % self.freq,dpi=300)
        if show: plt.draw()
        #plt.close(fig)

    def kde(self,column,show=True,ax_key=None,save=False):
        print "Kernel estimation..."
        data = self.df[column].dropna()
        if ax_key==None: fig,ax = plt.subplots(figsize=(5.9,4),dpi=120)
        else: ax=ax_key
        kernel = stats.gaussian_kde(data)
        print "Calculating histogram of dataset..."
        hist, bin_edges = np.histogram(data, bins =50,density=True)
        print "Plotting..."
        ax.bar(bin_edges[:-1], hist, width = np.diff(bin_edges),color=blue,alpha=0.7)
        ax.set_xlim(min(bin_edges), max(bin_edges))
        xaxis = np.linspace(min(bin_edges),max(bin_edges),200)
        ax.set_xlabel('Angular velocity bins (arcsec/s)')
        ax.set_ylabel('Probability density')
        ax.plot(xaxis,kernel(xaxis),color=red,lw=2)
        if ax_key==None:
            fig.tight_layout()
            if save:fig.savefig(self.folder_export+"hist_%s.png" % 'name',dpi=300)
            if show: plt.draw()
            #plt.close(fig)
        print "Done."
def toTimeIndex(dataframe,folder,freq=400.):
    """Returns the same dataframe but with the indices in DateTime format.
    The input dataframe must have mceFrameNumber indices.
    The time in the folder is considered as the starting time for the first mce frame number.
    """
    text=folder.split('/')[-2]
    ftime_str=text[0:8]+' '+text[9:17].replace('_',':') #foldertime
    ftime=pd.to_datetime(ftime_str,yearfirst=True)
    index=(dataframe.index-dataframe.index[0])/freq #time in seconds
    index=pd.to_timedelta(index,unit='s')
    time=ftime+index
    dataframe.index=time
    return dataframe   
def plotColumns(df,units='',xlabel='Index',ylabels=None):
    """Plot the N columns of the pd.Dataframe df in a Nx1 subplots layout"""
    data = df.dropna()
    N=len(data.columns)
    fig,axes =plt.subplots(N, 1, sharex=True, sharey=True)
    for i in range(N):
        column=data.columns[i]
        data[column].plot(ax=axes[i])
        if ylabels is None: axes[i].set_ylabel(column+' '+units)
        else: axes[i].set_ylabel(ylabels[i]+' '+units)
    axes[-1].set_xlabel(xlabel)
    fig.tight_layout()
    return fig
def plotQuaternions(df,time_label='Palestine Time',labels=None,styles=['b','r','g','k'],legend=False,xlim=None):
    """Plot the quaternions of the pd.Dataframe df in a 3x1 subplots layout (RA,DEC,ROLL)"""
    N=len(df.columns)
    fig,(axRA,axDEC,axROLL) =plt.subplots(3, 1, sharex=True, sharey=True)
    axRA.set_ylabel('RA (deg)')
    axDEC.set_ylabel('DEC (deg)')
    axROLL.set_ylabel('ROLL (deg)')
    axROLL.set_xlabel(time_label)
    for i in range(N):
        column=df.columns[i]
        data=df[column].dropna()
        style=styles[i%len(styles)]
        if isinstance(style, basestring):
            axRA.plot(data.index,[q.ra for q in data],style)
            axDEC.plot(data.index,[q.dec for q in data],style)
            axROLL.plot(data.index,[q.roll for q in data],style)
        else:
            axRA.plot(data.index,[q.ra for q in data],**style)
            axDEC.plot(data.index,[q.dec for q in data],**style)
            axROLL.plot(data.index,[q.roll for q in data],**style)
    if labels is None: labels=df.columns
    if xlim is not None:
        axRA.set_xlim(xlim)
        axDEC.set_xlim(xlim)
        axROLL.set_xlim(xlim)
    if legend:
        axRA.legend(labels,loc=0,markerscale=2,numpoints=1)
    fig.tight_layout()
    return fig
def plotInnovations(dataframesList,time_label='Palestine Time',labels=None,styles=['b','r','g','k'],legend=False,xlim=None):
    for df in dataframesList:
        pass
def plotCovs(df,time_label='Palestine Time',ylabels=None,labels=None,styles=['b','r','g','k'],legend=False,xlim=None,function=lambda x: x,rotate=False):
    """Plot the first three diagonal elements of P of the pd.Dataframe df in a 3x1 subplots layout (P11,P22,P33)"""
    N=len(df.columns)
    fig,(axRA,axDEC,axROLL) =plt.subplots(3, 1, sharex=True, sharey=True)
    if ylabels is None:
        axROLL.set_ylabel(r'$P_{00}$')
        axDEC.set_ylabel(r'$P_{11}$')
        axRA.set_ylabel(r'$P_{22}$')
    else:
        axRA.set_ylabel(ylabels[0])
        axDEC.set_ylabel(ylabels[1])
        axROLL.set_ylabel(ylabels[2])
    axROLL.set_xlabel(time_label)
    M=np.matrix([[0.693865,0,0.720106],[0,1,0],[-0.720106,0,0.693865]])
    for i in range(N):
        column=df.columns[i]
        data=df[column].dropna() #matrix P
        index=data.index
        if rotate:
            data=[M*P[:3,:3]*M.T for P in data]
        style=styles[i%len(styles)]
        ROLLdata=[function(P[0,0]) for P in data]
        DECdata=[function(P[1,1]) for P in data]
        RAdata=[function(P[2,2]) for P in data]
        if isinstance(style, basestring):
            axRA.plot(index,RAdata,style)
            axDEC.plot(index,DECdata,style)
            axROLL.plot(index,ROLLdata,style)
        else:
            axRA.plot(index,RAdata,**style)
            axDEC.plot(index,DECdata,**style)
            axROLL.plot(index,ROLLdata,**style)
    if labels is None: labels=df.columns
    if xlim is not None:
        axRA.set_xlim(xlim)
        axDEC.set_xlim(xlim)
        axROLL.set_xlim(xlim)
    if legend:
        axRA.legend(labels,loc=0,markerscale=2,numpoints=1)
    fig.tight_layout()
    return fig
def filterArray(x,N=200,R=0.9):
    "Smoothes peaks from the np.array x. N:size of the peak, R: Recouvrement of the gliding window"
    ic=N/2 #central index
    ip=np.arange(0,N)
    
    while(ip[-1]<len(x)):        
        v0=x[ip[0]]
        vc=x[ip[ic]]
        vf=x[ip[-1]]
        if not isinstance(vc, Quat):
            d0=vc-v0     
            df=vc-vf
            m=(vf+v0)/2
            th=0
        else:
            d0=np.sum((vc*v0.inv()).q[:3])
            df=np.sum((vc*vf.inv()).q[:3])
            m=Quat((v0.q+vf.q)/2)
            th=0.001
            
        if abs(d0)>th and abs(df)>th:
            s0=np.sign(d0)
            sf=np.sign(df)  
            if s0!=0 and s0==sf:
                x[ip[1:-1]]=m
        ip=ip+int(np.ceil((1-R)*N))
    return x       
    #===========================================================================
    # peakind = find_peaks_cwt(x,np.arange(1,N))
    # print "peaks: %s"%len(peakind)
    # return np.delete(x, peakind)
    #===========================================================================
def filterQuats(df,onlyQuats=True):
    "Removes peaks from the quaternions of the dataframe df"
    for column in df.columns:
        v=df[column].iloc[0]
        if not onlyQuats or isinstance(v, Quat):
            df[column]=filterArray(df[column].values, N=3, R=0.9)         
    return df
def filterDataframe(df,N=3, R=0.9):
    "Removes peaks from the dataframe df"
    for column in df.columns:
        v=df[column].iloc[0]
        df[column]=filterArray(df[column].values, N=N, R=R)         
    return df
def extractDuplicates(df,th=1e-3):
    "Removes rows where there are duplicates of the quaternions at the first column of the dataframe df"
    toExtract=[df.index[0]]
    for column in df.columns[0:]:
        i0=df.index[0]
        if isinstance(df[column].loc[i0], Quat):
            for i in df.index[1:]:
                v0=df[column].loc[i0].ra
                vc=df[column].loc[i].ra
                if  abs(vc-v0)>th:
                    toExtract.append(i)
                i0=i
    df=df.loc[toExtract]            
    return df