'''
Created on 28 abr. 2017

Based on Maxime's files.
The DataSet class is very similar, but using 'outer' merges

@author: Marc Casalprim
'''
#===============================================================================
# from itertools import combinations
# from itertools import groupby
# from numpy import sin,cos,arctan2,arcsin
#===============================================================================
import os
import pandas as pd
import numpy as np
import seaborn.apionly as sns
import matplotlib.pyplot as plt
import scipy.stats as stats
from scipy.signal.spectral import periodogram
from quat import Quat,normalize


# plotting parameters
#===============================================================================
# mpl.rcParams['xtick.labelsize'] = 11
# mpl.rcParams['xtick.major.size'] = 5
# mpl.rcParams['ytick.major.size'] = 5
# mpl.rcParams['xtick.minor.size'] = 5
# mpl.rcParams['ytick.minor.size'] = 5
# mpl.rcParams['ytick.labelsize'] = 11
# mpl.rcParams['axes.labelsize'] = 11
# mpl.rcParams['legend.fontsize'] = 11
# mpl.rcParams['font.size'] = 11
# mpl.rcParams['font.weight'] = 100
# #mpl.rcParams['lines.linewidth'] = 2
# mpl.rcParams['font.family'] = 'serif'
# mpl.rcParams['font.serif'] = 'Times New Roman'
#===============================================================================

red = sns.xkcd_rgb['pale red']
blue = sns.xkcd_rgb['denim blue']
lt_blue = sns.xkcd_rgb['pastel blue']
colors = [blue,'g',red]

def load_single_field(fieldname,datatype,nValues=None,start=None):
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
    df={}
    for field in fieldsList:
        df[field.label]=load_single_field(folder+field.fieldName,field.dtype,nValues=nValues,start=start)
        if field.indexName not in df: df[field.indexName]=load_single_field(folder+field.indexName,field.indexType,nValues=nValues,start=start)
    return df
        
def genQuaternions(dataframe,quats={'qest':['qi','qj','qk','qr'],'qI2G':['qi_sc','qj_sc','qk_sc','qr_sc'],'qI2S':['ra_sc','dec_sc','roll_sc']},norm=False):
    lists={}
    matrices={}
    for key in quats.keys() :
        lists[key]=[]
        matrices[key]=dataframe[quats[key]].as_matrix()


    for i in range(len(dataframe.index)):
        for key in quats.keys() :
            q=Quat(matrices[key][i])
            if norm: q=q.normalize()
            lists[key].append(q)
     
    return lists

    
