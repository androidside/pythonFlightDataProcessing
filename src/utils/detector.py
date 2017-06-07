'''
Created on Jun 5, 2017

@author: bettii
'''
import numpy as np
from numpy.fft import fft
import matplotlib.pyplot as plt

detMapfile='C:/Users/bettii/Desktop/det_map.txt'
dictMap={'error_r17_c9': (7, 5, 2), 'error_r14_c15': (0, 2, 3), 'error_r20_c11': (1, 0, 2), 'error_r8_c12': (6, 0, 3), 'error_r14_c12': (6, 4, 3), 'error_r8_c10': (2, 8, 2), 'error_r8_c11': (4, 2, 2), 'error_r14_c7': (0, 2, 1), 'error_r8_c14': (2, 8, 3), 'error_r8_c15': (4, 2, 3), 'error_r20_c7': (1, 0, 1), 'error_r20_c6': (0, 6, 1), 'error_r20_c5': (7, 8, 1), 'error_r20_c4': (8, 2, 1), 'error_r20_c3': (1, 0, 0), 'error_r20_c2': (0, 6, 0), 'error_r20_c1': (7, 8, 0), 'error_r20_c0': (8, 2, 0), 'error_r10_c7': (4, 0, 1), 'error_r20_c9': (7, 8, 2), 'error_r20_c8': (8, 2, 2), 'error_r4_c4': (6, 1, 1), 'error_r4_c5': (5, 7, 1), 'error_r4_c6': (2, 7, 1), 'error_r4_c7': (3, 2, 1), 'error_r4_c0': (6, 1, 0), 'error_r4_c1': (5, 7, 0), 'error_r4_c2': (2, 7, 0), 'error_r4_c3': (3, 2, 0), 'error_r4_c8': (6, 1, 2), 'error_r4_c9': (5, 7, 2), 'error_r22_c13': (6, 6, 3), 'error_r5_c13': (5, 8, 3), 'error_r5_c12': (5, 1, 3), 'error_r4_c14': (2, 7, 3), 'error_r5_c10': (3, 7, 2), 'error_r4_c12': (6, 1, 3), 'error_r4_c13': (5, 7, 3), 'error_r4_c10': (2, 7, 2), 'error_r8_c13': (4, 7, 3), 'error_r5_c9': (5, 8, 2), 'error_r5_c8': (5, 1, 2), 'error_r5_c7': (3, 1, 1), 'error_r5_c6': (3, 7, 1), 'error_r5_c5': (5, 8, 1), 'error_r5_c4': (5, 1, 1), 'error_r5_c3': (3, 1, 0), 'error_r5_c2': (3, 7, 0), 'error_r5_c1': (5, 8, 0), 'error_r5_c0': (5, 1, 0), 'error_r15_c14': (3, 4, 3), 'error_r19_c8': (5, 3, 2), 'error_r16_c14': (0, 5, 3), 'error_r16_c15': (0, 0, 3), 'error_r21_c7': (2, 3, 1), 'error_r16_c10': (0, 5, 2), 'error_r16_c11': (0, 0, 2), 'error_r16_c12': (8, 3, 3), 'error_r16_c13': (8, 8, 3), 'error_r13_c15': (0, 3, 3), 'error_r13_c14': (1, 4, 3), 'error_r22_c15': (2, 2, 3), 'error_r13_c11': (0, 3, 2), 'error_r13_c10': (1, 4, 2), 'error_r13_c13': (8, 5, 3), 'error_r13_c12': (7, 4, 3), 'error_r10_c11': (4, 0, 2), 'error_r22_c5': (6, 6, 1), 'error_r21_c14': (1, 6, 3), 'error_r3_c15': (3, 3, 3), 'error_r3_c14': (1, 7, 3), 'error_r21_c15': (2, 3, 3), 'error_r3_c11': (3, 3, 2), 'error_r3_c10': (1, 7, 2), 'error_r3_c13': (5, 6, 3), 'error_r3_c12': (7, 1, 3), 'error_r2_c10': (0, 7, 2), 'error_r2_c11': (2, 0, 2), 'error_r2_c12': (8, 1, 3), 'error_r2_c13': (5, 5, 3), 'error_r2_c14': (0, 7, 3), 'error_r2_c15': (2, 0, 3), 'error_r21_c13': (6, 5, 3), 'error_r8_c8': (6, 0, 2), 'error_r8_c9': (4, 7, 2), 'error_r21_c10': (1, 6, 2), 'error_r18_c11': (1, 2, 2), 'error_r8_c0': (6, 0, 0), 'error_r8_c1': (4, 7, 0), 'error_r8_c2': (2, 8, 0), 'error_r8_c3': (4, 2, 0), 'error_r8_c4': (6, 0, 1), 'error_r8_c5': (4, 7, 1), 'error_r8_c6': (2, 8, 1), 'error_r8_c7': (4, 2, 1), 'error_r10_c8': (4, 4, 2), 'error_r9_c15': (4, 1, 3), 'error_r9_c14': (3, 8, 3), 'error_r9_c13': (4, 8, 3), 'error_r9_c12': (5, 0, 3), 'error_r9_c11': (4, 1, 2), 'error_r9_c10': (3, 8, 2), 'error_r10_c0': (4, 4, 0), 'error_r14_c14': (2, 4, 3), 'error_r10_c3': (4, 0, 0), 'error_r10_c4': (4, 4, 1), 'error_r14_c13': (8, 6, 3), 'error_r14_c10': (2, 4, 2), 'error_r14_c5': (8, 6, 1), 'error_r18_c15': (1, 2, 3), 'error_r13_c9': (8, 5, 2), 'error_r1_c15': (2, 1, 3), 'error_r13_c8': (7, 4, 2), 'error_r9_c3': (4, 1, 0), 'error_r9_c2': (3, 8, 0), 'error_r9_c1': (4, 8, 0), 'error_r9_c0': (5, 0, 0), 'error_r9_c7': (4, 1, 1), 'error_r9_c6': (3, 8, 1), 'error_r9_c5': (4, 8, 1), 'error_r9_c4': (5, 0, 1), 'error_r9_c9': (4, 8, 2), 'error_r9_c8': (5, 0, 2), 'error_r1_c13': (6, 8, 3), 'error_r1_c12': (5, 2, 3), 'error_r1_c11': (2, 1, 2), 'error_r1_c10': (3, 6, 2), 'error_r22_c1': (6, 6, 0), 'error_r13_c5': (8, 5, 1), 'error_r22_c3': (2, 2, 0), 'error_r15_c4': (5, 4, 1), 'error_r15_c3': (0, 1, 0), 'error_r15_c2': (3, 4, 0), 'error_r15_c1': (8, 7, 0), 'error_r15_c0': (5, 4, 0), 'error_r22_c9': (6, 6, 2), 'error_r19_c7': (1, 1, 1), 'error_r5_c15': (3, 1, 3), 'error_r13_c7': (0, 3, 1), 'error_r15_c9': (8, 7, 2), 'error_r15_c8': (5, 4, 2), 'error_r15_c7': (0, 1, 1), 'error_r13_c6': (1, 4, 1), 'error_r15_c6': (3, 4, 1), 'error_r18_c12': (6, 3, 3), 'error_r13_c1': (8, 5, 0), 'error_r18_c10': (2, 5, 2), 'error_r7_c15': (4, 3, 3), 'error_r15_c5': (8, 7, 1), 'error_r18_c14': (2, 5, 3), 'error_r14_c1': (8, 6, 0), 'error_r0_c0': (6, 2, 0), 'error_r0_c1': (6, 7, 0), 'error_r0_c2': (2, 6, 0), 'error_r20_c10': (0, 6, 2), 'error_r0_c4': (6, 2, 1), 'error_r13_c3': (0, 3, 0), 'error_r0_c6': (2, 6, 1), 'error_r19_c6': (3, 5, 1), 'error_r0_c8': (6, 2, 2), 'error_r0_c9': (6, 7, 2), 'error_r13_c2': (1, 4, 0), 'error_r22_c7': (2, 2, 1), 'error_r6_c14': (0, 8, 3), 'error_r6_c15': (3, 0, 3), 'error_r6_c10': (0, 8, 2), 'error_r6_c11': (3, 0, 2), 'error_r6_c12': (8, 0, 3), 'error_r6_c13': (4, 5, 3), 'error_r10_c12': (4, 4, 3), 'error_r6_c8': (8, 0, 2), 'error_r6_c9': (4, 5, 2), 'error_r10_c15': (4, 0, 3), 'error_r6_c2': (0, 8, 0), 'error_r6_c3': (3, 0, 0), 'error_r6_c0': (8, 0, 0), 'error_r6_c1': (4, 5, 0), 'error_r6_c6': (0, 8, 1), 'error_r6_c7': (3, 0, 1), 'error_r6_c4': (8, 0, 1), 'error_r6_c5': (4, 5, 1), 'error_r2_c6': (0, 7, 1), 'error_r14_c11': (0, 2, 2), 'error_r2_c7': (2, 0, 1), 'error_r4_c11': (3, 2, 2), 'error_r5_c14': (3, 7, 3), 'error_r5_c11': (3, 1, 2), 'error_r15_c13': (8, 7, 3), 'error_r15_c12': (5, 4, 3), 'error_r2_c4': (8, 1, 1), 'error_r2_c5': (5, 5, 1), 'error_r2_c2': (0, 7, 0), 'error_r2_c3': (2, 0, 0), 'error_r2_c0': (8, 1, 0), 'error_r2_c1': (5, 5, 0), 'error_r16_c6': (0, 5, 1), 'error_r16_c7': (0, 0, 1), 'error_r16_c4': (8, 3, 1), 'error_r16_c5': (8, 8, 1), 'error_r16_c2': (0, 5, 0), 'error_r16_c3': (0, 0, 0), 'error_r16_c0': (8, 3, 0), 'error_r16_c1': (8, 8, 0), 'error_r19_c14': (3, 5, 3), 'error_r7_c9': (4, 6, 2), 'error_r7_c8': (7, 0, 2), 'error_r7_c5': (4, 6, 1), 'error_r7_c4': (7, 0, 1), 'error_r7_c7': (4, 3, 1), 'error_r16_c9': (8, 8, 2), 'error_r7_c1': (4, 6, 0), 'error_r7_c0': (7, 0, 0), 'error_r7_c3': (4, 3, 0), 'error_r7_c2': (1, 8, 0), 'error_r0_c12': (6, 2, 3), 'error_r3_c8': (7, 1, 2), 'error_r0_c10': (2, 6, 2), 'error_r0_c14': (2, 6, 3), 'error_r3_c1': (5, 6, 0), 'error_r3_c0': (7, 1, 0), 'error_r3_c3': (3, 3, 0), 'error_r3_c2': (1, 7, 0), 'error_r3_c5': (5, 6, 1), 'error_r3_c4': (7, 1, 1), 'error_r3_c7': (3, 3, 1), 'error_r3_c6': (1, 7, 1), 'error_r19_c9': (7, 7, 2), 'error_r16_c8': (8, 3, 2), 'error_r12_c10': (0, 4, 2), 'error_r19_c3': (1, 1, 0), 'error_r19_c2': (3, 5, 0), 'error_r19_c1': (7, 7, 0), 'error_r19_c0': (5, 3, 0), 'error_r21_c12': (7, 2, 3), 'error_r1_c9': (6, 8, 2), 'error_r19_c5': (7, 7, 1), 'error_r19_c4': (5, 3, 1), 'error_r1_c8': (5, 2, 2), 'error_r14_c8': (6, 4, 2), 'error_r2_c8': (8, 1, 2), 'error_r12_c12': (8, 4, 3), 'error_r18_c13': (7, 6, 3), 'error_r14_c4': (6, 4, 1), 'error_r13_c4': (7, 4, 1), 'error_r14_c6': (2, 4, 1), 'error_r2_c9': (5, 5, 2), 'error_r14_c0': (6, 4, 0), 'error_r13_c0': (7, 4, 0), 'error_r14_c2': (2, 4, 0), 'error_r14_c3': (0, 2, 0), 'error_r4_c15': (3, 2, 3), 'error_r0_c5': (6, 7, 1), 'error_r19_c15': (1, 1, 3), 'error_r17_c6': (1, 5, 1), 'error_r19_c13': (7, 7, 3), 'error_r19_c12': (5, 3, 3), 'error_r19_c11': (1, 1, 2), 'error_r19_c10': (3, 5, 2), 'error_r17_c1': (7, 5, 0), 'error_r17_c0': (7, 3, 0), 'error_r17_c3': (1, 3, 0), 'error_r17_c2': (1, 5, 0), 'error_r17_c5': (7, 5, 1), 'error_r17_c4': (7, 3, 1), 'error_r17_c7': (1, 3, 1), 'error_r17_c8': (7, 3, 2), 'error_r1_c3': (2, 1, 0), 'error_r1_c2': (3, 6, 0), 'error_r1_c1': (6, 8, 0), 'error_r1_c0': (5, 2, 0), 'error_r1_c7': (2, 1, 1), 'error_r1_c6': (3, 6, 1), 'error_r1_c5': (6, 8, 1), 'error_r1_c4': (5, 2, 1), 'error_r20_c13': (7, 8, 3), 'error_r12_c8': (8, 4, 2), 'error_r20_c12': (8, 2, 3), 'error_r12_c2': (0, 4, 0), 'error_r7_c10': (1, 8, 2), 'error_r12_c0': (8, 4, 0), 'error_r7_c12': (7, 0, 3), 'error_r12_c6': (0, 4, 1), 'error_r7_c14': (1, 8, 3), 'error_r12_c4': (8, 4, 1), 'error_r12_c14': (0, 4, 3), 'error_r21_c8': (7, 2, 2), 'error_r21_c9': (6, 5, 2), 'error_r14_c9': (8, 6, 2), 'error_r21_c4': (7, 2, 1), 'error_r21_c5': (6, 5, 1), 'error_r21_c6': (1, 6, 1), 'error_r15_c15': (0, 1, 3), 'error_r21_c0': (7, 2, 0), 'error_r21_c1': (6, 5, 0), 'error_r21_c2': (1, 6, 0), 'error_r21_c3': (2, 3, 0), 'error_r1_c14': (3, 6, 3), 'error_r7_c6': (1, 8, 1), 'error_r20_c15': (1, 0, 3), 'error_r20_c14': (0, 6, 3), 'error_r18_c0': (6, 3, 0), 'error_r18_c1': (7, 6, 0), 'error_r18_c2': (2, 5, 0), 'error_r18_c3': (1, 2, 0), 'error_r18_c4': (6, 3, 1), 'error_r18_c5': (7, 6, 1), 'error_r18_c6': (2, 5, 1), 'error_r18_c7': (1, 2, 1), 'error_r18_c8': (6, 3, 2), 'error_r18_c9': (7, 6, 2), 'error_r3_c9': (5, 6, 2), 'error_r21_c11': (2, 3, 2), 'error_r0_c13': (6, 7, 3), 'error_r17_c11': (1, 3, 2), 'error_r17_c10': (1, 5, 2), 'error_r17_c13': (7, 5, 3), 'error_r17_c12': (7, 3, 3), 'error_r17_c15': (1, 3, 3), 'error_r17_c14': (1, 5, 3), 'error_r7_c11': (4, 3, 2), 'error_r22_c11': (2, 2, 2), 'error_r15_c11': (0, 1, 2), 'error_r15_c10': (3, 4, 2), 'error_r7_c13': (4, 6, 3)}
detId={
    0:'C',
    1:'A',
    2:'B',
    3:'D'
    }
