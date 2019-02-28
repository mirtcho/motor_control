import matplotlib.pyplot as plt
import numpy as np
from scipy.signal import butter, lfilter
from scipy import signal
#next two imports are needed for chebishev and cauer optimal filter design
from scipy.signal import fir_filter_design as ffd
from scipy.signal import filter_design as ifd


import math as m
import csv

class Speed:
	Count = 0   # This represents the count of objects of this class
	def __init__(self):
		Speed.Count += 1
		print Speed.Count, 'Speed objects active'
		print("init arg=",self)
		self.gFname ='empty'
		self.MAX_FILE_LEN = 1150000
		self.displacement= range(0,self.MAX_FILE_LEN)
		self.position    = range(0,self.MAX_FILE_LEN)
		self.x           = range(0,self.MAX_FILE_LEN)

	def __del__(self):
	        Speed.Count -= 1
        	if Speed.Count == 0:
	            print 'Last Speed object deleted'
	        else:
	            print Speed.Count, 'Speed objects remaining'

	def read_file(self,fname='/mnt/hgfs/vm_share/trace/LowSpeed13ms_12Msps.txt'):
		i=0
		self.gFname=fname
		f = open (fname,"r")
		for ln_str in f:
			if i< self.MAX_FILE_LEN: # Skip last file lines. For overflow protection
				#remove header info from the first 13 lines
				if i>13:
					position_str= ln_str[1:-4]
					self.position[i-13] = int(position_str)
					if i>14:
						self.displacement[i-14]=(self.position[i-13]-self.position[i-14])
				else:
					self.position[i] = 0
					self.displacement[i]=0		
				if (i/1000.0) == int(i/1000):
					print ("position=%d  displacement=%d ",self.position[i-13],self.displacement[i-14])
				i=i+1
		f.close()
		self.TotalNrOfIncrements = i;
		print ("read lines =",i)		
		print("gFname=",self.gFname)
		plt.plot (self.x[8000:i-600],self.displacement[8000:i-600])
		plt.legend(('displacement'),loc='upper right')
		plt.title('Speed vs time')
		plt.show()

	def do_fft(self,n=65536,offset=100000):
		f=range(0,n)
		f_cpx= np.fft.fft(self.displacement[offset:offset+n])
		## workaaround to filter low freq . Please remove it. Used for presentation to bafang
		#for i in range (0,10):
		#	f_cpx.real[i]=0.0
		#	f_cpx.imag[i]=0.0
		#for i in range (10,240):
		#	f_cpx.real[i]= f_cpx.real[i]/50.0
		#	f_cpx.imag[i]= f_cpx.imag[i]/50.0
		#end workaround 
		plt.legend(('real','img'),loc='upper right')
		plt.plot(f,f_cpx.real,f_cpx.imag)
		plt.title('Velocity ripple spectrum '+self.gFname)
		plt.show()

	def do_fftr(self,n=65536,offset=100000):
		f=range(0,n)
		amplitude = range(0,n)
		f_cpx= np.fft.fft(self.displacement[offset:offset+n])
		for i in range (0,n):
			amplitude[i] = (f_cpx.real[i]*f_cpx.real[i]+f_cpx.imag[i]*f_cpx.imag[i])**0.5
			f[i]=f[i]   # *1024/n  # we have 1024 increments/rev - we use only S0 singal of 2048in/rev encoder
		plt.plot(f,amplitude)
		plt.title('Velocity ripple spectrum Amplitude'+self.gFname)
		plt.show()

	def do_lpf(self,ts=0.1,order=4,w0=1.0/512,Q=15):
		disp_lpf       = range(0,self.TotalNrOfIncrements)
		disp_lpf_notch = range(0,self.TotalNrOfIncrements)
		#design lpf filter
		b,a = butter (order,ts, 'low', False)
		disp_lpf = lfilter(b, a, self.displacement)
		# add notch filer - remove encoder misalignment
		b_notch, a_notch = signal.iirnotch(w0, Q)
		disp_lpf_notch=lfilter(b_notch, a_notch, disp_lpf)
		#plot graph
		plt.grid(which='both',axis='both')		
		plt.plot(self.x[50:self.TotalNrOfIncrements-1000],disp_lpf[50:self.TotalNrOfIncrements-1000], disp_lpf_notch[50:self.TotalNrOfIncrements-1000])
		#plt.plot(self.x[50:self.TotalNrOfIncrements-1000], disp_lpf_notch[50:self.TotalNrOfIncrements-1000])
		plt.legend(('lpf','lpf_notch'),loc='upper right')
		plt.title('Velocity ripple vs time '+self.gFname)
		plt.xlabel ('Increments')
		plt.ylabel ('Speed')
		plt.show()

	def do_filter(self,ts=1.0/30.0,order=6,max_deviation=6000):
		x=range(0,self.MAX_FILE_LEN)
		y2=range(0,self.MAX_FILE_LEN)
		y2_lpf=range(0,self.MAX_FILE_LEN)
		y2=self.displacement
		#do selective average 2 filter
		for i in range (0, self.MAX_FILE_LEN-4):	
			if abs(y2[i+1] - y2[i]) > max_deviation: #bigger than 5usec
				y2[i]  = (y2[i]+y2[i+1])/2
				y2[i+1]= (y2[i]+y2[i+1])/2
		#design lpf filter
		b,a = butter (order,ts, 'low', False)
		y2_lpf = lfilter(b, a, y2)
		#***************************
		#* design chebishev filter *
		#***************************
		# remez (fir) design arguements
		#Fpass = 10e6    # passband edge
		#Fstop = 11.1e6  # stopband edge, transition band 100kHz
		Wp = ts/2    	# pass normalized frequency=Fpass/(Fs)
		Ws = Wp *3.0   	# stop normalized frequency
		# iirdesign agruements
		Wip = 2*Wp 	# (Fpass)/(Fs/2)
		Wis = 2*Ws 	# (Fstop+1e6)/(Fs/2)
		Rp = 1          # passband ripple
		As = 120        # stopband attenuation
		# Create a FIR filter, the remez function takes a list of 
		# "bands" and the amplitude for each band.
		taps = 256 # was in example 4096, works good with 256
		br = ffd.remez(taps, [0, Wp, Ws, .5], [1,0], maxiter=100000) 
		print ('Remez out=',br)
		# The iirdesign takes passband, stopband, passband ripple, 
		# and stop attenuation.
		bc, ac = ifd.iirdesign(Wip, Wis, Rp, As, ftype='ellip')  
		bb, ab = ifd.iirdesign(Wip, Wis, Rp, As, ftype='cheby2')
		print ("Bc=", bc)
		print ("Ac=", ac)
		print ("Bb=", bb)
		print ("Ab=", ab)
		yc=signal.filtfilt(bc,ac,y2)
		yb=signal.filtfilt(bb,ab,y2)
		b_ind = 100000 #begin of plot index
		e_ind =-5000  #end offset
		plt.xlabel ('Inc')
		plt.ylabel ('ns/inc')
		plt.grid(which='both',axis='both')
		plt.plot(x[b_ind:e_ind], y2_lpf[b_ind:e_ind], x[b_ind:e_ind], yc[b_ind:e_ind] ,x[b_ind:e_ind],yb[b_ind:e_ind])
		plt.legend(('lpf','ele','che'),loc='upper right')
		plt.title('Velocity ripple filtered '+self.gFname)
		plt.show()
		#second plot is only filtered
		plt.grid(which='both',axis='both')
		plt.plot(x[b_ind:e_ind],yc[b_ind:e_ind])
		plt.title('Velocity ripple filtered '+self.gFname)
		plt.show()
		print ("yc[200000:200010]=",yc[200000:200010])
		print ("yb[200000:200010]=",yb[200000:200010])


	def diplacement_to_speed(self):
		#create position sector every 10usec
		a=1
		print(a)

	def park7(self):
		self.xx=range(0,800)
		self.ya=range(0,800)
		self.yb=range(0,800)
		self.q =range(0,800)
		self.d =range(0,800)
		for i in range(0,800):
			angle=i*m.pi/200
			h1_angle=5*angle
			h2_angle=7*angle
			self.yb[i]=30*m.sin(angle)+3*m.sin(h1_angle)+1.5*m.sin(h2_angle)
			self.ya[i]=30*m.cos(angle)+3*m.cos(h1_angle)+1.5*m.cos(h2_angle)
			self.d[i] =self.ya[i]*(m.cos(angle)-0.1*m.cos(h1_angle)-0.05*m.cos(h2_angle)) + self.yb[i]*(m.sin(angle)-0.1*m.sin(h1_angle)-0.05*m.sin(h2_angle))
			self.q[i] =self.yb[i]*(m.cos(angle)+0.1*m.cos(h1_angle)+0.05*m.cos(h2_angle)) - self.ya[i]*(m.sin(angle)+0.1*m.sin(h1_angle)+0.05*m.sin(h2_angle))
		plt.plot(self.xx,self.d,self.q)
		#plt.plot(self.xx,self.yb,self.d) # D is arround 0 Q~30
		plt.title('DQ transformation test')
		plt.legend(('D','Q'),loc='upper right')
		plt.show()

	def calc_aplha_beta(self,offset=0.0):
		self.xx=range(0,800)
		self.ya=range(0,800)
		self.yb=range(0,800)
		ia=range(0,800)
		ib=range(0,800)
		ic=range(0,800)
		yc=range(0,800)
		#park matrix
		T=[[2.0/3.0,-1.0/3.0,-1.0/3.0],[0,1.0/m.sqrt(3.0),-1.0/m.sqrt(3.0)],[1.0/3.0,1.0/3.0,1.0/3.0]]
		for i in range(0,800):
			angle=i*m.pi/200
			h1_angle=5*angle
			# create 3 phases Ia,Ib,Ic signals
			ia[i] = 1.0*m.sin(angle+offset)+0.07*m.sin(h1_angle+5*offset)
			ib[i] = 1.0*m.sin(angle+2*m.pi/3+offset)+0.07*m.sin(h1_angle+10*m.pi/3+5*offset)
			ic[i] = 1.0*m.sin(angle+4*m.pi/3+offset)+0.07*m.sin(h1_angle+20*m.pi/3+5*offset)
			#convert to alpha beta
			self.ya[i] = T[0][0]*ia[i]+T[0][1]*ib[i]+T[0][2]*ic[i]
			self.yb[i] = T[1][0]*ia[i]+T[1][1]*ib[i]+T[1][2]*ic[i]
			yc[i]      = T[2][0]*ia[i]+T[2][1]*ib[i]+T[2][2]*ic[i]
		#show input signals
		#plt.plot(self.xx,ia, self.xx,ib, self.xx,ic)
		#plt.title('Input signals Ia,IB with Ic 5-th harmonics')
		#plt.legend(('Ia','Ib','Ic'),loc='upper right')
		#plt.show()
		# show alpha beta 
		plt.plot(self.xx,self.ya, self.xx,self.yb, self.xx,yc)
		plt.title('ALpha transformation test with 5-th harmonics')
		plt.legend(('Alpha','Beta','Gama'),loc='upper right')
		plt.show()

	def park(self,offset=0):
		self.q =range(0,800)
		self.d =range(0,800)
		#create alpha beta signals
		self.calc_aplha_beta(offset)
		for i in range(0,800):
			angle=i*m.pi/200
			h1_angle=5*angle
			#real park
			self.d[i] =self.ya[i]*m.sin(angle) + self.yb[i]*m.cos(angle) # adds -0.07*cos(6*angle)
			self.q[i] =self.yb[i]*m.sin(angle) - self.ya[i]*m.cos(angle) # adds -0.07*sin(6*angle)

		plt.plot(self.xx,self.d,self.q)		
		plt.title('DQ transformation test with 5-th harmonics')
		plt.legend(('D','Q'),loc='upper right')
		plt.show()

	def park5(self,offset=0):
		self.q =range(0,800)
		self.d =range(0,800)
		#create alpha beta signals
		self.calc_aplha_beta(offset)
		for i in range(0,800):
			angle=i*m.pi/200
			h1_angle=5*angle
			#self.d[i] =self.ya[i]*(m.cos(angle)-0.07*m.cos(h1_angle)) + self.yb[i]*(m.sin(angle)-0.07*m.sin(h1_angle))
			#self.q[i] =self.yb[i]*(m.cos(angle)+0.07*m.cos(h1_angle)) - self.ya[i]*(m.sin(angle)+0.07*m.sin(h1_angle))
			#park pest tested works fine at 0 deg offset
			self.d[i] =self.ya[i]*(m.sin(angle)-0.07*m.sin(h1_angle)) + self.yb[i]*(m.cos(angle)+0.07*m.cos(h1_angle))##works dont tuch it!!!!
			self.q[i] =self.yb[i]*(m.sin(angle)+0.07*m.sin(h1_angle)) - self.ya[i]*(m.cos(angle)-0.07*m.cos(h1_angle))##works dont tuch it!!!!
		plt.plot(self.xx,self.d,self.q)		
		plt.title('DQ transformation test with 5-th harmonics')
		plt.legend(('D','Q'),loc='upper right')
		plt.show()

	def inv_park5(self):
		self.calc_ya= range(0,800)
		self.calc_yb= range(0,800)
		for i in range(0,800):
			angle=i*m.pi/200
			h1_angle=5*angle
			self.calc_ya[i] = self.q[i]*(m.cos(angle)+0.07*m.cos(h1_angle)) + self.d[i]*(m.sin(angle)+0.07*m.sin(h1_angle))#works with Iq=0
			self.calc_yb[i] = self.d[i]*(m.cos(angle)-0.07*m.cos(h1_angle)) - self.q[i]*(m.sin(angle)-0.07*m.sin(h1_angle))#works with Iq=0
		plt.plot(self.xx,self.calc_ya,self.calc_yb)
		#plt.plot(self.xx,self.ya,self.yb)
		plt.title('DQ Inverse transformation test with 5-th harmonics')
		plt.legend(('Alpha','Beta'),loc='upper right')
		plt.show()

	def inv_clark5(self):
		#not ready yet !!!
		self.calc_ia= range(0,800)
		self.calc_ib= range(0,800)
		self.calc_ic= range(0,800)
		T=[[1.0,0.0,1.0],[-0.5,m.sqrt(3)/2,1.0],[-0.5,-m.sqrt(3)/2,1.0]]
		for i in range(0,800):
			self.calc_ia[i]=T[0][0]*self.calc_ya[i] + T[0][1]*self.calc_yb[i] #gamma is zero
			self.calc_ib[i]=T[1][0]*self.calc_ya[i] + T[1][1]*self.calc_yb[i] #gamma is zero
			self.calc_ic[i]=T[2][0]*self.calc_ya[i] + T[2][1]*self.calc_yb[i] #gamma is zero
		#plot
		plt.plot(self.xx,self.calc_ia,self.xx,self.calc_ib,self.xx,self.calc_ic)
		plt.title('Inverse clark with 5-th harmonics')
		plt.legend(('Ia','Ib','Ic'),loc='upper right')
		plt.show()

	def sim_2d5(self):
		x=range(0,5*256)
		y1=range(0,5*256)
		for i in range(0,5*256):
			fi1=2*i*m.pi/(5*256) #0...2pi
			fi5=2*i*m.pi/256     #0..10pi
			a1=1.0
			a5=0.07
			x[i]=a1*m.cos(fi1)+a5*m.cos(fi5)
			y1[i]=a1*m.sin(fi1)+a5*m.sin(fi5)
		plt.plot(x,y1)
		plt.show()

	def do_fft_exaple(self):
		x=range(0,2048)
		f=range(0,2048)
		i=0
		for i in range (0,2048):
			x[i]=123*m.sin(m.pi*i/128)
		f_cpx= np.fft.fft(x)
		plt.plot(f,f_cpx.real,f_cpx.imag)
		plt.show()

	def c_cor(self):
		x=[36.22,38.62   ,   45.6,  51.16, 60.44 , 69.38 ,  76.8  , 90.0]
		y=[0.0  ,-0.72383,-2.43418,-3.668,-5.9425,-1.8744,-1.20737, 0 ]
		print x
		print y
		plt.plot (x,y)
		plt.title('correction curve from excel')
		plt.show()

