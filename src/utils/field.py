'''
Created on 01 may 2017

Functions and methods useful to read the fields in an Aurora archive.

@author: Marc Casalprim
'''
import os

class Field(object):
    '''
    Class describing a field located in an Aurora archive.  
            
    :param fieldName: name of the field, the whole file name
    :param dtype: string describing the datatype of the field (ie. 'f8' is a 64 bit float)
    :param indexName: file name of the time index associated with this field. If None, is fieldName.rsplit('.', 1)[0] + '.mceFrameNumber'
    :param indexType: string describing the datatype of the index field (ie. 'i8' is a 64 bit int)
    :param label: short name for the field.  In ``utils.dataset.Dataset`` it is used as the name for the dataframe columns. (if None, last word of the fieldName)
    :param conversion: multiplying factor of the data, useful to convert units
    :param function: function that will be applied to to the field data
    :param range: valid range of the field, any value outside +-range will be discarted. Useful to remove parsing errors.
    '''
    # DTYPES is a dictionary mapping each fieldName to a datatype
    # It can be generated using the getDtypes(folder) function
    DTYPES = {'error_r11_c3': 'i8', 'error_r11_c2': 'i8', 'error_r11_c1': 'i8',
    'sq1fb_r17_c20': 'i8', 'error_r11_c7': 'i8', 'error_r11_c6': 'i8',
    'error_r11_c5': 'i8', 'error_r11_c4': 'i8', 'error_r11_c9': 'i8',
    'error_r11_c8': 'i8', 'sq1fb_r17_c21': 'i8', 'fluxJump_r15_c19': 'i4',
    'sq1fb_r21_c3': 'i8', 'fluxJump_r10_c19': 'i4', 'sq1fb_r4_c17': 'i8',
    'sq1fb_r4_c16': 'i8', 'sq1fb_r4_c15': 'i8', 'sq1fb_r4_c14': 'i8',
    'sq1fb_r4_c13': 'i8', 'sq1fb_r4_c12': 'i8', 'sq1fb_r4_c11': 'i8',
    'sq1fb_r4_c10': 'i8', 'sq1fb_r4_c19': 'i8', 'sq1fb_r4_c18': 'i8',
    'fluxJump_r15_c15': 'i4', 'fluxJump_r10_c15': 'i4', 'sq1fb_r21_c2': 'i8',
    'PiperThermo.LHeShield': 'f4', 'fluxJump_r15_c17': 'i4',
    'bettii.ThermometersOutput.DO04': 'u1', 'fluxJump_r10_c17': 'i4',
    'bettii.ThermometersOutput.DO01': 'u1', 'bettii.ThermometersOutput.DO02':
    'u1', 'bettii.ThermometersOutput.DO03': 'u1', 'DSPIDMessage.demodRaw6':
    'i4', 'fluxJump_r15_c11': 'i4', 'DSPIDMessage.demodRaw4': 'i4',
    'DSPIDMessage.demodRaw5': 'i4', 'DSPIDMessage.demodRaw2': 'i4',
    'DSPIDMessage.demodRaw3': 'i4', 'DSPIDMessage.demodRaw0': 'i4',
    'fluxJump_r10_c11': 'i4', 'bettii.RTLowPriority.covarianceMatrix20': 'f8',
    'fluxJump_r15_c13': 'i4', 'fluxJump_r10_c13': 'i4', 'error_r13_c19': 'i8',
    'error_r13_c18': 'i8', 'bettii.StateVector.xEl': 'f4', 'error_r13_c15':
    'i8', 'error_r13_c14': 'i8', 'error_r13_c17': 'i8', 'error_r13_c16': 'i8',
    'error_r13_c11': 'i8', 'error_r13_c10': 'i8', 'error_r13_c13': 'i8',
    'error_r13_c12': 'i8', 'bettii.RTLowPriority.covarianceMatrix21': 'f8',
    'bettii.TimingApplyPIDLoop.loopStart': 'i4',
    'bettii.currentReadout.currentReadout_UPBTwo_5VChannel': 'f4',
    'TReadDiodeMessage.frameCounter': 'i8', 'userData': 'i4',
    'TReadStandardMessage.status': 'i4',
    'bettii.RTHighPriority.SCAnglesInertialGondolaRefFrameArcsecRa': 'f8',
    'bettii.RTLowPriority.SlewParametersPDarcsec': 'i4', 'error_r19_c6': 'i8',
    'PiperThermo.NIRBench2': 'f4', 'sq1fb_r15_c21': 'i8', 'sq1fb_r15_c20': 'i8',
    'bettii.DelayLines.WDLet': 'f4', 'error_r15_c7': 'i8', 'error_r15_c6': 'i8',
    'error_r15_c5': 'i8', 'error_r15_c4': 'i8', 'error_r15_c3': 'i8',
    'error_r15_c2': 'i8', 'error_r15_c1': 'i8',
    'bettii.RTLowPriority.TimingRTBetweenLoops': 'i4', 'error_r15_c9': 'i8',
    'error_r15_c8': 'i8', 'error_r18_c18': 'i8', 'error_r18_c19': 'i8',
    'error_r18_c12': 'i8', 'error_r18_c13': 'i8', 'error_r18_c10': 'i8',
    'error_r18_c11': 'i8', 'error_r18_c16': 'i8', 'error_r18_c17': 'i8',
    'error_r18_c14': 'i8', 'error_r18_c15': 'i8',
    'java_native_messaging.StarCameraAuxiliarySolution.roll_deg': 'f8',
    'java_native_messaging.StarCameraSolution.dec_deg': 'f8', 'error_r10_c12':
    'i8', 'error_r10_c13': 'i8', 'error_r10_c10': 'i8', 'error_r10_c11': 'i8',
    'error_r10_c16': 'i8', 'error_r10_c17': 'i8', 'error_r10_c14': 'i8',
    'error_r10_c15': 'i8', 'DSPIDMessage.coilIsenseRaw9': 'i4', 'error_r10_c18':
    'i8', 'error_r10_c19': 'i8', 'bettii.TimingApplyPIDLoop.readGains': 'i4',
    'error_r4_c16': 'i8', 'error_r4_c17': 'i8', 'error_r4_c14': 'i8',
    'error_r4_c15': 'i8', 'error_r16_c8': 'i8', 'error_r16_c9': 'i8',
    'error_r16_c6': 'i8', 'error_r16_c7': 'i8', 'error_r16_c4': 'i8',
    'error_r16_c5': 'i8', 'error_r16_c2': 'i8', 'error_r16_c3': 'i8',
    'error_r5_c16': 'i8', 'sq1fb_r7_c10': 'i8', 'sq1fb_r7_c11': 'i8',
    'sq1fb_r7_c12': 'i8', 'sq1fb_r7_c13': 'i8', 'sq1fb_r7_c14': 'i8',
    'error_r5_c15': 'i8', 'sq1fb_r7_c16': 'i8', 'sq1fb_r12_c18': 'i8',
    'sq1fb_r7_c18': 'i8', 'sq1fb_r12_c16': 'i8', 'sq1fb_r12_c15': 'i8',
    'sq1fb_r12_c14': 'i8', 'sq1fb_r12_c13': 'i8', 'sq1fb_r12_c12': 'i8',
    'sq1fb_r12_c11': 'i8', 'sq1fb_r12_c10': 'i8',
    'bettii.RTHighPriority.FirstSCReceived': 'u1',
    'bettii.ThermometersDemuxedCelcius.J1L48': 'f4', 'error_r13_c9': 'i8',
    'error_r13_c8': 'i8', 'bettii.RTLowPriority.covarianceMatrix32': 'f8',
    'error_r13_c5': 'i8', 'error_r13_c4': 'i8', 'error_r13_c7': 'i8',
    'error_r13_c6': 'i8', 'error_r13_c1': 'i8', 'error_r13_c3': 'i8',
    'error_r13_c2': 'i8', 'bettii.CommandedTipTilts.mceFrameNumber': 'i8',
    'bettii.TimingApplyPIDLoop.calculatePIDs': 'i4',
    'bettii.RTLowPriority.covarianceMatrix35': 'f8',
    'bettii.ThermometersDemuxedCelcius.TimeReadingSamplesMs': 'i4',
    'bettii.RTLowPriority.StarCameraRotatedqj': 'f8',
    'bettii.RTLowPriority.StarCameraRotatedqk': 'f8',
    'bettii.RTLowPriority.StarCameraRotatedqi': 'f8', 'DSPIDMessage.demodRaw8':
    'i4', 'error_r21_c21': 'i8', 'error_r21_c20': 'i8',
    'bettii.RTLowPriority.covarianceMatrix34': 'f8', 'sq1fb_r16_c9': 'i8',
    'sq1fb_r16_c8': 'i8', 'sq1fb_r16_c7': 'i8', 'sq1fb_r16_c6': 'i8',
    'sq1fb_r16_c5': 'i8', 'sq1fb_r16_c4': 'i8', 'sq1fb_r16_c3': 'i8',
    'sq1fb_r16_c2': 'i8', 'sq1fb_r16_c1': 'i8',
    'bettii.ThermometersDemuxedCelcius.J1L18': 'f4', 'error_r12_c21': 'i8',
    'error_r12_c20': 'i8', 'bettii.Magnetometer.RaDeg': 'f4',
    'DSPIDMessage.demodRaw1': 'i4',
    'java_native_messaging.StarCameraAuxiliarySolution.qr': 'f8',
    'TReadStandardMessage.temperature6': 'f4',
    'java_native_messaging.StarCameraAuxiliarySolution.qi': 'f8',
    'java_native_messaging.StarCameraAuxiliarySolution.qj': 'f8',
    'java_native_messaging.StarCameraAuxiliarySolution.qk': 'f8',
    'bettii.ThermometersDemuxedCelcius.J1L10': 'f4',
    'TReadStandardMessage.temperature0': 'f4', 'error_r8_c18': 'i8',
    'error_r8_c19': 'i8', 'TReadStandardMessage.temperature3': 'f4',
    'error_r8_c12': 'i8', 'error_r8_c13': 'i8', 'error_r8_c10': 'i8',
    'error_r8_c11': 'i8', 'error_r8_c16': 'i8', 'error_r8_c17': 'i8',
    'error_r8_c14': 'i8', 'error_r8_c15': 'i8',
    'bettii.ThermometersDemuxedCelcius.J2L19': 'f4',
    'bettii.currentReadout.currentReadout_UPBOne_negative15VChannel': 'f4',
    'TReadStandardMessage.aDacRaw15': 'i4', 'TReadStandardMessage.aDacRaw10':
    'i4', 'TReadStandardMessage.aDacRaw11': 'i4',
    'TReadStandardMessage.aDacRaw12': 'i4', 'TReadStandardMessage.aDacRaw13':
    'i4', 'sq1fb_r9_c16': 'i8', 'sq1fb_r9_c17': 'i8', 'sq1fb_r9_c14': 'i8',
    'bettii.RTHighPriority.EstimatorErrorRespectLastSCElArcsec': 'f8',
    'sq1fb_r8_c10': 'i8', 'sq1fb_r9_c12': 'i8', 'sq1fb_r8_c16': 'i8',
    'bettii.RTLowPriority.RawStarcameraQuaternionFXPqj': 'f4',
    'bettii.RTLowPriority.RawStarcameraQuaternionFXPqk': 'f4',
    'bettii.RTLowPriority.RawStarcameraQuaternionFXPqi': 'f4', 'sq1fb_r8_c15':
    'i8', 'sq1fb_r9_c11': 'i8',
    'bettii.RTLowPriority.RawStarcameraQuaternionFXPqr': 'f4', 'error_r21_c6':
    'i8', 'fluxJump_r2_c16': 'i4', 'fluxJump_r2_c17': 'i4', 'sq1fb_r4_c20':
    'i8', 'fluxJump_r2_c15': 'i4', 'fluxJump_r2_c12': 'i4', 'fluxJump_r2_c13':
    'i4', 'fluxJump_r2_c10': 'i4', 'fluxJump_r2_c11': 'i4', 'fluxJump_r2_c18':
    'i4', 'fluxJump_r2_c19': 'i4', 'error_r21_c2': 'i8',
    'TReadDiodeMessage.aDac8': 'f4', 'TReadDiodeMessage.aDac9': 'f4',
    'TReadDiodeMessage.aDac6': 'f4', 'TReadDiodeMessage.aDac7': 'f4',
    'TReadDiodeMessage.aDac4': 'f4', 'error_r21_c3': 'i8',
    'TReadDiodeMessage.aDac2': 'f4', 'TReadDiodeMessage.aDac3': 'f4',
    'TReadDiodeMessage.aDac0': 'f4', 'TReadDiodeMessage.aDac1': 'f4',
    'bettii.ThermometersOutput.DO17': 'u1', 'bettii.ThermometersOutput.DO16':
    'u1', 'bettii.ThermometersOutput.DO19': 'u1',
    'bettii.ThermometersOutput.DO18': 'u1',
    'bettii.RTHighPriority.SCAnglesInertialGondolaRefFrameArcsecDec': 'f8',
    'fluxJump_r3_c20': 'i4', 'fluxJump_r3_c21': 'i4',
    'bettii.RTLowPriority.TimingRTPlotsRaDec': 'i4',
    'DSPIDMessage.coilDACRaw12': 'i4', 'DSPIDMessage.coilDACRaw13': 'i4',
    'DSPIDMessage.coilDACRaw10': 'i4', 'DSPIDMessage.coilDACRaw11': 'i4',
    'bettii.GriffinsGalil.griffinBAngleDegrees': 'f8',
    'DSPIDMessage.coilDACRaw15': 'i4', 'fluxJump_r14_c18': 'i4',
    'fluxJump_r14_c19': 'i4', 'fluxJump_r14_c10': 'i4', 'fluxJump_r14_c11':
    'i4', 'fluxJump_r14_c12': 'i4', 'fluxJump_r14_c13': 'i4',
    'fluxJump_r14_c14': 'i4', 'fluxJump_r14_c15': 'i4', 'fluxJump_r14_c16':
    'i4', 'fluxJump_r14_c17': 'i4', 'bettii.TimingSensorsLoop.triggerGyro':
    'i4', 'bettii.ThermometersDemuxedCelcius.J4L1': 'f4',
    'bettii.ThermometersDemuxedCelcius.J4L7': 'f4',
    'bettii.ThermometersDemuxedCelcius.J4L5': 'f4',
    'bettii.ThermometersDemuxedCelcius.J4L9': 'f4',
    'bettii.currentReadout.currentReadout_UPBTwo_28VChannel': 'f4',
    'bettii.TimingSensorsLoop.loopStart': 'i4', 'PiperThermo.OpticsBench': 'f4',
    'sq1fb_r6_c20': 'i8', 'sq1fb_r6_c21': 'i8', 'error_r18_c21': 'i8',
    'error_r18_c20': 'i8', 'bettii.WheelsGalil.mceFrameNumber': 'i8',
    'error_r21_c16': 'i8', 'bettii.TipTilts.mceFrameNumberEthercat': 'i8',
    'IvTemperatures.mceFrameNumber': 'i8', 'error_r10_c21': 'i8',
    'error_r10_c20': 'i8', 'mceFrameNumber': 'i8',
    'bettii.currentReadout.voltageReadout_UPBOne_5VChannel': 'f4',
    'sq1fb_r9_c21': 'i8', 'sq1fb_r9_c20': 'i8',
    'bettii.RTLowPriority.RawStarcameraElDeg': 'f4',
    'AnalogOutMessage.analogOut1': 'f4', 'PiperThermo.Cal1kohm': 'f4',
    'java_native_messaging.StarCameraSolution.az_deg': 'f8',
    'bettii.RTHighPriority.TimingRTCounterOver10ms': 'i4',
    'bettii.GyroReadings.triggerNum': 'i4',
    'bettii.currentReadout.currentReadout_UPBOne_12VChannel': 'f4',
    'bettii.RTLowPriority.RawStarcameraRaDeg': 'f4', 'fluxJump_r5_c1': 'i4',
    'fluxJump_r5_c3': 'i4', 'fluxJump_r5_c2': 'i4', 'fluxJump_r5_c5': 'i4',
    'fluxJump_r5_c4': 'i4', 'fluxJump_r5_c7': 'i4', 'fluxJump_r5_c6': 'i4',
    'fluxJump_r5_c9': 'i4', 'fluxJump_r5_c8': 'i4', 'AnalogInMessage.aDC6':
    'f4', 'TReadDiodeMessage.demodRaw1': 'i4',
    'bettii.ThermometersDemuxedCelcius.J2L49': 'f4', 'AnalogInMessage.aDC7':
    'f4', 'bettii.ThermometersDemuxedCelcius.J2L45': 'f4',
    'bettii.ThermometersDemuxedCelcius.J2L47': 'f4',
    'bettii.ThermometersDemuxedCelcius.J2L41': 'f4', 'AnalogInMessage.aDC4':
    'f4', 'bettii.ThermometersDemuxedCelcius.J2L43': 'f4',
    'AnalogInMessage.aDC5': 'f4', 'bettii.RTLowPriority.mceFrameNumber': 'i8',
    'AnalogInMessage.aDC0': 'f4', 'AnalogInMessage.aDC1': 'f4',
    'bettii.WheelsGalil.tva': 'i4', 'DSPIDMessage.coilIsense15': 'f4',
    'bettii.RTHighPriority.computedEstimatorElevation': 'f8',
    'DSPIDMessage.coilIsense11': 'f4', 'DSPIDMessage.coilIsense10': 'f4',
    'DSPIDMessage.coilIsense13': 'f4', 'DSPIDMessage.demodRaw7': 'i4',
    'java_native_messaging.StarCameraAuxiliarySolution.dec_deg': 'f8',
    'java_native_messaging.StarCameraAuxiliarySolution.sigma_ra': 'f8',
    'bettii.StepperGalil.tdb': 'i4', 'bettii.StepperGalil.tda': 'i4',
    'bettii.RTHighPriority.GriffinManualSendPositionAbosuluteA': 'u1',
    'bettii.RTHighPriority.GriffinManualSendPositionAbosuluteB': 'u1',
    'MasterMessage.uBCFrameCount': 'i8', 'error_r10_c8': 'i8', 'error_r10_c9':
    'i8', 'error_r10_c1': 'i8', 'error_r10_c2': 'i8', 'error_r10_c3': 'i8',
    'error_r10_c4': 'i8', 'error_r10_c5': 'i8', 'error_r10_c6': 'i8',
    'error_r10_c7': 'i8', 'TReadDiodeMessage.aDacRaw14': 'i4',
    'bettii.DelayLines.WDLut': 'f4', 'bettii.ThermometersDemuxedCelcius.J1L42':
    'f4', 'fluxJump_r1_c5': 'i4', 'fluxJump_r1_c4': 'i4', 'fluxJump_r1_c7':
    'i4', 'fluxJump_r1_c6': 'i4', 'fluxJump_r1_c1': 'i4',
    'AnalogInMessage.aDCRaw6': 'f4', 'fluxJump_r1_c3': 'i4', 'fluxJump_r1_c2':
    'i4', 'bettii.ThermometersDemuxedCelcius.J1L44': 'f4',
    'AnalogInMessage.aDCRaw9': 'f4', 'AnalogInMessage.aDCRaw8': 'f4',
    'fluxJump_r1_c9': 'i4', 'fluxJump_r1_c8': 'i4', 'PiperThermo.LHeTank': 'f4',
    'sq1fb_r21_c5': 'i8', 'sq1fb_r21_c4': 'i8', 'TReadDiodeMessage.gDac11':
    'i4', 'sq1fb_r21_c7': 'i8', 'sq1fb_r21_c6': 'i8', 'sq1fb_r21_c1': 'i8',
    'sq1fb_r5_c8': 'i8', 'sq1fb_r13_c1': 'i8', 'sq1fb_r13_c2': 'i8',
    'sq1fb_r13_c3': 'i8', 'sq1fb_r13_c4': 'i8', 'sq1fb_r13_c5': 'i8',
    'sq1fb_r13_c6': 'i8', 'sq1fb_r13_c7': 'i8', 'sq1fb_r13_c8': 'i8',
    'sq1fb_r5_c1': 'i8', 'sq1fb_r5_c2': 'i8', 'sq1fb_r5_c3': 'i8',
    'sq1fb_r5_c4': 'i8', 'sq1fb_r5_c5': 'i8', 'sq1fb_r5_c6': 'i8',
    'sq1fb_r5_c7': 'i8', 'DSPIDMessage.coilIsenseRaw2': 'i4',
    'DSPIDMessage.coilIsenseRaw3': 'i4', 'DSPIDMessage.coilIsenseRaw0': 'i4',
    'DSPIDMessage.coilIsenseRaw1': 'i4', 'fluxJump_r2_c8': 'i4',
    'fluxJump_r2_c9': 'i4', 'DSPIDMessage.coilIsenseRaw4': 'i4',
    'DSPIDMessage.coilIsenseRaw5': 'i4', 'fluxJump_r2_c4': 'i4',
    'fluxJump_r2_c5': 'i4', 'fluxJump_r2_c6': 'i4', 'fluxJump_r2_c7': 'i4',
    'fluxJump_r2_c1': 'i4', 'fluxJump_r2_c2': 'i4', 'fluxJump_r2_c3': 'i4',
    'DSPIDMessage.pidAccumulator': 'i4',
    'bettii.RTLowPriority.MeasurementErrorCovarianceMatrixR22': 'f8',
    'bettii.RTLowPriority.RawStarcameraAzDeg': 'f4',
    'bettii.RTLowPriority.MeasurementErrorCovarianceMatrixR20': 'f8',
    'PiperThermo.NIRBench': 'f4', 'bettii.Magnetometer.AzimuthDeg': 'f4',
    'bettii.WheelsGalil.ttbDec': 'i4', 'error_r19_c9': 'i8', 'error_r19_c8':
    'i8', 'error_r19_c3': 'i8', 'error_r19_c2': 'i8', 'error_r19_c1': 'i8',
    'error_r19_c7': 'i8', 'error_r1_c9': 'i8', 'error_r19_c5': 'i8',
    'error_r19_c4': 'i8', 'error_r1_c8': 'i8', 'fluxJump_r7_c9': 'i4',
    'fluxJump_r7_c8': 'i4', 'fluxJump_r7_c7': 'i4', 'fluxJump_r7_c6': 'i4',
    'fluxJump_r7_c5': 'i4', 'fluxJump_r7_c4': 'i4', 'fluxJump_r7_c3': 'i4',
    'fluxJump_r7_c2': 'i4', 'fluxJump_r7_c1': 'i4',
    'TReadDiodeMessage.aDacRaw12': 'i4', 'TReadDiodeMessage.aDacRaw11': 'i4',
    'TReadDiodeMessage.aDacRaw10': 'i4', 'error_r17_c1': 'i8', 'error_r17_c3':
    'i8', 'error_r17_c2': 'i8', 'error_r17_c5': 'i8', 'error_r17_c4': 'i8',
    'error_r17_c7': 'i8', 'error_r17_c6': 'i8', 'error_r17_c9': 'i8',
    'error_r17_c8': 'i8', 'error_r12_c8': 'i8', 'error_r12_c9': 'i8',
    'error_r12_c2': 'i8', 'error_r12_c3': 'i8', 'error_r12_c1': 'i8',
    'error_r12_c6': 'i8', 'error_r12_c7': 'i8', 'error_r12_c4': 'i8',
    'error_r12_c5': 'i8', 'sq1fb_r8_c13': 'i8', 'sq1fb_r8_c12': 'i8',
    'sq1fb_r8_c11': 'i8', 'sq1fb_r9_c15': 'i8', 'sq1fb_r8_c17': 'i8',
    'sq1fb_r9_c13': 'i8', 'sq1fb_r9_c10': 'i8', 'sq1fb_r8_c14': 'i8',
    'error_r21_c4': 'i8', 'error_r21_c5': 'i8', 'sq1fb_r8_c19': 'i8',
    'sq1fb_r8_c18': 'i8', 'error_r21_c1': 'i8', 'sq1fb_r9_c18': 'i8',
    'sq1fb_r9_c19': 'i8',
    'bettii.RTHighPriority.GriffinManualPositionAbosuluteB': 'i4',
    'bettii.RTHighPriority.GriffinManualPositionAbosuluteA': 'i4',
    'bettii.currentReadout.currentReadout_UPBOne_28VChannel': 'f4',
    'PiperThermo.Cal100kohm': 'f4', 'sq1fb_r17_c4': 'i8', 'sq1fb_r17_c5': 'i8',
    'sq1fb_r17_c6': 'i8', 'sq1fb_r17_c7': 'i8', 'sq1fb_r17_c1': 'i8',
    'sq1fb_r17_c2': 'i8', 'sq1fb_r17_c3': 'i8', 'sq1fb_r17_c8': 'i8',
    'sq1fb_r17_c9': 'i8', 'DSPIDMessage.gnd': 'f4',
    'bettii.GpsReadings.longitudeDegrees': 'f4', 'TReadDiodeMessage.demodRaw2':
    'i4', 'TReadDiodeMessage.demodRaw3': 'i4', 'TReadDiodeMessage.demodRaw0':
    'i4', 'bettii.DelayLines.CDLloopIteration': 'i4',
    'TReadDiodeMessage.demodRaw6': 'i4', 'TReadDiodeMessage.demodRaw7': 'i4',
    'TReadDiodeMessage.demodRaw4': 'i4', 'TReadDiodeMessage.demodRaw5': 'i4',
    'AnalogInMessage.status': 'i4', 'TReadDiodeMessage.demodRaw8': 'i4',
    'TReadDiodeMessage.demodRaw9': 'i4',
    'bettii.PIDInputMomDump.positionMeasurement': 'f4', 'sq1fb_r14_c20': 'i8',
    'sq1fb_r14_c21': 'i8', 'bettii.TimingApplyPIDLoop.applyPIDLoopDuration':
    'i4', 'DSPIDMessage.vsupplyRaw': 'i4',
    'bettii.ThermometersDemuxedCelcius.J3L50': 'f4',
    'bettii.GyroReadings.temperatureDegF_Y': 'i4',
    'bettii.GyroReadings.temperatureDegF_X': 'i4',
    'bettii.GyroReadings.temperatureDegF_Z': 'i4',
    'java_native_messaging.StarCameraSolution.qi': 'f8',
    'bettii.DelayLines.CDLproportional': 'f4', 'fluxJump_r12_c21': 'i4',
    'fluxJump_r12_c20': 'i4', 'java_native_messaging.StarCameraSolution.qr':
    'f8', 'DSPIDMessage.analogInRaw': 'i4',
    'bettii.TimingApplyPIDLoop.betweenapplyPIDLoops': 'i4',
    'java_native_messaging.StarCameraSolution.qk': 'f8',
    'java_native_messaging.StarCameraSolution.qj': 'f8',
    'java_native_messaging.StarCameraSolution.ra_deg': 'f8',
    'TReadDiodeMessage.aDac10': 'f4', 'bettii.ThermometersDemuxedCelcius.J2L29':
    'f4', 'bettii.TimingApplyPIDLoop.checkLimits': 'i4',
    'bettii.StepperGalil.mceFrameNumber': 'i8',
    'bettii.RTLowPriority.TimingRTRotateTarget': 'i4',
    'bettii.ThermometersDemuxedCelcius.J2L25': 'f4', 'TReadDiodeMessage.aDac15':
    'f4', 'bettii.ThermometersDemuxedCelcius.J2L23': 'f4', 'DSPIDMessage.gDac':
    'i4', 'bettii.TipTilts.PiezoWDLVMON1': 'f4',
    'bettii.TipTilts.PiezoWDLVMON3': 'f4', 'bettii.TipTilts.PiezoWDLVMON2':
    'f4', 'bettii.AngleSensorOutput.KYOffsetPixels': 'f4',
    'IvTemperatures.milliKelvin': 'f4', 'error_r20_c20': 'i8', 'error_r20_c21':
    'i8', 'DSPIDMessage.analogOutRaw14': 'i4', 'DSPIDMessage.analogOutRaw11':
    'i4', 'DSPIDMessage.analogOutRaw10': 'i4',
    'bettii.GyroReadings.mceFrameNumber': 'i8', 'DSPIDMessage.analogOutRaw12':
    'i4', 'bettii.currentReadout.currentReadout_UPBTwo_negative15VChannel':
    'f4', 'bettii.TipTilts.PiezoWDLVMONY': 'f4',
    'bettii.TipTilts.PiezoWDLVMONX': 'f4',
    'java_native_messaging.StarCameraSolution.frame_number': 'i8',
    'error_r13_c20': 'i8', 'error_r13_c21': 'i8', 'bettii.Magnetometer.TimeLST':
    'f4', 'bettii.PIDOutputCCMG.derivative': 'f4', 'fluxJump_r19_c20': 'i4',
    'fluxJump_r19_c21': 'i4', 'error_r21_c8': 'i8',
    'bettii.PIDInputCCMG.positionTarget': 'f4', 'error_r21_c9': 'i8',
    'bettii.ThermometersOutput.AI0': 'f4', 'bettii.ThermometersOutput.AI1':
    'f4', 'bettii.ThermometersOutput.AI2': 'f4',
    'bettii.ThermometersOutput.AI3': 'f4', 'sq1fb_r17_c16': 'i8',
    'bettii.ThermometersOutput.AI5': 'f4', 'bettii.ThermometersOutput.AI6':
    'f4', 'bettii.ThermometersOutput.AI7': 'f4', 'error_r16_c1': 'i8',
    'bettii.FpgaState.state': 'i4', 'fluxJump_r3_c10': 'i4',
    'bettii.RTLowPriority.MeasurementErrorCovarianceMatrixR12': 'f8',
    'bettii.RTLowPriority.MeasurementErrorCovarianceMatrixR10': 'f8',
    'bettii.RTLowPriority.MeasurementErrorCovarianceMatrixR11': 'f8',
    'java_native_messaging.StarCameraAuxiliarySolution.el_deg': 'f8',
    'sq1fb_r7_c15': 'i8', 'bettii.ThermometersDemuxedCelcius.J4L19': 'f4',
    'sq1fb_r12_c19': 'i8', 'bettii.ThermometersDemuxedCelcius.J4L11': 'f4',
    'sq1fb_r7_c17': 'i8', 'bettii.ThermometersDemuxedCelcius.J4L15': 'f4',
    'bettii.ThermometersDemuxedCelcius.J4L17': 'f4', 'sq1fb_r12_c17': 'i8',
    'sq1fb_r7_c19': 'i8', 'TReadStandardMessage.aDac11': 'f4',
    'TReadStandardMessage.aDac10': 'f4', 'DSPIDMessage.pidP': 'i4',
    'TReadStandardMessage.aDac12': 'f4', 'TReadStandardMessage.aDac15': 'f4',
    'TReadStandardMessage.aDac14': 'f4', 'AnalogInMessage.aDCRaw20': 'f4',
    'AnalogInMessage.aDCRaw21': 'f4', 'AnalogInMessage.aDCRaw26': 'f4',
    'sq1fb_r8_c20': 'i8', 'sq1fb_r8_c21': 'i8', 'sq1fb_r15_c18': 'i8',
    'sq1fb_r15_c19': 'i8', 'sq1fb_r15_c14': 'i8', 'sq1fb_r15_c15': 'i8',
    'sq1fb_r15_c16': 'i8', 'sq1fb_r15_c17': 'i8', 'sq1fb_r15_c10': 'i8',
    'sq1fb_r15_c11': 'i8', 'sq1fb_r15_c12': 'i8', 'sq1fb_r15_c13': 'i8',
    'error_r21_c7': 'i8', 'bettii.RTHighPriority.TelescopeRaDeg': 'f8',
    'DSPIDMessage.pidSetPointRaw': 'i4', 'TReadDiodeMessage.demodRaw14': 'i4',
    'TReadDiodeMessage.demodRaw15': 'i4',
    'bettii.ThermometersDemuxedCelcius.J3L48': 'f4',
    'TReadDiodeMessage.demodRaw10': 'i4', 'TReadDiodeMessage.demodRaw11': 'i4',
    'TReadDiodeMessage.demodRaw12': 'i4', 'TReadDiodeMessage.demodRaw13': 'i4',
    'bettii.ThermometersDemuxedCelcius.J3L42': 'f4',
    'bettii.ThermometersDemuxedCelcius.J3L40': 'f4',
    'bettii.ThermometersDemuxedCelcius.J3L46': 'f4',
    'bettii.ThermometersDemuxedCelcius.J3L44': 'f4',
    'bettii.BoopSysInfo.mceFrameNumber': 'i8', 'DSPIDMessage.analogOutRaw13':
    'i4', 'sq1fb_r7_c21': 'i8', 'sq1fb_r7_c20': 'i8', 'fluxJump_r12_c16': 'i4',
    'fluxJump_r12_c17': 'i4', 'fluxJump_r12_c14': 'i4', 'fluxJump_r12_c15':
    'i4', 'fluxJump_r12_c12': 'i4', 'fluxJump_r12_c13': 'i4',
    'fluxJump_r12_c10': 'i4', 'fluxJump_r12_c11': 'i4', 'error_r12_c10': 'i8',
    'error_r12_c11': 'i8', 'error_r12_c12': 'i8', 'error_r12_c13': 'i8',
    'error_r12_c14': 'i8', 'error_r12_c15': 'i8', 'error_r12_c16': 'i8',
    'error_r12_c17': 'i8', 'error_r8_c8': 'i8', 'error_r8_c9': 'i8',
    'MasterMessage.frameCounter': 'i8', 'error_r8_c1': 'i8', 'error_r8_c2':
    'i8', 'error_r8_c3': 'i8', 'error_r8_c4': 'i8', 'error_r8_c5': 'i8',
    'error_r8_c6': 'i8', 'error_r8_c7': 'i8', 'fluxJump_r4_c8': 'i4',
    'fluxJump_r4_c9': 'i4', 'fluxJump_r4_c2': 'i4', 'fluxJump_r4_c3': 'i4',
    'fluxJump_r4_c1': 'i4', 'fluxJump_r4_c6': 'i4', 'fluxJump_r4_c7': 'i4',
    'fluxJump_r4_c4': 'i4', 'fluxJump_r4_c5': 'i4', 'error_r1_c19': 'i8',
    'error_r1_c18': 'i8', 'error_r1_c17': 'i8', 'error_r1_c16': 'i8',
    'error_r1_c15': 'i8', 'error_r1_c14': 'i8', 'error_r1_c13': 'i8',
    'error_r1_c12': 'i8', 'error_r1_c11': 'i8', 'error_r1_c10': 'i8',
    'bettii.TimingApplyPIDLoop.readControls': 'i4', 'DSPIDMessage.vsupply':
    'f4', 'TReadDiodeMessage.gDac4': 'i4',
    'bettii.RTLowPriority.covarianceMatrix31': 'f8', 'TReadDiodeMessage.gDac6':
    'i4', 'TReadDiodeMessage.gDac7': 'i4', 'TReadDiodeMessage.gDac0': 'i4',
    'TReadDiodeMessage.gDac1': 'i4', 'TReadDiodeMessage.gDac2': 'i4',
    'bettii.RTLowPriority.covarianceMatrix30': 'f8', 'TReadDiodeMessage.gDac8':
    'i4', 'TReadDiodeMessage.gDac9': 'i4', 'error_r20_c13': 'i8',
    'error_r20_c12': 'i8', 'error_r20_c11': 'i8', 'error_r20_c10': 'i8',
    'error_r20_c17': 'i8', 'error_r20_c16': 'i8', 'error_r20_c15': 'i8',
    'error_r20_c14': 'i8', 'sq1fb_r11_c6': 'i8', 'error_r20_c19': 'i8',
    'error_r20_c18': 'i8', 'sq1fb_r11_c7': 'i8',
    'bettii.currentReadout.currentReadout_UPBTwo_15VChannel': 'f4',
    'sq1fb_r11_c4': 'i8', 'sq1fb_r11_c5': 'i8', 'TReadStandardMessage.aDac13':
    'f4', 'bettii.RTLowPriority.TimingRTGenerateSC': 'i4',
    'AnalogInMessage.aDCRaw25': 'f4', 'bettii.RTHighPriority.TelescopeDecDeg':
    'f8', 'sq1fb_r7_c4': 'i8',
    'bettii.RTHighPriority.EstimatorErrorRespectLastSCRollArcsec': 'f8',
    'sq1fb_r7_c5': 'i8', 'bettii.RTHighPriority.MomDumpSpeedManualValue': 'i4',
    'sq1fb_r4_c3': 'i8', 'sq1fb_r4_c2': 'i8', 'sq1fb_r4_c1': 'i8',
    'sq1fb_r4_c7': 'i8', 'sq1fb_r4_c6': 'i8', 'sq1fb_r4_c5': 'i8',
    'sq1fb_r4_c4': 'i8', 'DSPIDMessage.pidSetPoint': 'f4', 'sq1fb_r4_c9': 'i8',
    'sq1fb_r4_c8': 'i8', 'DSPIDMessage.coilIsenseRaw14': 'i4',
    'DSPIDMessage.coilIsenseRaw15': 'i4', 'DSPIDMessage.coilIsenseRaw10': 'i4',
    'DSPIDMessage.coilIsenseRaw11': 'i4', 'DSPIDMessage.coilIsenseRaw12': 'i4',
    'DSPIDMessage.coilIsenseRaw13': 'i4', 'fluxJump_r5_c20': 'i4',
    'fluxJump_r5_c21': 'i4', 'DSPIDMessage.demodRaw14': 'i4',
    'DSPIDMessage.demodRaw15': 'i4', 'DSPIDMessage.demodRaw10': 'i4',
    'DSPIDMessage.demodRaw11': 'i4', 'DSPIDMessage.demodRaw12': 'i4',
    'DSPIDMessage.demodRaw13': 'i4', 'bettii.Magnetometer.Latitude': 'f4',
    'DSPIDMessage.coilDACRaw8': 'i4', 'DSPIDMessage.coilDACRaw9': 'i4',
    'DSPIDMessage.coilDACRaw0': 'i4', 'DSPIDMessage.coilDACRaw1': 'i4',
    'DSPIDMessage.coilDACRaw2': 'i4', 'DSPIDMessage.coilDACRaw3': 'i4',
    'DSPIDMessage.coilDACRaw4': 'i4', 'DSPIDMessage.coilDACRaw5': 'i4',
    'DSPIDMessage.coilDACRaw6': 'i4', 'DSPIDMessage.coilDACRaw7': 'i4',
    'fluxJump_r3_c3': 'i4', 'fluxJump_r3_c2': 'i4', 'fluxJump_r3_c1': 'i4',
    'fluxJump_r3_c7': 'i4', 'fluxJump_r3_c6': 'i4', 'fluxJump_r3_c5': 'i4',
    'fluxJump_r3_c4': 'i4', 'fluxJump_r3_c9': 'i4', 'fluxJump_r3_c8': 'i4',
    'java_native_messaging.StarCameraAuxiliarySolution.sigma_roll': 'f8',
    'fluxJump_r6_c8': 'i4', 'fluxJump_r6_c9': 'i4', 'AnalogInMessage.aDCRaw15':
    'f4', 'AnalogInMessage.aDCRaw14': 'f4', 'AnalogInMessage.aDCRaw13': 'f4',
    'AnalogInMessage.aDCRaw12': 'f4', 'AnalogInMessage.aDCRaw11': 'f4',
    'AnalogInMessage.aDCRaw10': 'f4', 'fluxJump_r6_c1': 'i4', 'fluxJump_r6_c2':
    'i4', 'fluxJump_r6_c3': 'i4', 'fluxJump_r6_c4': 'i4', 'fluxJump_r6_c5':
    'i4', 'fluxJump_r6_c6': 'i4', 'fluxJump_r6_c7': 'i4', 'fluxJump_r14_c21':
    'i4', 'fluxJump_r14_c20': 'i4', 'bettii.Magnetometer.RollDeg': 'f4',
    'fluxJump_r18_c14': 'i4', 'fluxJump_r18_c15': 'i4', 'fluxJump_r18_c16':
    'i4', 'fluxJump_r18_c17': 'i4', 'fluxJump_r18_c10': 'i4',
    'fluxJump_r18_c11': 'i4', 'fluxJump_r18_c12': 'i4', 'fluxJump_r18_c13':
    'i4', 'AnalogInMessage.aDC': 'f4', 'fluxJump_r18_c18': 'i4',
    'fluxJump_r18_c19': 'i4', 'bettii.RTHighPriority.estimatedBiasXarcsec':
    'f8', 'sq1fb_r6_c19': 'i8', 'sq1fb_r6_c18': 'i8', 'sq1fb_r6_c15': 'i8',
    'sq1fb_r6_c14': 'i8', 'sq1fb_r6_c17': 'i8', 'sq1fb_r6_c16': 'i8',
    'sq1fb_r6_c11': 'i8', 'sq1fb_r6_c10': 'i8', 'sq1fb_r6_c13': 'i8',
    'sq1fb_r6_c12': 'i8',
    'bettii.ThermometersDemuxedCelcius.TimeEnergizersUpMs': 'i4',
    'bettii.RTLowPriority.MeasurementErrorCovarianceMatrixR01': 'f8',
    'bettii.RTLowPriority.MeasurementErrorCovarianceMatrixR00': 'f8',
    'bettii.RTLowPriority.MeasurementErrorCovarianceMatrixR02': 'f8',
    'bettii.GriffinsGalil.griffinCAngleDegrees': 'f8',
    'DSPIDMessage.analogOut13': 'f4',
    'bettii.RTLowPriority.RawStarcameraRaError': 'f4',
    'bettii.ThermometersDemuxedCelcius.J4L25': 'f4',
    'bettii.RTLowPriority.TimingRTFPGAInOut': 'i4',
    'bettii.ThermometersDemuxedCelcius.J4L21': 'f4',
    'bettii.ThermometersDemuxedCelcius.J4L23': 'f4',
    'bettii.ThermometersDemuxedCelcius.J4L29': 'f4', 'bettii.BoopSysInfo.cpu2':
    'f4', 'java_native_messaging.StarCameraSolution.sigma_dec': 'f8',
    'fluxJump_r18_c2': 'i4', 'fluxJump_r18_c3': 'i4', 'fluxJump_r18_c1': 'i4',
    'fluxJump_r18_c6': 'i4', 'fluxJump_r18_c7': 'i4', 'fluxJump_r18_c4': 'i4',
    'fluxJump_r18_c5': 'i4', 'fluxJump_r18_c8': 'i4', 'fluxJump_r18_c9': 'i4',
    'bettii.RTLowPriority.StarCameraRotatedqr': 'f8', 'sq1fb_r21_c19': 'i8',
    'sq1fb_r21_c18': 'i8', 'sq1fb_r21_c15': 'i8', 'sq1fb_r21_c14': 'i8',
    'sq1fb_r21_c17': 'i8', 'sq1fb_r21_c16': 'i8', 'sq1fb_r21_c11': 'i8',
    'sq1fb_r21_c10': 'i8', 'sq1fb_r21_c13': 'i8', 'sq1fb_r21_c12': 'i8',
    'bettii.TimingSensorsLoop.writeToIndicator': 'i4', 'sq1fb_r1_c21': 'i8',
    'sq1fb_r1_c20': 'i8', 'bettii.RTHighPriority.SCSolutionsFound': 'i4',
    'error_r9_c17': 'i8', 'error_r9_c16': 'i8', 'error_r9_c15': 'i8',
    'error_r9_c14': 'i8', 'error_r9_c13': 'i8', 'error_r9_c12': 'i8',
    'error_r9_c11': 'i8', 'error_r9_c10': 'i8', 'fluxJump_r9_c20': 'i4',
    'fluxJump_r9_c21': 'i4', 'error_r9_c19': 'i8', 'error_r9_c18': 'i8',
    'DSPIDMessage.coilDAC13': 'f4', 'DSPIDMessage.coilDAC12': 'f4',
    'DSPIDMessage.coilDAC11': 'f4', 'DSPIDMessage.coilDAC10': 'f4',
    'DSPIDMessage.coilDAC15': 'f4', 'DSPIDMessage.coilDAC14': 'f4',
    'TReadDiodeMessage.aDac14': 'f4', 'AnalogInMessage.gain': 'i4',
    'error_r15_c20': 'i8', 'error_r15_c21': 'i8',
    'bettii.ThermometersDemuxedCelcius.J1L16': 'f4',
    'bettii.ThermometersDemuxedCelcius.J1L14': 'f4',
    'bettii.ThermometersDemuxedCelcius.J1L12': 'f4',
    'bettii.StateVector.mceFrameNumber': 'i8', 'error_r1_c20': 'i8',
    'error_r1_c21': 'i8', 'fluxJump_r16_c21': 'i4', 'fluxJump_r16_c20': 'i4',
    'bettii.RTLowPriority.estimatedGyroYarcsec': 'f8',
    'bettii.StateVector.vxEl': 'f4',
    'bettii.RTLowPriority.SlewParametersTotalDistanceToCover': 'f4',
    'bettii.TimingApplyPIDLoop.commandAndReadoutGalils': 'i4',
    'java_native_messaging.StarCameraSolution.el_deg': 'f8',
    'MasterMessage.latestMceFrameNumber': 'i8',
    'bettii.RTHighPriority.SCAnglesInertialGondolaRefFrameArcsecRoll': 'f8',
    'DSPIDMessage.address': 'i4', 'fluxJump_r5_c15': 'i4', 'fluxJump_r5_c14':
    'i4', 'fluxJump_r5_c17': 'i4', 'fluxJump_r5_c16': 'i4', 'fluxJump_r5_c11':
    'i4', 'fluxJump_r5_c10': 'i4', 'fluxJump_r5_c13': 'i4', 'fluxJump_r5_c12':
    'i4', 'error_r1_c3': 'i8', 'error_r1_c2': 'i8', 'error_r1_c1': 'i8',
    'error_r1_c7': 'i8', 'error_r1_c6': 'i8', 'error_r1_c5': 'i8',
    'error_r1_c4': 'i8', 'bettii.PIDInputMomDump.velocityTarget': 'f4',
    'PiperThermo.3HeSwitch': 'f4', 'DSPIDMessage.frameCounter': 'i8',
    'error_r3_c20': 'i8', 'error_r3_c21': 'i8', 'error_r14_c18': 'i8',
    'sq1fb_r1_c19': 'i8', 'sq1fb_r1_c16': 'i8', 'AnalogInMessage.aDCRaw28':
    'f4', 'AnalogInMessage.aDCRaw29': 'f4', 'sq1fb_r1_c17': 'i8',
    'AnalogInMessage.aDCRaw22': 'f4', 'AnalogInMessage.aDCRaw23': 'f4',
    'DSPIDMessage.analogOut14': 'f4', 'DSPIDMessage.analogOut15': 'f4',
    'DSPIDMessage.analogOut12': 'f4', 'sq1fb_r1_c14': 'i8',
    'DSPIDMessage.analogOut10': 'f4', 'DSPIDMessage.analogOut11': 'f4',
    'error_r14_c15': 'i8', 'error_r14_c12': 'i8',
    'AnalogOutMessage.analogOut25': 'f4', 'sq1fb_r1_c13': 'i8',
    'bettii.RTLowPriority.TimingRTPreviousTicks': 'i4', 'sq1fb_r1_c10': 'i8',
    'sq1fb_r1_c11': 'i8', 'AnalogOutMessage.analogOut24': 'f4',
    'bettii.RTHighPriority.StarCameraTriggerStatus': 'i4',
    'bettii.RTLowPriority.RawStarcameraDecDeg': 'f4',
    'TReadDiodeMessage.demod15': 'f4', 'TReadDiodeMessage.demod14': 'f4',
    'TReadDiodeMessage.demod11': 'f4', 'TReadDiodeMessage.demod10': 'f4',
    'TReadDiodeMessage.demod13': 'f4', 'TReadDiodeMessage.demod12': 'f4',
    'PiperThermo.Cal20kohm': 'f4', 'bettii.WheelsGalil.ttaInt': 'i4',
    'bettii.ThermometersDemuxedCelcius.J4L33': 'f4',
    'bettii.ThermometersDemuxedCelcius.J4L31': 'f4',
    'bettii.ThermometersDemuxedCelcius.J4L37': 'f4',
    'bettii.ThermometersDemuxedCelcius.J4L35': 'f4',
    'bettii.ThermometersDemuxedCelcius.J4L39': 'f4', 'fluxJump_r7_c19': 'i4',
    'fluxJump_r7_c18': 'i4', 'fluxJump_r7_c17': 'i4', 'fluxJump_r7_c16': 'i4',
    'fluxJump_r7_c15': 'i4', 'fluxJump_r7_c14': 'i4', 'fluxJump_r7_c13': 'i4',
    'fluxJump_r7_c12': 'i4', 'fluxJump_r7_c11': 'i4', 'fluxJump_r7_c10': 'i4',
    'bettii.RTLowPriority.TimingRTPlotSetpoints': 'i4',
    'bettii.TimingSensorsLoop.notifyRTMain': 'i4',
    'TReadStandardMessage.aDacRaw14': 'i4', 'sq1fb_r20_c8': 'i8',
    'sq1fb_r20_c9': 'i8', 'bettii.GpsReadings.secondUTC': 'f4', 'sq1fb_r20_c2':
    'i8', 'sq1fb_r20_c3': 'i8', 'sq1fb_r20_c1': 'i8', 'sq1fb_r20_c6': 'i8',
    'sq1fb_r20_c7': 'i8', 'sq1fb_r20_c4': 'i8', 'sq1fb_r20_c5': 'i8',
    'AnalogOutMessage.analogOut20': 'f4',
    'bettii.RTLowPriority.RawStarcameraMceFrameNumberWhenSCTriggered': 'i8',
    'sq1fb_r1_c18': 'i8', 'error_r14_c19': 'i8', 'error_r14_c16': 'i8',
    'error_r14_c17': 'i8', 'error_r14_c14': 'i8', 'sq1fb_r1_c15': 'i8',
    'sq1fb_r1_c12': 'i8', 'error_r14_c13': 'i8', 'error_r14_c10': 'i8',
    'error_r14_c11': 'i8', 'bettii.CommandedTipTilts.manuallyCommanded': 'u1',
    'bettii.ThermometersOutput.AI4': 'f4', 'error_r9_c3': 'i8', 'error_r9_c2':
    'i8', 'error_r9_c1': 'i8', 'error_r9_c7': 'i8', 'error_r9_c6': 'i8',
    'error_r9_c5': 'i8', 'error_r9_c4': 'i8', 'error_r9_c9': 'i8',
    'error_r9_c8': 'i8', 'MasterMessage.status': 'i4',
    'AnalogOutMessage.analogOut22': 'f4', 'fluxJump_r9_c19': 'i4',
    'fluxJump_r9_c18': 'i4', 'error_r9_c20': 'i8', 'error_r9_c21': 'i8',
    'fluxJump_r9_c11': 'i4', 'fluxJump_r9_c10': 'i4', 'fluxJump_r9_c13': 'i4',
    'fluxJump_r9_c12': 'i4', 'fluxJump_r9_c15': 'i4', 'fluxJump_r9_c14': 'i4',
    'fluxJump_r9_c17': 'i4', 'fluxJump_r9_c16': 'i4', 'fluxJump_r4_c10': 'i4',
    'fluxJump_r4_c11': 'i4', 'fluxJump_r4_c12': 'i4', 'fluxJump_r4_c13': 'i4',
    'fluxJump_r4_c14': 'i4', 'fluxJump_r4_c15': 'i4', 'fluxJump_r4_c16': 'i4',
    'fluxJump_r4_c17': 'i4', 'fluxJump_r4_c18': 'i4', 'fluxJump_r4_c19': 'i4',
    'bettii.RTLowPriority.TimingRTPropagateTrueSC': 'i4',
    'bettii.DelayLines.CDLvelTarget': 'f4', 'AnalogOutMessage.frameCounter':
    'i8', 'error_r15_c13': 'i8', 'error_r15_c12': 'i8', 'error_r15_c11': 'i8',
    'error_r15_c10': 'i8', 'error_r15_c17': 'i8', 'error_r15_c16': 'i8',
    'error_r15_c15': 'i8', 'error_r15_c14': 'i8', 'error_r15_c19': 'i8',
    'error_r15_c18': 'i8', 'AnalogOutMessage.analogOut29': 'f4',
    'bettii.DelayLines.WDLvelMeasurement': 'f4',
    'bettii.PIDInputCCMG.velocityTarget': 'f4', 'bettii.DelayLines.WDLintegral':
    'f4', 'bettii.MiscCriticals.mceFrameNumber': 'i8', 'DSPIDMessage.status':
    'i4', 'bettii.RTHighPriority.targetDEC': 'f8',
    'bettii.TipTilts.PiezoKSGSMONX': 'f4', 'bettii.TipTilts.PiezoKSGSMONY':
    'f4', 'fluxJump_r16_c12': 'i4', 'fluxJump_r16_c13': 'i4',
    'fluxJump_r16_c10': 'i4', 'fluxJump_r16_c11': 'i4', 'fluxJump_r16_c16':
    'i4', 'fluxJump_r16_c17': 'i4', 'fluxJump_r16_c14': 'i4',
    'fluxJump_r16_c15': 'i4', 'fluxJump_r16_c18': 'i4', 'fluxJump_r16_c19':
    'i4', 'bettii.GpsReadings.latitudeDegrees': 'f4', 'sq1fb_r15_c6': 'i8',
    'sq1fb_r15_c7': 'i8', 'fluxJump_r6_c21': 'i4', 'fluxJump_r6_c20': 'i4',
    'bettii.PIDOutputCCMG.mceFrameNumber': 'i8', 'TReadStandardMessage.gDac15':
    'i4', 'TReadStandardMessage.gDac14': 'i4', 'TReadStandardMessage.gDac13':
    'i4', 'TReadStandardMessage.gDac12': 'i4', 'TReadStandardMessage.gDac11':
    'i4', 'TReadStandardMessage.gDac10': 'i4', 'error_r4_c21': 'i8',
    'error_r4_c20': 'i8',
    'bettii.currentReadout.currentReadout_UPBTwo_12VChannel': 'f4',
    'fluxJump_r19_c19': 'i4', 'fluxJump_r19_c18': 'i4',
    'bettii.ThermometersDemuxedCelcius.J4L13': 'f4', 'fluxJump_r19_c11': 'i4',
    'fluxJump_r19_c10': 'i4', 'fluxJump_r19_c13': 'i4', 'fluxJump_r19_c12':
    'i4', 'fluxJump_r19_c15': 'i4', 'fluxJump_r19_c14': 'i4',
    'fluxJump_r19_c17': 'i4', 'fluxJump_r19_c16': 'i4', 'sq1fb_r15_c8': 'i8',
    'sq1fb_r15_c9': 'i8', 'java_native_messaging.StarCameraSolution.sigma_ra':
    'f8', 'AnalogInMessage.aDCRaw31': 'f4', 'AnalogInMessage.aDCRaw30': 'f4',
    'fluxJump_r2_c14': 'i4', 'sq1fb_r4_c21': 'i8',
    'TReadStandardMessage.frameCounter': 'i8', 'DSPIDMessage.analogOut4': 'f4',
    'DSPIDMessage.analogOut5': 'f4', 'DSPIDMessage.analogOut6': 'f4',
    'DSPIDMessage.analogOut7': 'f4', 'DSPIDMessage.analogOut0': 'f4',
    'DSPIDMessage.analogOut1': 'f4', 'DSPIDMessage.analogOut2': 'f4',
    'DSPIDMessage.analogOut3': 'f4', 'DSPIDMessage.analogOut8': 'f4',
    'DSPIDMessage.analogOut9': 'f4', 'bettii.GpsReadings.altitudeMeters': 'f4',
    'fluxJump_r20_c9': 'i4', 'fluxJump_r20_c8': 'i4', 'fluxJump_r20_c5': 'i4',
    'fluxJump_r20_c4': 'i4', 'fluxJump_r20_c7': 'i4', 'fluxJump_r20_c6': 'i4',
    'fluxJump_r20_c1': 'i4', 'fluxJump_r20_c3': 'i4', 'fluxJump_r20_c2': 'i4',
    'TReadStandardMessage.nsum': 'i4', 'sq1fb_r12_c9': 'i8', 'sq1fb_r12_c8':
    'i8', 'sq1fb_r12_c3': 'i8', 'sq1fb_r12_c2': 'i8', 'sq1fb_r12_c1': 'i8',
    'sq1fb_r12_c7': 'i8', 'sq1fb_r12_c6': 'i8', 'sq1fb_r12_c5': 'i8',
    'sq1fb_r12_c4': 'i8', 'bettii.ThermometersOutput.TimeReadingSamplesMs':
    'i4', 'TReadDiodeMessage.aDac5': 'f4',
    'bettii.ThermometersOutput.mceFrameNumber': 'i8', 'error_r14_c21': 'i8',
    'error_r14_c20': 'i8', 'error_r3_c15': 'i8', 'error_r6_c18': 'i8',
    'error_r6_c19': 'i8', 'sq1fb_r20_c20': 'i8', 'error_r6_c14': 'i8',
    'error_r6_c15': 'i8', 'error_r6_c16': 'i8', 'error_r6_c17': 'i8',
    'error_r6_c10': 'i8', 'error_r6_c11': 'i8', 'error_r6_c12': 'i8',
    'error_r6_c13': 'i8', 'bettii.TimingSensorsLoop.totalLoopTime': 'i4',
    'bettii.RTHighPriority.GondolaRaDeg': 'f8', 'error_r3_c19': 'i8',
    'fluxJump_r4_c21': 'i4', 'fluxJump_r4_c20': 'i4', 'error_r2_c15': 'i8',
    'DSPIDMessage.externalTemp': 'f4',
    'bettii.TimingApplyPIDLoop.writeToIndicator': 'i4',
    'bettii.DelayLines.WDLposTarget': 'f4',
    'bettii.ThermometersDemuxedCelcius.J1L38': 'f4', 'error_r14_c8': 'i8',
    'error_r14_c9': 'i8', 'error_r14_c4': 'i8', 'error_r14_c5': 'i8',
    'error_r14_c6': 'i8', 'error_r14_c7': 'i8', 'error_r14_c1': 'i8',
    'error_r14_c2': 'i8', 'error_r14_c3': 'i8', 'fluxJump_r20_c20': 'i4',
    'fluxJump_r20_c21': 'i4', 'bettii.RTLowPriority.TimingRTPlotGyroVelocities':
    'i4', 'bettii.AngleSensorOutput.WDLXOffsetPixels': 'f4', 'error_r2_c18':
    'i8', 'DSPIDMessage.coilDAC3': 'f4', 'DSPIDMessage.coilDAC2': 'f4',
    'DSPIDMessage.coilDAC1': 'f4', 'DSPIDMessage.coilDAC0': 'f4',
    'DSPIDMessage.coilDAC7': 'f4', 'DSPIDMessage.coilDAC6': 'f4',
    'DSPIDMessage.coilDAC5': 'f4', 'DSPIDMessage.coilDAC4': 'f4',
    'DSPIDMessage.coilDAC9': 'f4', 'DSPIDMessage.coilDAC8': 'f4',
    'error_r16_c21': 'i8', 'error_r16_c20': 'i8', 'sq1fb_r19_c10': 'i8',
    'sq1fb_r19_c11': 'i8', 'error_r2_c19': 'i8', 'sq1fb_r19_c12': 'i8',
    'sq1fb_r19_c13': 'i8', 'sq1fb_r19_c14': 'i8', 'error_r18_c1': 'i8',
    'error_r18_c2': 'i8', 'error_r18_c3': 'i8', 'error_r18_c4': 'i8',
    'error_r7_c3': 'i8', 'error_r18_c6': 'i8', 'error_r18_c7': 'i8',
    'error_r18_c8': 'i8', 'error_r18_c9': 'i8', 'sq1fb_r19_c17': 'i8',
    'bettii.PIDInputMomDump.mceFrameNumber': 'i8', 'error_r17_c19': 'i8',
    'error_r17_c18': 'i8', 'bettii.TimingSensorsLoop.writeStarcamOptions': 'i4',
    'bettii.ThermometersDemuxedCelcius.J2L17': 'f4', 'error_r17_c11': 'i8',
    'error_r17_c10': 'i8', 'error_r17_c13': 'i8', 'error_r17_c12': 'i8',
    'error_r17_c15': 'i8', 'error_r17_c14': 'i8', 'error_r17_c17': 'i8',
    'error_r17_c16': 'i8', 'error_r4_c11': 'i8', 'DSPIDMessage.boardTempRaw':
    'i4', 'fluxJump_r10_c18': 'i4', 'fluxJump_r15_c18': 'i4',
    'fluxJump_r10_c14': 'i4', 'fluxJump_r15_c14': 'i4', 'fluxJump_r10_c16':
    'i4', 'fluxJump_r15_c16': 'i4', 'fluxJump_r10_c10': 'i4',
    'fluxJump_r15_c10': 'i4', 'fluxJump_r10_c12': 'i4', 'fluxJump_r15_c12':
    'i4', 'bettii.WheelsGalil.ttbInt': 'i4', 'error_r3_c3': 'i8',
    'error_r11_c21': 'i8', 'sq1fb_r18_c19': 'i8', 'sq1fb_r18_c18': 'i8',
    'sq1fb_r18_c15': 'i8', 'sq1fb_r18_c14': 'i8', 'sq1fb_r18_c17': 'i8',
    'sq1fb_r18_c16': 'i8', 'sq1fb_r18_c11': 'i8', 'sq1fb_r18_c10': 'i8',
    'sq1fb_r18_c13': 'i8', 'sq1fb_r18_c12': 'i8', 'error_r5_c13': 'i8',
    'error_r5_c12': 'i8', 'error_r5_c11': 'i8', 'error_r5_c10': 'i8',
    'error_r4_c12': 'i8', 'error_r4_c13': 'i8', 'error_r4_c10': 'i8',
    'error_r5_c14': 'i8', 'error_r5_c19': 'i8', 'error_r5_c18': 'i8',
    'error_r4_c18': 'i8', 'error_r4_c19': 'i8',
    'TReadStandardMessage.temperature5': 'f4',
    'TReadStandardMessage.temperature4': 'f4',
    'TReadStandardMessage.temperature7': 'f4', 'bettii.ThermometersOutput.DO0':
    'u1', 'TReadStandardMessage.temperature1': 'f4',
    'bettii.ThermometersOutput.DO6': 'u1', 'bettii.ThermometersOutput.DO5':
    'u1', 'TReadStandardMessage.temperature2': 'f4',
    'TReadStandardMessage.temperature9': 'f4',
    'TReadStandardMessage.temperature8': 'f4', 'PiperThermo.H1RG': 'f4',
    'TReadDiodeMessage.address': 'i4', 'DSPIDMessage.boardTemp': 'f4',
    'fluxJump_r18_c21': 'i4', 'fluxJump_r18_c20': 'i4', 'sq1fb_r13_c18': 'i8',
    'sq1fb_r13_c19': 'i8', 'bettii.ThermometersOutput.Mod3AI0': 'i4',
    'bettii.ThermometersOutput.Mod3AI2': 'i4', 'sq1fb_r13_c12': 'i8',
    'sq1fb_r13_c13': 'i8', 'sq1fb_r13_c10': 'i8', 'sq1fb_r13_c11': 'i8',
    'sq1fb_r13_c16': 'i8', 'sq1fb_r13_c17': 'i8', 'sq1fb_r13_c14': 'i8',
    'sq1fb_r13_c15': 'i8', 'bettii.PIDOutputCCMG.integral': 'f4',
    'AnalogOutMessage.analogOut14': 'f4', 'AnalogOutMessage.analogOut15': 'f4',
    'AnalogOutMessage.analogOut16': 'f4', 'AnalogOutMessage.analogOut17': 'f4',
    'AnalogOutMessage.analogOut11': 'f4', 'AnalogOutMessage.analogOut12': 'f4',
    'bettii.AngleSensorOutput.mceFrameNumber': 'i8',
    'AnalogOutMessage.analogOut13': 'f4', 'error_r7_c20': 'i8', 'error_r7_c21':
    'i8', 'PiperThermo.LN2Tank': 'f4', 'AnalogOutMessage.analogOut18': 'f4',
    'AnalogOutMessage.analogOut19': 'f4', 'bettii.Magnetometer.mceFrameNumber':
    'i8', 'TReadDiodeMessage.aDac11': 'f4', 'TReadDiodeMessage.aDac12': 'f4',
    'TReadDiodeMessage.aDac13': 'f4', 'sq1fb_r21_c20': 'i8', 'sq1fb_r21_c21':
    'i8', 'DSPIDMessage.coilDACRaw14': 'i4', 'bettii.StepperGalil.wheelsAngle':
    'f4', 'bettii.currentReadout.currentReadout_UPBOne_36VChannel': 'f4',
    'bettii.PIDInputMomDump.positionTarget': 'f4', 'fluxJump_r21_c14': 'i4',
    'fluxJump_r21_c15': 'i4', 'fluxJump_r21_c16': 'i4', 'fluxJump_r21_c17':
    'i4', 'fluxJump_r21_c10': 'i4', 'fluxJump_r21_c11': 'i4',
    'fluxJump_r21_c12': 'i4', 'fluxJump_r21_c13': 'i4', 'fluxJump_r21_c18':
    'i4', 'fluxJump_r21_c19': 'i4', 'bettii.PIDInputCCMG.mceFrameNumber': 'i8',
    'DSPIDMessage.analogIn': 'f4',
    'java_native_messaging.StarCameraAuxiliarySolution.ra_deg': 'f8',
    'sq1fb_r2_c10': 'i8', 'java_native_messaging.StarCameraSolution.roll_deg':
    'f8', 'bettii.WheelsGalil.ttaDec': 'i4',
    'bettii.ThermometersDemuxedCelcius.J1L26': 'f4',
    'bettii.ThermometersDemuxedCelcius.J1L24': 'f4',
    'bettii.ThermometersDemuxedCelcius.J1L22': 'f4',
    'bettii.ThermometersDemuxedCelcius.J1L20': 'f4',
    'bettii.ThermometersDemuxedCelcius.J4L3': 'f4',
    'bettii.ThermometersDemuxedCelcius.J1L28': 'f4', 'sq1fb_r2_c13': 'i8',
    'sq1fb_r10_c15': 'i8', 'sq1fb_r10_c14': 'i8', 'sq1fb_r10_c17': 'i8',
    'sq1fb_r10_c16': 'i8', 'sq1fb_r10_c11': 'i8', 'sq1fb_r10_c10': 'i8',
    'sq1fb_r10_c13': 'i8', 'sq1fb_r10_c12': 'i8', 'sq1fb_r10_c19': 'i8',
    'sq1fb_r10_c18': 'i8', 'bettii.DelayLines.CDLrawV': 'f4', 'sq1fb_r19_c8':
    'i8', 'sq1fb_r19_c9': 'i8', 'sq1fb_r19_c2': 'i8', 'sq1fb_r19_c3': 'i8',
    'sq1fb_r19_c1': 'i8', 'sq1fb_r19_c6': 'i8', 'sq1fb_r19_c7': 'i8',
    'sq1fb_r19_c4': 'i8', 'sq1fb_r19_c5': 'i8',
    'bettii.Magnetometer.MagnetometerID': 'i4',
    'bettii.currentReadout.voltageReadout_UPBTwo_5VChannel': 'f4',
    'AnalogInMessage.samplesPerChannel': 'i4', 'PiperThermo.Exchanger': 'f4',
    'bettii.Magnetometer.mceFrameNumberWhenMeasured': 'i8',
    'bettii.RTLowPriority.RawStarcameraExpTime': 'i4',
    'bettii.RTLowPriority.covarianceMatrix15': 'f8',
    'bettii.RTLowPriority.covarianceMatrix14': 'f8',
    'bettii.RTLowPriority.covarianceMatrix13': 'f8',
    'bettii.RTLowPriority.covarianceMatrix12': 'f8',
    'bettii.RTLowPriority.covarianceMatrix11': 'f8',
    'bettii.RTLowPriority.covarianceMatrix10': 'f8',
    'bettii.ThermometersOutput.TimeEnergizersUpMs': 'i4', 'error_r5_c20': 'i8',
    'error_r5_c21': 'i8', 'bettii.StateVector.var_xEl': 'f4', 'sq1fb_r20_c21':
    'i8', 'error_r3_c14': 'i8', 'error_r3_c17': 'i8', 'error_r3_c16': 'i8',
    'error_r3_c11': 'i8', 'error_r3_c10': 'i8', 'error_r3_c13': 'i8',
    'error_r3_c12': 'i8', 'error_r2_c10': 'i8', 'error_r2_c11': 'i8',
    'error_r2_c12': 'i8', 'error_r2_c13': 'i8', 'error_r2_c14': 'i8',
    'error_r3_c18': 'i8', 'error_r2_c16': 'i8', 'error_r2_c17': 'i8',
    'sq1fb_r2_c12': 'i8', 'sq1fb_r17_c12': 'i8',
    'bettii.currentReadout.currentReadout_UPBTwo_36VChannel': 'f4',
    'sq1fb_r17_c13': 'i8', 'sq1fb_r10_c5': 'i8', 'sq1fb_r10_c4': 'i8',
    'sq1fb_r10_c7': 'i8', 'sq1fb_r10_c6': 'i8', 'sq1fb_r10_c1': 'i8',
    'sq1fb_r17_c10': 'i8', 'sq1fb_r10_c3': 'i8', 'sq1fb_r10_c2': 'i8',
    'sq1fb_r17_c11': 'i8', 'sq1fb_r10_c9': 'i8', 'sq1fb_r10_c8': 'i8',
    'bettii.DelayLines.WDLloopIteration2': 'i4', 'sq1fb_r13_c21': 'i8',
    'sq1fb_r13_c20': 'i8', 'error_r12_c18': 'i8',
    'bettii.RTHighPriority.EstimatorErrorRespectLastSCAzArcsec': 'f8',
    'error_r12_c19': 'i8', 'fluxJump_r7_c20': 'i4', 'fluxJump_r7_c21': 'i4',
    'bettii.RTLowPriority.GriffinAAngleDegrees': 'f8',
    'bettii.ThermometersCCMG.mod4AI0': 'f4', 'error_r19_c20': 'i8',
    'error_r19_c21': 'i8', 'bettii.GpsReadings.hourUTC': 'i4',
    'fluxJump_r12_c18': 'i4', 'fluxJump_r12_c19': 'i4',
    'TReadStandardMessage.address': 'i4', 'DSPIDMessage.latestMceFrameNumber':
    'i8', 'bettii.RTHighPriority.Elevation': 'f8',
    'bettii.currentReadout.mceFrameNumber': 'i8', 'sq1fb_r16_c20': 'i8',
    'sq1fb_r16_c21': 'i8', 'sq1fb_r14_c9': 'i8', 'sq1fb_r14_c8': 'i8',
    'fluxJump_r21_c1': 'i4', 'fluxJump_r21_c6': 'i4', 'fluxJump_r21_c7': 'i4',
    'fluxJump_r21_c4': 'i4', 'fluxJump_r21_c5': 'i4', 'sq1fb_r14_c1': 'i8',
    'sq1fb_r14_c3': 'i8', 'sq1fb_r14_c2': 'i8', 'sq1fb_r14_c5': 'i8',
    'sq1fb_r14_c4': 'i8', 'sq1fb_r14_c7': 'i8', 'sq1fb_r14_c6': 'i8',
    'bettii.RTHighPriority.mceFrameNumber': 'i8', 'sq1fb_r11_c21': 'i8',
    'sq1fb_r11_c20': 'i8', 'bettii.RTLowPriority.qk': 'f8',
    'bettii.RTLowPriority.qj': 'f8', 'bettii.RTLowPriority.qi': 'f8',
    'bettii.RTLowPriority.TimingRTSendToAurora': 'i4', 'PiperThermo.4HeSwitch':
    'f4', 'bettii.RTLowPriority.SlewParametersDeccelerationPhaseStarted': 'u1',
    'bettii.ThermometersDemuxedCelcius.J1L50': 'f4',
    'bettii.RTLowPriority.RawStarcameraRollError': 'f4',
    'AnalogInMessage.aDC29': 'f4', 'AnalogInMessage.aDC28': 'f4',
    'AnalogInMessage.aDC25': 'f4', 'AnalogInMessage.aDC24': 'f4',
    'AnalogInMessage.aDC27': 'f4', 'AnalogInMessage.aDC26': 'f4',
    'AnalogInMessage.aDC21': 'f4', 'AnalogInMessage.aDC20': 'f4',
    'AnalogInMessage.aDC23': 'f4', 'AnalogInMessage.aDC22': 'f4',
    'bettii.ThermometersDemuxedCelcius.J2L9': 'f4', 'bettii.PIDOutputCCMG.et':
    'f4', 'bettii.ThermometersDemuxedCelcius.J2L7': 'f4',
    'bettii.ThermometersDemuxedCelcius.J2L1': 'f4',
    'bettii.ThermometersDemuxedCelcius.J2L3': 'f4',
    'bettii.RTHighPriority.EstimatedAzimuthVelocityArcsec': 'f8',
    'DSPIDMessage.coilVMon': 'f4', 'sq1fb_r3_c14': 'i8', 'sq1fb_r3_c15': 'i8',
    'sq1fb_r3_c16': 'i8', 'sq1fb_r3_c17': 'i8', 'sq1fb_r3_c10': 'i8',
    'sq1fb_r3_c11': 'i8', 'sq1fb_r3_c12': 'i8', 'sq1fb_r3_c13': 'i8',
    'sq1fb_r3_c18': 'i8', 'sq1fb_r3_c19': 'i8', 'AnalogInMessage.aDCRaw4': 'f4',
    'TReadDiodeMessage.demod5': 'f4', 'TReadDiodeMessage.demod4': 'f4',
    'TReadDiodeMessage.demod7': 'f4', 'TReadDiodeMessage.demod6': 'f4',
    'TReadDiodeMessage.demod1': 'f4', 'TReadDiodeMessage.demod0': 'f4',
    'TReadDiodeMessage.demod3': 'f4', 'TReadDiodeMessage.demod2': 'f4',
    'TReadDiodeMessage.demod9': 'f4', 'TReadDiodeMessage.demod8': 'f4',
    'DSPIDMessage.demodRaw9': 'i4', 'TReadStandardMessage.demod4': 'f4',
    'error_r5_c17': 'i8', 'TReadStandardMessage.demod6': 'f4',
    'TReadStandardMessage.demod7': 'f4', 'TReadStandardMessage.demod0': 'f4',
    'TReadStandardMessage.demod1': 'f4', 'TReadStandardMessage.demod2': 'f4',
    'TReadStandardMessage.demod3': 'f4', 'TReadStandardMessage.demod8': 'f4',
    'TReadStandardMessage.demod9': 'f4', 'bettii.Magnetometer.MagneticFieldY':
    'i4', 'bettii.Magnetometer.MagneticFieldX': 'i4',
    'bettii.Magnetometer.MagneticFieldZ': 'i4',
    'bettii.ThermometersDemuxedCelcius.J3L30': 'f4',
    'bettii.ThermometersDemuxedCelcius.J3L8': 'f4', 'fluxJump_r17_c3': 'i4',
    'fluxJump_r17_c2': 'i4', 'fluxJump_r6_c18': 'i4', 'fluxJump_r6_c19': 'i4',
    'fluxJump_r17_c7': 'i4', 'fluxJump_r17_c6': 'i4', 'fluxJump_r17_c5': 'i4',
    'fluxJump_r17_c4': 'i4', 'fluxJump_r6_c12': 'i4', 'fluxJump_r6_c13': 'i4',
    'fluxJump_r6_c10': 'i4', 'fluxJump_r6_c11': 'i4', 'fluxJump_r6_c16': 'i4',
    'fluxJump_r6_c17': 'i4', 'fluxJump_r6_c14': 'i4', 'fluxJump_r6_c15': 'i4',
    'fluxJump_r13_c7': 'i4', 'fluxJump_r13_c6': 'i4', 'fluxJump_r13_c5': 'i4',
    'fluxJump_r13_c4': 'i4', 'fluxJump_r13_c3': 'i4', 'fluxJump_r13_c2': 'i4',
    'fluxJump_r13_c1': 'i4', 'bettii.RTLowPriority.covarianceMatrix03': 'f8',
    'bettii.Magnetometer.QuaternionFXPqi': 'f4', 'fluxJump_r13_c9': 'i4',
    'fluxJump_r13_c8': 'i4', 'fluxJump_r8_c6': 'i4', 'fluxJump_r21_c2': 'i4',
    'sq1fb_r9_c6': 'i8', 'sq1fb_r9_c7': 'i8', 'fluxJump_r8_c2': 'i4',
    'fluxJump_r8_c3': 'i4', 'sq1fb_r9_c2': 'i8', 'fluxJump_r21_c3': 'i4',
    'sq1fb_r9_c8': 'i8', 'sq1fb_r9_c9': 'i8', 'fluxJump_r8_c8': 'i4',
    'fluxJump_r8_c9': 'i4', 'bettii.ThermometersDemuxedCelcius.J3L2': 'f4',
    'fluxJump_r15_c1': 'i4', 'fluxJump_r15_c3': 'i4', 'fluxJump_r15_c2': 'i4',
    'fluxJump_r15_c5': 'i4', 'fluxJump_r15_c4': 'i4', 'fluxJump_r15_c7': 'i4',
    'fluxJump_r15_c6': 'i4', 'fluxJump_r15_c9': 'i4', 'fluxJump_r15_c8': 'i4',
    'bettii.RTLowPriority.SlewParametersAccelarcsecss': 'i4',
    'bettii.currentReadout.currentReadout_UPBOne_15VChannel': 'f4',
    'fluxJump_r21_c8': 'i4', 'fluxJump_r21_c9': 'i4',
    'bettii.ThermometersDemuxedCelcius.J3L4': 'f4',
    'bettii.TimingSensorsLoop.readGyroStarcamTipTilts': 'i4',
    'bettii.RTHighPriority.crossElevation': 'f8', 'sq1fb_r1_c8': 'i8',
    'sq1fb_r1_c9': 'i8', 'sq1fb_r1_c4': 'i8', 'sq1fb_r1_c5': 'i8',
    'sq1fb_r1_c6': 'i8', 'sq1fb_r1_c7': 'i8', 'bettii.TipTilts.PiezoKVMON3':
    'f4', 'sq1fb_r1_c1': 'i8', 'sq1fb_r1_c2': 'i8', 'sq1fb_r1_c3': 'i8',
    'bettii.RTLowPriority.SlewParametersAzTargetInitial': 'f4',
    'bettii.ThermometersDemuxedCelcius.J3L6': 'f4',
    'bettii.AngleSensorOutput.mceFrameNumberWhenTriggered': 'i8',
    'fluxJump_r19_c9': 'i4', 'fluxJump_r19_c8': 'i4', 'fluxJump_r19_c5': 'i4',
    'fluxJump_r19_c4': 'i4', 'fluxJump_r19_c7': 'i4', 'fluxJump_r19_c6': 'i4',
    'fluxJump_r19_c1': 'i4', 'DSPIDMessage.demod14': 'f4', 'fluxJump_r19_c3':
    'i4', 'fluxJump_r19_c2': 'i4', 'TReadDiodeMessage.gDac5': 'i4',
    'sq1fb_r5_c21': 'i8', 'sq1fb_r5_c20': 'i8',
    'bettii.DelayLines.CDLposTarget': 'f4', 'bettii.GpsReadings.minuteUTC':
    'i4', 'bettii.RTLowPriority.SlewParametersDecceleration': 'f4',
    'bettii.TipTilts.PiezoKVMONY': 'f4', 'bettii.TipTilts.PiezoKVMONX': 'f4',
    'TReadDiodeMessage.gDac3': 'i4', 'TReadDiodeMessage.aDacRaw15': 'i4',
    'DSPIDMessage.pidError': 'i4', 'error_r19_c19': 'i8', 'error_r19_c18': 'i8',
    'error_r19_c17': 'i8', 'error_r19_c16': 'i8', 'error_r19_c15': 'i8',
    'error_r19_c14': 'i8', 'error_r19_c13': 'i8', 'error_r19_c12': 'i8',
    'error_r19_c11': 'i8', 'error_r19_c10': 'i8', 'fluxJump_r11_c5': 'i4',
    'fluxJump_r11_c4': 'i4', 'fluxJump_r11_c7': 'i4', 'fluxJump_r11_c6': 'i4',
    'fluxJump_r11_c1': 'i4', 'fluxJump_r11_c3': 'i4', 'fluxJump_r11_c2': 'i4',
    'fluxJump_r11_c9': 'i4', 'fluxJump_r11_c8': 'i4', 'sq1fb_r16_c19': 'i8',
    'sq1fb_r16_c18': 'i8', 'AnalogOutMessage.status': 'i4', 'sq1fb_r16_c13':
    'i8', 'sq1fb_r16_c12': 'i8', 'sq1fb_r16_c11': 'i8', 'sq1fb_r16_c10': 'i8',
    'sq1fb_r16_c17': 'i8', 'sq1fb_r16_c16': 'i8', 'sq1fb_r16_c15': 'i8',
    'sq1fb_r16_c14': 'i8', 'TReadDiodeMessage.aDacRaw13': 'i4', 'error_r6_c21':
    'i8', 'error_r6_c20': 'i8', 'bettii.TimingSensorsLoop.mceFrameNumber': 'i8',
    'bettii.TimingSensorsLoop.previousTicks': 'i4', 'rampValue': 'i4',
    'bettii.RTLowPriority.qr': 'f8', 'bettii.Magnetometer.QuaternionFXPqj':
    'f4', 'sq1fb_r3_c2': 'i8', 'sq1fb_r3_c3': 'i8', 'sq1fb_r3_c1': 'i8',
    'sq1fb_r3_c6': 'i8', 'sq1fb_r3_c7': 'i8', 'sq1fb_r3_c4': 'i8',
    'sq1fb_r3_c5': 'i8', 'bettii.WheelsGalil.tvb': 'i4', 'sq1fb_r3_c8': 'i8',
    'sq1fb_r3_c9': 'i8', 'bettii.ThermometersDemuxedCelcius.J1L40': 'f4',
    'fluxJump_r13_c19': 'i4', 'fluxJump_r13_c18': 'i4', 'sq1fb_r21_c9': 'i8',
    'sq1fb_r21_c8': 'i8', 'bettii.ThermometersDemuxedCelcius.J1L46': 'f4',
    'fluxJump_r13_c13': 'i4', 'fluxJump_r13_c12': 'i4', 'fluxJump_r13_c11':
    'i4', 'fluxJump_r13_c10': 'i4', 'fluxJump_r13_c17': 'i4',
    'fluxJump_r13_c16': 'i4', 'fluxJump_r13_c15': 'i4', 'fluxJump_r13_c14':
    'i4', 'bettii.PIDInputCCMG.positionMeasurement': 'f4',
    'AnalogInMessage.aDC30': 'f4', 'AnalogInMessage.aDC31': 'f4',
    'bettii.MiscCriticals.chassisTemperatureCelsius': 'f4', 'fluxJump_r20_c19':
    'i4', 'fluxJump_r20_c18': 'i4', 'fluxJump_r20_c11': 'i4',
    'fluxJump_r20_c10': 'i4', 'fluxJump_r20_c13': 'i4', 'fluxJump_r20_c12':
    'i4', 'fluxJump_r20_c15': 'i4', 'fluxJump_r20_c14': 'i4',
    'fluxJump_r20_c17': 'i4', 'fluxJump_r20_c16': 'i4', 'error_r16_c14': 'i8',
    'error_r16_c15': 'i8', 'error_r16_c16': 'i8', 'error_r16_c17': 'i8',
    'error_r16_c10': 'i8', 'error_r16_c11': 'i8', 'error_r16_c12': 'i8',
    'error_r16_c13': 'i8', 'bettii.ThermometersDemuxedCelcius.J2L27': 'f4',
    'MasterMessage.pICFrameCount': 'i8', 'error_r16_c18': 'i8', 'error_r16_c19':
    'i8', 'bettii.ThermometersDemuxedCelcius.J2L21': 'f4', 'sq1fb_r19_c21':
    'i8', 'sq1fb_r19_c20': 'i8', 'error_r17_c20': 'i8', 'error_r17_c21': 'i8',
    'bettii.RTLowPriority.covarianceMatrix25': 'f8',
    'bettii.RTLowPriority.covarianceMatrix22': 'f8', 'fluxJump_r5_c19': 'i4',
    'bettii.RTLowPriority.covarianceMatrix23': 'f8', 'sq1fb_r18_c9': 'i8',
    'sq1fb_r18_c8': 'i8', 'sq1fb_r18_c5': 'i8', 'sq1fb_r18_c4': 'i8',
    'sq1fb_r18_c7': 'i8', 'sq1fb_r18_c6': 'i8', 'sq1fb_r18_c1': 'i8',
    'sq1fb_r18_c3': 'i8', 'sq1fb_r18_c2': 'i8',
    'bettii.RTLowPriority.TimingRTEKFPropagate': 'i4', 'fluxJump_r5_c18': 'i4',
    'sq1fb_r11_c2': 'i8', 'sq1fb_r11_c3': 'i8',
    'bettii.RTLowPriority.covarianceMatrix33': 'f8', 'sq1fb_r11_c1': 'i8',
    'fluxJump_r10_c21': 'i4', 'fluxJump_r10_c20': 'i4', 'sq1fb_r7_c8': 'i8',
    'sq1fb_r7_c9': 'i8', 'sq1fb_r7_c6': 'i8', 'sq1fb_r7_c7': 'i8',
    'sq1fb_r11_c8': 'i8', 'sq1fb_r11_c9': 'i8', 'sq1fb_r7_c2': 'i8',
    'sq1fb_r7_c3': 'i8', 'sq1fb_r7_c1': 'i8', 'sq1fb_r18_c20': 'i8',
    'sq1fb_r18_c21': 'i8', 'fluxJump_r11_c20': 'i4', 'fluxJump_r11_c21': 'i4',
    'fluxJump_r1_c20': 'i4', 'fluxJump_r1_c21': 'i4', 'sq1fb_r2_c20': 'i8',
    'sq1fb_r2_c21': 'i8', 'bettii.RTHighPriority.CCMGStepperSpeedManualValue':
    'i4', 'TReadDiodeMessage.latestMceFrameNumber': 'i8', 'fluxJump_r1_c11':
    'i4', 'fluxJump_r1_c10': 'i4', 'bettii.RTHighPriority.estimatedBiasYarcsec':
    'f8', 'fluxJump_r1_c13': 'i4', 'fluxJump_r1_c12': 'i4', 'fluxJump_r1_c15':
    'i4', 'java_native_messaging.StarCameraAuxiliarySolution.serial_number':
    'i4', 'fluxJump_r1_c14': 'i4', 'fluxJump_r1_c16': 'i4',
    'bettii.TimingSensorsLoop.betweenLoops': 'i4', 'bettii.PIDOutputMomDump.et':
    'f4', 'sq1fb_r5_c18': 'i8', 'sq1fb_r5_c19': 'i8', 'sq1fb_r5_c12': 'i8',
    'sq1fb_r5_c13': 'i8', 'sq1fb_r5_c10': 'i8', 'sq1fb_r5_c11': 'i8',
    'sq1fb_r5_c16': 'i8', 'sq1fb_r5_c17': 'i8', 'sq1fb_r5_c14': 'i8',
    'sq1fb_r5_c15': 'i8', 'fluxJump_r15_c20': 'i4', 'fluxJump_r15_c21': 'i4',
    'error_r7_c19': 'i8', 'error_r7_c18': 'i8', 'sq1fb_r15_c4': 'i8',
    'sq1fb_r15_c5': 'i8', 'sq1fb_r15_c2': 'i8', 'sq1fb_r15_c3': 'i8',
    'sq1fb_r15_c1': 'i8', 'error_r7_c11': 'i8', 'error_r7_c10': 'i8',
    'error_r7_c13': 'i8', 'error_r7_c12': 'i8', 'error_r7_c15': 'i8',
    'error_r7_c14': 'i8', 'error_r7_c17': 'i8', 'error_r7_c16': 'i8',
    'bettii.Magnetometer.PitchDeg': 'f4', 'DSPIDMessage.externalTempRaw': 'i4',
    'bettii.RTHighPriority.EstimatedRollVelocityArcsec': 'f8',
    'bettii.ThermometersOutput.NumOfSamples': 'i4',
    'bettii.ThermometersDemuxedCelcius.mceFrameNumber': 'i8',
    'bettii.RTHighPriority.TimingRTLoopDuration': 'i4',
    'bettii.TipTilts.mceFrameNumber': 'i8', 'fluxJump_r21_c21': 'i4',
    'fluxJump_r21_c20': 'i4', 'error_r4_c4': 'i8', 'error_r4_c5': 'i8',
    'error_r4_c6': 'i8', 'error_r4_c7': 'i8', 'AnalogOutMessage.analogOut10':
    'f4', 'error_r4_c1': 'i8', 'error_r4_c2': 'i8', 'error_r4_c3': 'i8',
    'error_r4_c8': 'i8', 'error_r4_c9': 'i8',
    'bettii.ThermometersDemuxedCelcius.J2L5': 'f4',
    'TReadStandardMessage.demodRaw15': 'i4', 'TReadStandardMessage.demodRaw14':
    'i4', 'TReadStandardMessage.demodRaw11': 'i4',
    'TReadStandardMessage.demodRaw10': 'i4', 'TReadStandardMessage.demodRaw13':
    'i4', 'TReadStandardMessage.demodRaw12': 'i4',
    'TReadStandardMessage.demodRaw1': 'i4', 'TReadStandardMessage.demodRaw0':
    'i4', 'TReadStandardMessage.demodRaw3': 'i4',
    'TReadStandardMessage.demodRaw2': 'i4', 'TReadStandardMessage.demodRaw5':
    'i4', 'TReadStandardMessage.demodRaw4': 'i4',
    'TReadStandardMessage.demodRaw7': 'i4', 'TReadStandardMessage.demodRaw6':
    'i4', 'TReadStandardMessage.demodRaw9': 'i4',
    'TReadStandardMessage.demodRaw8': 'i4', 'fluxJump_r13_c20': 'i4',
    'fluxJump_r13_c21': 'i4', 'TReadStandardMessage.temperature15': 'f4',
    'TReadStandardMessage.temperature14': 'f4',
    'TReadStandardMessage.temperature11': 'f4',
    'TReadStandardMessage.temperature10': 'f4',
    'TReadStandardMessage.temperature13': 'f4', 'bettii.DelayLines.CDLintegral':
    'f4', 'bettii.ThermometersDemuxedCelcius.J2L39': 'f4',
    'bettii.ThermometersDemuxedCelcius.J2L35': 'f4',
    'bettii.ThermometersDemuxedCelcius.J2L37': 'f4',
    'bettii.ThermometersDemuxedCelcius.J2L31': 'f4',
    'bettii.ThermometersDemuxedCelcius.J2L33': 'f4',
    'bettii.ThermometersDemuxedCelcius.J3L38': 'f4',
    'bettii.ThermometersDemuxedCelcius.J3L36': 'f4',
    'bettii.ThermometersDemuxedCelcius.J3L34': 'f4',
    'bettii.ThermometersDemuxedCelcius.J3L32': 'f4', 'DSPIDMessage.gndRaw':
    'i4', 'sq1fb_r8_c9': 'i8', 'sq1fb_r8_c8': 'i8', 'sq1fb_r8_c7': 'i8',
    'sq1fb_r8_c6': 'i8', 'sq1fb_r8_c5': 'i8', 'sq1fb_r8_c4': 'i8',
    'sq1fb_r8_c3': 'i8', 'sq1fb_r8_c2': 'i8', 'sq1fb_r8_c1': 'i8',
    'TReadStandardMessage.demod14': 'f4', 'TReadStandardMessage.demod15': 'f4',
    'TReadStandardMessage.demod12': 'f4', 'TReadStandardMessage.demod13': 'f4',
    'TReadStandardMessage.demod10': 'f4', 'TReadStandardMessage.demod11': 'f4',
    'bettii.DelayLines.CDLet': 'f4', 'bettii.DelayLines.WDLvelTarget': 'f4',
    'bettii.PIDOutputCCMG.ut': 'f4', 'sq1fb_r10_c20': 'i8', 'sq1fb_r10_c21':
    'i8', 'PiperThermo.4HePump': 'f4', 'error_r6_c8': 'i8', 'error_r6_c9': 'i8',
    'error_r6_c2': 'i8', 'error_r6_c3': 'i8',
    'bettii.RTLowPriority.covarianceMatrix24': 'f8', 'error_r6_c1': 'i8',
    'error_r6_c6': 'i8', 'error_r6_c7': 'i8', 'error_r6_c4': 'i8',
    'error_r6_c5': 'i8', 'AnalogOutMessage.latestMceFrameNumber': 'i8',
    'bettii.DelayLines.mceFrameNumber': 'i8', 'error_r2_c6': 'i8',
    'error_r2_c7': 'i8', 'error_r2_c4': 'i8', 'error_r2_c5': 'i8',
    'error_r2_c2': 'i8', 'error_r2_c3': 'i8', 'fluxJump_r1_c17': 'i4',
    'error_r2_c1': 'i8', 'fluxJump_r1_c19': 'i4', 'fluxJump_r1_c18': 'i4',
    'error_r2_c8': 'i8', 'error_r2_c9': 'i8', 'error_r2_c21': 'i8',
    'error_r2_c20': 'i8',
    'bettii.currentReadout.currentReadout_UPBOne_5VChannel': 'f4',
    'bettii.DelayLines.WDLposMeasurement': 'f4', 'fluxJump_r16_c8': 'i4',
    'fluxJump_r16_c9': 'i4', 'fluxJump_r16_c1': 'i4', 'fluxJump_r16_c2': 'i4',
    'fluxJump_r16_c3': 'i4', 'fluxJump_r16_c4': 'i4', 'fluxJump_r16_c5': 'i4',
    'fluxJump_r16_c6': 'i4', 'fluxJump_r16_c7': 'i4', 'bettii.WheelsGalil.teb':
    'i4', 'bettii.WheelsGalil.tea': 'i4', 'fluxJump_r12_c8': 'i4',
    'fluxJump_r12_c9': 'i4', 'bettii.StateVector.bias_xEl': 'f4',
    'fluxJump_r12_c4': 'i4', 'fluxJump_r12_c5': 'i4', 'fluxJump_r12_c6': 'i4',
    'fluxJump_r12_c7': 'i4', 'fluxJump_r12_c1': 'i4', 'fluxJump_r12_c2': 'i4',
    'fluxJump_r12_c3': 'i4', 'bettii.RTHighPriority.SCLoopsBetweenSCsolutions':
    'i4', 'fluxJump_r9_c9': 'i4', 'fluxJump_r9_c8': 'i4', 'fluxJump_r9_c5':
    'i4', 'fluxJump_r9_c4': 'i4', 'fluxJump_r9_c7': 'i4', 'fluxJump_r9_c6':
    'i4', 'fluxJump_r9_c1': 'i4', 'fluxJump_r9_c3': 'i4', 'fluxJump_r9_c2':
    'i4', 'java_native_messaging.StarCameraAuxiliarySolution.sigma_dec': 'f8',
    'fluxJump_r14_c6': 'i4', 'fluxJump_r14_c7': 'i4', 'fluxJump_r14_c4': 'i4',
    'fluxJump_r14_c5': 'i4', 'fluxJump_r14_c2': 'i4', 'fluxJump_r14_c3': 'i4',
    'fluxJump_r14_c1': 'i4', 'fluxJump_r14_c8': 'i4', 'fluxJump_r14_c9': 'i4',
    'bettii.TimingApplyPIDLoop.mceFrameNumber': 'i8', 'sq1fb_r20_c18': 'i8',
    'sq1fb_r20_c19': 'i8', 'DSPIDMessage.coilIsense14': 'f4', 'sq1fb_r20_c10':
    'i8', 'sq1fb_r20_c11': 'i8', 'sq1fb_r20_c12': 'i8', 'sq1fb_r20_c13': 'i8',
    'sq1fb_r20_c14': 'i8', 'sq1fb_r20_c15': 'i8', 'sq1fb_r20_c16': 'i8',
    'sq1fb_r20_c17': 'i8', 'AnalogInMessage.aDCRaw17': 'f4',
    'AnalogInMessage.aDCRaw16': 'f4',
    'bettii.RTHighPriority.EstimatedElevationVelocityArcsec': 'f8',
    'TReadStandardMessage.aDacRaw2': 'i4', 'AnalogOutMessage.analogOut': 'i4',
    'DSPIDMessage.coilIsense12': 'f4', 'AnalogOutMessage.analogOut27': 'f4',
    'bettii.ThermometersDemuxedCelcius.NumOfSamples': 'i4',
    'AnalogOutMessage.analogOut26': 'f4', 'AnalogOutMessage.analogOut21': 'f4',
    'AnalogInMessage.aDCRaw': 'i4', 'TReadStandardMessage.aDacRaw7': 'i4',
    'AnalogOutMessage.analogOut23': 'f4',
    'bettii.RTLowPriority.TimingRTModeManager': 'i4',
    'TReadStandardMessage.aDacRaw5': 'i4', 'fluxJump_r8_c14': 'i4',
    'fluxJump_r8_c15': 'i4', 'fluxJump_r8_c16': 'i4', 'fluxJump_r8_c17': 'i4',
    'fluxJump_r8_c10': 'i4', 'fluxJump_r8_c11': 'i4', 'fluxJump_r8_c12': 'i4',
    'fluxJump_r8_c13': 'i4', 'fluxJump_r8_c18': 'i4', 'fluxJump_r8_c19': 'i4',
    'error_r20_c7': 'i8', 'error_r20_c6': 'i8', 'error_r20_c5': 'i8',
    'error_r20_c4': 'i8', 'error_r20_c3': 'i8', 'error_r20_c2': 'i8',
    'error_r20_c1': 'i8', 'AnalogInMessage.aDCRaw18': 'f4', 'error_r20_c9':
    'i8', 'error_r20_c8': 'i8', 'bettii.PIDOutputMomDump.integral': 'f4',
    'bettii.RTLowPriority.estimatedGyroZarcsec': 'f8',
    'TReadStandardMessage.demod5': 'f4',
    'bettii.GyroReadings.angularVelocityFilteredY': 'i4',
    'bettii.GyroReadings.angularVelocityFilteredX': 'i4',
    'bettii.GyroReadings.angularVelocityFilteredZ': 'i4',
    'bettii.DelayLines.WDLloopIteration': 'i4', 'sq1fb_r11_c10': 'i8',
    'sq1fb_r11_c11': 'i8', 'fluxJump_r10_c8': 'i4', 'fluxJump_r10_c9': 'i4',
    'sq1fb_r11_c14': 'i8', 'sq1fb_r11_c15': 'i8', 'sq1fb_r11_c16': 'i8',
    'sq1fb_r11_c17': 'i8', 'fluxJump_r10_c2': 'i4', 'fluxJump_r10_c3': 'i4',
    'bettii.BoopSysInfo.cpu1': 'f4', 'fluxJump_r10_c1': 'i4', 'fluxJump_r10_c6':
    'i4', 'fluxJump_r10_c7': 'i4', 'fluxJump_r10_c4': 'i4', 'fluxJump_r10_c5':
    'i4', 'bettii.AngleSensorOutput.WDLYOffsetPixels': 'f4',
    'AnalogInMessage.aDC15': 'f4', 'AnalogInMessage.aDC16': 'f4',
    'AnalogInMessage.aDC17': 'f4', 'AnalogInMessage.aDC10': 'f4',
    'bettii.ThermometersOutput.Iteration': 'i4', 'AnalogInMessage.aDC12': 'f4',
    'AnalogInMessage.aDC13': 'f4', 'AnalogInMessage.aDC18': 'f4',
    'AnalogInMessage.aDC19': 'f4', 'bettii.CommandedTipTilts.KX': 'f4',
    'bettii.CommandedTipTilts.KY': 'f4',
    'bettii.RTLowPriority.RawStarcameraNumMatched': 'i4', 'sq1fb_r2_c5': 'i8',
    'sq1fb_r2_c4': 'i8', 'sq1fb_r2_c7': 'i8', 'sq1fb_r2_c6': 'i8',
    'sq1fb_r2_c1': 'i8', 'sq1fb_r2_c3': 'i8', 'sq1fb_r2_c2': 'i8',
    'sq1fb_r2_c9': 'i8', 'sq1fb_r2_c8': 'i8', 'fluxJump_r17_c17': 'i4',
    'fluxJump_r17_c16': 'i4', 'fluxJump_r17_c15': 'i4', 'fluxJump_r17_c14':
    'i4', 'fluxJump_r17_c13': 'i4', 'fluxJump_r17_c12': 'i4',
    'fluxJump_r17_c11': 'i4', 'fluxJump_r17_c10': 'i4', 'fluxJump_r17_c19':
    'i4', 'fluxJump_r17_c18': 'i4',
    'java_native_messaging.StarCameraSolution.sigma_roll': 'f8',
    'AnalogInMessage.latestMceFrameNumber': 'i8', 'sq1fb_r3_c21': 'i8',
    'sq1fb_r3_c20': 'i8', 'bettii.ThermometersDemuxedCelcius.J3L28': 'f4',
    'bettii.ThermometersDemuxedCelcius.J3L24': 'f4',
    'bettii.ThermometersDemuxedCelcius.J3L26': 'f4',
    'bettii.ThermometersDemuxedCelcius.J3L20': 'f4',
    'bettii.ThermometersDemuxedCelcius.J3L22': 'f4', 'sq1fb_r6_c1': 'i8',
    'sq1fb_r6_c3': 'i8', 'sq1fb_r6_c2': 'i8', 'sq1fb_r6_c5': 'i8',
    'sq1fb_r6_c4': 'i8', 'sq1fb_r6_c7': 'i8', 'sq1fb_r6_c6': 'i8',
    'sq1fb_r6_c9': 'i8', 'sq1fb_r6_c8': 'i8', 'fluxJump_r17_c1': 'i4',
    'AnalogInMessage.address': 'i4', 'TReadDiodeMessage.nsum': 'i4',
    'bettii.AngleSensorOutput.KXOffsetPixels': 'f4',
    'bettii.GyroReadings.angularVelocityZ': 'i4',
    'bettii.Magnetometer.QuaternionFXPqr': 'f4', 'masterMceFrameNumber': 'i8',
    'fluxJump_r17_c9': 'i4', 'bettii.RTLowPriority.TimingRTEKFUpdate': 'i4',
    'AnalogOutMessage.analogOut2': 'f4', 'AnalogOutMessage.analogOut3': 'f4',
    'AnalogOutMessage.analogOut0': 'f4', 'fluxJump_r17_c8': 'i4',
    'AnalogOutMessage.analogOut6': 'f4', 'AnalogOutMessage.analogOut7': 'f4',
    'AnalogOutMessage.analogOut4': 'f4', 'AnalogOutMessage.analogOut5': 'f4',
    'AnalogOutMessage.analogOut8': 'f4', 'AnalogOutMessage.analogOut9': 'f4',
    'AnalogInMessage.aDC8': 'f4', 'AnalogInMessage.aDC9': 'f4',
    'bettii.RTLowPriority.covarianceMatrix53': 'f8',
    'bettii.RTLowPriority.covarianceMatrix52': 'f8',
    'bettii.RTLowPriority.covarianceMatrix51': 'f8',
    'bettii.RTLowPriority.covarianceMatrix50': 'f8', 'AnalogInMessage.aDC2':
    'f4', 'AnalogInMessage.aDC3': 'f4',
    'bettii.RTLowPriority.covarianceMatrix55': 'f8',
    'bettii.RTLowPriority.covarianceMatrix54': 'f8',
    'bettii.RTLowPriority.covarianceMatrix04': 'f8',
    'bettii.GyroReadings.angularVelocityX': 'i4',
    'bettii.RTLowPriority.covarianceMatrix05': 'f8',
    'bettii.currentReadout.frameNumberLoopEthercatWhenCurrentWasReadout': 'i8',
    'PiperThermo.3HePump': 'f4', 'bettii.RTLowPriority.covarianceMatrix00':
    'f8', 'TReadDiodeMessage.gDac14': 'i4', 'TReadDiodeMessage.gDac15': 'i4',
    'TReadDiodeMessage.gDac12': 'i4', 'TReadDiodeMessage.gDac13': 'i4',
    'TReadDiodeMessage.gDac10': 'i4', 'bettii.RTLowPriority.covarianceMatrix01':
    'f8', 'bettii.GyroReadings.angularVelocityY': 'i4',
    'bettii.RTLowPriority.covarianceMatrix02': 'f8',
    'bettii.DelayLines.WDLproportional': 'f4',
    'bettii.PIDOutputMomDump.derivative': 'f4',
    'bettii.RTLowPriority.TimingRTGenerateGyroVel': 'i4', 'fluxJump_r2_c21':
    'i4', 'fluxJump_r2_c20': 'i4', 'bettii.Magnetometer.QuaternionFXPqk': 'f4',
    'bettii.TimingApplyPIDLoop.writeTipTiltsandMCEmemoryItems': 'i4',
    'sq1fb_r9_c4': 'i8', 'fluxJump_r8_c7': 'i4',
    'bettii.ThermometersOutput.DO20': 'u1', 'bettii.ThermometersOutput.DO21':
    'u1', 'fluxJump_r8_c4': 'i4', 'fluxJump_r8_c5': 'i4',
    'bettii.RTLowPriority.RawStarcameraDecError': 'f4', 'sq1fb_r9_c1': 'i8',
    'fluxJump_r3_c19': 'i4', 'fluxJump_r3_c18': 'i4', 'fluxJump_r3_c13': 'i4',
    'fluxJump_r3_c12': 'i4', 'fluxJump_r3_c11': 'i4', 'fluxJump_r8_c1': 'i4',
    'fluxJump_r3_c17': 'i4', 'fluxJump_r3_c16': 'i4', 'fluxJump_r3_c15': 'i4',
    'fluxJump_r3_c14': 'i4', 'bettii.PIDInputMomDump.velocityMeasurement': 'f4',
    'bettii.Magnetometer.DecDeg': 'f4',
    'java_native_messaging.StarCameraAuxiliarySolution.frame_number': 'i8',
    'bettii.RTLowPriority.FPGALoaded': 'u1',
    'bettii.PIDInputCCMG.velocityMeasurement': 'f4', 'fluxJump_r8_c21': 'i4',
    'fluxJump_r8_c20': 'i4', 'error_r5_c9': 'i8', 'error_r5_c8': 'i8',
    'error_r5_c7': 'i8', 'error_r5_c6': 'i8', 'error_r5_c5': 'i8',
    'error_r5_c4': 'i8', 'error_r5_c3': 'i8', 'error_r5_c2': 'i8',
    'error_r5_c1': 'i8', 'TReadStandardMessage.gDac9': 'i4',
    'TReadStandardMessage.gDac8': 'i4', 'TReadStandardMessage.gDac7': 'i4',
    'TReadStandardMessage.gDac6': 'i4', 'TReadStandardMessage.gDac5': 'i4',
    'TReadStandardMessage.gDac4': 'i4', 'TReadStandardMessage.gDac3': 'i4',
    'TReadStandardMessage.gDac2': 'i4', 'TReadStandardMessage.gDac1': 'i4',
    'TReadStandardMessage.gDac0': 'i4',
    'bettii.ThermometersDemuxedCelcius.J4L47': 'f4',
    'bettii.ThermometersDemuxedCelcius.J4L45': 'f4',
    'bettii.ThermometersDemuxedCelcius.J4L43': 'f4', 'sq1fb_r14_c17': 'i8',
    'bettii.ThermometersDemuxedCelcius.J4L41': 'f4', 'sq1fb_r14_c16': 'i8',
    'bettii.ThermometersDemuxedCelcius.J4L27': 'f4',
    'bettii.ThermometersDemuxedCelcius.J4L49': 'f4',
    'bettii.PIDOutputMomDump.ut': 'f4', 'error_r21_c17': 'i8',
    'bettii.currentReadout.msElapsedBetweenReadouts': 'i8',
    'bettii.PIDOutputMomDump.mceFrameNumber': 'i8', 'bettii.DelayLines.WDLrawV':
    'f4', 'bettii.GriffinsGalil.mceFrameNumber': 'i8',
    'DSPIDMessage.analogOutRaw9': 'i4', 'DSPIDMessage.analogOutRaw8': 'i4',
    'AnalogOutMessage.analogOut30': 'f4', 'AnalogOutMessage.analogOut31': 'f4',
    'DSPIDMessage.analogOutRaw1': 'i4', 'DSPIDMessage.analogOutRaw0': 'i4',
    'DSPIDMessage.analogOutRaw3': 'i4', 'DSPIDMessage.analogOutRaw2': 'i4',
    'DSPIDMessage.analogOutRaw5': 'i4', 'DSPIDMessage.analogOutRaw4': 'i4',
    'DSPIDMessage.analogOutRaw7': 'i4', 'DSPIDMessage.analogOutRaw6': 'i4',
    'bettii.DelayLines.CDLloopIteration2': 'i4', 'bettii.DelayLines.CDLut':
    'f4', 'bettii.ThermometersDemuxedCelcius.J1L30': 'f4',
    'AnalogInMessage.aDCRaw3': 'f4', 'bettii.RTLowPriority.TimingRTMatrices':
    'i4', 'bettii.ThermometersDemuxedCelcius.J1L32': 'f4',
    'AnalogInMessage.aDCRaw2': 'f4', 'AnalogInMessage.aDCRaw1': 'f4',
    'bettii.ThermometersDemuxedCelcius.J1L34': 'f4', 'AnalogInMessage.aDCRaw0':
    'f4', 'AnalogInMessage.aDCRaw7': 'f4',
    'bettii.ThermometersDemuxedCelcius.J1L36': 'f4', 'AnalogInMessage.aDCRaw5':
    'f4', 'fluxJump_r17_c20': 'i4', 'fluxJump_r17_c21': 'i4',
    'bettii.PIDOutputCCMG.proportional': 'f4', 'AnalogOutMessage.address': 'i4',
    'bettii.ThermometersDemuxedCelcius.J3L18': 'f4',
    'bettii.ThermometersDemuxedCelcius.J3L10': 'f4',
    'bettii.ThermometersDemuxedCelcius.J3L12': 'f4',
    'bettii.ThermometersDemuxedCelcius.J3L14': 'f4',
    'bettii.DelayLines.CDLvelMeasurement': 'f4',
    'bettii.ThermometersDemuxedCelcius.J3L16': 'f4', 'sq1fb_r19_c18': 'i8',
    'sq1fb_r19_c19': 'i8', 'error_r7_c9': 'i8', 'error_r7_c8': 'i8',
    'error_r7_c5': 'i8', 'error_r7_c4': 'i8', 'error_r7_c7': 'i8',
    'error_r7_c6': 'i8', 'error_r7_c1': 'i8', 'sq1fb_r19_c15': 'i8',
    'sq1fb_r19_c16': 'i8', 'error_r7_c2': 'i8', 'error_r3_c9': 'i8',
    'error_r3_c8': 'i8', 'DSPIDMessage.pidI': 'i4',
    'bettii.ThermometersDemuxedCelcius.J2L15': 'f4',
    'bettii.ThermometersDemuxedCelcius.J2L13': 'f4',
    'bettii.ThermometersDemuxedCelcius.J2L11': 'f4', 'error_r3_c1': 'i8',
    'error_r11_c20': 'i8', 'error_r3_c2': 'i8', 'error_r3_c5': 'i8',
    'error_r3_c4': 'i8', 'error_r3_c7': 'i8', 'error_r3_c6': 'i8',
    'MasterMessage.address': 'i4',
    'java_native_messaging.StarCameraSolution.serial_number': 'i4',
    'AnalogInMessage.frameCounter': 'i8', 'sq1fb_r9_c5': 'i8',
    'bettii.ThermometersCCMG.mod3AI2': 'f4', 'bettii.ThermometersCCMG.mod3AI3':
    'f4', 'bettii.ThermometersCCMG.mod3AI0': 'f4',
    'bettii.ThermometersCCMG.mod3AI1': 'f4',
    'bettii.RTLowPriority.covarianceMatrix40': 'f8',
    'bettii.RTLowPriority.covarianceMatrix41': 'f8',
    'bettii.RTLowPriority.covarianceMatrix42': 'f8',
    'bettii.RTLowPriority.covarianceMatrix43': 'f8',
    'bettii.RTLowPriority.covarianceMatrix44': 'f8',
    'bettii.RTLowPriority.covarianceMatrix45': 'f8',
    'TReadStandardMessage.latestMceFrameNumber': 'i8',
    'TReadDiodeMessage.status': 'i4', 'bettii.TimingApplyPIDLoop.previousticks':
    'i4', 'fluxJump_r11_c11': 'i4', 'fluxJump_r11_c10': 'i4',
    'fluxJump_r11_c13': 'i4', 'fluxJump_r11_c12': 'i4', 'fluxJump_r11_c15':
    'i4', 'fluxJump_r11_c14': 'i4', 'fluxJump_r11_c17': 'i4',
    'fluxJump_r11_c16': 'i4', 'fluxJump_r11_c19': 'i4', 'fluxJump_r11_c18':
    'i4', 'bettii.GriffinsGalil.TPB': 'i4', 'bettii.GriffinsGalil.TPC': 'i4',
    'bettii.GriffinsGalil.TPA': 'i4', 'sq1fb_r2_c11': 'i8', 'sq1fb_r17_c17':
    'i8', 'sq1fb_r17_c14': 'i8', 'sq1fb_r17_c15': 'i8', 'sq1fb_r2_c15': 'i8',
    'sq1fb_r2_c14': 'i8', 'sq1fb_r2_c17': 'i8', 'sq1fb_r2_c16': 'i8',
    'sq1fb_r2_c19': 'i8', 'sq1fb_r2_c18': 'i8', 'sq1fb_r17_c18': 'i8',
    'sq1fb_r17_c19': 'i8', 'DSPIDMessage.coilIsense5': 'f4',
    'DSPIDMessage.coilIsense4': 'f4', 'DSPIDMessage.coilIsense7': 'f4',
    'DSPIDMessage.coilIsense6': 'f4', 'DSPIDMessage.coilIsense1': 'f4',
    'DSPIDMessage.coilIsense0': 'f4', 'DSPIDMessage.coilIsense3': 'f4',
    'DSPIDMessage.coilIsense2': 'f4', 'DSPIDMessage.coilIsense9': 'f4',
    'DSPIDMessage.coilIsense8': 'f4', 'bettii.FpgaState.mceFrameNumber': 'i8',
    'java_native_messaging.StarCameraAuxiliarySolution.az_deg': 'f8',
    'bettii.CommandedTipTilts.WDLX': 'f4', 'bettii.CommandedTipTilts.WDLY':
    'f4', 'bettii.RTLowPriority.RawStarcameraRollDeg': 'f4',
    'AnalogInMessage.aDCRaw27': 'f4', 'TReadStandardMessage.aDac9': 'f4',
    'TReadStandardMessage.aDac8': 'f4', 'TReadStandardMessage.aDac5': 'f4',
    'TReadStandardMessage.aDac4': 'f4', 'TReadStandardMessage.aDac7': 'f4',
    'TReadStandardMessage.aDac6': 'f4', 'TReadStandardMessage.aDac1': 'f4',
    'TReadStandardMessage.aDac0': 'f4', 'TReadStandardMessage.aDac3': 'f4',
    'TReadStandardMessage.aDac2': 'f4', 'AnalogInMessage.aDCRaw24': 'f4',
    'bettii.RTHighPriority.targetRA': 'f8', 'bettii.DelayLines.WDLderivative':
    'f4', 'bettii.RTHighPriority.SCSolutionsRequested': 'i4', 'sq1fb_r9_c3':
    'i8', 'bettii.RTLowPriority.TimingRTLoopStart': 'i4', 'sq1fb_r11_c12': 'i8',
    'bettii.TipTilts.PiezoKVMON2': 'f4', 'sq1fb_r11_c13': 'i8',
    'bettii.TipTilts.PiezoKVMON1': 'f4', 'DSPIDMessage.aDac': 'f4',
    'sq1fb_r5_c9': 'i8', 'sq1fb_r11_c18': 'i8', 'DSPIDMessage.demod9': 'f4',
    'DSPIDMessage.demod8': 'f4', 'sq1fb_r11_c19': 'i8', 'DSPIDMessage.demod5':
    'f4', 'DSPIDMessage.demod4': 'f4', 'DSPIDMessage.demod7': 'f4',
    'DSPIDMessage.demod6': 'f4', 'DSPIDMessage.demod1': 'f4',
    'DSPIDMessage.demod0': 'f4', 'DSPIDMessage.demod3': 'f4',
    'DSPIDMessage.demod2': 'f4', 'DSPIDMessage.aDacRaw': 'i4',
    'TReadStandardMessage.temperature12': 'f4',
    'bettii.GpsReadings.approximatMmceFrameNumber': 'i8', 'sq1fb_r13_c9': 'i8',
    'bettii.PIDOutputMomDump.proportional': 'f4',
    'bettii.TipTilts.PiezoWDLSGSMONX': 'f4', 'bettii.TipTilts.PiezoWDLSGSMONY':
    'f4', 'AnalogInMessage.aDCRaw19': 'f4',
    'bettii.RTLowPriority.estimatedGyroXarcsec': 'f8',
    'bettii.ThermometersDemuxedCelcius.J1L8': 'f4',
    'bettii.ThermometersDemuxedCelcius.J1L6': 'f4',
    'bettii.ThermometersDemuxedCelcius.J1L4': 'f4',
    'bettii.ThermometersDemuxedCelcius.J1L2': 'f4',
    'bettii.ThermometersCCMG.mceFrameNumber': 'i8', 'DSPIDMessage.demod11':
    'f4', 'TReadStandardMessage.aDacRaw8': 'i4',
    'TReadStandardMessage.aDacRaw9': 'i4', 'PiperThermo.Cal50kohm': 'f4',
    'AnalogOutMessage.analogOut28': 'f4', 'DSPIDMessage.demod10': 'f4',
    'DSPIDMessage.coilVMonRaw': 'i4', 'TReadStandardMessage.aDacRaw3': 'i4',
    'TReadStandardMessage.aDacRaw0': 'i4', 'TReadStandardMessage.aDacRaw1':
    'i4', 'TReadStandardMessage.aDacRaw6': 'i4', 'DSPIDMessage.demod13': 'f4',
    'TReadStandardMessage.aDacRaw4': 'i4', 'error_r18_c5': 'i8',
    'AnalogInMessage.aDC14': 'f4', 'DSPIDMessage.demod12': 'f4',
    'DSPIDMessage.demod15': 'f4', 'sq1fb_r12_c20': 'i8', 'sq1fb_r12_c21': 'i8',
    'AnalogInMessage.aDC11': 'f4',
    'bettii.RTLowPriority.SlewParametersVsetpointsarcsecs': 'i4',
    'AnalogInMessage.numberOfChannels': 'i4',
    'bettii.GriffinsGalil.griffinAAngleDegrees': 'f8',
    'DSPIDMessage.coilIsenseRaw6': 'i4', 'DSPIDMessage.coilIsenseRaw7': 'i4',
    'bettii.StepperGalil.tpb': 'i4', 'bettii.StepperGalil.tpa': 'i4',
    'DSPIDMessage.coilIsenseRaw8': 'i4', 'sq1fb_r14_c11': 'i8', 'sq1fb_r14_c10':
    'i8', 'sq1fb_r14_c13': 'i8', 'sq1fb_r14_c12': 'i8', 'sq1fb_r14_c15': 'i8',
    'sq1fb_r14_c14': 'i8', 'error_r21_c18': 'i8', 'error_r21_c19': 'i8',
    'sq1fb_r14_c19': 'i8', 'sq1fb_r14_c18': 'i8', 'error_r21_c14': 'i8',
    'error_r21_c15': 'i8', 'error_r21_c12': 'i8', 'error_r21_c13': 'i8',
    'error_r21_c10': 'i8', 'error_r21_c11': 'i8', 'TReadDiodeMessage.aDacRaw9':
    'i4', 'TReadDiodeMessage.aDacRaw8': 'i4', 'TReadDiodeMessage.aDacRaw7':
    'i4', 'TReadDiodeMessage.aDacRaw6': 'i4', 'TReadDiodeMessage.aDacRaw5':
    'i4', 'TReadDiodeMessage.aDacRaw4': 'i4', 'TReadDiodeMessage.aDacRaw3':
    'i4', 'TReadDiodeMessage.aDacRaw2': 'i4', 'TReadDiodeMessage.aDacRaw1':
    'i4', 'TReadDiodeMessage.aDacRaw0': 'i4', 'error_r11_c17': 'i8',
    'error_r11_c16': 'i8', 'error_r11_c15': 'i8', 'error_r11_c14': 'i8',
    'error_r11_c13': 'i8', 'error_r11_c12': 'i8', 'error_r11_c11': 'i8',
    'error_r11_c10': 'i8', 'error_r11_c19': 'i8', 'error_r11_c18': 'i8',
    'bettii.WheelsGalil.torqueB': 'f4', 'bettii.WheelsGalil.torqueA': 'f4',
    'bettii.DelayLines.CDLderivative': 'f4',
    'bettii.RTHighPriority.estimatedBiasZarcsec': 'f8',
    'bettii.DelayLines.CDLposMeasurement': 'f4',
    'bettii.RTHighPriority.computedEstimatorAzimuth': 'f8', 'error_r8_c21':
    'i8', 'error_r8_c20': 'i8', 'bettii.RTHighPriority.GondolaDecDeg': 'f8',
    'bettii.RTHighPriority.SCLoopsSinceLastSolution': 'i4',
    'bettii.RTLowPriority.MeasurementErrorCovarianceMatrixR21': 'f8'}

    def __init__(self, fieldName, dtype='f8', indexName=None, indexType='i8', label=None, conversion=1, function=lambda x: x, range=1e10):
        '''
        Constructor
        '''
        if indexName is None: indexName = fieldName.rsplit('.', 1)[0] + '.mceFrameNumber'  # the index seems to be always in this format
        if label is None: label = fieldName.split('.')[-1]  # we get the last word of the fieldname for the label
        if label == 'mceFrameNumber':  # it seems to be a index, we index it by itself
            label = fieldName
            dtype = indexType
            indexName = fieldName
        if self.DTYPES is None or fieldName not in self.DTYPES or dtype is not 'f8': self.dtype = dtype 
        else: self.dtype = self.DTYPES[fieldName]
        self.fieldName = fieldName  # filename of the field
        self.function = function  # function to apply on the field data
        self.indexName = indexName  # field name of the field's index
        self.indexType = indexType  # dtype of the index
        self.label = label  # label used as columnLabel on the pd.Dataframe generated in DataSet class
        self.conversion = conversion  # multiplying factor, to convert the units if we want
        self.range = range  # acceptable range



