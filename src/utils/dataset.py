'''Created on 28 abr. 2017

Conatins useful functions to read and plot the fields archived by Aurora. The DataSet class reads and creates a ``pandas.Dataframe`` object containing the desired fields.

@author: Marc Casalprim
'''
import pandas as pd
import numpy as np
from quat import Quat
from config import os,plt
from thermometers import unwrapCounter



def load_single_field(filename, datatype, nValues=None, start=None):
    """Reads a binary file. It uses the ``np.fromfile`` function.
    
    :param filename: complete filename of the field to read
    :param datatype: data type of the binary file (eg. int32 -> 'i4')
    :param nValues: number of values we want to read (if None, all of them)
    :param start: value from where we start counting nValues (if None, starting from the end of file)
    :return: values of the field
    :rtype: np.array
    
    """
    type_str_native = ">" + datatype
    type_str_final = "<" + datatype  # change endianness
    
    if nValues is None:
        field = np.fromfile(filename, dtype=np.dtype(type_str_native))
    else:
        bpv = int(datatype[-1])  # bytes per value
        f = open(filename, "rb")
        try:
            if start is None:
                nBytes = nValues * bpv 
                f.seek(-nBytes, os.SEEK_END)
            else:
                nBytes = start * bpv
                f.seek(nBytes, os.SEEK_SET)
    
        
            field = np.fromfile(f, dtype=np.dtype(type_str_native), count=nValues)
        finally:
            f.close()

    field = field.astype(type_str_final)
    return field

def load_fields(fieldsList, folder=None, nValues=None, start=None):
    """Reads the fields in fieldsList that are in the folder
    
    :param fieldsList: list of utisl.field.Field to read
    :param folder: folder where the fields will be read
    :param nValues: number of values we want to read (if None, all of them)
    :param start: value from where we start counting nValues (if None, starting from the end of file)
    :return: dictionary of ``np.array`` keyed by the field's label
    :rtype: dict
    
    """
    df = {}
    for field in fieldsList:
        df[field.label] = load_single_field(folder + field.fieldName, field.dtype, nValues=nValues, start=start)
        if field.indexName not in df: df[field.indexName] = load_single_field(folder + field.indexName, field.indexType, nValues=nValues, start=start)
    return df
        
def genQuaternions(dataframe, quats={'qest':['qi', 'qj', 'qk', 'qr'], 'qI2G':['qi_sc', 'qj_sc', 'qk_sc', 'qr_sc'], 'qI2S':['ra_sc', 'dec_sc', 'roll_sc']}, norm=False, filter=False):
    '''Generates a dictionary of lists of ``:meth:~`utils.quat.Quat``` objects using the columns of the dataframe defined by the quats dictionary values.
    The returned dictionary will have the same keys as quats
    
    :param dataframe: pandas.DataFrame object, with
    :param quats: dictionary defining the columns to read that will be passed to the :meth:`utils.quat.Quat` contructor
    :param norm: normalize quaternion?
    :param filter: filter the quaternions?
    :return: dictionary of utils.Quat lists, keyed by quats keys.
    '''
    lists = {}
    matrices = {}
    for key in quats.keys() :
        lists[key] = []
        matrices[key] = dataframe[quats[key]].as_matrix()


    for i in range(len(dataframe.index)):
        for key in quats.keys() :
            v = matrices[key][i]
            q = Quat(v)
            if filter:
                if len(v) == 4:
                    if abs(q) > 1.5 or abs(q) < 0.7:
                        q = np.nan
                else:
                    if np.mean(abs(v[:2])) < 0.01:
                        q = np.nan
            if norm and not filter and isinstance(q, Quat): q = q.normalize()
            lists[key].append(q)
     
    return lists

def extractGyrosAndStarcam(dataframe, labels_gyros=['gyroX', 'gyroY', 'gyroZ'], label_triggers='triggers', labels_scerrors=['ra_err', 'dec_err', 'roll_err']):
    '''Returns three dataframes with the Groscopes, Starcamera and Quaternions data respectively.
    Synchronizes the Starcamera with the triggers. Useful for the Estimator classes.
    
    :param dataframe: pandas dataframe containing all the infromation to extract
    :param labels_gyros: columns of the dataframe that contain the gyroscopes information
    :param label_triggers: column of the dataframe that contains the triggers information
    :param labels_scerrors: columns of the dataframe that contain the star camera uncertainties information
    :return: gyros,sc,quats: pandas dataframes with the gyroscopes, star camera and quaternions data respectively.
    '''
    SClabels = ['qI2G', 'qI2S']

    print "Creating Starcam dataframe..."
    triggers = dataframe[label_triggers].drop_duplicates()
    L = 1e300
    while (L - len(triggers)) > 0:
        L = len(triggers)
        triggers = triggers[[(triggers.loc[mceFN] < max(triggers.index) and triggers.loc[mceFN] > (min(triggers.index) - 10000)) for mceFN in triggers.index]]
    subdf = dataframe.loc[triggers.index].drop_duplicates(subset=['dec_sc', 'ra_sc', 'roll_sc']).dropna()
    index = triggers.loc[subdf.index].index  # values #here we can index the sc dataframe with the triggers (using .values instead of .index), they dont seem to be
    sc = pd.DataFrame(genQuaternions(subdf, norm=True, filter=True), index=index)[SClabels].dropna()
    if labels_scerrors is not None: sc[labels_scerrors] = dataframe[labels_scerrors].loc[sc.index]
    sc[label_triggers] = triggers.loc[subdf.index]
    print "Number of solutions: %s" % len(sc)
    print "Generating estimator quaternions..."
    quats = genQuaternions(dataframe, quats={'qest':['qi', 'qj', 'qk', 'qr']}, norm=True)['qest']
    print "Filtering..."

    Ps = extractPs(dataframe)
    est = dataframe[['biasX','biasY','biasZ']]
    est['P']=Ps
    est['qest']=quats
    est = filterQuats(est)
    
 
    if labels_gyros is not None: gyros = dataframe[labels_gyros].dropna().interpolate(method='values')
    else: gyros = None
    # print 'Done'  
    return gyros, sc, est
