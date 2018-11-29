import matplotlib.pyplot as plt
import numpy as np
from scipy.signal import butter, lfilter
from scipy import signal

import math as m

A1 = 1.0
A2 = -0.5
fi2= 0;

d_theta_int16_256 = range(0,255) # scale value for firmware 

def plot_graph():
	plt.figure()
	x = np.arange(0, 6.28, 0.1)
	y = np.sin(x)
	plt.plot(x, y)
	plt.show()

def create():
	x     = range(0,20000)
	y1    = range(0,20000)
	y12   = range(0,20000)
	for i in range(0,20000):
		theta = i/100.0
		y1[i]=A1*m.sin(theta)
		y12[i]=y1[i]+A2*m.sin(2*theta+fi2)
		alpha = i % (200.0*m.pi)
	plt.plot (x,y1,y12)
	plt.legend(('first','first&second'),loc='upper-right')
	plt.title('Harmonics visualization')
	plt.show()


def c_sin():
	x      = range(0,20000)
	y_d    = range(0,20000)
	y_sum  = range(0,20000)

	for i in range(0,20000):
		theta = i/100.0
		y_d[i]=Ld*m.sin(theta)
		alpha = i % (200.0*m.pi)		
		correction=0
		if alpha>=(100*m.pi/3) and alpha<=(200*m.pi/3):			# pi/3...2*pi/3
			if alpha<=(100*m.pi/2):
				a_corr=(alpha-(100*m.pi/3))/(100*m.pi/6)
			else:
				a_corr=((200*m.pi/3)-alpha)/(100*m.pi/6)
			angle=0.09*(alpha-(100*m.pi/3))
			correction=-a_corr*(Lq-Ld)*m.sin(angle)
		y_sum[i]= Ld*m.sin(theta)+correction



	plt.plot (x,y_d,y_sum)
	plt.legend(('first','second'),loc='upper-right')
	plt.title('Back EMF cacluation')

	plt.show()

def c_sin2():
	x      = range(0,2000)
	y_d    = range(0,2000)
	y_sum  = range(0,2000)

	for i in range(0,2000):
		theta = i/100.0
		y_d[i]=Lq*m.sin(theta)
		alpha = i % (200.0*m.pi)		
		correction=0
		if alpha>=(100*m.pi/6) and alpha<=(100*m.pi/3):			# pi/6...pi/3
			angle=0.06*(alpha-(100*m.pi/6))
			correction=0.2*(Lq-Ld)*m.sin(angle)
			
		if alpha>=(200*m.pi/3) and alpha<=(500*m.pi/6):			# 2pi/3...5pi/6
			angle=0.06*(alpha-(500*m.pi/6))
			correction=-0.2*(Lq-Ld)*m.sin(angle)
		y_sum[i]= Lq*m.sin(theta)-correction



	plt.plot (x,y_sum)
	plt.legend(('first','second'),loc='upper-right')
	plt.title('Back EMF cacluation')

	plt.show()

