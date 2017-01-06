"""
Tektronix RSA306 API: Block IQ Data
Author: Morgan Allison
Date Created: 5/15
Date edited: 2/16
Windows 7 64-bit
Python 2.7.9 64-bit (Anaconda 3.7.0)
NumPy 1.8.1, MatPlotLib 1.3.1
To get Anaconda: http://continuum.io/downloads
Anaconda includes NumPy and MatPlotLib
"""

from ctypes import *
import numpy as np
import matplotlib.pyplot as plt
import os

"""
################################################################
C:\Tektronix\RSA306 API\lib\x64 needs to be added to the 
PATH system environment variable
################################################################
"""
os.chdir("C:\\Tektronix\\RSA306 API\\lib\\x64")
rsa300 = WinDLL("RSA300API.dll")


"""#################CLASSES AND FUNCTIONS#################"""
class IQHeader(Structure):
   _fields_ = [('acqDataStatus', c_uint16),
   ('acquisitionTimestamp', c_uint64),
   ('frameID', c_uint32), ('trigger1Index', c_uint16),
   ('trigger2Index', c_uint16), ('timeSyncIndex', c_uint16)]


"""#################INITIALIZE VARIABLES#################"""
#search/connect
longArray = c_long*10
deviceIDs = longArray()
deviceSerial = c_wchar_p('')
numFound = c_int(0)
serialNum = c_char_p('')
nomenclature = c_char_p('')
header = IQHeader()

#main SA parameters
refLevel = c_double(0)
cf = c_double(1e9)
iqBandwidth = c_double(40e6)
recordLength = c_long(1024)
mode = c_int(0)
level = c_double(-10)
iqSampleRate = c_double(0)
runMode = c_int(0)
timeoutMsec = c_int(1000)
ready = c_bool(False)

#data transfer variables
iqArray =  c_float*recordLength.value
iData = iqArray()
qData = iqArray()
startIndex = c_int(0)


"""#################SEARCH/CONNECT#################"""
#search the USB 3.0 bus for an RSA306
ret = rsa300.Search(deviceIDs, byref(deviceSerial), byref(numFound))
if ret != 0:
   print('Error in Search: ' + str(ret))
if numFound.value < 1:
   print('No instruments found. Exiting script.')
   exit()
elif numFound.value == 1:
   print('One device found.')
   print('Device Serial Number: ' + deviceSerial.value)
else:
   print('2 or more instruments found.')
   #note: the API can only currently access one at a time

#connect to the first RSA306
ret = rsa300.Connect(deviceIDs[0])
if ret != 0:
   print('Error in Connect: ' + str(ret))


"""#################CONFIGURE INSTRUMENT#################"""
rsa300.Preset()
rsa300.SetReferenceLevel(refLevel)
rsa300.SetCenterFreq(cf)
rsa300.SetIQBandwidth(iqBandwidth)
rsa300.SetIQRecordLength(recordLength)
rsa300.SetTriggerMode(mode)
rsa300.SetIFPowerTriggerLevel(level)


"""#################ACQUIRE/PROCESS DATA#################"""
rsa300.Run()

#get relevant settings values
#this requires that the RSA306 be running
rsa300.GetReferenceLevel(byref(refLevel))
rsa300.GetCenterFreq(byref(cf))
rsa300.GetIQBandwidth(byref(iqBandwidth))
rsa300.GetIQRecordLength(byref(recordLength))
rsa300.GetTriggerMode(byref(mode))
rsa300.GetIFPowerTriggerLevel(byref(level))
rsa300.GetRunState(byref(runMode))
rsa300.GetIQSampleRate(byref(iqSampleRate))

print('Run Mode:' + str(runMode.value))
print('Reference level: ' + str(refLevel.value) + 'dBm')
print('Center frequency: ' + str(cf.value/1e6) + 'MHz')
print('Bandwidth: ' + str(iqBandwidth.value/1e6) + 'MHz')
print('Record length: ' + str(recordLength.value))
print('Trigger mode: ' + str(mode.value))
print('Trigger level: ' + str(level.value) + 'dBm')
print('Sample rate: ' + str(iqSampleRate.value) + 'Samples/sec')

#check for data ready
while ready.value == False:
   ret = rsa300.WaitForIQDataReady(timeoutMsec, byref(ready))

#as a bonus, get the IQ header even though it's not used
ret = rsa300.GetIQHeader(byref(header))
if ret != 0:
   print('Error in GetIQHeader: ' + str(ret))
print('Got IQ Header')

#query I and Q data
rsa300.GetIQDataDeinterleaved(byref(iData), byref(qData), startIndex, recordLength)
print('Got IQ data')

#convert ctypes array to numpy array for ease of use
I = np.ctypeslib.as_array(iData)
Q = np.ctypeslib.as_array(qData)


"""#################IQ VS TIME PLOT#################"""
time = np.linspace(0,recordLength.value/iqSampleRate.value,recordLength.value)

plt.subplot(211)
plt.title('I and Q vs Time')
plt.plot(time*1e3,I,'b')
plt.ylabel('I (V)')
plt.subplot(212)
plt.plot(time*1e3,Q,'r')
plt.ylabel('Q (V)')
plt.xlabel('Time (msec)')
plt.show()

print('Disconnecting.')
ret = rsa300.Disconnect()