def extractPs(dataframe):
    data=dataframe[['P00','P01','P02','P10','P11','P12','P20','P21','P22']]
    L=len(data.P00)
    Ps=[np.eye(3)]*L

    for i in range(L):
        m=(data.iloc[i].as_matrix())
        P=m.reshape((3,3))
        Ps[i]=P
    return Ps
        
class DataSet():
    '''Class containing useful methods to read and generate a pandas dataframe containing the desired fields.
    Derived from Maxime's original codes. The dataframe is stored as the attribute df.
    '''
    def __init__(self, folder=None, freq=400., min=None, max=None, folder_export=None, nValues=None, start=None, verbose=False, rpeaks=False, estimator=False, starcam=False, fieldsList=[], foldersList=[], droplist=[], timeIndex=False):
        '''Constructs a DataSet object
        Loads a list of fields fieldsList, the estimator data or the starcamera data dpeending on the correct parameters
        
        :param folder: folder where the fields in fieldsList are located
        :param freq: frequency of the mce (default 400Hz)
        :param min: minimum mceFN value
        :param max: maximum mceFN value
        :param folder_export: folder where the plots will be saved
        :param nValues: number of values to read from the files (if None, all the file is read)
        :param start: value from where we start to read (if None, we count nValues from the end)
        :param verbose: Print progress of the dataframe generation
        :param rpeaks: Remove rows were all fields have values less than 1 (typical error when using telemetry archives)
        :param estimator: read estimator data?
        :param starcam: read starcam data?
        :param fieldsList: list of utils.field.Field objects, representing the fields to store on the dataframe.
        :param foldersList: list of folders, data will be merged
        :param droplist: list of columns to drop before returning DataSet object
        '''
        
        self.folder = folder
        self.times = dict()  # dict storing np.arrays of the different indexes, to avoid loading them every time               
        self.df = pd.DataFrame()
        self.freq = freq
        self.min = min
        self.max = max
        if len(foldersList) < 2:
            if len(foldersList) == 1: self.folder = foldersList[0]
            self.readListFields(fieldsList, rpeaks=rpeaks, nValues=nValues, start=start, verbose=verbose, timeIndex=timeIndex)
        else:
            self.folder = foldersList[0]
            self.readMultipleFolders(fieldsList, foldersList, rpeaks=rpeaks, verbose=verbose, timeIndex=True)
        
        if estimator:
            self.readEstimator()
        if starcam:
            self.readStarcamera()
        
        if not self.df.empty:
            self.df = self.df.dropna(axis=0, how='all')
            self.df = self.df.drop(droplist)
            if rpeaks:  # remove return to 0 peaks
                self.df = self.df.loc[(self.df.abs() >= 1).any(1)]  # remove rows were ALL fields have a value <1           
            # self.df = self.df.loc[self.min:self.max,:]
                
        if folder_export == None: self.folder_export = self.folder.split('/')[-1]
        else: self.folder_export = folder_export
        
    def readListFields(self, fieldsList, folder=None, rpeaks=True, verbose=False, nValues=None, start=None, timeIndex=False):
        '''Reads a list of fields and stores the new fields in the df attribute
        
        :param fieldsList: list of utils.field.Field objects
        :param folder: folder where the fields are located
        :param rpeaks: remove peaks? (where all the values are zero)
        :param verbose: print progress?
        :param nValues: number of values to read
        :param start: where to start reading the files
        :param timeIndex: index by time? (derived from the folder name)
        '''
        if folder is None: folder = self.folder
        i = 0
        if verbose: print 'Reading list of ' + str(len(fieldsList)) + ' fields.'
        for field in fieldsList:
            i = i + 1
            if verbose: print str(100 * i / len(fieldsList)) + '%',
            self.readField(field, folder=folder, rpeaks=rpeaks, verbose=verbose, nValues=nValues, start=start)
        if verbose: print ''
        self.df = self.df.dropna(axis=0, how='all').sort_index()
        self.df = self.df.loc[self.min:self.max, :]
        if timeIndex and len(self.df.index) > 0:
            text = folder.split('/')[-2]
            ftime_str = text[0:8] + ' ' + text[9:17].replace('_', ':')  # foldertime
            ftime = pd.to_datetime(ftime_str, yearfirst=True)
            index = (self.df.index - self.df.index[0]) / self.freq  # time in seconds
            index = pd.to_timedelta(index, unit='s')
            time = ftime + index
            self.df.index = time
        if rpeaks:  # remove return to 0 peaks
            self.df = self.df.loc[(self.df.abs() >= 1).any(1)]  # remove rows were all fields have a value <1
    def readField(self, field, folder=None, rpeaks=True, verbose=False, nValues=None, start=None, timeIndex=False):
        '''Reads a single field and updates the dataframe df accordingly.
        
        :param field: utils.field.Field object to read
        :param folder: folder where the fileds are located (if None, uses self.folder)
        :param rpeaks: remove peaks? (where all the values are zero)
        :param verbose: print progress?
        :param nValues: number of values to read
        :param start: where to start reading the files
        :param timeIndex: index by time? (derived from the folder name)
        '''
        if folder is None: folder = self.folder
        
        try:
            field_data = field.function(load_single_field(folder + field.fieldName, field.dtype, nValues=nValues, start=start)) * field.conversion
            Lraw = len(field_data)
            timeName = field.indexName
            timeType = field.indexType
            if nValues is None: #if we read everything in the file (we consider no RT)
                if timeName in self.times.keys(): time = self.times[timeName] #use the same time index if its already read
                else:
                    if verbose: print 'Time reference ' + timeName + ' not loaded in local dataset yet. Adding...',
                    time = load_single_field(folder + timeName, timeType)
                    self.times[timeName] = time #store the time for future reference
            elif start is None: #if we start from the end (we consider RT)
                    if verbose: print 'Time reference ' + timeName + ' not loaded in local dataset yet. Adding...',
                    time = load_single_field(folder + timeName, timeType, nValues=nValues)  # reading index every time, reading last nValues from the end
                    self.times[timeName] = time
            else: #if the start is determined (we consider RT)
                if timeName in self.times.keys():
                    d = (start + nValues) - len(self.times[timeName])  # number of extra values we need
                    if d > 0:
                        if verbose: print 'Expanding time index ' + timeName + ' in local dataset...'
                        time = load_single_field(folder + timeName, timeType, nValues=d, start=len(self.times[timeName])) #read extra values
                        self.times[timeName] = np.concatenate((self.times[timeName], time)) #add them to the stored time                    
                else:
                    if verbose: print 'Time reference ' + timeName + ' not loaded in local dataset yet. Adding...'
                    time = load_single_field(folder + timeName, timeType, nValues=start + nValues, start=0) #read all file from the beggining until nValues
                    self.times[timeName] = time #store it
                
                time = (self.times[timeName])[start:start + nValues] #desired time index
            
            label = field.label
            
            if label in self.df.keys() and len(self.df[label].as_matrix()) == len(field_data): #if field already in df and has the same number of values
                if verbose: print label + ' already in dataframe.'
            else:
                indmin = 50000  # minimum index, frame number (the archives start with low mceframenumbers and then jump to the actual frame n umber)
                if field.fieldName == 'bettii.GpsReadings.altitudeMeters' or 'PiperThermo' in field.fieldName:  # its PIPER or GPS data (theres no mceframenumber)
                    time = self.times['bettii.RTLowPriority.mceFrameNumber']  # get another mceFN vector of this archive
                    L = len(field_data)
                    time = time[time > indmin]
                    DT = (time[-1] - time[0])
                    time = np.round(np.linspace(time[0], time[0] + DT, L)) #generate a virtual time vector with the same dimensions as field_data
                if "TRead" in field.fieldName:  # its TRead message (using frame counter)
                    time = (unwrapCounter(time) + indmin) * 400  # time has to be TRead[...].frameCounter
                if field.indexName == 'bettii.ThermometersDemuxedCelcius.mceFrameNumber':  # its a thermometer, bad timing
                    field_data = field_data[field_data != 0] #removing zeros of the thermometers
                    L = len(field_data)
                    time = time[time > indmin]
                    time = np.linspace(time[0], time[-1], L)  # we expand the time (i dont understand the logic of the thermomemeters mceframenumber)
                L = min(len(field_data), len(time))
                df_tmp = pd.DataFrame({label:field_data[:L]}, index=time[:L]).sort_index()  # create temporal dataframe
                df_tmp = df_tmp[~df_tmp.index.duplicated(keep='first')]  # remove values with duplicated index
                df_tmp = df_tmp[np.abs(df_tmp[label].as_matrix()) <= field.range]  # keep only the ones that are within fields range.
                df_tmp = df_tmp[df_tmp.index > indmin]  # keep only meaningful index (a FN less than indmin is impossible)
                if False and not df_tmp.empty: #disabled part of the code to remove outliers
                    z = (np.abs(df_tmp.index) - np.mean(df_tmp.index)) / np.std(df_tmp.index)
                    df_tmp = df_tmp[z < 2]  # keep only meaningful index (drop outliers >2sigmas), seems dangerous but there are always bad mceFN that mess the entire plot
                if timeIndex and len(df_tmp.index) > 0: #time index conversion, using the folder name as the time at df_tmp.index[0]
                    text = folder.split('/')[-2]
                    ftime_str = text[0:8] + ' ' + text[9:17].replace('_', ':').replace('-', '')  # foldertime
                    ftime = pd.to_datetime(ftime_str, yearfirst=True)
                    index = (df_tmp.index - df_tmp.index[0]) / self.freq  # time in seconds
                    index = pd.to_timedelta(index, unit='s')
                    time = ftime + index
                    df_tmp.index = time
                if self.df.empty: self.df = df_tmp #assign the new dataframe
                elif label in self.df: self.df = self.df.combine_first(df_tmp) #add extra information of the field already existant in the dataframe
                else: self.df = pd.merge(self.df, df_tmp, how='outer', left_index=True, right_index=True) #add the new field
                if verbose: print field.fieldName + ' read. ' + str(Lraw) + ' raw values. ' + str(len(df_tmp)) + ' deduplicated values.'
        except Exception as e:
            raise
            print 'ERROR reading ' + field.fieldName + ':', e
    
    def readMultipleFolders(self, fieldsList, foldersList, rpeaks=False, verbose=False, timeIndex=True):
        """Stores in self.df a new pd.DatFrame object containing
        the fieldsList data from all the folders in foldersList.
        The indexing of the DataFrame is a DatetimeIndex by default
        (timeIndex=True), using the date and time of the folder name.
        
        :param fieldsList: list of utils.field.Field objects
        :param foldersList: list of folders where the fields are located
        :param rpeaks: remove peaks? (where all the values are zero)
        :param verbose: print progress?
        :param timeIndex: index by time? (derived from the folder name)

        """
        i = 0
        dftmp = pd.DataFrame()  # temporal dataframe where all the data is being merged
        for folder in foldersList:
            if verbose: print 'Reading list of ' + str(len(fieldsList)) + ' fields from folder ' + folder + '.'
            self.times = dict()
            self.df = pd.DataFrame()  # reset of self.df, that way we can use readField method
            for field in fieldsList:
                i = i + 1
                if verbose: print str(100 * i / len(foldersList) / len(fieldsList)) + '%',
                self.readField(field, folder=folder, rpeaks=rpeaks, verbose=verbose, timeIndex=False)
            if verbose: print ''
            self.df = self.df.dropna(axis=0, how='all')
            # if True, change mceFN indexing to a DatetimeIndex
            # Using folder name as the time for the first mce frame
            if timeIndex and len(self.df.index) > 0:
                text = folder.split('/')[-2]
                ftime_str = text[0:8] + ' ' + text[9:17].replace('_', ':')  # foldertime
                ftime = pd.to_datetime(ftime_str, yearfirst=True)
                index = (self.df.index - self.df.index[0]) / self.freq  # time in seconds
                index = pd.to_timedelta(index, unit='s')
                time = ftime + index
                self.df.index = time
            if dftmp.empty: dftmp = self.df
            else: dftmp = dftmp.combine_first(self.df)
            
        self.df = dftmp

