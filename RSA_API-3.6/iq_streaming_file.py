"""
Simple IQ Streaming Example using API for RSA306
Author: Morgan Allison
Date created: 10/5/15
Date edited: 11/18/15
Windows 7 64-bit
Python 2.7.9 64-bit (Anaconda 3.7.0)
NumPy 1.8.1, MatPlotLib 1.3.1
To get Anaconda: http://continuum.io/downloads
Anaconda includes NumPy and MatPlotLib
"""

from ctypes import *
import time, os

"""
################################################################
C:\Tektronix\RSA306 API\lib\x64 needs to be added to the 
PATH system environment variable
################################################################
"""
os.chdir("C:\\Tektronix\\RSA306 API\\lib\\x64")
rsa300 = WinDLL("RSA300API.dll")


"""#################CLASSES AND FUNCTIONS#################"""
class IQSTRMFILEINFO(Structure):
   _fields_ = [('numberSamples', c_uint64), 
   ('sample0Timestamp', c_uint64),
   ('triggerSampleIndex', c_uint64), 
   ('triggerTimestamp', c_uint64),
   ('acqStatus', c_uint32), 
   ('filenames', c_wchar_p)]

def iqstream_status_parser(acqStatus):
	#this function parses the IQ streaming status variable
	if acqStatus == 0:
		print('No error.')
	if (bool(acqStatus & 0x10000)):	#mask bit 16
		print('Input overrange.')
	if (bool(acqStatus & 0x40000)):	#mask bit 18
		print('Input buffer > 75{} full.'.format('%'))
	if (bool(acqStatus & 0x80000)):	#mask bit 19
		print('Input buffer overflow. IQStream processing too slow, data loss has occurred.')
	if (bool(acqStatus & 0x100000)):	#mask bit 20
		print('Output buffer > 75{} full.'.format('%'))
	if (bool(acqStatus & 0x200000)):	#mask bit 21
		print('Output buffer overflow. File writing too slow, data loss has occurred.')


"""#################INITIALIZE VARIABLES#################"""
#search/connect
longArray = c_long*10
deviceIDs = longArray()
deviceSerial = c_wchar_p('')
numFound = c_int(0)

#main SA parameters
cf = c_double(1e9)
refLevel = c_double(0)
bwHz_req = c_double(20e6)
bwHz_act = c_double(0)
sRate = c_double(0)

#Stream Control Variables
filenameBase = c_char_p('C:\SignalVu-PC Files\sample')
#dest: 0 = client, 1 = .tiq, 2 = .siq, 3 = .siqd/.siqh
dest = c_int(3)
#dtype: 0 = single, 1 = int32, 2 = int16
dtype = c_int(2)
#SuffixCtl: 0 = none, 1 = YYYY.MM.DD.hh.mm.ss.msec, 3 = -xxxxx autoincrement
suffixCtl = c_int(3)
#streaming status boolean variable
complete = c_bool(False)
#write status boolean variable (always true if non-triggered acquisition)
writing = c_bool(False)
#file duration
durationMsec = c_int(100)
#time to wait between streaming loopCounts
waitTime = durationMsec.value/1e3/10
#bool used for streaming loopCount control
streaming = True
loopCount = 0
iqstream_info = IQSTRMFILEINFO()


<<<<<<< HEAD
"""#################SEARCH/CONNECT#################"""
=======
""#################SEARCH/CONNECT#################"""
>>>>>>> refs/remotes/origin/master
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
<<<<<<< HEAD
   #note: the API can only access one at a time
=======
   #note: the API can only currently access one at a time
>>>>>>> refs/remotes/origin/master

#connect to the first RSA306
ret = rsa300.Connect(deviceIDs[0])
if ret != 0:
   print('Error in Connect: ' + str(ret))


"""#################CONFIGURE INSTRUMENT#################"""
rsa300.Preset()
rsa300.SetCenterFreq(cf)
rsa300.SetReferenceLevel(refLevel)
rsa300.IQSTREAM_SetAcqBandwidth(bwHz_req)
rsa300.IQSTREAM_GetAcqParameters(byref(bwHz_act), byref(sRate))
rsa300.IQSTREAM_SetOutputConfiguration(dest, dtype)
rsa300.IQSTREAM_SetDiskFilenameBase(filenameBase)
rsa300.IQSTREAM_SetDiskFilenameSuffix(suffixCtl)
rsa300.IQSTREAM_SetDiskFileLength(durationMsec)


"""#################STREAMING#################"""
"""
Note: When the time limit specified by msec is reached, there is a de facto 
IQSTREAM_Stop(). Acquisition can be terminated early by explicitly sending 
IQSTREAM_Stop().

The order of these next two commands is of paramount importance. 
Most problems are caused/solved by switching the order of these commands.
Run() MUST BE SENT before IQSTREAM_Start()
"""
rsa300.Run()
rsa300.IQSTREAM_Start()

#Streaming control loop example, feel free to make your own
while streaming == True:
	time.sleep(waitTime)
	rsa300.IQSTREAM_GetDiskFileWriteStatus(byref(complete), byref(writing))
	if complete.value == True:
		streaming = False

rsa300.IQSTREAM_GetFileInfo(byref(iqstream_info))
iqstream_status_parser(iqstream_info.acqStatus)

print('File saved at {}'.format(filenameBase.value))
print('Disconnecting.')
rsa300.Disconnect()