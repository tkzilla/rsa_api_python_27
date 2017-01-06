import ctypes
from ctypes import *
from pylab import *
import numpy as np
import matplotlib.animation as animation
import time
from matplotlib.widgets import Button
import matplotlib.pyplot as plt

rsa300 = ctypes.WinDLL("RSA300API.dll")
intArray = c_int * 10
searchIDs = intArray()
deviceserial = c_wchar_p()
numFound = c_int()

ret = rsa300.Search(searchIDs, byref(deviceserial), byref(numFound))

if ret != 0:
	print "Run error: " + str(ret)
else:
	rsa300.Connect(searchIDs[0])
	
aLen = 1280
length = c_int(aLen)
rsa300.SetIQRecordLength(length)

cf = c_double(2e9)
rsa300.SetCenterFreq(cf)

rl = c_double(-10)
rsa300.SetReferenceLevel(rl)

iqLen = aLen * 2
floatArray = c_float * iqLen

#triggerMode = c_int(True)
#rsa300.SetTriggerMode(triggerMode)
trigPos = c_double(25.0)
rsa300.SetTriggerPositionPercent(trigPos)

iqBW = c_double(40e6)
rsa300.SetIQBandwidth(iqBW)

def getIQData():
	ready = c_bool(False)
	
	ret = rsa300.Run()
	if ret != 0:
			print "Run error: " + str(ret)
	ret = rsa300.WaitForIQDataReady(10000, byref(ready))
	if ret != 0:
		print "WaitForIQDataReady error: " + str(ret)
	iqData = floatArray()
	startIndex = c_int(0)
	if ready:
		ret = rsa300.GetIQData(iqData, startIndex, length)
		if ret != 0:
			print "GetIQData error: " + str(ret)
		iData = range(0,aLen)
		qData = range(0,aLen)
		for i in range(0,aLen):
			iData[i] = iqData[i*2]
			qData[i] = iqData[i*2+1]
	
	z = [(x + 1j*y) for x, y in zip(iData,qData)]
	
	cf = c_double(0)
	rsa300.GetCenterFreq(byref(cf))
	spec2 = mlab.specgram(z, NFFT=aLen, Fs=56e6)
	f = [(x + cf)/1e6 for x in spec2[1]]
	#close()
	#r = spec2[0]
	spec = np.fft.fft(z, aLen)
	r = [x * 1 for x in abs(spec)]
	r = np.fft.fftshift(r)
	return [iData, qData, z, r, f]

def init():
	#line.set_data([], [])
	#line2.set_data([], [])
	#line3.set_data([], [])
	return line, line2, line3,

def update(i):
	x = np.linspace(0, aLen, aLen)
	iq = getIQData()
	f = iq[4]
	i = iq[0]
	q = iq[1]
	
	r = iq[3]
	#print iq[4][1][0:10]
	line.set_data(x, i)
	line2.set_data(x, q)
	ax2.set_xlim(f[0], f[len(f) - 1])
	line3.set_data(f, r)
	
	ax2.set_xticks( [ round(f[int(8.0/56*len(f))]), round(f[int(18.0/56*len(f))]), f[len(f)/2], round(f[int(38.0/56*len(f))]), round(f[int(48.0/56*len(f))]) ] )
	#ax2.relim()
	return line, line2, line3,
	
fig = figure()

ax2 = fig.add_subplot(211)
ax2.set_xlim(0, aLen)
ax2.set_ylim(0, 1e2)
ax2.set_yscale('symlog')

xlabel('RefLevel = ' + str(rl.value) + ' dBm')
title('IQBandwith = ' + str(iqBW.value / 1e6) + ' MHz')
ax = fig.add_subplot(212)
ax.set_xlim(0, aLen)
ax.set_ylim(-15e-3, 15e-3)

xlabel('CF = ' + str(cf.value / 1e6) + ' MHz')
line, = ax.plot([], [], lw=2)
line2, = ax.plot([], [], lw=2)
line3, = ax2.plot([], [], lw=2)



