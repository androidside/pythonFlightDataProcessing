'''
Created on Jul 12, 2017

Thermometry conversion class using demodRaw values from TRead messages. It emulates the Calibrator `java class at gov.nasa.gsfc.aurora.common.piperthermometry`

@author: bettii
'''
import numpy as np
from numpy import log
class Calibrator(object):
    '''
    classdocs
    '''


    def __init__(self, filename):
        '''
        Constructor
        '''
        temps=[]
        values=[]
        with open(filename) as f:
            lines = f.read().splitlines()
        for line in lines:
            if line and '#' not in line:
                s=line.split(',')
                temps.append(float(s[0]))
                values.append(float(s[1]))
        self.temps=np.array(temps)
        self.values=np.array(values)
        self.min=min(self.values)
        self.max=max(self.values)
    
    def getTemperature(self,res):
        if res>self.max or res<self.min:
            return 0
        firstIndex=None
        for i in range(len(self.values)):
            if res > self.values[i]:
                secondIndex=i
                firstIndex=i-1
                break
        if firstIndex is None or firstIndex<0:
            return 0
        
        x1 = self.temps[firstIndex];
        y1 = self.values[firstIndex];
    
        x2 = self.temps[secondIndex];
        y2 = self.values[secondIndex];

        z = (x1 / x2)**(1 / (y2 - y1));
        b = y1 + (log(x1)) / (log(z));

        temperature = z**(b-res)

        return temperature   
    def getRes(self,raw):
        volts=4.096*4.99/65536/65536*13107/2/66*raw
        return volts
        return volts    