def generateDictMap():
    with open(detMapfile,'rb') as f:
        for line in f.read().split('\r')[1:-1]:
            l= line.split()
            if len(l)==4 and l[2].isdigit():
                col=int(l[0])
                dictMap['error_r'+l[1]+'_c'+str(col)]=(int(l[2])-1,int(l[3])-1,0)   #detC
                dictMap['error_r'+l[1]+'_c'+str(col+4)]=(int(l[2])-1,int(l[3])-1,1) #detA
                dictMap['error_r'+l[1]+'_c'+str(col+8)]=(int(l[2])-1,int(l[3])-1,2) #detB
                dictMap['error_r'+l[1]+'_c'+str(col+12)]=(int(l[2])-1,int(l[3])-1,3)#detD
def dataframe2matrices(dataframe):
    L=len(dataframe.index)

    det={
        0:np.zeros((9,9,L)),
        1:np.zeros((9,9,L)),
        2:np.zeros((9,9,L)),
        3:np.zeros((9,9,L))
        }
    for field in dataframe.columns:
        if field in dictMap:
            vert,horiz,detId=dictMap[field]
            det[detId][vert, horiz, :]=dataframe[field].values;
    for i in range(4):
        det[i]=np.rot90(det[i],i)
        m=np.mean(det[i],axis=2)
        det[i]=det[i]-m[:,:,np.newaxis]
    return det