#===============================================================================
#     def readEstimator(self, folder=None, timeDivider=1):
#         if folder is None: folder = self.folder
#         # covariance matrix
#         Cov00 = np.sqrt(load_single_field(folder + 'bettii.RTLowPriority.MeasurementErrorCovarianceMatrixR00', 'f8')) / 4.8484e-6
#         Cov11 = np.sqrt(load_single_field(folder + 'bettii.RTLowPriority.MeasurementErrorCovarianceMatrixR11', 'f8')) / 4.8484e-6
#         Cov22 = np.sqrt(load_single_field(folder + 'bettii.RTLowPriority.MeasurementErrorCovarianceMatrixR22', 'f8')) / 4.8484e-6
# 
#         # estimator (show only diagonal values)
#         Q00 = np.sqrt(load_single_field(folder + 'bettii.RTLowPriority.covarianceMatrix00', 'f8')) / 4.8484e-6
#         Q11 = np.sqrt(load_single_field(folder + 'bettii.RTLowPriority.covarianceMatrix11', 'f8')) / 4.8484e-6
#         Q22 = np.sqrt(load_single_field(folder + 'bettii.RTLowPriority.covarianceMatrix22', 'f8')) / 4.8484e-6
#         Q33 = np.sqrt(load_single_field(folder + 'bettii.RTLowPriority.covarianceMatrix33', 'f8')) / 4.8484e-6
#         Q44 = np.sqrt(load_single_field(folder + 'bettii.RTLowPriority.covarianceMatrix44', 'f8')) / 4.8484e-6
#         Q55 = np.sqrt(load_single_field(folder + 'bettii.RTLowPriority.covarianceMatrix55', 'f8')) / 4.8484e-6
# 
#         # bias
#         biasX = load_single_field(folder + 'bettii.RTHighPriority.estimatedBiasXarcsec', 'f8')
#         biasY = load_single_field(folder + 'bettii.RTHighPriority.estimatedBiasYarcsec', 'f8')
#         biasZ = load_single_field(folder + 'bettii.RTHighPriority.estimatedBiasZarcsec', 'f8')
#         
#         self.times['bettii.RTLowPriority.mceFrameNumber'] = load_single_field(folder + 'bettii.RTLowPriority.mceFrameNumber', 'i8')
# 
#         # estimator
#         qr_list = load_single_field(folder + 'bettii.RTLowPriority.qr', 'f8')
#         qi_list = load_single_field(folder + 'bettii.RTLowPriority.qi', 'f8')
#         qj_list = load_single_field(folder + 'bettii.RTLowPriority.qj', 'f8')
#         qk_list = load_single_field(folder + 'bettii.RTLowPriority.qk', 'f8')
#         estimated_quatlist = [Quat(normalize((qi_list[i], qj_list[i], qk_list[i], qr_list[i]))) for i in range(len(qr_list))]
#         est_ra = [q.ra * 3600. for q in estimated_quatlist]
#         est_dec = [q.dec * 3600. for q in estimated_quatlist]
#         est_roll = [q.roll * 3600. for q in estimated_quatlist]
# 
#         estimatorData = {'Cov00':Cov00, 'Cov11':Cov11, 'Cov22':Cov22,
#                         'Q00':Q00, 'Q11':Q11, 'Q22':Q22, 'Q33':Q33, 'Q44':Q44, 'Q55':Q55,
#                         'ra':est_ra, 'dec':est_dec, 'roll':est_roll, 'est_q':estimated_quatlist
#                         }
#         biasData = {'biasX':biasX, 'biasY':biasY, 'biasZ':biasZ}
#         df_estimator = pd.DataFrame(estimatorData, index=self.times['bettii.RTLowPriority.mceFrameNumber'] / timeDivider)
#         df_estimator.drop_duplicates(inplace=True)
# 
#         df_bias = pd.DataFrame(biasData, index=self.times['bettii.RTHighPriority.mceFrameNumber'] / timeDivider)
#         df_bias.drop_duplicates(inplace=True)
#         df_tmp = pd.merge(self.df, df_estimator, how='outer', left_index=True, right_index=True)
#         self.df = pd.merge(df_tmp, df_bias, how='outer', left_index=True, right_index=True)
#     
#     def readStarcamera(self, folder=None, timeDivider=1):
#         if folder is None: folder = self.folder
#         # ## star camera loading
#         # Load star camera trigger number
#         # this is the mceFrameNumber at which the starcamera trigger occurred, and which is processed by the starFinder
#         starcam_trigger = load_single_field(folder + 'bettii.RTLowPriority.RawStarcameraMceFrameNumberWhenSCTriggered', 'i8')
#          
#         self.times['bettii.RTLowPriority.mceFrameNumber'] = load_single_field(folder + 'bettii.RTLowPriority.mceFrameNumber', 'i8')
#          
#         meas_qr_list = load_single_field(folder + 'bettii.RTLowPriority.StarCameraRotatedqr', 'f8')
#         meas_qi_list = load_single_field(folder + 'bettii.RTLowPriority.StarCameraRotatedqi', 'f8')
#         meas_qj_list = load_single_field(folder + 'bettii.RTLowPriority.StarCameraRotatedqj', 'f8')
#         meas_qk_list = load_single_field(folder + 'bettii.RTLowPriority.StarCameraRotatedqk', 'f8')
#  
#         starcamsol = {'triggers': starcam_trigger,
#                     'meas_qr': meas_qr_list,
#                     'meas_qi': meas_qi_list,
#                     'meas_qj': meas_qj_list,
#                     'meas_qk': meas_qk_list,
#                     }
#         df_solution = pd.DataFrame(starcamsol, index=self.times['bettii.RTLowPriority.mceFrameNumber'] / timeDivider)
#         df_solution.drop_duplicates(inplace=True)
#         df_solution = df_solution.loc[np.abs(df_solution['meas_qr']) > 1e-10]
#         df_solution = df_solution.loc[np.abs(df_solution['meas_qr']) <= 1.0]
#         df_solution = df_solution.loc[np.abs(df_solution['meas_qi']) <= 1.0]
#         df_solution = df_solution.loc[np.abs(df_solution['meas_qj']) <= 1.0]
#         df_solution = df_solution.loc[np.abs(df_solution['meas_qk']) <= 1.0]
#         df_solution = df_solution.drop_duplicates(subset='triggers')  # only keeps the unique values for triggers
#          
#         # convert to ra/dec/roll
#         # print df_solution.iloc[5][['meas_qi','meas_qj','meas_qk','meas_qr']]
#         measured_quatlist = [Quat(normalize(df_solution.loc[mceFN][['meas_qi', 'meas_qj', 'meas_qk', 'meas_qr']])) for mceFN in df_solution.index]
#         meas_ra_calc = [q.ra * 3600. for q in measured_quatlist]
#         meas_dec_calc = [q.dec * 3600. for q in measured_quatlist]
#         meas_roll_calc = [q.roll * 3600. for q in measured_quatlist]
#          
#         meas_radecroll = {'ra_sc':meas_ra_calc,
#                         'dec_sc':meas_dec_calc,
#                         'roll_sc':meas_roll_calc,
#                         'q_sc': measured_quatlist
#                         }
#         df_solution = pd.merge(df_solution, pd.DataFrame(meas_radecroll, index=df_solution.index), how='inner', left_index=True, right_index=True)
#         df_solution = df_solution.drop(['meas_qi', 'meas_qj', 'meas_qk', 'meas_qr'], 1)
#          
#         self.df = pd.merge(self.df, df_solution, how='outer', left_index=True, right_index=True)
#  
#     def simplePlot(self, val, minMax=[], ylabel="", origin=0, ax_key=None, save=False, draw=True, realTime=True, name=None, color=sns.xkcd_rgb['denim blue']):
#         print "simplePlot, Loading %s data..." % val
#         if ax_key == None: fig, ax = plt.subplots(figsize=(5.9, 4), dpi=120)
#         else: ax = ax_key
#         data = self.df[val].dropna()
#         ax.set_xlabel("Time (s)")
#         ax.set_ylabel(ylabel)
#         ax.grid(True)
#         if realTime: ax.plot(data.index / self.freq - origin, data, label=val, color=color)
#         else: ax.plot(data.index - origin, data, label=val, color=color)
#         if minMax != []:
#             ax.set_xlim = minMax
#         ax.legend(loc='best')
#         if ax_key == None:
#             fig.tight_layout()
#             if save: 
#                 if name == None: fig.savefig(self.folder_export + "simplePlot_%s.png" % val, dpi=300)
#                 else: fig.savefig(self.folder_export + name + "_%s.png" % val, dpi=300)
#             if draw: plt.draw()
#             # plt.close(fig)
#         print "Done."
#     def simple2DPlot(self, field1, field2, minMax=[], xlabel="", ylabel="", ax_key=None, save=False, draw=True, realTime=True, name=None, kde=False, color=sns.xkcd_rgb['denim blue']):
#         print "simple2DPlot, Loading data..."
#         if ax_key == None: fig, ax = plt.subplots(figsize=(5.9, 4), dpi=120)
#         else: ax = ax_key
#         data = self.df[[field1, field2]].dropna()
#         data1 = data[field1]
#         data2 = data[field2]
#         ax.set_xlabel(xlabel)
#         ax.set_ylabel(ylabel)
#         ax.grid(True)
#         ax.scatter(data1, data2, color=color, alpha=0.4)
#         if kde:
#             sns.kdeplot(data1, data2, ax=ax)
#         ax.set_xlabel(xlabel)
#         ax.set_ylabel(ylabel)
#         ax.grid(True)
#         if ax_key == None:
#             fig.tight_layout()
#             if save: 
#                 if name == None: fig.savefig(self.folder_export + "simple2DPlot_%s_%s.png" % (field1, field2), dpi=300)
#                 else: fig.savefig(self.folder_export + name + "_%s_%s.png" % (field1, field2), dpi=300)
#             if draw: plt.draw()
#             # plt.close(fig)
#         print "Done."
#      
#     def integralPlot(self, val, minMax=[], ylabel="", save=False, show=True, realTime=True, name=None):
#         print "Loading %s data..." % val
#         fig, ax = plt.subplots(figsize=(5.9, 4), dpi=120)
#         data = np.cumsum(self.df[val]) / np.float(self.freq)
#         ax.set_xlabel("Time (s)")
#         ax.set_ylabel(ylabel)
#         ax.grid(True)
#         if realTime: ax.plot(self.df.index / 400., data, label=val, color=blue)
#         else: ax.plot(self.df.index, data, label=val, color=blue)
#         if minMax != []:
#             ax.set_xlim = minMax
#         ax.legend(loc='best')
#         fig.tight_layout()
#         if save: 
#             if name == None: fig.savefig(self.folder_export + "integralPlot_%s.png" % val, dpi=300)
#             else: fig.savefig(self.folder_export + name + "_%s.png" % val, dpi=300)
#         if show: plt.draw()
#         # plt.close(fig)
#         print "Done."
#  
#          
#     def PSD(self, column, draw=True, save=False, loglog=True, ax_key=None, minPlot=None, name=None, minMax=[], units='(arcsec/s)$^2$/Hz'):
#         print "PSD, Loading data..."
#         data = self.df[column].dropna()
#         if ax_key == None: fig, ax = plt.subplots(figsize=(5.9, 4), dpi=120)
#         else: ax = ax_key
#         print "Calculating power spectral density..."
#         f, Pxx_den = periodogram(data, self.freq)
#         if loglog: ax.loglog(f, Pxx_den, label=column)
#         else:ax.plot(f, Pxx_den, label=column)
#         ax.set_xlabel('Frequency [Hz]')
#         ax.set_ylabel('PSD [' + units + ']')
#         if minPlot != None and minMax == []: ax.set_xlim([minPlot, max(f)])
#         elif minMax != []: ax.set_xlim(minMax)
#         ax.set_ylim([min(Pxx_den), max(Pxx_den)])
#         ax.legend(loc='best')
#         ax.grid(True)
#         if ax_key == None:
#             fig.tight_layout()
#             if save:
#                 if name == None: fig.savefig(self.folder_export + "PSD%d.png" % self.freq, dpi=300)
#                 else: fig.savefig(self.folder_export + name + "_%d.png" % self.freq, dpi=300)
#             if draw: plt.draw()
#             # plt.close(fig)
#         print "Done."
#  
#     def multiPSD(self, columns, show=True, save=False, loglog=False, name=None, minMax=[], units='(arcsec/s)$^2$/Hz'):
#         print "Plotting multiple PSDs"
#         fig, axlist = plt.subplots(len(columns), figsize=(5.9, 8), dpi=120)
#         for i in range(len(columns)):
#             ax = axlist[i]
#             self.PSD(columns[i], save=False, loglog=loglog, ax_key=ax, minPlot=0.001, minMax=minMax, units=units)
#             if minMax != []:
#                 ax.set_xlim = minMax
#         fig.tight_layout()
#         if save:
#             if name == None: fig.savefig(self.folder_export + "multiPSD%d.png" % self.freq, dpi=300)
#             else: fig.savefig(self.folder_export + name + "_%d.png" % self.freq, dpi=300)
#         if show: plt.draw()
#         # plt.close(fig)
#  
#     def kde(self, column, show=True, ax_key=None, save=False):
#         print "Kernel estimation..."
#         data = self.df[column].dropna()
#         if ax_key == None: fig, ax = plt.subplots(figsize=(5.9, 4), dpi=120)
#         else: ax = ax_key
#         kernel = stats.gaussian_kde(data)
#         print "Calculating histogram of dataset..."
#         hist, bin_edges = np.histogram(data, bins=50, density=True)
#         print "Plotting..."
#         ax.bar(bin_edges[:-1], hist, width=np.diff(bin_edges), color=blue, alpha=0.7)
#         ax.set_xlim(min(bin_edges), max(bin_edges))
#         xaxis = np.linspace(min(bin_edges), max(bin_edges), 200)
#         ax.set_xlabel('Angular velocity bins (arcsec/s)')
#         ax.set_ylabel('Probability density')
#         ax.plot(xaxis, kernel(xaxis), color=red, lw=2)
#         if ax_key == None:
#             fig.tight_layout()
#             if save:fig.savefig(self.folder_export + "hist_%s.png" % 'name', dpi=300)
#             if show: plt.draw()
#             # plt.close(fig)
#         print "Done."
#===============================================================================

