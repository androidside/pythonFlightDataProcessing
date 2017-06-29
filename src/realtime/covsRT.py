'''
Created on 28 abr. 2017

Main script

@author: Marc Casalprim
'''
print 'Imports...'
import matplotlib as mpl
import warnings
from matplotlib.style import use
from utils.dataset import DataSet,plt,np,pd
from utils.field import Field,getDtypes#,getFieldsContaining,getFieldsRegex



if __name__ == '__main__':
    #folder = "C:/17-05-17_00_36_34/"
    folder = "X:/17-05-24_00_50_03/"
        
    fieldsList=[]
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
    fieldsList.append(Field('bettii.RTHighPriority.estimatedBiasXarcsec',label='bx'))
    fieldsList.append(Field('bettii.RTHighPriority.estimatedBiasYarcsec',label='by'))
    fieldsList.append(Field('bettii.RTHighPriority.estimatedBiasZarcsec',label='bz'))
    
    use('seaborn-bright') 
    #mpl.rcParams['toolbar'] = 'None'
    mpl.rcParams['axes.grid'] = True
    warnings.filterwarnings("ignore")
    #mpl.rcParams['axes.formatter.useoffset'] = False

    
    ds = DataSet(folder,rpeaks=True)
    ds.readListFields(fieldsList, nValues=1000,verbose=True,rpeaks=False)   
    #ds.readListFields(fieldsList, nValues=nValues,start=nValues*i,verbose=False) #for simulation
    
    data=ds.df.copy()
    #initial plot
    fig=[]
    ax={}
    fig.append(plt.figure()) 
    ax['x']=(plt.subplot(311,ylabel='bias X (arcsec)'))
    ax['y']=(plt.subplot(312,ylabel='bias Y (arcsec)'))
    ax['z']=(plt.subplot(313,xlabel='Time (frames)',ylabel='bias Z (arcsec)'))

    fig.append(plt.figure()) 
    ax['00']=plt.subplot(311,ylabel='P00')
    ax['11']=plt.subplot(312,ylabel='P11')
    ax['22']=plt.subplot(313,xlabel='Time (frames)',ylabel='P22')
    
    fig.append(plt.figure()) 
    ax['00r']=plt.subplot(311,ylabel='P00 rotated')
    ax['11r']=plt.subplot(312,ylabel='P11 rotated')
    ax['22r']=plt.subplot(313,xlabel='Time (frames)',ylabel='P22 rotated')
    
    fig.append(plt.figure()) 
    ax['33']=plt.subplot(311,ylabel='P33')
    ax['44']=plt.subplot(312,ylabel='P44')
    ax['55']=plt.subplot(313,xlabel='Time (frames)',ylabel='P55')
    
    
    data['bx'].plot(ax=ax['x'])
    data['by'].plot(ax=ax['y'])
    data['bz'].plot(ax=ax['z'])
    
    
    data['P00'].plot(ax=ax['00'])
    data['P11'].plot(ax=ax['11'])
    data['P22'].plot(ax=ax['22'])
    data['P33'].plot(ax=ax['33'])
    data['P44'].plot(ax=ax['44'])
    data['P55'].plot(ax=ax['55']) 
    
    #Just to initialize
    data['P00rot'] = data['P00']
    data['P11rot'] = data['P11']
    data['P22rot'] = data['P22']
      
    data['P00rot'].plot(ax=ax['00r'])
    data['P11rot'].plot(ax=ax['11r'])
    data['P22rot'].plot(ax=ax['22r'])

    
    
    #for a in ax.values(): a.get_yaxis().get_major_formatter().set_useOffset(False)

    
    m={} #map axes to columns
    for a in ax.keys(): m[a]=[l.get_label() for l in ax[a].get_lines()]
    
    #plt.ion()
     
    plt.draw()
    for f in fig: f.tight_layout()
    lastNValues=4000
    nValues=1200
    while True:
        #print 'Reading bytes from '+str(nValues*i)+' to '+str(nValues*(i+1)) 
        ds.readListFields(fieldsList, nValues=nValues,verbose=False,rpeaks=False)   

        st=max(ds.df.index)-lastNValues #starting time for the x axis

        dat=ds.df.loc[st:,:].copy()
        del ds.df
        ds.df=dat.loc[st:,:] #we delete some memory
        
        df_tmp=dat[['P00','P01','P02','P10','P11','P12','P20','P21','P22']].dropna()
        L=len(df_tmp.P00)
        P00rot=[0]*L
        P11rot=[0]*L
        P22rot=[0]*L
        M=np.matrix([[0.693865,0,0.720106],[0,1,0],[-0.720106,0,0.693865]])
        mat=df_tmp.as_matrix()
        for i in range(L):
            ma=mat[i]
            P0=ma.reshape((3,3))
            P0rot=M*P0*M.T
            D=np.sqrt(np.diag(P0rot))/4.8484e-6
            P00rot[i]=D[0];P11rot[i]=D[1];P22rot[i]=D[2];
          
        d={'P00rot': P00rot,'P11rot': P11rot,'P22rot': P22rot}
        df_tmp=pd.DataFrame(d,index=df_tmp.index).dropna()
        data=pd.merge(df_tmp,dat,how='outer',left_index=True,right_index=True)
        try:
            x=data.index
            xlims=(min(x),max(x))
            for key in ax.keys():
                columns=m[key]
                axis=ax[key]
                lines=axis.get_lines()
                ylims=[+1e30,-1e30]
                for k in range(len(lines)) :
                    line=lines[k]
                    column=columns[k]
                    y=data[column].dropna()
                    x=y.index
                    y=y.values
                    line.set_data(x,y)
                    ylims[0]=min(min(y),ylims[0])
                    ylims[1]=max(max(y),ylims[1])
                axis.set_xlim(xlims)
                axis.set_ylim(ylims)
                #axis.autoscale()

        except Exception, err:
            print err      


        plt.draw()
        for f in fig: f.tight_layout()
        plt.pause(0.1)
    plt.show()

    