class Emf2():
	def __init__(self):
		# init static vars
		self.xx=range(0,800)
		#input signals time domain
		self.ia_ref=range(0,800)
		self.ia=range(0,800)
		self.ib=range(0,800)
		self.ic=range(0,800)
		# alpha beta gamma
		self.ya=range(0,800)
		self.yb=range(0,800)
		self.yc=range(0,800)
		#dq
		self.q1 =range(0,800)
		self.d1 =range(0,800)
		self.q5 =range(0,800)
		self.d5 =range(0,800)
		self.d1_av=range(0,800)# used by back tranformation for sim model
		self.q1_av=range(0,800)
		# inverse calculated signals 
		#alpha beta
		self.calc_ya= range(0,800)
		self.calc_yb= range(0,800)
		#time domain 3 phase
		self.calc_ia= range(0,800)
		self.calc_ib= range(0,800)
		self.calc_ic= range(0,800)

	def calc_aplha_beta(self,offset=0.0):
		#park matrix
		#T=[[2.0/3.0,-1.0/3.0,-1.0/3.0],[0,1.0/m.sqrt(3.0),-1.0/m.sqrt(3.0)],[1.0/3.0,1.0/3.0,1.0/3.0]] # from wikipedia
		T=[[1.0,0,0],[1.0/m.sqrt(3),2.0/m.sqrt(3),0],[0,0,0]] # from arm lib
		for i in range(0,800):
			angle=i*m.pi/200
			h1_angle=5*angle
			#create reference signal - only fundamental
			self.ia_ref[i]=1.0*m.cos(angle+offset)
			# create 3 phases Ia,Ib,Ic signals
			self.ia[i] = 1.0*m.cos(angle+offset)+0.07*m.cos(h1_angle+5*offset)
			self.ic[i] = 1.0*m.cos(angle+2*m.pi/3+offset)+0.07*m.cos(h1_angle+10*m.pi/3+5*offset)
			self.ib[i] = 1.0*m.cos(angle+4*m.pi/3+offset)+0.07*m.cos(h1_angle+20*m.pi/3+5*offset)
			#convert to alpha beta
			self.ya[i] = T[0][0]*self.ia[i]+T[0][1]*self.ib[i]+T[0][2]*self.ic[i] # y coordinate stator
			self.yb[i] = T[1][0]*self.ia[i]+T[1][1]*self.ib[i]+T[1][2]*self.ic[i] # x coordinate stator
			self.yc[i] = T[2][0]*self.ia[i]+T[2][1]*self.ib[i]+T[2][2]*self.ic[i]
		#show input signals abc frame
		plt.plot(self.xx,self.ia, self.xx,self.ib, self.xx,self.ic)
		plt.title('Input signals Ia,IB with Ic 5-th harmonics')
		plt.legend(('Ia','Ib','Ic'),loc='upper right')
		plt.show()
		# show alpha beta frame
		plt.plot(self.xx,self.ya, self.xx,self.yb, self.xx,self.yc)
		plt.title('ALpha transformation test with 5-th harmonics')
		plt.legend(('Alpha','Beta','Gama'),loc='upper right')
		plt.show()

	def clark(self,offset=0):
		#create alpha beta signals with 5-th harmomic
		self.calc_aplha_beta(offset)
		d1_av=0
		q1_av=0
		for i in range(0,800):
			stator_angle=i*m.pi/200
			theta=stator_angle-m.pi/2.0- 0*m.pi/2 #		
			#real park
			self.d1[i] =  self.ya[i]*m.cos(theta) + self.yb[i]*m.sin(theta) 
			self.q1[i] = -self.ya[i]*m.sin(theta) + self.yb[i]*m.cos(theta)
			d1_av = d1_av+self.d1[i]
			q1_av = q1_av+self.q1[i]
		d1_av=d1_av/800
		q1_av=q1_av/800
		print "d1_av=",d1_av,"q1_av=",q1_av
		for i in range(0,800):
			angle=i*m.pi/200
			theta=angle-0*m.pi/2 # -90degree from stator vector to make Id=0			
			h1_angle=6*theta
			self.d5[i] = (self.q1[i]-q1_av) *m.cos(h1_angle) + (self.d1[i]-d1_av) *m.sin(h1_angle) 
			self.q5[i] =-(self.q1[i]-q1_av) *m.sin(h1_angle) + (self.d1[i]-d1_av) *m.cos(h1_angle)  # from wikipedia - arm librrary was negative
			self.d1_av[i]=d1_av  # vector used by back transformation
			self.q1_av[i]=q1_av
		plt.plot(self.xx,self.d1,self.q1)		
		plt.title('DQ transformation test with 5-th harmonics')
		plt.legend(('D1','Q1'),loc='upper right')
		plt.show()
		plt.plot(self.xx,self.d5,self.q5)		
		plt.title('DQ transformation test with 5-th harmonics')
		plt.legend(('D5','Q5'),loc='upper right')
		plt.show()

	def inv_park(self):
		for i in range(0,800):
			angle=i*m.pi/200
			theta=angle # -90degree from stator vector to make Id=0
			h1_angle=5*theta
			y1b=self.d1_av[i]*m.cos(theta)    - self.q1_av[i]*m.sin(theta)  ## alpha and beta for H1 and h5 are swaped????????????
			y1a=self.d1_av[i]*m.sin(theta)    + self.q1_av[i]*m.cos(theta)
			y5a=self.d5[i]   *m.cos(h1_angle) - self.q5[i]   *m.sin(h1_angle)
			y5b=self.d5[i]   *m.sin(h1_angle) + self.q5[i]   *m.cos(h1_angle)
			self.calc_ya[i]=(y1a+y5a)
			self.calc_yb[i]=(y1b+y5b) 
		plt.plot(self.xx,self.calc_ya,self.calc_yb)
		#plt.plot(self.xx,self.ya,self.yb)
		plt.title('DQ Inverse transformation test with 5-th harmonics')
		plt.legend(('Alpha','Beta'),loc='upper right')
		plt.show()


	def inv_clark(self):
		T=[[1.0,0.0,1.0],[-0.5,m.sqrt(3)/2,1.0],[-0.5,-m.sqrt(3)/2,1.0]]#from wikipedia
		for i in range(0,800):
			self.calc_ia[i]=T[0][0]*self.calc_ya[i] + T[0][1]*self.calc_yb[i] #gamma is zero  
			self.calc_ib[i]=T[1][0]*self.calc_ya[i] + T[1][1]*self.calc_yb[i] #gamma is zero
			self.calc_ic[i]=T[2][0]*self.calc_ya[i] + T[2][1]*self.calc_yb[i] #gamma is zero
		#plot
		plt.plot(self.xx,self.calc_ia,self.xx,self.calc_ib,self.xx,self.calc_ic)
		plt.title('Inverse clark with 5-th harmonics')
		plt.legend(('Ia','Ib','Ic'),loc='upper right')
		plt.show()

	def test(self,offset=0):
		self.clark(offset)
		self.inv_park()
		self.inv_clark()
		plt.plot(self.xx,self.ia,self.xx,self.calc_ia)
		plt.title('Test graph whole tranformation')
		plt.legend(('Ia','Ia_calc'),loc='upper right')
		plt.show()

	def test2(self,offset=0,d5_attn=0.0,q5_attn=1.0): # test signal with zero Iq6-th harm
		self.clark(offset)
		for i in range(0,800): # attenuate d and q 5-th harmomics
			self.d5[i]= self.d5[i] * d5_attn
			self.q5[i]= self.q5[i] * q5_attn
		self.inv_park()
		self.inv_clark()
		plt.plot(self.xx,self.ia,self.xx,self.calc_ia,self.xx,self.ia_ref)
		plt.title('Test graph whole tranformation')
		plt.legend(('Ia','Ia_calc',"IaCos"),loc='upper right')
		plt.show()