def toTimeIndex(dataframe, folder, freq=400.):
    """Returns the same dataframe but with the indices in DateTime format.
    The input dataframe must have mceFrameNumber indices.
    The time in the folder is considered as the starting time for the first mce frame number.   
    
    :param dataframe: pd.Dataframe object
    :param folder: folder name
    :param freq: frequency of the index (default 400 Hz)
    :return: dataframe with DateTime indices
    :rtype: pd.Dataframe
    
    """
    text = folder.split('/')[-2]
    ftime_str = text[0:8] + ' ' + text[9:17].replace('_', ':')  # foldertime
    ftime = pd.to_datetime(ftime_str, yearfirst=True)
    index = (dataframe.index - dataframe.index[0]) / freq  # time in seconds
    index = pd.to_timedelta(index, unit='s')
    time = ftime + index
    dataframe.index = time
    return dataframe   

def plotColumns(df, units='', xlabel='Index', ylabels=None):
    """Plot the N columns of the pd.Dataframe df in a Nx1 subplots layout
    
    :param df: pd.Dataframe object
    :param units: string to add at the end of the ylabels
    :param xlabel: label of the x axis
    :param ylabels: labels of the y axis (if None, ylabels=df.columns)
    :return: figure
    """
    data = df.dropna()
    N = len(data.columns)
    fig, axes = plt.subplots(N, 1, sharex=True, sharey=True)
    for i in range(N):
        column = data.columns[i]
        data[column].plot(ax=axes[i])
        if ylabels is None: axes[i].set_ylabel(column + ' ' + units)
        else: axes[i].set_ylabel(ylabels[i] + ' ' + units)
    axes[-1].set_xlabel(xlabel)
    fig.tight_layout()
    return fig
