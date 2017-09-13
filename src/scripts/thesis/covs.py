'''
Created on 28 Aug 2017

Plotting of the estimated biases and the diagonal values of the covariance matrix P
In addition, a plot of the diagonal values of the P rotated by the qGyros2Starcam.

See utils.dataset.plotCovs() to obtain similar results

@author: Marc Casalprim
'''
print 'Imports...'

from utils.dataset import os,pd,DataSet,plt,np,filterDataframe
from utils.field import Field,getDtypes#,getFieldsContaining,getFieldsRegex



if __name__ == '__main__':
    folder = "C:/17-05-23_00_59_52/"
    folder='D:/GondolaFlightArchive/17-06-09_01_51_04/'
    folder='F:/GondolaFlightArchive/17-06-09_07_09_25/'
    
    save_folder='C:/Users/bettii/thesis/'
    img_folder=save_folder+'plots/covs/'
    
    if not os.path.exists(img_folder):
        os.makedirs(img_folder)
    Field.DTYPES=getDtypes(folder)
    
    fieldsList=[]

    fieldsList.append(Field('bettii.RTLowPriority.MeasurementErrorCovarianceMatrixR00',label='R00',conversion=1/4.8484e-6))
    fieldsList.append(Field('bettii.RTLowPriority.MeasurementErrorCovarianceMatrixR11',label='R11',conversion=1/4.8484e-6))
    fieldsList.append(Field('bettii.RTLowPriority.MeasurementErrorCovarianceMatrixR22',label='R22',conversion=1/4.8484e-6))
    fieldsList.append(Field('bettii.RTLowPriority.covarianceMatrix00',label='P00'))
    fieldsList.append(Field('bettii.RTLowPriority.covarianceMatrix01',label='P01'))
    fieldsList.append(Field('bettii.RTLowPriority.covarianceMatrix02',label='P02'))
    fieldsList.append(Field('bettii.RTLowPriority.covarianceMatrix10',label='P10'))
    fieldsList.append(Field('bettii.RTLowPriority.covarianceMatrix11',label='P11'))
    fieldsList.append(Field('bettii.RTLowPriority.covarianceMatrix12',label='P12'))
    fieldsList.append(Field('bettii.RTLowPriority.covarianceMatrix20',label='P20'))
    fieldsList.append(Field('bettii.RTLowPriority.covarianceMatrix21',label='P21'))
    fieldsList.append(Field('bettii.RTLowPriority.covarianceMatrix22',label='P22'))
    fieldsList.append(Field('bettii.RTLowPriority.covarianceMatrix33',label='P33'))
    fieldsList.append(Field('bettii.RTLowPriority.covarianceMatrix44',label='P44'))
    fieldsList.append(Field('bettii.RTLowPriority.covarianceMatrix55',label='P55'))

    fieldsList.append(Field('bettii.RTHighPriority.estimatedBiasXarcsec',label='biasX'))
    fieldsList.append(Field('bettii.RTHighPriority.estimatedBiasYarcsec',label='biasY')) 
    fieldsList.append(Field('bettii.RTHighPriority.estimatedBiasZarcsec',label='biasZ')) 

   
    initial_time=None#20300000 #in frame number
    final_time = None#22723333 #in frame number
    
    ds = DataSet(folder,fieldsList=fieldsList,min=initial_time,max=final_time,verbose=True,timeIndex=True)
    
    print 'Dataframe shape:', ds.df.shape
    print "Converting to Palestine Time..."
    ds.df.index=ds.df.index-pd.Timedelta(hours=5) #Palestine time conversion (Archives folder names are in UTC)

    org=ds.df
    print "Downsample.."
    M=99
    ds.df=ds.df.iloc[::M].copy()
    ds.df=ds.df.iloc[::3]
    print"Filtering..."
    aux=filterDataframe(ds.df.copy(),N=7,R=0.5)
    aux=filterDataframe(aux,N=3,R=0.9)
    ds.df=aux

    
    print "Plotting..."
    time_label='Time'
    
    fig,axes =plt.subplots(3, 1, sharex=True, sharey=True)
    data=ds.df[['biasX','biasY','biasZ']].dropna()
    axes[0].set_ylabel(r'$bias_X$')
    axes[1].set_ylabel(r'$bias_Y$')
    axes[2].set_ylabel(r'$bias_Z$')
    axes[2].set_xlabel(time_label)
    data['biasX'].plot(ax=axes[0])
    data['biasY'].plot(ax=axes[1])
    data['biasZ'].plot(ax=axes[2])
    fig.tight_layout()
    fig.subplots_adjust(hspace=0.11)
    fig.savefig(img_folder+"biases.png")
     
    fig,axes =plt.subplots(3, 1, sharex=True, sharey=True)
    data=ds.df[['P00','P11','P22']].dropna()
    axes[0].set_ylabel(r'$P_{00}$')
    axes[1].set_ylabel(r'$P_{11}$')
    axes[2].set_ylabel(r'$P_{22}$')
    axes[2].set_xlabel(time_label)
    data['P00'].plot(ax=axes[0])
    data['P11'].plot(ax=axes[1])
    data['P22'].plot(ax=axes[2])
    fig.tight_layout()
    fig.subplots_adjust(hspace=0.11)
    fig.savefig(img_folder+"covs_g.png")
    
    fig,axes =plt.subplots(3, 1, sharex=True, sharey=True)
    data=ds.df[['P33','P44','P55']].dropna()
    axes[0].set_ylabel(r'$P_{33}$')
    axes[1].set_ylabel(r'$P_{44}$')
    axes[2].set_ylabel(r'$P_{55}$')
    axes[2].set_xlabel(time_label)
    data['P33'].plot(ax=axes[0])
    data['P44'].plot(ax=axes[1])
    data['P55'].plot(ax=axes[2])
    fig.tight_layout()
    fig.subplots_adjust(hspace=0.11)    
    
    print "Rotating..."    
    data=ds.df[['P00','P01','P02','P10','P11','P12','P20','P21','P22']].dropna()
    L=len(data.P00)
    P00rot=[0]*L
    P11rot=[0]*L
    P22rot=[0]*L
    M=np.matrix([[0.693865,0,0.720106],[0,1,0],[-0.720106,0,0.693865]])
    for i in range(L):
        m=(data.iloc[i].as_matrix())
        P0=m.reshape((3,3))
        P0rot=M*P0*M.T
        D=np.diag(P0rot)#np.sqrt(np.diag(P0rot))/4.8484e-6
        P00rot[i]=D[0];P11rot[i]=D[1];P22rot[i]=D[2];
    
    d={'P00': P00rot,'P11': P11rot,'P22': P22rot}
    data=pd.DataFrame(d,index=data.index).dropna()
    
    fig,axes =plt.subplots(3, 1, sharex=True, sharey=True)
    data=pd.DataFrame(d,index=data.dropna().index).dropna()#.apply(lambda x : np.sqrt(x)/4.8484e-6)
    axes[0].set_ylabel(r'${P_{rot}}_{00}$')
    axes[1].set_ylabel(r'${P_{rot}}_{11}$')
    axes[2].set_ylabel(r'${P_{rot}}_{22}$')
    axes[2].set_xlabel(time_label)
    data['P00'].plot(ax=axes[0])
    data['P11'].plot(ax=axes[1])
    data['P22'].plot(ax=axes[2])
    fig.tight_layout()
    fig.subplots_adjust(hspace=0.11)
    fig.savefig(img_folder+"covs_sc.png")
    
    fig,axes =plt.subplots(3, 1, sharex=True, sharey=True)
    data=pd.DataFrame(d,index=ds.df[['P00']].dropna().index).dropna().apply(lambda x : np.sqrt(x)/4.8484e-6)
    axes[0].set_ylabel(r'$\sigma_{RA}\ (arcsec)$')
    axes[1].set_ylabel(r'$\sigma_{DEC}\ (arcsec)$')
    axes[2].set_ylabel(r'$\sigma_{ROLL}\ (arcsec)$')
    axes[2].set_xlabel(time_label)
    data['P00'].plot(ax=axes[2])
    data['P11'].plot(ax=axes[1])
    data['P22'].plot(ax=axes[0])
    fig.tight_layout()
    fig.subplots_adjust(hspace=0.11)
    
    columns=[r'$\sigma_{ROLL}$',r'$\sigma_{DEC}$',r'$\sigma_{RA}$']
    data.columns=columns
    ax=data[columns].plot()
    ax.set_xlabel(time_label)
    ax.set_ylabel('Uncertainty (arcsec)')
    ax.figure.tight_layout()
    ax.figure.savefig(img_folder+"sigmas.png")
    
    print "Show..."    
    plt.show()