class Fixed:
	Count = 0   # This represents the count of objects of this class
	def __init__(self):
		Fixed.Count += 1
		print Fixed.Count, 'Fixed objects active'
		self.sin_table=range(0,65)
		#fill in the table
		for i in range (0,65):
			self.sin_table[i]=int((1-0.07)*0xffffffff*m.sin(i*m.pi/128)) # 0...pi/2
			print ',',hex(self.sin_table[i]);
		print("init arg=",self)
		# init static vars

	def __del__(self):
	        Fixed.Count -= 1
        	if Fixed.Count == 0:
	            print 'Last Fixed object deleted'
	        else:
	            print Fixed.Count, 'Fixed objects remaining'

	def sin(self,angle): #angle 32bit signed -127...+127-> -pi..+pi
		ret_val=0
		i_angle = angle & 0xff # go to one period -pi...+pi
		if i_angle>=0 and i_angle<=0x40: #0...+pi/2
			ret_val=self.sin_table[i_angle]
		if i_angle>0x40 and i_angle<=0x80: # +pi/2...+pi
			ret_val=self.sin_table[0x40-(i_angle-0x40)]
		if i_angle>0x80 and i_angle<=0xc0: #???
			ret_val=-self.sin_table[i_angle-0x80]
		if i_angle>0xc0 and i_angle<=0xff: # ???
			ret_val=-self.sin_table[0x40-(i_angle-0xc0)]
		return ret_val

	def cos(self,angle): #angle 32bit signed -127...+127-> -pi..+pi
		ret_val=0
		i_angle = angle & 0xff # go to one period -pi...+pi
		if i_angle>=0 and i_angle<=0x40: #0...+pi/2
			ret_val=self.sin_table[0x40-i_angle]
		if i_angle>0x40 and i_angle<=0x80: # +pi/2...+pi
			ret_val=-self.sin_table[i_angle-0x40]
		if i_angle>0x80 and i_angle<=0xc0: #???
			ret_val=-self.sin_table[0x40-(i_angle-0x80)]
		if i_angle>0xc0 and i_angle<=0xff: # ???
			ret_val=self.sin_table[i_angle-0xc0]
		return ret_val

	def print_sin_table(self):		
		x=range(0,65)
		plt.plot(x,self.sin_table)
		plt.show()

	def test_sin(self):		
		x    =range(0,512)
		y_sin=range(0,512)
		y_cos=range(0,512)
		for i in range (0,512):
			y_sin[i]=self.sin(i)
			y_cos[i]=self.cos(i)
		plt.plot(x,y_sin,y_cos)
		plt.show()

	def do_sin_table_ready(self,Iq=1024,factor=0.15):
		#this function create 256 element in16_t table ready to use for firmware in performas normalization of factor 0.15
		# assumption is that Iq=1024
		# Icomp = 0.15*Iq*sin(alpha)
		x = range(0,256)
		sin_table_ready=range(0,256)
		for i in range(0,256):
			sin_table_ready[i]=int (1024*0.15*m.sin(2*m.pi*i/256))
		print sin_table_ready
		plt.plot(x,sin_table_ready)
		plt.show()

	