def c_sin3():
	x      = range(0,2000)	# angle
	y_q    = range(0,2000)  # ideal sin wave Uq ->Lq
	y_sum  = range(0,2000)	# bafang back EMF.
	corr_theta =  range(0,2000) # angle from bafang backEMF waveform
	normal_theta =range(0,2000) # angle from ideal sin waveform
	d_theta      =range(0,2000)
	#256 bytes tables
	x_256       = range(0,255)
	d_theta_256 = range(0,255)

	for i in range(0,2000):
		theta = i/100.0
		y_q[i]=Lq*m.sin(theta)
		alpha = i % (200.0*m.pi)		
		correction=0
		if alpha>=(100*m.pi*0.20) and alpha<=(100*m.pi/3):			# 36,00....60deg
			correction = (Lq-Ld)*((alpha-100*m.pi*0.20)/(100*m.pi*(1.0/3.0-0.2)))**1
		if alpha>(100*m.pi/3) and alpha<=(100*m.pi*0.388):			# 60.....70deg
			dV = (5.09425 - 1.87844)/5.09425
			correction = (Lq-Ld) - (Lq-Ld)*dV*((alpha-100*m.pi/3)/(100*m.pi*(0.388-1.0/3)))
		if alpha>(100*m.pi*0.388) and alpha<=(100*m.pi*0.5):			# 70.....90deg
			dV = 1.87844/5.09425
			correction = (Lq-Ld)*dV*((100*m.pi*0.5-alpha)/(100*m.pi*(0.5- 0.388)))**3
		##correction for 90....180deg.
		if alpha>=(200*m.pi/3) and alpha<=(100*m.pi*0.8):			# 120 .....144deg
			correction = (Lq-Ld)*((100*m.pi*0.8-alpha)/(100*m.pi*(0.8-2.0/3)))**1
		if alpha>(100*m.pi*0.611) and alpha<=(200*m.pi/3):			# 110.....120deg
			dV = (5.09425 - 1.87844)/5.09425
			correction = (Lq-Ld)*dV*((alpha - 100*m.pi*0.611)/(100*m.pi*(2.0/3-0.611)))
			correction = correction + (Lq-Ld)*1.87844/5.09425
		if alpha>(100*m.pi*0.5) and alpha<=(100*m.pi*0.611):			# 90.....110deg
			dV = 1.87844/5.09425
			correction = (Lq-Ld)*dV*((100*m.pi*0.5-alpha)/(100*m.pi*(0.5- 0.611)))**3
		#correction for angles180....270deg.
		if alpha>=(100*m.pi*1.20) and alpha<=(400*m.pi/3):			# 180+ 36,00....60deg
			correction = -(Lq-Ld)*((alpha-100*m.pi*1.20)/(100*m.pi*(4.0/3.0-1.2)))**1	
		if alpha>(400*m.pi/3) and alpha<=(100*m.pi*1.388):			# 180+ 60.....70deg
			dV = (5.09425 - 1.87844)/5.09425
			correction = (Lq-Ld) - (Lq-Ld)*dV*((alpha-400*m.pi/3)/(100*m.pi*(1.388-4.0/3)))
			correction = -correction
		if alpha>(100*m.pi*1.388) and alpha<=(300*m.pi*0.5):			# 180+ 70.....90deg
			dV = 1.87844/5.09425
			correction = -(Lq-Ld)*dV*((300*m.pi*0.5-alpha)/(100*m.pi*(1.5- 1.388)))**3
		#correction for 270...360 deg
		if alpha>=(500*m.pi/3) and alpha<=(100*m.pi*1.8):			# 180 + 120 .....144deg
			correction = -(Lq-Ld)*((100*m.pi*1.8-alpha)/(100*m.pi*(1.8-5.0/3)))**1
		if alpha>(100*m.pi*1.611) and alpha<=(500*m.pi/3):			# 180+ 110.....120deg
			dV= (5.09425 - 1.87844)/5.09425
			correction = (Lq-Ld)*dV*((alpha - 100*m.pi*1.611)/(100*m.pi*(5.0/3-1.611)))
			correction = correction + (Lq-Ld)*1.87844/5.09425
			correction =-correction
		if alpha>(100*m.pi*1.5) and alpha<=(100*m.pi*1.611):			# 180+ 90.....110deg
			dV = 1.87844/5.09425
			correction = -(Lq-Ld)*dV*((100*m.pi*1.5-alpha)/(100*m.pi*(1.5- 1.611)))**3
		y_sum[i]= Lq*m.sin(theta)-0.4*correction
		if alpha>=(100*m.pi*1.5) or alpha<=(100*m.pi*0.5):			# -90....+90deg
			corr_theta[i] = m.asin(y_sum[i]/Lq)
			normal_theta[i] = m.asin(y_q[i]/Lq) 
		if alpha>(100*m.pi*0.5) and alpha<(100*m.pi):				# +90....+180deg
			corr_theta[i] = m.pi/2 + m.acos(y_sum[int(i)]/Lq) 			# to be checked???? checked OK
			normal_theta[i] = m.pi/2 + m.acos(y_q[i]/Lq) 
		if alpha>(100*m.pi) and alpha<(300*m.pi/2):				# -180....-90deg
			corr_theta[i] = -m.pi - m.asin(y_sum[i]/Lq) 			# to be checked????
			normal_theta[i] = -m.pi - m.asin(y_q[i]/Lq)
		# create Theta compensation value dTheta
		d_theta[i] = corr_theta[i] - normal_theta[i]
		#resample to 256 value table 00....255 -> -pi....+pi
		i_256=0		
		if alpha>(0) and alpha<=(100*m.pi):				# 0....180deg ->index 0....128
			i_256 = int(alpha*127/(100*m.pi))
			d_theta_256[i_256] = d_theta[i]
		if alpha > (100*m.pi):						# 180....360deg -> -pi....0 ->index 0....128
			i_256 = int(128+ (alpha-100*m.pi)*127/(100*m.pi))
			d_theta_256[i_256] = -d_theta[i]			#in dq domain is always positive
		d_theta_256[127]   = 0 #workarroind for +pi	
		d_theta_int16_256[ 127 ] = 0
		d_theta_int16_256[i_256] = int(d_theta_256[i_256]*32768/m.pi)   # +pi=7fff -pi=0x8000

	print d_theta_int16_256
	#plt.plot (x,y_sum)
	#plt.plot(x,corr_theta,normal_theta)
	#plt.plot(x,corr_theta,d_theta)
	# 256 elemnts
	#plt.plot(x_256,d_theta_256)
	plt.plot(x_256,d_theta_int16_256)
	plt.legend(('corrected','ideal'),loc='upper-right')
	#plt.title('Back EMF cacluation')
	plt.title('Angle correction table')

	plt.show()


def c_cor():
	x=[36.22,38.62   ,   45.6,  51.16, 60.44 , 69.38 ,  76.8  , 90.0]
	y=[0.0  ,-0.72383,-2.43418,-3.668,-5.9425,-1.8744,-1.20737, 0 ]
	print x
	print y
	plt.plot (x,y)
	plt.title('correction curve from excel')
	plt.show()