def next(event):
	rsa300.Stop()
	cf = c_double(0)
	rsa300.GetCenterFreq(byref(cf))
	cf = c_double(cf.value + 10e6)
	rsa300.SetCenterFreq(cf)
	rsa300.Run()
	ax.set_xlabel('CF = ' + str(cf.value / 1e6) + ' MHz')
	
def prev(event):
	rsa300.Stop()
	cf = c_double(0)
	rsa300.GetCenterFreq(byref(cf))
	cf = c_double(cf.value - 10e6)
	rsa300.SetCenterFreq(cf)
	rsa300.Run()
	ax.set_xlabel('CF = ' + str(cf.value / 1e6) + ' MHz')
	
def up(event):
	rsa300.Stop()
	rl = c_double(0)
	rsa300.GetReferenceLevel(byref(rl))
	rl = c_double(rl.value + 5.0)
	rsa300.SetReferenceLevel(rl)
	rsa300.Run()
	ax2.set_xlabel('RefLevel = ' + str(rl.value) + ' dBm')
	
def down(event):
	rsa300.Stop()
	rl = c_double(0)
	rsa300.GetReferenceLevel(byref(rl))
	rl = c_double(rl.value - 5.0)
	rsa300.SetReferenceLevel(rl)
	rsa300.Run()
	ax2.set_xlabel('RefLevel = ' + str(rl.value) + ' dBm')

def trigger(event):
	rsa300.Stop()
	trigMode = c_int(True)
	rsa300.GetTriggerMode(byref(trigMode))
	trigMode = c_int(not trigMode.value)
	rsa300.SetTriggerMode(trigMode)
	rsa300.Run()
	
def more(event):
	rsa300.Stop()
	iqBQ = c_double(0)
	rsa300.GetIQBandwidth(byref(iqBQ))
	iqBQ = c_double(iqBQ.value * 2)
	rsa300.SetIQBandwidth(iqBQ)
	rsa300.Run()
	ax2.set_title('IQBandwith = ' + str(iqBQ.value / 1e6) + ' MHz')

def less(event):
	rsa300.Stop()
	iqBQ = c_double(0)
	rsa300.GetIQBandwidth(byref(iqBQ))
	iqBQ = c_double(iqBQ.value / 2)
	rsa300.SetIQBandwidth(iqBQ)
	rsa300.Run()
	ax2.set_title('IQBandwith = ' + str(iqBQ.value / 1e6) + ' MHz')
	
	
axbuttonNext = plt.axes([0.91, 0.02, 0.070, 0.05])
bnext = Button(axbuttonNext, 'Next')
bnext.on_clicked(next)

axbuttonPrev = plt.axes([0.02, 0.02, 0.070, 0.05])
bprev = Button(axbuttonPrev, 'Prev')
bprev.on_clicked(prev)

axbuttonUp = plt.axes([0.02, 0.92, 0.12, 0.05])
bup = Button(axbuttonUp, 'Ref Up')
bup.on_clicked(up)

axbuttonDown = plt.axes([0.145, 0.92, 0.12, 0.05])
bdown = Button(axbuttonDown, 'Ref Down')
bdown.on_clicked(down)

axbuttonTrigger = plt.axes([0.85, 0.92, 0.12, 0.05])
btrigger = Button(axbuttonTrigger, 'Trigger')
btrigger.on_clicked(trigger)

axbuttonMore = plt.axes([0.81, 0.02, 0.070, 0.05])
bmore = Button(axbuttonMore, 'More')
bmore.on_clicked(more)

axbuttonLess = plt.axes([0.12, 0.02, 0.070, 0.05])
bless = Button(axbuttonLess, 'Less')
bless.on_clicked(less)

ani = animation.FuncAnimation(fig, update, init_func=init, frames=200, interval=10, blit=True)
show()

#def end():
rsa300.Stop()
rsa300.Disconnect()

