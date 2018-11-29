import matplotlib.pyplot as plt
import numpy as np
from scipy.signal import butter, lfilter
from scipy import signal

import math as m

Acc_rms = 220*220.0*512

def plot_graph():
	plt.figure()
	x = np.arange(0, 6.28, 0.1)
	y = np.sin(x)
	plt.plot(x, y)
	plt.show()

def get_sample(t):
	dt= t % T_SIGNAL
	return 220.0*sin(dT)

def calc_rms(sample):
	global Acc_rms
	Acc_rms -= (Acc_rms/512)
	Acc_rms += (sample*sample)
	rms= m.sqrt(Acc_rms/512)
	return (rms)

def all(order=1,ts=0.001,Q=10):
	x=range (0, 20000)
	y=range (0, 20000)
	yy=range(0, 20000)
	y_sqrt=range(0, 20000)
	i=0
	while i < 4000:
		y[i]  = 220.0*m.sqrt(2)*m.sin( i/100.0)
		y_sqrt[i]= m.sqrt(y[i]*y[i])
		yy[i] = calc_rms(y[i])
		i += 1
	while i < 8000:
		y[i]  = 180.0*m.sqrt(2)*m.sin( i/100.0)
		y_sqrt[i]= m.sqrt(y[i]*y[i])
		yy[i] = calc_rms(y[i])
		i += 1
	while i < 14000:
		y[i]  = 260.0*m.sqrt(2)*m.sin( i/100.0)
		y_sqrt[i]= m.sqrt(y[i]*y[i])
		yy[i] = calc_rms(y[i])
		i += 1
	while i < len(x):
		y[i]  = 230.0*m.sqrt(2)*m.sin( i/100.0)
		y_sqrt[i]= m.sqrt(y[i]*y[i])
		yy[i] = calc_rms(y[i])
		i += 1

#LPF filter
	b,a = butter (order,ts, 'low', False)
	yy_lpf100 = lfilter(b, a, yy)

#resample and second lpf
	yy_lpf100_1KHz = yy_lpf100[0::20] # 20KHz->1kHz
	b2,a2        = butter (1,7.0/1000, 'low', False)              # Fc=7Hz at Fs=1Khz
	yy_lpf7_1KHz = lfilter(b2, a2,yy_lpf100_1KHz)
	yy_lpf7      = signal.resample (yy_lpf7_1KHz,20000)   #1KHz->20kHz


#notch filter
	w0= 2/314.15926
	b_notch, a_notch = signal.iirnotch(w0, Q)
	yy_notch=lfilter(b_notch, a_notch, yy)

	#plt.plot (yy_lpf,yy_notch)
        print "size is "
	print len(yy_lpf7)
#	plt.plot (range(0,1000),yy_lpf100_1KHz,yy_lpf7_1KHz)

	plt.plot (x,yy_lpf7,yy_notch)
#	plt.plot (x,yy_lpf100,yy_lpf7)
	plt.legend(('Old','New'),loc='upper-right')
	plt.title('Exisiting implementation vs New /notch filter 50Hz q=5/')

	plt.show()


def all_notch(Q=10,w0=2/314.15926):
	x=range (0, 20000)
	y=range (0, 20000)
	yy=range(0, 20000)
	i=0
	while i < 4000:
		y[i]  = 220.0*m.sqrt(2)*m.sin( i/100.0)
		yy[i] = calc_rms(y[i])
		i += 1
	while i < 8000:
		y[i]  = 180.0*m.sqrt(2)*m.sin( i/100.0)
		yy[i] = calc_rms(y[i])
		i += 1
	while i < 14000:
		y[i]  = 260.0*m.sqrt(2)*m.sin( i/100.0)
		yy[i] = calc_rms(y[i])
		i += 1
	while i < len(x):
		y[i]  = 230.0*m.sqrt(2)*m.sin( i/100.0)
		yy[i] = calc_rms(y[i])
		i += 1

#notch filter
	b_notch, a_notch = signal.iirnotch(w0, Q)
	yy_notch=lfilter(b_notch, a_notch, yy)

	plt.plot (x,yy_notch)
	plt.show()





def close():
	plt.close()
	

