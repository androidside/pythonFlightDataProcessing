'''
Created on :'Jul 10, 2017

@author: Marc Casalprim
'''
import os
import pandas as pd
import numpy as np
from utils.calibrator import Calibrator

package_directory = os.path.dirname(os.path.abspath(__file__))
prefix=package_directory+'\\thermoCalibrations\\'
DC3 = prefix + "DiodeCal3.txt";
DT670 = prefix + "DT-670.txt";
FbDiode = prefix + "FbDiode.txt";
Ru = prefix + "RuO2mean.txt";
X6 = prefix + "X65096.txt";
X7 = prefix + "X65097.txt";

calFbDiode = Calibrator(FbDiode);
calRu = Calibrator(Ru);
calDC3 = Calibrator(DC3);
calDT670 = Calibrator(DT670);

calibrators={'demodRaw0':calFbDiode,
             'demodRaw1':calDC3,
             'demodRaw2':calDC3,
             'demodRaw3':calDC3,
             'demodRaw4':calDC3,
             'demodRaw5':calDT670,
             'demodRaw6':calDT670,
             'demodRaw7':calDT670,
             'demodRaw8':calDT670,
             'demodRaw9':calDT670,
             'demodRaw10':calDT670,
             'demodRaw11':calDT670,
             'std_demodRaw0':calRu,
             'std_demodRaw1':calRu,
             'std_demodRaw2':Calibrator(X7),
             'std_demodRaw3':Calibrator(X6),
             }
PiperNames={'demodRaw0':"Exchanger",
             'demodRaw1':"4HePump",
             'demodRaw2':"3HePump",
             'demodRaw3':"4HeSwitch",
             'demodRaw4':"3HeSwitch",
             'demodRaw5':"OpticsBench",
             'demodRaw6':"LHeTank",
             'demodRaw7':"LHeShield",
             'demodRaw8':"NIRBench",
             'demodRaw9':"H1RG",
             'demodRaw10':"NIRBench2",
             'demodRaw11':"LN2Tank",
             'std_demodRaw0':"3HeColdHead",
             'std_demodRaw1':"4HeColdHead",
             'std_demodRaw2':"BatwingRight",
             'std_demodRaw3':"BatwingLeft",
             }
def getTemperaturesFromRawDataFrame(rawdf):
    """Returns a new dataframe with the calculated temperatures.
    Raw DataFrame format: all columns from Standard message start with std_"""
    data={}
    for column in rawdf.columns:
        if "demodRaw" in column and column in calibrators.keys():
            calibrator=calibrators[column]

            gdaclabel=column.replace('demodRaw','gDac')
            adaclabel=column.replace('demodRaw','aDac')
            nsumlabel=column.replace('demodRaw','nsum').split('m')[0]+'m'
            rawValues=rawdf[column].values
            if "std" in column:
                delta=0.007833*rawValues/rawdf[nsumlabel].values
                X=100*65536/4.99*rawdf[adaclabel].values/rawdf[gdaclabel].values*4/72.5
                volts= 220100*delta/(X-delta)              
            else:
                delta=rawValues/2/rawdf[nsumlabel].values
                gain=65536.0/rawdf[gdaclabel].values
                volts=delta*4.096/65536*4.99/gain           
            getTemperature = np.vectorize(calibrator.getTemperature, otypes=[np.float])
            temperatures=getTemperature(volts)            
            name=PiperNames[column]
            data[name]=temperatures
    df=pd.DataFrame(data,index=rawdf.index)
    #df=df.loc[(df.abs()>=0.001).any(1)]
    return df

def unwrapCounter(counter):
    """Returns the evolution of the counter but unwrapping modulo 255"""
    if len(counter)<10:
        return counter
    d=np.diff(counter)
    d=np.append(d,d[-1])
    unwrapped=counter
    offset=0
    for i,c in enumerate(counter):
        unwrapped[i]=offset+c
        if d[i]<0:
            offset=offset+255
    return unwrapped