class Emf:
	Count = 0   # This represents the count of objects of this class
	def __init__(self):
		Emf.Count += 1
		print Emf.Count, 'Emf objects active'
		print("init arg=",self)
		self.MAX_FILE_LEN = 14000010  # scope has 14MPoints
		self.len = 2000000
		self.u_vs_t = range (0,self.len) # one period of backEMF volatge
		self.i_vs_t = range (0,self.len) # one period of backI_EMF scaled up/down to reference back_U_EMF
		self.dIdT   = range (0,self.len) # used for inductance calculation L(t)
		self.t      = range (0,self.len) # time axis

	def __del__(self):
	        Emf.Count -= 1
        	if Emf.Count == 0:
	            print 'Last Emf object deleted'
	        else:
	            print Emf.Count, 'Emf objects remaining'

	def find_zero_emf(self,wave_form,bIndex=0, eIndex=13999999,treshold=0.05):
		for i in range(bIndex,eIndex):
			if (wave_form[i]) >=treshold:
				return i
		return i

	def scopeEMF(self, fname='/mnt/hgfs/vm_share/trace/BackEMF_rigol.csv'):
		# read the scope CSV file
		scope_uemf= range(0,self.MAX_FILE_LEN)
		x         = range(0,self.MAX_FILE_LEN)
		with open(fname) as csv_file:
			csv_reader = csv.reader(csv_file, delimiter=',')
			line_count = 0
			for row in csv_reader:
				if line_count == 0:
					print('Column names are {", ".join(row)}')
					line_count += 1
				else:
					if line_count>3 and line_count < 14000000:					
						scope_uemf[line_count] = float(row[1])
						#print line_count,',',self.scope_uemf[line_count]
					line_count += 1					
		    	print('Processedlines',line_count)
		csv_file.close()
		#find reference backUEMF period and create self.UvsT[] and self.len
		#one period find manualy from the whole scoipe capture
		bIndex = self.find_zero_emf(scope_uemf,7050000,13999999,0.25)
		eIndex = self.find_zero_emf(scope_uemf,7250000,13999999,0.25)
		#design lpf filter
		order=6
		ts = 0.002
		b,a = butter (order,ts, 'low', False)
		self.u_vs_t[0:eIndex-bIndex] = lfilter(b, a, scope_uemf[bIndex:eIndex])
		self.u_vs_t[0]=0
		self.u_vs_t[eIndex-bIndex]=0
		#find the filtered zero cross point
		self.u_vs_t_bbIndex = self.find_zero_emf(self.u_vs_t,500,eIndex-bIndex,0.0)
		self.u_vs_t_eeIndex = self.find_zero_emf(self.u_vs_t,int(0.8*(eIndex-bIndex)),eIndex-bIndex,0.0)
		scope_ts=1.0e-7
		self.u_period       =scope_ts*(self.u_vs_t_eeIndex - self.u_vs_t_bbIndex)
		self.u_nr_ofsample_per_period= self.u_vs_t_eeIndex - self.u_vs_t_bbIndex
		# plot in time domain
		#plt.plot(x[20:13999900],scope_uemf[20:13999900])
		plt.plot(self.t[0:eIndex-bIndex],scope_uemf[bIndex:eIndex],self.t[0:eIndex-bIndex],self.u_vs_t[0:eIndex-bIndex])
		plt.title('Bafang BackUEMF scope waveform')
		plt.legend(('NonFilter','LPF'),loc='upper right')
		plt.show()

	def scopeIEMF(self, fname='/mnt/hgfs/vm_share/trace/BackIEMF_rigol_use3_4period.csv'):
		#read the scope CSV file
		scope_iemf= range(0,self.MAX_FILE_LEN)
		x         = range(0,self.MAX_FILE_LEN)
		with open(fname) as csv_file:
			csv_reader = csv.reader(csv_file, delimiter=',')
			line_count = 0
			for row in csv_reader:
				if line_count == 0:
					print('Column names are {", ".join(row)}')
					line_count += 1
				else:
					if line_count>3 and line_count < 14000000:					
						scope_iemf[line_count] = float(row[1])
						#print line_count,',',self.scope_emf[line_count]
					line_count += 1					
		    	print('Processedlines',line_count)
		csv_file.close()
		#get the BeginIndex and Endindex of 3-th period
		bIndex = self.find_zero_emf(scope_iemf,10000000,13999999,-0.15)
		eIndex = self.find_zero_emf(scope_iemf,10500000,13999999,0.45)
		#filter the I_EMF()
		order=4
		ts = 0.001
		b,a = butter (order,ts, 'low', False)
		lpf_i_vs_t=range(0,eIndex-bIndex)
		lpf_i_vs_t[0:eIndex-bIndex] = lfilter(b, a, scope_iemf[bIndex:eIndex])
		# find the real zero cross after filtering
		bbIndex = self.find_zero_emf(lpf_i_vs_t,3000,eIndex-bIndex,0.0)
		eeIndex = self.find_zero_emf(lpf_i_vs_t,int(0.8*(eIndex-bIndex)),eIndex-bIndex,0.0)
		scope_ts=2.5e-7
		self.i_period=scope_ts*(eeIndex-bbIndex)
		i_nr_of_sample_per_period = eeIndex-bbIndex
		# rescale the IEMF to reference UEMF and create self.IvsT[]
		amplitude_scale = self.i_period/self.u_period  						# time based scaling Ts-scope taken into account
		self.i_vs_t = range(0,self.u_nr_ofsample_per_period)
		for i in range (0,self.u_nr_ofsample_per_period):
			self.i_vs_t[i]=amplitude_scale*lpf_i_vs_t[int(i*i_nr_of_sample_per_period/self.u_nr_ofsample_per_period)]
		# plot in time domain
		#plt.plot(x[bIndex:eIndex],scope_iemf[bIndex:eIndex],x[bIndex:eIndex],lpf_i_vs_t[0:eIndex-bIndex])
		#plt.title('Bafang Current BackIEMF scope waveform')
		#plt.legend(('Scope','LPF'),loc='upper right')
		#plt.show()
		#show only the lpf
		plt.plot(x[bbIndex:eeIndex],lpf_i_vs_t[bbIndex:eeIndex])
		plt.show()
		# show scaled I(t) and U(t)
		xx=range(0,self.u_nr_ofsample_per_period)	
		plt.plot(xx,self.i_vs_t,xx,5.134357*np.array(self.u_vs_t[self.u_vs_t_bbIndex:self.u_vs_t_eeIndex]))
		plt.legend(('I(t)','c*U(t)'),loc='upper right')
		plt.show()


