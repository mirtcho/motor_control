import matplotlib.pyplot as plt
import numpy as np
from scipy.signal import butter, lfilter
from scipy import signal

import math as m

class O4:
	Count = 0   # This represents the count of objects of this class
	def __init__(self):
		O4.Count += 1
		print (O4.Count, 'O4 objects active')
		print("init arg=",self)
		self.TOTAL_SAMPLES = 1000
		#input signal
		self.Ia			= list(range (0,self.TOTAL_SAMPLES))
		self.Ib			= list(range (0,self.TOTAL_SAMPLES))
		self.Ic			= list(range (0,self.TOTAL_SAMPLES))
		self.Theta		= list(range (0,self.TOTAL_SAMPLES))
		#Alpha beta
		self.Ialpha     = list(range (0,self.TOTAL_SAMPLES))
		self.Ibeta		= list(range (0,self.TOTAL_SAMPLES))
		self.Id			= list(range (0,self.TOTAL_SAMPLES))
		self.Iq			= list(range (0,self.TOTAL_SAMPLES))
		#output inv_park
		self.ISalpha	= list(range (0,self.TOTAL_SAMPLES))
		self.ISbeta		= list(range (0,self.TOTAL_SAMPLES))		
		#inv clarke
		self.IS1		= list(range (0,self.TOTAL_SAMPLES))
		self.IS2		= list(range (0,self.TOTAL_SAMPLES))
		self.IS3		= list(range (0,self.TOTAL_SAMPLES))
		#output SVM
		self.IOa		= list(range (0,self.TOTAL_SAMPLES))
		self.IOb		= list(range (0,self.TOTAL_SAMPLES))
		self.IOc		= list(range (0,self.TOTAL_SAMPLES))
		self.sector		= list(range (0,self.TOTAL_SAMPLES))
		
	def __del__(self):
	        O4.Count -= 1
        	if O4.Count == 0:
	            print ('Last O4 object deleted')
	        else:
	            print (O4.Count, 'O4 objects remaining')

	def arm_inv_clarke (self,Ialpha,Ibeta):
		Ia=Ialpha
		Ib=Ibeta*m.sqrt(3)/2.0 - Ialpha*0.5
		return (Ia,Ib)
		
	def modif_inv_clarke(self,Ialpha,Ibeta):
		#(Ib,Ia)=self.arm_inv_clarke(Ibeta,Ialpha) #swaped alpha,beta & Ia,Ib
		(Ia,Ib)=self.arm_inv_clarke(Ialpha,Ibeta) #not modified
		Ic=-(Ia+Ib)
		return Ia,Ib,Ic

	def CalcTimes(self,T1,T2):
		PWM_PERIOD_LIMIT=1 #5325 at O4 since it controlls dierct PWM timer
		Tc=PWM_PERIOD_LIMIT-(T1+T2)
		Tb=Tc+T1
		Ta=Tb+T2
		#invert
		Tc=PWM_PERIOD_LIMIT-Tc
		Tb=PWM_PERIOD_LIMIT-Tb
		Ta=PWM_PERIOD_LIMIT-Ta
		return Ta,Tb,Tc
		
	def SVM(self,ia,ib,ic):
		#calculate sector
		sector=0
		if (ia>0):
			sector=sector+1
		if (ib>0):
			sector=sector+2
		if (ic>0):
			sector=sector+4
		#clamp section not implemented
		#clamp inputs  ia,ib,ic +-PWM_PERIOD_LIMIT=+-5325@O4 +-1 for simuation
		if sector==1:
			I1, I3, I2 = self.CalcTimes(-ib,-ic)
		if sector==2:
			I3, I1, I2 = self.CalcTimes( ia, ic)
		if sector==3:
			I1, I2, I3 = self.CalcTimes( ib, ia)
		if sector==4:
			I3, I2, I1 = self.CalcTimes(-ia,-ib)
		if sector==5:
			I3, I1, I2 = self.CalcTimes( ia, ic)
		if sector==6:
			I2, I3, I1 = self.CalcTimes( ic, ib)
		if (sector==0 or sector==7):
			#wrong combination assert or zero output!!
			I1=0
			I2=0
			I3=0
		return I1,I2,I3,sector
		
	def SVM_new(self,ia,ib,ic):
		#https://www.embedded.com/painless-mcu-implementation-of-space-vector-modulation-for-electric-motor-systems/
		#find max
		if (ia>=ib) and (ia>=ic):
				max=ia
		if (ib>ia) and (ib>ic):
				max=ib
		if (ic>ia) and (ic>ia):
			max=ic
		#min		
		if (ia<=ib) and (ia<=ic):
			min=ia
		if (ib<ia) and (ib<ic):
			min=ib
		if (ic<ia) and (ic<ib):
			min=ic
		Neutral=(max+min)/2.0	
		I1=ia-Neutral
		I2=ib-Neutral
		I3=ic-Neutral
		return I1,I2,I3,Neutral

	def create(self):
		for i in range(0,self.TOTAL_SAMPLES):
			self.Theta[i] =i*2*m.pi/self.TOTAL_SAMPLES
			self.Ia[i] = m.sin(self.Theta[i])
			self.Ib[i] = m.sin(self.Theta[i]+2*m.pi/3.0)
			self.Ic[i] = m.sin(self.Theta[i]+4*m.pi/3.0)
			#clarke as is from arm_math-> stm32 lib
			self.Ialpha[i] = self.Ia[i];
			self.Ibeta[i]  = self.Ia[i]/m.sqrt(3)+2*self.Ib[i]/m.sqrt(3)
			#park stm32 - but inverted Theta to -Theta
			#Theta=-Theta
			self.Id[i] = self.Ialpha[i]*m.cos(self.Theta[i]) + self.Ibeta[i]*m.sin(self.Theta[i])
			self.Iq[i] = self.Ibeta[i]*m.cos(self.Theta[i]) - self.Ialpha[i]*m.sin(self.Theta[i])
			#inv park
			self.ISalpha[i] = self.Id[i]*m.cos(self.Theta[i]) - self.Iq[i]*m.sin(self.Theta[i])
			self.ISbeta[i] = self.Id[i]*m.sin(self.Theta[i]) + self.Iq[i]*m.cos(self.Theta[i])
			#modified inf crake
			self.IS1[i], self.IS2[i], self.IS3[i]=self.modif_inv_clarke(self.ISalpha[i], self.ISbeta[i])			
			#SVM
			self.IOa[i], self.IOb[i], self.IOc[i], self.sector[i]=self.SVM_new(self.IS1[i], self.IS2[i], self.IS3[i])

	def pl(self):
			plt.plot (self.Theta,self.Ia, self.Theta,self.Ib, self.Theta,self.Ic)
			plt.legend(('abc'),loc='upper right')
			plt.title('Initial signals')
			plt.show()
			#show alpha beta
			plt.plot (self.Theta,self.Ialpha, self.Theta,self.Ibeta)
			plt.legend(('AB'),loc='upper right')
			plt.title('Alpha Beta')
			plt.show()
			#show DQ
			plt.plot (self.Theta,self.Id, self.Theta,self.Iq)
			plt.legend(('dq'),loc='upper right')
			plt.title('DQ')
			plt.show()
			#show inv park output
			plt.plot (self.Theta,self.ISalpha, self.Theta,self.ISbeta)
			plt.legend(('AB'),loc='upper right')
			plt.title('INV park to Alpha Beta')
			plt.show()
			#show modified inv clarke output
			plt.plot (self.Theta,self.IS1, self.Theta,self.IS2, self.Theta,self.IS3)
			plt.legend(('ABC'),loc='upper right')
			plt.title('Modified INV clarke outpur before SVM')
			plt.show()			
			#show modified inv clarke output
			plt.plot (self.Theta,self.IOa, self.Theta,self.IOb, self.Theta,self.IOc,self.Theta,self.sector)
			plt.legend(('abcs'),loc='upper right')
			plt.title('SVM Outputs Ioa,Iob,Ioc and sector')
			plt.show()			