def plotQuaternions(df, time_label='Palestine Time', labels=None, styles=['b', 'r', 'g', 'k'], legend=False, xlim=None):
    '''Plot the quaternions of the pd.Dataframe df in a 3x1 subplots layout (RA,DEC,ROLL)
    
    :param df: a pd.Dataframe containing exclusively utils.quat.Quat objects
    :param time_label: label of the x axis
    :param labels: legend labels of every column (if None, use df.columns as labels)
    :param styles: plot styles or kwargs of every column
    :param legend: show legend?
    :param xlim: limits of the x axis [xmin,xmax]
    :return: figure
    :rtype: matplotlib.figure
    '''
    N = len(df.columns)
    fig, (axRA, axDEC, axROLL) = plt.subplots(3, 1, sharex=True, sharey=True)
    axRA.set_ylabel('RA (deg)')
    axDEC.set_ylabel('DEC (deg)')
    axROLL.set_ylabel('ROLL (deg)')
    axROLL.set_xlabel(time_label)
    for i in range(N):
        column = df.columns[i]
        data = df[column].dropna()
        style = styles[i % len(styles)]
        if isinstance(style, basestring):
            axRA.plot(data.index, [q.ra for q in data], style)
            axDEC.plot(data.index, [q.dec for q in data], style)
            axROLL.plot(data.index, [q.roll for q in data], style)
        else:
            axRA.plot(data.index, [q.ra for q in data], **style)
            axDEC.plot(data.index, [q.dec for q in data], **style)
            axROLL.plot(data.index, [q.roll for q in data], **style)
    if labels is None: labels = df.columns
    if xlim is not None:
        axRA.set_xlim(xlim)
        axDEC.set_xlim(xlim)
        axROLL.set_xlim(xlim)
    if legend:
        axRA.legend(labels, loc=0, markerscale=2, numpoints=1)
    fig.tight_layout()
    return fig