def getFieldsContaining(substring, folder, indexName=None, dtype='f8'):
    """Return a list of fields in the folder containing a substring
    
    :param substring: string we are looking for
    :param folder: folder containing the files we want to search
    :param indexName: name of the indexing field for the fields found
    :param dtype: numpy Array-protocol type string (ie. INT64 should be 'i4')
    :return: list of :class:~`utilsfield.Field` objects
    :rtype: `list`   
    """
    print 'Generating fields list...'
    fieldsList = []
    for filename in os.listdir(folder):
        if substring in filename:
            field = Field(filename, indexName=indexName, dtype=getFormat(filename, folder))
            fieldsList.append(field)
    if len(fieldsList) == 1: return fieldsList[0]
    return fieldsList

def getFieldsRegex(regex, folder):
    """Return a list of fields in the folder matching the regular expression regex.
    It uses the function :mod:`re.match`.
    
    :param regex: regular expression
    :param folder: folder where we want to search the fields
    :return: list of :class:~`utilsfield.Field` objects
    :rtype: `list`
    """
    import re
    print 'Generating fields list...'
    fieldsList = []
    for filename in os.listdir(folder):
        if re.match(regex, filename) is not None:
            field = Field(filename, dtype=getFormat(filename, folder))
            fieldsList.append(field)
    if len(fieldsList) == 1: return fieldsList[0]
    return fieldsList

