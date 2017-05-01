'''
Created on 28 abr. 2017

@author: Marc Casalprim
'''
print 'Imports...'
from utils.dataset import DataSet
from utils.field import *
import matplotlib.pyplot as plt
import seaborn as sns


if __name__ == '__main__':

    folder = "X:/17-04-24_19_02_57/"
    
    #===========================================================================
    # fieldsList=[]
    # 
    # fieldsList.append(Field('bettii.RTHighPriority.crossElevation'))
    # fieldsList.append(Field('bettii.RTHighPriority.elevation'))
    # fieldsList.append(Field('bettii.RTHighPriority.TelescopeDecDeg'))
    # fieldsList.append(Field('bettii.RTHighPriority.TelescopeRaDeg'))
    #  
    # fieldsList.append(Field('bettii.GyroReadings.angularVelocityX',label='gyroX',dtype='i4',conversion=0.0006304))
    # fieldsList.append(Field('bettii.GyroReadings.angularVelocityY',label='gyroY',dtype='i4',conversion=0.0006437))
    # fieldsList.append(Field('bettii.GyroReadings.angularVelocityZ',label='gyroZ',dtype='i4',conversion=0.0006324))
    #===========================================================================
    
    fieldsList = getFieldsContaining('bettii.ThermometersOutput.A',folder)   
    
    #fieldsList = getFieldsRegex('bettii.[U-Z]+',folder)   
      
    ds = DataSet(folder,fieldsList=fieldsList,min=28315)
    
    print 'Dataframe shape:', ds.df.shape
    
    f=ds.simplePlot('AI0')
    
    g=ds.multiPSD(['AI0','AI2','AI7'])
    #print 'Plotting scatter plot...'
    #g = sns.pairplot(ds.df.dropna())
 
    #===========================================================================
    # print ds.df['crossElevation'].dropna()
    # print ds.df['gyroX']
    # f=ds.simplePlot('crossElevation')
    # i=ds.simplePlot('gyroX')
    # data = ds.df[['elevation','crossElevation','TelescopeDecDeg']].dropna()
    #  
    # sns.set(style="ticks", color_codes=True)
    #  
    # plt.figure()    
    # h=sns.tsplot(data.elevation,color='blue')
    #===========================================================================
 
     
    #plt.draw()
    #print ds.df
    #ds.simplePlot('elevation')
    #===========================================================================
    # gyros = ['gyroX','gyroY','gyroZ']
    # 
    # ds.plotGyros(show=show)
    # fig,axlist = plt.subplots(3,figsize=(5.9,8),dpi=120)
    # for i in range(3):
    #     ax = axlist[i]
    #     ax.scatter(ds.df.index/400.,ds.df[gyros[i]],color=blue)
    # plt.show()
    # ds.multiPSD(gyros,show=show,loglog=True)
    # ds.multiPSD(gyros,show=show,loglog=False,name="multiPSD_no_loglog")
    # ds.multiPSD(gyros,show=show,loglog=False,name="multiPSD_no_loglog_zoom",minMax=[24,28])
    # 
    # ds.scatterPlots(['gyroX','gyroY'],show=show)
    # ds.scatterPlots(['gyroX','gyroZ'],show=show)
    # ds.scatterPlots(['gyroY','gyroZ'],show=show)
    #===========================================================================
    plt.show()