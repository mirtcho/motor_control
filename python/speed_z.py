import matplotlib.pyplot as plt
import numpy as np
from scipy.signal import butter, lfilter
from scipy import signal

import math as m
import csv


class SpeedZ:
	Count = 0   # This represents the count of objects of this class
	def __init__(self):
		SpeedZ.Count += 1
		print SpeedZ.Count, 'Speed objects active'
		print("init arg=",self)
		self.gFname ='empty'
		self.MAX_FILE_LEN = 950000
		self.inc_dt      = range(0,self.MAX_FILE_LEN)
		self.z_pulse     = range(0,self.MAX_FILE_LEN)
		self.x           = range(0,self.MAX_FILE_LEN)

	def __del__(self):
	        Speed.Count -= 1
        	if Speed.Count == 0:
	            print 'Last Speed object deleted'
	        else:
	            print Speed.Count, 'Speed objects remaining'

	def read_file(self,fname='/mnt/hgfs/vm_share/trace/S0_Index_6_7msec_6MHz.txt'):
		i=0
		self.gFname=fname
		f = open (fname,"r")
		for ln_str in f:
			if ln_str.count(' ') == 2: 				# check for index pulse
				# process index data
				index_detected = True
				self.z_pulse[i-14]=30000
				position_str= ln_str[1:-6]
				self.prev_position=int(position_str)
				#keep previous displacement?
				self.inc_dt[i-14]=self.inc_dt[i-15]
			else: 
				#remove header info from the first 13 lines
				if i>13:
					self.z_pulse[i-14]=0
					position_str= ln_str[1:-4]
					position = int(position_str)
					if i>14:
						self.inc_dt[i-14]=position-self.prev_position
					self.prev_position=position
				else:
					self.prev_position = 0
					position=0
					self.inc_dt[i]=0		
				if (i/1000.0) == int(i/1000):
					print ("position=%d  dT/inc=%d ",position,self.inc_dt[i-14])
			i=i+1
		f.close()
		self.TotalNrOfIncrements = i;
		print ("read lines =",i)		
		print("gFname=",self.gFname)
		plt.plot (self.x[8000:i-600],self.inc_dt[8000:i-600] ,self.z_pulse[8000:i-600])
		plt.legend(('dt/increment','Z'),loc='upper right')
		plt.title('Speed vs time')
		plt.show()

	def do_avg2(self, n=20480, ts=0.1,order=6):
		x=range(0,n)
		y2=range(0,n)
		y2_lpf=range(0,n)
		z24 = range(0,n)
		# averge from two samples
		j=0
		b_index=int(0.5*self.TotalNrOfIncrements)
		for i in range(b_index,b_index+n,2):
			y2[j]  = (self.inc_dt[i]+self.inc_dt[i+1])*0.5
			y2[j+1]= y2[j]
			j=j+2
		#show fft
		self.do_fft(y2)
		#create z24 signal
		z_pulse_index=0
		j=0
		for i in range(b_index,b_index+n):
			z24[j]=0
			if self.z_pulse[i] > 0 : #detect the index pulse
				z_pulse_index=i
				harmonic=1
			if (z_pulse_index > 0) and (abs((i-z_pulse_index)-int(1024.0/24.0*harmonic))<1):
				harmonic=harmonic+1
				z24[j]= 30000
			j=j+1
		#design lpf filter
		b,a = butter (order,ts, 'low', False)
		y2_lpf = lfilter(b, a, y2)
		#plot
		plt.legend(('dt/increment','Z','Z24'),loc='upper right')
		plt.title('dT/inc filtered vs increments')
		plt.plot(x,y2_lpf,x,self.z_pulse[b_index:b_index+n]) # ,x,z24)
		plt.show()
		#show filtered fft
		self.do_fft(y2_lpf)
		
	def do_lpf(self,ts=0.1,order=4,w0=1.0/512,Q=5):
		disp_lpf       = range(0,self.TotalNrOfIncrements)
		disp_lpf_notch = range(0,self.TotalNrOfIncrements)
		#design lpf filter
		b,a = butter (order,ts, 'low', False)
		disp_lpf = lfilter(b, a, self.inc_dt)
		# add notch filer - remove encoder misalignment
		b_notch, a_notch = signal.iirnotch(w0, Q)
		disp_lpf_notch=lfilter(b_notch, a_notch, disp_lpf)
		#plot graph
		begin_index=50
		end_index= self.TotalNrOfIncrements-1000		
		#plt.plot(self.x[50:self.TotalNrOfIncrements-1000],disp_lpf[50:self.TotalNrOfIncrements-1000], disp_lpf_notch[50:self.TotalNrOfIncrements-1000])
		plt.plot(self.x[begin_index:end_index], disp_lpf_notch[begin_index:end_index],self.z_pulse[begin_index:end_index])
		plt.title('Velocity ripple vs time '+self.gFname)
		plt.xlabel ('Increments')
		plt.ylabel ('Speed')
		plt.show()

	def do_fft(self,y=[],n=1024,offset=300):
		f=range(0,n)
		f_cpx= np.fft.fft(y[offset:offset+n])
		plt.plot(f,f_cpx.real,f_cpx.imag)
		plt.title('Velocity ripple spectrum '+self.gFname)
		plt.show()



class Speed:
	Count = 0   # This represents the count of objects of this class
	def __init__(self):
		Speed.Count += 1
		print Speed.Count, 'Speed objects active'
		print("init arg=",self)
		self.gFname ='empty'
		self.MAX_FILE_LEN = 950000
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
		for i in range (0,10):
			f_cpx.real[i]=0.0
			f_cpx.imag[i]=0.0
		for i in range (10,240):
			f_cpx.real[i]= f_cpx.real[i]/50.0
			f_cpx.imag[i]= f_cpx.imag[i]/50.0
		#end workaround 
		plt.plot(f,f_cpx.real,f_cpx.imag)
		plt.title('Velocity ripple spectrum '+self.gFname)
		plt.show()

	def do_lpf(self,ts=0.1,order=4,w0=1.0/512,Q=5):
		disp_lpf       = range(0,self.TotalNrOfIncrements)
		disp_lpf_notch = range(0,self.TotalNrOfIncrements)
		#design lpf filter
		b,a = butter (order,ts, 'low', False)
		disp_lpf = lfilter(b, a, self.displacement)
		# add notch filer - remove encoder misalignment
		b_notch, a_notch = signal.iirnotch(w0, Q)
		disp_lpf_notch=lfilter(b_notch, a_notch, disp_lpf)
		#plot graph		
		#plt.plot(self.x[50:self.TotalNrOfIncrements-1000],disp_lpf[50:self.TotalNrOfIncrements-1000], disp_lpf_notch[50:self.TotalNrOfIncrements-1000])
		plt.plot(self.x[50:self.TotalNrOfIncrements-1000], disp_lpf_notch[50:self.TotalNrOfIncrements-1000])
		plt.title('Velocity ripple vs time '+self.gFname)
		plt.xlabel ('Increments')
		plt.ylabel ('Speed')
		plt.show()

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
		#inlut signals time domain
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