def data2matrices(data,index=None,center=True,dead=[]):
    L=len(index)
    if index is None : index=range(len(data[data.keys()[0]]))
    det={
        0:np.zeros((9,9,L)),
        1:np.zeros((9,9,L)),
        2:np.zeros((9,9,L)),
        3:np.zeros((9,9,L))
        }
    for field in data.keys():
        if field not in dead and field in dictMap:
            vert,horiz,detId=dictMap[field]
            det[detId][vert, horiz, :]=data[field][index];
    for i in range(4):
        det[i]=np.rot90(det[i],i)
        if center:
            m=np.mean(det[i],axis=2)
            det[i]=det[i]-m[:,:,np.newaxis]
    return det

def getFFTs(matrix,sindex=0,eindex=None):
    ft={}
    for k in range(4):
        psd=abs(fft(matrix[k],axis=2))
        L=len(psd[0,0])
        psd[:,:,0]=0
        ft[k]=psd[:,:,:L/2]
    return ft

def createImagesAxes(title=''):
    axes={}
    fig, axarr = plt.subplots(nrows=2,ncols=2, sharex=True, sharey=True)
    #fig.tight_layout()
    fig.subplots_adjust(hspace=0.01,wspace=0.01)
    fig.suptitle(title)
    for k in range(4):
        i,j=divmod(k,2)
        axes[k]=axarr[i,j]
        axes[k].imshow(np.zeros((9,9)),interpolation='none')
        axes[k].set_title("Detector "+detId[k])
    return axes
