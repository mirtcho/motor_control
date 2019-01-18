import matplotlib.pyplot as plt
import numpy as np
from scipy.signal import butter, lfilter
from scipy import signal

import math as m

class RMS:
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



class Bafang_math:
	def I(self):
		x=range (0,800)
		y=range (0,800) #current y(t) 
		for i in range (0,800):
			y[i]= (100*abs(m.cos(2*m.pi*i/800)+4*0.028*m.cos(10*m.pi*i/800)))**0.5
		plt.plot(x,y)
		plt.show()
	def V_FF(self,a=127,n=256,h=1.0):
		self.x=range (0,n)
		self.sin_table=range (0,n) #back_emf compensation only the harmonics ripple
		for i in range(0,n):
			self.sin_table[i]=int(a*m.sin(2*m.pi*h*i/n))
		print self.sin_table
		plt.plot(self.x,self.sin_table)
		plt.show()

	def cos(self,a=127,n=256,h=1):
		x=range(0,n)
		self.cos_table=range(0,n)
		for i in range(0,n):
			self.cos_table[i]=int(a*m.cos(2*m.pi*i/n))
			print "%4d," % self.cos_table[i],
		plt.plot(x,self.cos_table)
		plt.show()

	def do_6th(self):
		y6=range(0,256)
		for theta in range(0,256):
			theta_6th = 6*theta
			y6[theta]=self.sin_table[theta_6th&0xff]
		plt.plot(self.x,y6)
		plt.show()
class Emf:
	def create(self):
		x=range (0,800)
		emf=range (0,800) #backEMF L3 to neutral
		flux_link=range (0,800)
		for i in range (0,800):
			emf[i]      = 29*m.cos(2*m.pi*i/200) - 3*m.cos(2*5*m.pi*i/200)+0.5*m.cos(2*7*m.pi*i/200)+0.75*m.cos(2*11*m.pi*i/200)          # create four periods of 200 points 200=800/4
			flux_link[i]= 29*m.sin(2*m.pi*i/200) - 3/5.0*m.sin(2*5*m.pi*i/200)+0.5/7*m.sin(2*7*m.pi*i/200)+0.75/11*m.sin(2*11*m.pi*i/200) # Calculated from equation "Flux Linkage =integral(emf) dt"
		plt.title ("Bafang sintesized BackEMF and calculated flux linkage")
		plt.legend(('EMF','FluxLnk'),loc='upper right')
		plt.plot(x,emf,flux_link)
		plt.show()
	