def plotInnovations(ests,sc, time_label='Palestine Time', units='arcsec', conv=lambda x : abs(x)*3600, labels=None, styles=['b', 'r', 'g', 'k'], legend=False, xlim=None, sync=False, rotation=True):
    '''Plot the errors between the estimated attitudes in the list of dataframes ests and the star camera solutions in the dataframe sc
    
    :param ests: list of pd.Dataframe containing a qest column
    :param sc: pd.Dataframe containing the star camera information (qI2G column)
    :param time_label: label of the x axis
    :param units: string describing the units of the values
    :param conv: function to be passed at every error
    :param labels: legend labels of every pd.Dataframe in ests (if None, the labels are the position in the ests list)
    :param styles: plot styles or kwargs of every pd.Dataframe in ests
    :param legend: show legend?
    :param xlim: limits of the x axis [xmin,xmax]
    :param sync: plot synchronized with time?
    :param rotation: compute the errors in the SC reference frame?
    :return: figure
    :rtype: matplotlib.figure    
    '''
    index=sc.index[2:]
    t=index
    L=len(index)
    M=len(ests)
    dRA=np.zeros(L)
    dDEC=np.zeros(L)
    dROLL=np.zeros(L)
    if not sync:
        t=range(L) #plot without synchronizing with the time
        time_label='Solution number'
    fig, (axRA, axDEC, axROLL) = plt.subplots(3, 1, sharex=True, sharey=True)
    axRA.set_ylabel('RA ('+units+')')
    axDEC.set_ylabel('DEC ('+units+')')
    axROLL.set_ylabel('ROLL ('+units+')')
    axROLL.set_xlabel(time_label)
    for i,est in enumerate(ests):        
        for j,ind in enumerate(index):
            qest=est.qest.loc[ind]
            qsc=sc.qI2G.loc[ind]
            if rotation:
                qsc=sc.qI2S.loc[ind] #solution in SC reference frame
                qG2S=qsc*sc.qI2G.loc[ind].inv() #rotation between the two reference frames (Gyros and Starcam)
                #print qG2S            
                qest=qG2S*qest #qest in SC reference frame
            dRA[j]=conv(qest.ra-qsc.ra)
            dDEC[j]=conv(qest.dec-qsc.dec)
            dROLL[j]=conv(qest.roll-qsc.roll)
        style = styles[i % len(styles)]
        if isinstance(style, basestring):
            axRA.plot(t, dRA, style)
            axDEC.plot(t, dDEC, style)
            axROLL.plot(t, dROLL, style)
        else:
            axRA.plot(t, dRA, **style)
            axDEC.plot(t, dDEC, **style)
            axROLL.plot(t, dROLL, **style)
    if labels is None: labels = map(chr, range(ord('0'), ord('0')+M+1))
    if xlim is not None:
        axRA.set_xlim(xlim)
        axDEC.set_xlim(xlim)
        axROLL.set_xlim(xlim)
    if legend:
        axRA.legend(labels, loc=0, markerscale=2, numpoints=1)
    fig.tight_layout()
    return fig