def createDataAxes(title='',dets=range(4)):
    axes={}
    for k in dets:
        fig, axs = plt.subplots(nrows=9,ncols=9, sharex=True, sharey=True)
        axes[k]=axs
        fig.tight_layout()
        fig.subplots_adjust(hspace=0,wspace=0)

        for i in range(9):
            for j in range(9):
                axs[i,j].plot([])
        axs[0,3].set_title(title+", detector "+detId[k])
    return axes

def plotImages(data,axes,sum=None,cmap="viridis"):
    #===========================================================================
    # cmap = plt.get_cmap(cmap)
    # cmap.set_bad('white')
    #===========================================================================
    for k in axes.keys():
        if sum is None: image=data[k][:,:,-1] #we pick the last
        else: image=np.sum(data[k],axis=2)
        axes[k].imshow(np.ma.masked_values(image, 0,atol=1e-13),interpolation='none',cmap=cmap)
    axes[axes.keys()[0]].figure.canvas.draw() #draw canvas from the first ax (is the same for all of them)
def plotData(data,axes,downsample=20):
    for k in axes.keys():
        ylims=[1e30,-1e30]
        for i in range(9):
            for j in range(9):
                L=len(data[k][i,j,:])
                x=range(0,L,downsample)
                y=data[k][i,j,0:L:downsample]
                ax=axes[k][i,j]
                line=ax.get_lines()[0]
                line.set_data(x,y)
                xlims=(min(x),max(x))
                ylims[0]=min(min(y),ylims[0])
                ylims[1]=max(max(y),ylims[1])
        ax.set_xlim(xlims)
        ax.set_ylim(ylims)
    axes[axes.keys()[0]][0,0].figure.canvas.draw() #draw canvas from the first ax (is the same for all of them)