ThermometerName = {76:'J3L12',
3:'J3L28',
4:'J3L4',
5:'J3L16',
#6:'J2L49',  #Broken
7:'J4L29',
8:'J1L4',
9:'J3L22',
11:'J2L25',
12:'J4L21',
13:'J4L19',
14:'J1L18',
15:'J1L6',
16:'J1L8',
17:'J2L21',
18:'J4L9',
20:'J3L14',
21:'J1L30',
22:'J3L10',
23:'J2L3',
#24:'J4L1',  #Broken
25:'J1L40',
26:'J3L46',
#27:'J3L44',  #Broken
28:'J3L32',
29:'J3L30',
30:'J1L20',
32:'J1L12',
33:'J3L36',
34:'J3L40',
35:'J4L35',
36:'J4L41',
37:'J4L39',
38:'J4L37',
39:'J4L31',
40:'J3L34',
41:'J1L38',
43:'J4L33',
45:'J2L13',
46:'J2L9',
48:'J2L19',
51:'J2L29',
52:'J2L31',
53:'J2L17',
54:'J2L33',
55:'J2L15',
56:'J2L23',
57:'J2L7',
58:'J3L26',
59:'J2L47',
60:'J3L8',
61:'J3L6',
62:'J3L24',
63:'J4L3',
64:'J4L11',
65:'J4L7',
66:'J4L25',
67:'J4L15',
68:'J3L48',
69:'J3L18',
70:'J3L38',
71:'J4L13',
72:'J2L45',
73:'J4L23',
77:'J1L32',
78:'J3L2',
79:'J2L5',
80:'J4L43',
81:'J2L27',
82:'J2L43',
83:'J4L5',
84:'J4L17',
85:'J1L14',
86:'J4L27',
87:'J4L45',
88:'J1L10',
89:'J1L2',
90:'J2L41',
91:'J1L16',
92:'J1L36',
93:'J1L24',
94:'J2L35',
95:'J1L34',
96:'J1L28',
97:'J1L26',
98:'J2L39',
99:'J2L11'}
ThermometerNumber = {v: k for k, v in ThermometerName.iteritems()}  # mapping name to a number

ThermometerLocationByNumber={1:'R2',
76:'Leach 1',
3:'Momentum dump',
4:'C6',
5:'C9',
#6:'magneto box',
7:'R14',
8:'L6',
9:'C8',
10:'cRIO',
11:'C1',
12:'R13',
13:'R10',
14:'L13',
15:'L14',
16:'left siderostat right',
17:'C5',
18:'R4',
19:'Broken',
20:'C7',
21:'L starcam',
22:'Top Dewar',
23:'C2',
#24:'R6',
25:'L5',
26:'cRio plate',
#27:'cRio corner UL',
28:'cRio corner DL',
29:'cRio corner UR',
30:'L2',
31:'Broken',
32:'L4',
33:'crio back',
34:'R422 opto-isolator',
35:'Ford',
36:'Ford power board',
37:'Ford heat dissipation',
38:'Ford heat dissipation',
39:'CCMG Galil',
40:'crio back',
41:'L Stepper Motor',
42:'Broken',
43:'Griffin Galil',
44:'Broken',
45:'Gyro 1',
46:'Gyro 2',
47:'Broken',
48:'Gyro 3',
49:'Gyro corner',
50:'Broken',
51:'L telescope left',
52:'L flat mirror left',
53:'Griffin K mirror',
54:'L telescope up',
55:'L telescope right',
56:'L flat mirror right',
57:'K mirror tip/tilt',
58:'DL voice coil board - L',
59:'R starcam',
60:'Ethernet hub',
61:'Delay line board',
62:'Extension chassis',
63:'R telescope up',
64:'R telescope right',
65:'R telescope left',
66:'R flat mirror (left)',
67:'R flat mirror ring',
68:'Router power board',
69:'Tip Tilt board',
70:'5 Volt regulator',
71:'right flat mirror left',
72:'R starcam lens',
73:'R9',
74:'Broken',
75:'Broken',
76:'CDL Power board',
77:'L starcam lens',
78:'C12',
79:'Warm delay line',
80:'Stepper Galil',
81:'Warm delay line tip/tilt',
82:'R stepper motor',
83:'R siderostat top forward',
84:'R griffin rotor',
85:'L siderostat left',
86:'R siderostat top backwards',
87:'R siderostat bottom',
88:'L siderostat bottom',
89:'L griffin motor',
90:'FR6',
91:'FL6',
92:'FL8',
93:'FL7',
94:'FR8',
95:'FL9',
96:'FL3',
97:'FL2',
98:'FR5',
99:'FC6'}
ThermometerNumberByLocation = {v: k for k, v in ThermometerLocationByNumber.iteritems()}  # mapping location to a number