def plotCovs(df, time_label='Palestine Time', ylabels=None, labels=None, styles=['b', 'r', 'g', 'k'], legend=False, xlim=None, function=lambda x: x, rotate=False):
    '''Plot the first three diagonal elements of the matrices in the dataframe df in a 3x1 subplots layout (P11,P22,P33)
    
    :param df: a pd.Dataframe containing exclusively columns of np.matrix objects greater than 3x3
    :ptype: ``pd.Dataframe``
    :param time_label: label of the x axis
    :param ylabels: y axis labels of the three subplots, in order top-bottom
    :param labels: legend labels of every column (if None, use df.columns as labels)
    :param styles: plot styles or kwargs of every column
    :param legend: show legend?
    :param xlim: limits of the x axis [xmin,xmax]
    :param function: function to be passed at every diagonal element
    :param rotate: rotate the covariance matrix -46 degrees? (represent in SC reference frame)
    :return: figure
    :rtype: matplotlib.figure
    '''
    
    N = len(df.columns)
    if N>1:
        if labels is None: labels = df.columns
        fig, (axRA, axDEC, axROLL) = plt.subplots(3, 1, sharex=True, sharey=True)
        if ylabels is None:
            axROLL.set_ylabel(r'$P_{00}$')
            axDEC.set_ylabel(r'$P_{11}$')
            axRA.set_ylabel(r'$P_{22}$')
        else:
            axRA.set_ylabel(ylabels[0])
            axDEC.set_ylabel(ylabels[1])
            axROLL.set_ylabel(ylabels[2])
    else:
        fig, axRA = plt.subplots(1, 1, sharex=True, sharey=True)
        axDEC=axRA;axROLL=axRA;
        if labels is None: labels=[r'$P_{00}$',r'$P_{11}$',r'$P_{00}$']
        styles=[{}]
    axROLL.set_xlabel(time_label)
    M = np.matrix([[0.693865, 0, 0.720106], [0, 1, 0], [-0.720106, 0, 0.693865]])
    for i in range(N):
        column = df.columns[i]
        data = df[column].dropna()  # matrix P
        index = data.index
        if rotate:
            data = [M * P[:3, :3] * M.T for P in data]
        style = styles[i % len(styles)]
        ROLLdata = [function(P[0, 0]) for P in data]
        DECdata = [function(P[1, 1]) for P in data]
        RAdata = [function(P[2, 2]) for P in data]
        if isinstance(style, basestring):
            axRA.plot(index, RAdata, style)
            axDEC.plot(index, DECdata, style)
            axROLL.plot(index, ROLLdata, style)
        else:
            axRA.plot(index, RAdata, **style)
            axDEC.plot(index, DECdata, **style)
            axROLL.plot(index, ROLLdata, **style)
    
    if xlim is not None:
        axROLL.set_xlim(xlim)
    if legend:
        axRA.legend(labels, loc=0, markerscale=2, numpoints=1)
    fig.tight_layout()
    return fig
