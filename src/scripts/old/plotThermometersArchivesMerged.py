'''
Created on 10 jul. 2017

Script for plotting thermometers data from different archives

@author: Marc Casalprim
'''
print 'Imports...'
import os
import matplotlib as mpl
from matplotlib.style import use
from utils.dataset import DataSet, plt, np, pd
from utils.field import Field, getFieldsContaining



if __name__ == '__main__':

    folders = []
    root_folder = 'F:/GondolaFlightArchive/'
    subdirs = next(os.walk(root_folder))[1]
    folders = [root_folder + subdir + '/' for subdir in subdirs]

    save_folder = 'C:/Users/bettii/thermometers/'
    img_folder = save_folder + "plots/"
    

    
    folder = folders[0]
    fieldsList = getFieldsContaining('bettii.ThermometersDemuxedCelcius.J', folder)

    for field in fieldsList:
        field.range = 90
    
            
    ds = DataSet(fieldsList=fieldsList, foldersList=folders, verbose=True, rpeaks=False)

    print "Converting to Palestine Time..."
    ds.df.index = ds.df.index - pd.Timedelta(hours=5)  # Palestine time conversion (Archives folder names are in UTC)
    ds.df=ds.df.ix[pd.to_datetime('06/09/2017 00:00:00'):pd.to_datetime('06/09/2017 04:00:00')] #slicing
    
    ds.df = ds.df.dropna(axis=1, how='all').interpolate(method='time')
    ds.df.dropna(inplace=True)
    
    Ngroups = 20
    group = {}
    for i in range(Ngroups):
        group[i] = []
    for label in ds.df.columns:
        if len(label) <= 4:
            j = 0
        else:
            j = int(label[3])
            if j > 4: j = 4
        if "J1" in label:
            group[0 + j].append(label)
        elif "J2" in label:
            group[5 + j].append(label)
        elif "J3" in label:
            group[10 + j].append(label)
        elif "J4" in label:
            group[15 + j].append(label)
    Ngroups = len(group.keys())    
    use('seaborn-bright')
    mpl.rcParams['axes.grid'] = True
    

    time_label = 'Palestine Time'
    
    M = 1  # downsample factor
    ds.df = ds.df.iloc[::M]
    
    print "Generating plots.."

    print "Plotting thermometers data..."
    for i in range(Ngroups):
        fig = plt.figure()
        ax = plt.subplot(111, xlabel=time_label, ylabel='Temperature [Celsius]')
        data = ds.df[group[i]].dropna(how='all').interpolate(method='time')
        data.plot(ax=ax, style='.', markersize=2.0)
        plt.legend(markerscale=3, numpoints=20)
        fig.tight_layout()
        fig.savefig(img_folder + "thermometers_" + '-'.join(group[i]) + ".png")
    
    print "Saving CSV..."
    ds.df.to_csv(save_folder + "thermometers.txt", sep='\t', float_format='%.2f', index_label='Palestine time  ', date_format="%Y-%m-%d %H:%M:%S")
    print "Saved"
    
    print "Show..."
    plt.show()