def getFormat(fieldName, folder):
    """Return the data type of the fieldName using the format file in folder
    
    :param fieldName: full name of the field file
    :param folder: folder where the ``format`` file is located
    :return: numpy Array-protocol type string (ie. INT64 should be 'i4')
    :rtype: `str`
    """
    formatFile = open(folder + 'format')
    dic = {'INT32':'i4',
         'INT64':'i8',
         'UINT8':'u1',
         'FLOAT32':'f4',
         'FLOAT64':'f8'}
    try:
        for line in formatFile:
            if fieldName in line:
                dtype = dic[line.split()[2]]
                return dtype
        # return 'f8'    
    finally:
        formatFile.close()
def getDtypes(folder):
    """Return the data types of all fieldNames using the format file in folder
    
    :param folder: folder where the file ``format`` is located
    :return: dictionary of type strings keyed by fieldName
    :rtype: `dict`
    """
    formatFile = open(folder + 'format')
    dic = {'INT32':'i4',
         'INT64':'i8',
         'UINT8':'u1',
         'FLOAT32':'f4',
         'FLOAT64':'f8'}
    dtypes = {}
    try:
        for line in formatFile:
            try:
                fieldName, typ = line.split()[0:3:2]
                dtypes[fieldName] = dic[typ] 
            except Exception as err:
                pass

    finally:
        formatFile.close()
        return dtypes        