def filterArray(x, N=200, R=0.9):
    '''Smoothes peaks of the np.array x.
    
    :param x: np.array to filter
    :param N: width of the peaks to remove
    :param R: overlapping ratio of the gliding window [0,1]
    :return: a filtered np.array with the same dimensions as x
    :rtype: np.array
    '''
    x=np.array(x)
    ic = N / 2  # central index
    ip = np.arange(0, N) #indexes of the window
    
    #this algorithm is very specific for the type of peaks we encounter. Maybe more efficient and general implementations can be found.
    while(ip[-1] < len(x)): #while the window is inside x     
        v0 = x[ip[0]] #first value in the window
        vc = x[ip[ic]] #central value of the window
        vf = x[ip[-1]] #last value in the window
        if not isinstance(vc, Quat): #if its not a Quaternion
            d0 = vc - v0     
            df = vc - vf
            m = (vf + v0) / 2
            th = 0
        else: #if it is a Quaternion
            d0 = np.sum((vc * v0.inv()).q[:3]) #angular part of the difference quaternion
            df = np.sum((vc * vf.inv()).q[:3])
            m = Quat((v0.q + vf.q) / 2) #mean quaternion
            th = 0.001
            
        if abs(d0) > th and abs(df) > th: #if the difference is higher than th
            s0 = np.sign(d0)
            sf = np.sign(df)  
            if s0 != 0 and s0 == sf: #and the sign of both differences is the same
                x[ip[1:-1]] = m #asign the average between v0 and vf to the whole window
        ip = ip + int(np.ceil((1 - R) * N)) #we glide the window
    return x       

def filterQuats(df, onlyQuats=True):
    '''Filters peaks of the dataframe df with quaternions. It uses filterArray(df[column].values, N=3, R=0.9)
    
    :param df: a pd.DataFrame object
    :param onlyQuats: filter only the columns with quaternions? (if False it has the same effect as filterDataframe(df))
    :return: the df filtered, of the same size
    :rtype: pd.DataFrame
    '''
    for column in df.columns:
        v = df[column].iloc[0]
        if not onlyQuats or isinstance(v, Quat):
            df[column] = filterArray(df[column].values, N=3, R=0.9)         
    return df
def filterDataframe(df, N=3, R=0.9):
    '''Removes peaks from the dataframe df. It uses filterArray(df[column].values, N, R)
    
    :param df: a pd.DataFrame object
    :param N: width of the peaks to remove
    :param R: overlapping ratio of the gliding window [0,1]
    :return: the df filtered, of the same size
    :rtype: pd.DataFrame
    '''
    for column in df.columns:
        v = df[column].iloc[0]
        df[column] = filterArray(df[column].values, N=N, R=R)         
    return df
def extractDuplicates(df, th=1e-3):
    '''Removes rows where there are duplicates of the quaternions at the first column of the dataframe df
    
    :param df: a pd.DataFrame object
    :param th: tolerance of the difference in degrees between the RA coordinates of the duplicate quaternions (default 1e-3)
    :return: the df with the duplicates removed
    :rtype: pd.DataFrame
    '''
    toExtract = [df.index[0]]
    for column in df.columns[0:]:
        i0 = df.index[0]
        if isinstance(df[column].loc[i0], Quat):
            for i in df.index[1:]:
                v0 = df[column].loc[i0].ra
                vc = df[column].loc[i].ra
                if  abs(vc - v0) > th: #if the next values are not equal in ra, extract them later
                    toExtract.append(i)
                i0 = i
    df = df.loc[toExtract] #we keep the first appearance of every different value            
    return df
