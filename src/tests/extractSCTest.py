'''
Created on Jul 27, 2017

@author: bettii
'''
from utils.estimator import readAndSave
if __name__ == '__main__':
    folder="F:/GondolaFlightArchive/17-06-09_01_51_04/"
    gyros,sc,quats=readAndSave(folder)
    a=1