class Bafang():
	def do_backEMF(self,a5=3,fi5=0.0):
		xx=range(0,800)
		y=range(0,800)
		y11=range(0,800)
		a7=0.5
		fi7=0
		a11=0.75
		fi11=0
		for i in range(0,800):
			y[i]=30*m.sin(i*m.pi/200)+a5*m.sin(fi5 + 5*i*m.pi/200)+a7*m.sin(fi7 + 7*i*m.pi/200)+a11*m.sin(fi11 + 11*i*m.pi/200)
			y11[i]=30*m.sin(i*m.pi/200)
		plt.plot(xx,y)
		plt.title('Simulatte BackEMF Bafang')
		plt.show()

	def try_flux(self,h_nr=10,a_harm_m=0.3,fi10=0.0):
		xx=range(0,800)
		y=range(0,800)
		y11=range(0,800)
		for i in range(0,800):
			a_harm=a_harm_m*m.sin(i*m.pi/200)**2
			y[i]=m.sin(i*m.pi/200)+a_harm*m.sin(fi10 + h_nr*i*m.pi/200)
			y11[i]=m.sin(i*m.pi/200)
		plt.plot(xx,y)
		plt.title('Simulatte Bafang Flux ')
		plt.show()

	def calc_flux(self,Omega=1):
		#this function usee backEMF as given by Bafang. 
		# The backEMF given by Bafang matches closely my measurements
		# Flux(t) = Integral (BackEMF(t))dT
		# BackEMF from Bafang document == My Mesaured BackEMF - seems to be correct
		# BackEMF = 29*sin(Omega*t) + 3*sin(5*Omega*t) + 0.5*sin(7*Omega*t) + 0.75*sin(11*Omega*t)
		# Flux(t) = Integral (BackEMF(t))dT
		# Flux(t) = -1/Omega(29*cos(Omega*t) + 3/5*cos(5*Omega*t) + 0.5/7*cos(7*Omega*t) + 0.75/11*cos(11*Omega*t)
		xx=range(0,800)
		y=range(0,800)
		for i in range(0,800):		
			y[i]=-1/Omega*(29*m.cos(i*m.pi/200)+0.6*m.cos(5*i*m.pi/200)+0.072*m.cos(7*i*m.pi/200)+0.07*m.cos(11*i*m.pi/200))	
		plt.plot(xx,y)
		plt.title('Calculate Bafang Flux from given BackEMF')
		plt.show()
