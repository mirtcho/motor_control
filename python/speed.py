import matplotlib.pyplot as plt
import numpy as np
from scipy.signal import butter, lfilter
from scipy import signal

import math as m
import csv

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


	def do_bafang(self,a5=3,fi5=0.0):
		xx=range(0,800)
		y=range(0,800)
		for i in range(0,800):
			y[i]=30*m.sin(i*m.pi/200)+a5*m.sin(fi5 + 5*i*m.pi/200)
		plt.plot(xx,y)
		plt.title('Simulatte BackEMF Bafang')
		plt.show()

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
		T=[[2.0/3.0,-1.0/3.0,-1.0/3.0],[0,1.0/m.sqrt(3.0),-1.0/m.sqrt(3.0)],[1.0/3.0,1.0/3.0,1.0/3.0]]
		for i in range(0,800):
			angle=i*m.pi/200
			h1_angle=5*angle
			# create 3 phases Ia,Ib,Ic signals
			self.ia[i] = 1.0*m.sin(angle+offset)+0.07*m.sin(h1_angle+5*offset)
			self.ib[i] = 1.0*m.sin(angle+2*m.pi/3+offset)+0.07*m.sin(h1_angle+10*m.pi/3+5*offset)
			self.ic[i] = 1.0*m.sin(angle+4*m.pi/3+offset)+0.07*m.sin(h1_angle+20*m.pi/3+5*offset)
			#convert to alpha beta
			self.ya[i] = T[0][0]*self.ia[i]+T[0][1]*self.ib[i]+T[0][2]*self.ic[i]
			self.yb[i] = T[1][0]*self.ia[i]+T[1][1]*self.ib[i]+T[1][2]*self.ic[i]
			self.yc[i] = T[2][0]*self.ia[i]+T[2][1]*self.ib[i]+T[2][2]*self.ic[i]
		#show input signals
		#plt.plot(self.xx,self.ia, self.xx,self.ib, self.xx,self.ic)
		#plt.title('Input signals Ia,IB with Ic 5-th harmonics')
		#plt.legend(('Ia','Ib','Ic'),loc='upper right')
		#plt.show()
		# show alpha beta 
		#plt.plot(self.xx,self.ya, self.xx,self.yb, self.xx,self.yc)
		#plt.title('ALpha transformation test with 5-th harmonics')
		#plt.legend(('Alpha','Beta','Gama'),loc='upper right')
		#plt.show()

	def clark(self,offset=0):
		#create alpha beta signals with 5-th harmomic
		self.calc_aplha_beta(offset)
		d1_av=0
		q1_av=0
		for i in range(0,800):
			angle=i*m.pi/200			
			#real park
			self.d1[i] = self.ya[i]*m.sin(angle) + self.yb[i]*m.cos(angle) 
			self.q1[i] = self.yb[i]*m.sin(angle) - self.ya[i]*m.cos(angle)
			d1_av = d1_av+self.d1[i]
			q1_av = q1_av+self.q1[i]
		d1_av=d1_av/800
		q1_av=q1_av/800
		print "d1_av=",d1_av,"q1_av=",q1_av
		for i in range(0,800):
			angle=i*m.pi/200			
			h1_angle=6*angle
			self.d5[i] = (self.q1[i]-q1_av) *m.sin(h1_angle) + (self.d1[i]-d1_av) *m.cos(h1_angle) 
			self.q5[i] = (self.d1[i]-d1_av) *m.sin(h1_angle) - (self.q1[i]-q1_av) *m.cos(h1_angle)
			self.d1_av[i]=d1_av  # used by back transformation
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
			h1_angle=5*angle
			y1a=self.q1_av[i]*m.cos(angle)    + self.d1_av[i]*m.sin(angle)
			y1b=self.d1_av[i]*m.cos(angle)    - self.q1_av[i]*m.sin(angle)
			y5a=self.q5[i]   *m.cos(h1_angle) + self.d5[i]   *m.sin(h1_angle)
			y5b=self.d5[i]   *m.cos(h1_angle) - self.q5[i]   *m.sin(h1_angle)
			self.calc_ya[i]=(y1a+y5a)
			self.calc_yb[i]=(y1b+y5b) 
			#self.calc_ya[i] = self.q[i]*(m.cos(angle)+0.07*m.cos(h1_angle)) + self.d[i]*(m.sin(angle)+0.07*m.sin(h1_angle))#works with Iq=0
			#self.calc_yb[i] = self.d[i]*(m.cos(angle)-0.07*m.cos(h1_angle)) - self.q[i]*(m.sin(angle)-0.07*m.sin(h1_angle))#works with Iq=0
		plt.plot(self.xx,self.calc_ya,self.calc_yb)
		#plt.plot(self.xx,self.ya,self.yb)
		plt.title('DQ Inverse transformation test with 5-th harmonics')
		plt.legend(('Alpha','Beta'),loc='upper right')
		plt.show()


	def inv_clark(self):
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

	
class Emf:
	Count = 0   # This represents the count of objects of this class
	def __init__(self):
		Emf.Count += 1
		print Emf.Count, 'Emf objects active'
		print("init arg=",self)
		self.MAX_FILE_LEN = 14000010  # scope has 14MPoints
		self.scope_emf = range(0,self.MAX_FILE_LEN)
		self.x         = range(0,self.MAX_FILE_LEN)

	def __del__(self):
	        Emf.Count -= 1
        	if Emf.Count == 0:
	            print 'Last Emf object deleted'
	        else:
	            print Emf.Count, 'Emf objects remaining'

	def find_zero_emf(self,bIndex=0, eIndex=13999999,treshold=0.05):
		for i in range(bIndex,eIndex):
			if abs(self.scope_emf[i]) <=treshold:
				return i
		return i

	def scopeEMF(self, fname='/mnt/hgfs/vm_share/trace/BackEMF_rigol.csv'):
		# read the scope CSV file
		with open(fname) as csv_file:
			csv_reader = csv.reader(csv_file, delimiter=',')
			line_count = 0
			for row in csv_reader:
				if line_count == 0:
					print('Column names are {", ".join(row)}')
					line_count += 1
				else:
					if line_count>3 and line_count < 14000000:					
						self.scope_emf[line_count] = float(row[1])
						#print line_count,',',self.scope_emf[line_count]
					line_count += 1					
		    	print('Processedlines',line_count)
		csv_file.close()
		# FFT
		bIndex = self.find_zero_emf(8000000)
		eIndex = self.find_zero_emf(10000000)
		print 'bIndex=',bIndex,'eIndex=',eIndex
		f=range(0,eIndex-bIndex)
		f_cpx= np.fft.fft(self.scope_emf[bIndex:eIndex])
		#delete aritifital harmonics caused by speed deviation
		for i in range(0,eIndex-bIndex):
			if i/11.0 != i/11:
				f_cpx.imag[i]=0;
				f_cpx.real[i]=0;
			#normalize frequency to 11 periods
			f[i]=f[i]/11.0
		f_cpx.real[0]=0;
		f_cpx.imag[0]=0;
		#normalize amplitude
		f_cpx.real=f_cpx.real/1e7
		f_cpx.imag=f_cpx.imag/1e7
		##########plt.plot(f,f_cpx.real,'r--',f,f_cpx.imag,'-bs')##############
		plt.plot(f[:250],f_cpx.real[:250],'r--',f[:250],f_cpx.imag[:250],'b--')
		plt.title('Bafang BackEMF scope waveform FFT')
		plt.legend(('Real','Img'),loc='upper right')
		plt.show()
		# plot in time domain
		#plt.plot(self.x,self.scopeEMF[20:13999900])
		#plt.title('Bafang BackEMF scope waveform')
		#plt.legend(('D','Q'),loc='upper right')
		#plt.show()