def getIndexRangeLastStroke(CDLposTarget,CDLmceFN,masterMceFn):
    L=len(masterMceFn)
    t2=np.diff(np.diff(CDLposTarget))
    th=0 #threshold for the second derivative
    
    ups=np.where(t2>th)[0]+1 #indexes of change of slope in target
    downs=np.where(t2<th)[0]+1
    
    if downs.size>0 and ups.size>0: #ups and downs
        lastu=ups[-1]
        lastd=downs[-1] #last down
        if lastd>lastu:
            fnfirst=CDLmceFN[lastu]
            fnlast=CDLmceFN[lastd]
        else:
            fnfirst=CDLmceFN[lastd]
            fnlast=CDLmceFN[lastu]
        ifirst=(np.abs(masterMceFn-fnfirst)).argmin() #index of the nearest fn in master
        ilast=(np.abs(masterMceFn-fnlast)).argmin()   #index of the nearest fn in master
        index=range(ifirst,ilast+1)
    elif downs.size>0 and ups.size<=0: #only downs
        lastd=downs[-1] #last down
        fnfirst=CDLmceFN[lastd]
        ifirst=(np.abs(masterMceFn-fnfirst)).argmin() #index of the nearest fn in master
        if ifirst>L/2: index=range(ifirst+1)
        else: index=range(ifirst,L)
    elif downs.size<=0 and ups.size>0: #only ups
        lastu=ups[-1] #last up
        fnfirst=CDLmceFN[lastu]
        ifirst=(np.abs(masterMceFn-fnfirst)).argmin() #index of the nearest fn in master
        if ifirst>L/2: index=range(ifirst+1)
        else: index=range(ifirst,L)
    else:
        index=range(L)   
    return index
def getDeadPixels(filename='dead_pixels.txt'):
    dead=[]
    with open(filename,'rb') as f:
        for line in f:
            field=line.split(None, 1)[0]
            dead.append(field)
    return dead