class Dq():
	Count = 0   # This represents the count of objects of this class
	def __init__(self):
		Dq.Count += 1
		print Dq.Count, 'Dq objects active'
		print("init arg=",self)
		self.len = 800
		self.Ia  = range (0,self.len)    # one period of current wave
		self.Ib  = range (0,self.len)
		self.Ic  = range (0,self.len)
		self.Ialpha = range (0,self.len) # Aplha beta currents
		self.Ibeta  = range (0,self.len)
		self.Igama  = range (0,self.len)
		self.Id  = range (0,self.len)    # DQ
		self.Iq  = range (0,self.len)
		self.Ialpha_inv = range (0,self.len) # Inverse transformation varibales
		self.Ibeta_inv  = range (0,self.len)
		self.Ia_inv  = range (0,self.len)    # one period of current wave
		self.Ib_inv  = range (0,self.len)
		self.Ic_inv  = range (0,self.len)
		self.t   = range (0,self.len) # time axis

	def create(self,h5=0.05,h7=0.0,h11=0.0):
		for i in range(0,self.len):		
			self.Ia[i]=m.cos(i*m.pi/200         )+h5*m.cos(5*i*m.pi/200          )+h7*m.cos(7*i*m.pi/200          )+h11*m.cos(11*i*m.pi/200          )
			self.Ic[i]=m.cos(i*m.pi/200+2*m.pi/3)+h5*m.cos(5*i*m.pi/200+10*m.pi/3)+h7*m.cos(7*i*m.pi/200+14*m.pi/3)+h11*m.cos(11*i*m.pi/200+22*m.pi/3)
			self.Ib[i]=m.cos(i*m.pi/200+4*m.pi/3)+h5*m.cos(5*i*m.pi/200+20*m.pi/3)+h7*m.cos(7*i*m.pi/200+28*m.pi/3)+h11*m.cos(11*i*m.pi/200+44*m.pi/3)
		#show input signals abc frame
		plt.plot(self.t,self.Ia,self.t,self.Ib,self.t,self.Ic)
		plt.title('Original singals abc frame')
		plt.legend(('Ia','Ib','Ic'),loc='upper right')
		plt.show()
		#convert to alpha beta
		#park matrix
		#T=[[2.0/3.0,-1.0/3.0,-1.0/3.0],[0,1.0/m.sqrt(3.0),-1.0/m.sqrt(3.0)],[1.0/3.0,1.0/3.0,1.0/3.0]] # from wikipedia
		T=[[1.0,0,0],[1.0/m.sqrt(3),2.0/m.sqrt(3),0],[0,0,0]] # from arm lib
		for i in range(0,self.len):
			self.Ialpha[i] = T[0][0]*self.Ia[i]+T[0][1]*self.Ib[i]+T[0][2]*self.Ic[i] # y coordinate stator
			self.Ibeta[i]  = T[1][0]*self.Ia[i]+T[1][1]*self.Ib[i]+T[1][2]*self.Ic[i] # x coordinate stator
			self.Igama[i]  = T[2][0]*self.Ia[i]+T[2][1]*self.Ib[i]+T[2][2]*self.Ic[i]
		# show alpha beta frame
		plt.plot(self.t,self.Ialpha, self.t,self.Ibeta, self.t,self.Igama)
		plt.title('Alpha transformation with 5-th,7-th and 11-th harmonics')
		plt.legend(('Alpha','Beta','Gama'),loc='upper right')
		plt.show()
		#go to DQ
		Id_av_sum=0.0
		Iq_av_sum=0.0
		for i in range(0,self.len):
			stator_angle=i*m.pi/200
			theta=stator_angle - m.pi/2.0- 0*m.pi/2
			#real park
			self.Id[i] =  self.Ialpha[i]*m.cos(theta) + self.Ibeta[i]*m.sin(theta) 
			self.Iq[i] = -self.Ialpha[i]*m.sin(theta) + self.Ibeta[i]*m.cos(theta)
			Id_av_sum+=self.Id[i]
			Iq_av_sum+=self.Iq[i]
		self.Id_av=Id_av_sum/self.len
		self.Iq_av=Iq_av_sum/self.len
		# show DQ frame
		plt.plot(self.t,self.Id, self.t,self.Iq)
		plt.title('DQ transformation with 5-th,7-th and 11-th harmonics')
		plt.legend(('Id','Iq'),loc='upper right')
		plt.show()

	def inv_park(self):
		for i in range(0,self.len):
			angle=i*m.pi/200
			theta=angle # -90degree from stator vector to make Id=0
			self.Ibeta_inv[i] =self.Id[i]*m.cos(theta)    - self.Iq[i]*m.sin(theta)  ## alpha and beta for H1 and h5 are swaped????????????
			self.Ialpha_inv[i]=self.Id[i]*m.sin(theta)    + self.Iq[i]*m.cos(theta)
		plt.plot(self.t,self.Ialpha_inv,self.t,self.Ibeta_inv)
		plt.title('DQ Inverse transformation test with 5-th,7-th and 11-th harmonics')
		plt.legend(('Alpha','Beta'),loc='upper right')
		plt.show()

	def inv_clark(self):
		T=[[1.0,0.0,1.0],[-0.5,m.sqrt(3)/2,1.0],[-0.5,-m.sqrt(3)/2,1.0]]#from wikipedia
		for i in range(0,800):
			self.Ia_inv[i]=T[0][0]*self.Ialpha_inv[i] + T[0][1]*self.Ibeta_inv[i] #gamma is zero  
			self.Ib_inv[i]=T[1][0]*self.Ialpha_inv[i] + T[1][1]*self.Ibeta_inv[i] #gamma is zero
			self.Ic_inv[i]=T[2][0]*self.Ialpha_inv[i] + T[2][1]*self.Ibeta_inv[i] #gamma is zero
		#plot
		plt.plot(self.t,self.Ia_inv,self.t,self.Ib_inv,self.t,self.Ic_inv)
		plt.title('Inverse clark with 5-th 7-th and 11-th harmonics')
		plt.legend(('Ia','Ib','Ic'),loc='upper right')
		plt.show()

	def test(self,Iq_attn=1.0,Id_attn=1.0):	
		self.create()
		Ia_perfect=range(0,self.len)
		y=0.0
		#attenuate harmonics
		for i in range(0,self.len):
			self.Id[i]=self.Id[i] -(1-Id_attn)*(self.Id[i]-self.Id_av)
			self.Iq[i]=self.Iq[i] -(1-Iq_attn)*(self.Iq[i]-self.Iq_av)
			Ia_perfect[i]=m.cos(i*m.pi/200 )
		self.inv_park()
		self.inv_clark()
		#plot before and after
		plt.plot(self.t,self.Ia,self.t,self.Ia_inv,self.t,Ia_perfect)
		plt.title('Inverse clark with 5-th 7-th and 11-th harmonics')
		plt.legend(('Ia','Ia_inv','Cos'),loc='upper right')
		plt.show()

	def __del__(self):
	        Dq.Count -= 1
        	if Dq.Count == 0:
	            print 'Last DQ object deleted'
	        else:
	            print Dq.Count, 'DQ objects remaining'



class Cor():
	def tst(self,Q=10,f0=30,fs=40000):
		x=range (0,fs)
		y=range (0,fs)
		y_out=range (0,fs)
		for i in range (0,fs):
			y[i]=1.0*m.sin(2*m.pi*i*50/fs) +0.2*m.sin(2*m.pi*i*30/fs)
		b, a = signal.iirpeak(f0/fs,Q)   # normallized frequency f0/f_sample
		y_out = lfilter(b, a, y)
		plt.plot(x,y,y_out)
		plt.title('Resonant Filter')
		plt.show()

	


