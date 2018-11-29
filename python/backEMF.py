import matplotlib.pyplot as plt
import numpy as np
from scipy.signal import butter, lfilter
from scipy import signal

import math as m

Lq = 0.665
Ld = 0.397

d_theta_int16_256 = range(0,255) # scale value for firmware 

def plot_graph():
	plt.figure()
	x = np.arange(0, 6.28, 0.1)
	y = np.sin(x)
	plt.plot(x, y)
	plt.show()

def create():
	x      = range(0,20000)
	y_q    = range(0,20000)
	y_d    = range(0,20000)
	y_sum  = range(0,20000)
	y_lin  = range(0,20000)
	y_sin04_066 = range(0,20000)
	y_quad = range(0,20000)

	for i in range(0,20000):
		theta = i/100.0
		y_q[i]=Lq*m.sin(theta)
		y_d[i]=Ld*m.sin(theta)
		alpha = i % (200.0*m.pi)
		#calculate L_lin 
		l_quad=0.0;
		if alpha>=0.0 and alpha<=(100*m.pi/2.0):			# 0...pi/2
			fraction=alpha/(50.0*m.pi)
			l_lin=Ld+(Lq-Ld)*fraction
			l_quad= Ld+(Lq-Ld)*fraction*fraction
		if alpha>(50.0*m.pi) and alpha<=(100.0*m.pi): 			# pi/2....pi
			l_lin=Lq - (Lq-Ld)*(alpha-(50.0*m.pi)) /(50.0*m.pi) 	# Lin = lq - (lq-ld)* (Alpha-90deg)/90deg
		if alpha>(100.0*m.pi) and alpha<=(150.0*m.pi):	 		# pi....3*pi/2
			l_lin=Ld + (Lq-Ld)*(alpha-(100*m.pi))/(50*m.pi) 	# Lin = ld+ (lq-ld)* (Alpha-180deg)/90deg
		if alpha> (150.0*m.pi) and alpha<(200.0*m.pi): 			# 3*pi/2....2*pi
			l_lin=Lq - (Lq-Ld)*(alpha-(150*m.pi))/(50*m.pi) 	# Lin = lq+ (lq-ld)* (Alpha-270deg)/90deg
		y_lin[i]= l_lin*m.sin(theta)
		y_quad[i]=l_quad*m.sin(theta)
		#calc y -sum sin(Theta)
		y_sum[i]=Lq*m.sin(theta)*Ld*m.cos(theta) + Lq*m.cos(theta)*Ld*m.sin(theta)
		#calc sin....0,397....0,665
		a=0.5*(Lq+Ld)+0.5*(Lq-Ld)*m.sin(2*theta)
		y_sin04_066[i]=a*m.sin(theta)



	plt.plot (x,y_lin,y_quad)
	plt.legend(('first','second'),loc='upper-right')
	plt.title('Back EMF cacluation')

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