class DataSet():
        
    def __init__(self,folder=None,freq=400.,min=None,max=None,folder_export = None, nValues=None, start=None, verbose=False, rpeaks=True,estimator=False,starcam=False,fieldsList=[],foldersList=[],droplist = []):
        '''
        return a DataSet object containing df, a Pandas data frame indexed on the mceFramenumber
        Loads a list of fields fieldsList, the estimator data or the starcamera data dpeending on the correct parameters
        '''
        
        self.folder = folder
        self.times=dict() #dict storing np.arrays of the different indexes, to avoid loading them every time               
        self.df = pd.DataFrame()
        self.freq = freq
        self.min=min
        self.max=max
        if len(foldersList)<2:        self.readListFields(fieldsList,rpeaks=rpeaks,nValues=nValues,start=start,verbose=verbose)
        else:
            self.folder=foldersList[0]
            self.readMultipleFolders(fieldsList,foldersList,rpeaks=rpeaks, verbose=verbose)
        if estimator:
            self.readEstimator()
        if starcam:
            self.readStarcamera()
        
        if not self.df.empty:
            self.df = self.df.dropna(axis=0,how='all')
            self.df = self.df.drop(droplist)
            if rpeaks: #remove peaks
                self.df=self.df.loc[(self.df.abs()>=1).any(1)]  #remove rows were all fields have a value <1           
            self.df = self.df.loc[self.min:self.max,:]
                
        if folder_export == None: self.folder_export = self.folder.split('/')[-1]
        else: self.folder_export = folder_export
        
    def readListFields(self,fieldsList,folder=None,timeDivider=1,rpeaks=True, verbose=False, nValues=None,start=None,timeIndex=False):
        i=0
        if verbose: print 'Reading list of '+str(len(fieldsList))+' fields.'
        for field in fieldsList:
            i=i+1
            if verbose: print str(100*i/len(fieldsList))+'%', 
            self.readField(field, folder=folder,timeDivider=timeDivider,rpeaks=rpeaks,verbose=verbose,nValues=nValues,start=start)
        if verbose: print ''
        self.df = self.df.dropna(axis=0,how='all')
        self.df = self.df.loc[self.min:self.max,:]
        if rpeaks: #remove peaks
            self.df=self.df.loc[(self.df.abs()>=1).any(1)]  #remove rows were all fields have a value <1
    def readField(self,field,folder=None,timeDivider=1,rpeaks=True,verbose=False,nValues=None,start=None,timeIndex=False):
        if folder is None: folder=self.folder
        
        try:
            field_data = field.function(load_single_field(folder+field.fieldName,field.dtype,nValues=nValues,start=start))*field.conversion
            
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
                if field.fieldName=='bettii.GpsReadings.altitudeMeters': #its GPS data (no mceframenumber)
                    time=self.times['bettii.RTLowPriority.mceFrameNumber'] #get another mceFN vector of this archive
                    L=len(field_data)
                    time=time[time>1000]
                    time=np.linspace(time[0], time[-1], L)
                if field.indexName=='bettii.ThermometersDemuxedCelcius.mceFrameNumber': #its a thermometer
                    field_data=field_data[field_data!=0]
                    L=len(field_data)
                    time=time[time>1000]
                    time=np.linspace(time[0], time[-1], L)
                L=len(field_data)
                df_tmp = pd.DataFrame({label:field_data},index=time[:L]).sort_index()
                df_tmp = df_tmp[~df_tmp.index.duplicated(keep='first')] #remove values with duplicated index
                df_tmp=df_tmp[np.abs(df_tmp[label].as_matrix())<= field.range] #keep only the ones that are within fields range.
                df_tmp=df_tmp[df_tmp.index>1000] #keep only meaningful index (a FN less than 1000 is impossible)
                if not df_tmp.empty:
                    z=(np.abs(df_tmp.index)-np.mean(df_tmp.index))/np.std(df_tmp.index)
                    df_tmp=df_tmp[z<2] #keep only meaningful index (drop outliers >2sigmas)
                if timeIndex and len(df_tmp.index)>0:
                    text=folder.split('/')[-2]
                    ftime_str=text[0:8]+' '+text[9:17].replace('_',':') #foldertime
                    ftime=pd.to_datetime(ftime_str,yearfirst=True)
                    index=(df_tmp.index-df_tmp.index[0])/self.freq #time in seconds
                    index=pd.to_timedelta(index,unit='s')
                    time=ftime+index
                    df_tmp.index=time
                if self.df.empty: self.df = df_tmp
                elif label in self.df: self.df = self.df.combine_first(df_tmp)
                else: self.df =        pd.merge(self.df,df_tmp,how='outer',left_index=True,right_index=True) 
                if verbose: print field.fieldName+' read. '+str(len(field_data))+' raw values. '+str(len(df_tmp))+' deduplicated values.'
        except Exception as e:
            raise
            print 'ERROR reading '+field.fieldName+':', e
    
    def readMultipleFolders(self,fieldsList,foldersList,rpeaks=False, verbose=False,timeIndex=True):
        i=0
        dftmp=pd.DataFrame()
        for folder in foldersList:
            if verbose: print 'Reading list of '+str(len(fieldsList))+' fields from folder '+folder+'.'
            self.times=dict()
            self.df=pd.DataFrame()
            for field in fieldsList:
                i=i+1
                if verbose: print str(100*i/len(foldersList)/len(fieldsList))+'%', 
                self.readField(field, folder=folder,rpeaks=rpeaks,verbose=verbose,timeIndex=False)
            if verbose: print ''
            self.df = self.df.dropna(axis=0,how='all')
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
        
        # trigger pulses (aligned with mceFrameNmber); this tells us how long the exposure time was, in number of frames (400Hz)
        #position given by the star camera corresponds should be compared to the estimated position at the 
        # at the location of the trigger (the index of this pulse) + half the amount of this pulse's value
        
        #=======================================================================
        # starcam_trigger_pulses =load_single_field(folder+'bettii.RTHighPriority.StarCameraTriggerStatus','i8')
        # 
        # 
        # #sort out the triggers and bad data lines
        # pulses = pd.DataFrame({'duration': starcam_trigger_pulses},index = self.times['bettii.RTHighPriority.mceFrameNumber']/timeDivider)
        # pulses.drop_duplicates(inplace=True)
        # durations = self.pulses.loc[df_solution['triggers']]
        # durations = pd.DataFrame(durations,index = durations.index)
        # df_solution = pd.merge(df_solution,durations,how='inner',left_on='triggers',right_index=True)
        # df_solution = df_solution.dropna(axis=0)
        # df_solution['trigger_center'] = df_solution['triggers']+np.round(df_solution['duration']/8)*4
        #=======================================================================
        
        # what are the estimated values?
        #self.df = pd.merge(self.df,df_solution,how='outer',left_on='trigger_center',right_index=True)
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
        
def plotColumns(df,units=''):
    data = df.dropna()
    plt.figure()
    N=len(data.columns)
    for i in range(N):
        column=data.columns[i]
        ax=plt.subplot(N,1,i)
        data[column].plot(ax=ax)
        ax.set_ylabel(column+' '+units)
    ax.set_xlabel('Index')