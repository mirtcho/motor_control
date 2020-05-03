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
		#output inv_clark
		self.ISalpha	= list(range (0,self.TOTAL_SAMPLES))
		self.ISbeta		= list(range (0,self.TOTAL_SAMPLES))
		#self.ISc		= list(range (0,self.TOTAL_SAMPLES))
		#output SVM
		self.IOa		= list(range (0,self.TOTAL_SAMPLES))
		self.IOb		= list(range (0,self.TOTAL_SAMPLES))
		self.IOc		= list(range (0,self.TOTAL_SAMPLES))
		
		
	def __del__(self):
	        O4.Count -= 1
        	if O4.Count == 0:
	            print ('Last O4 object deleted')
	        else:
	            print (O4.Count, 'O4 objects remaining')

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
			self.Id[i] = self.Ialpha[i]*m.cos(-self.Theta[i]) + self.Ibeta[i]*m.sin(-self.Theta[i])
			self.Iq[i] = self.Ibeta[i]*m.cos(-self.Theta[i]) - self.Ialpha[i]*m.sin(-self.Theta[i])
			#inv park
			self.ISalpha[i] = self.Id[i]*m.cos(self.Theta[i]) - self.Iq[i]*m.sin(self.Theta[i])
			self.ISbeta[i] = self.Id[i]*m.sin(self.Theta[i]) + self.Iq[i]*m.cos(self.Theta[i])
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
			#show inv clarke output
			plt.plot (self.Theta,self.ISalpha, self.Theta,self.ISbeta)
			plt.legend(('AB'),loc='upper right')
			plt.title('INC clarcke to Alpha Beta')
			plt.show()
			
