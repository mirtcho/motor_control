from bench_tools import Yokogawa as Yokogawa

import numpy as np
import matplotlib.pyplot as plt


class Test:
	def __init__(self,ip='10.0.0.74'):
		self.yokogawa = Yokogawa(ip)		
	def acq(self):
		self.sample_time=float(self.yokogawa.request_xscale())*10/float(self.yokogawa.request_length())
		self.motor_speed = []
		self.t = []
		print ('sample time =', self.sample_time )
		start=1
		stop=24999000
		print ('Reading Channel 1 data from Yokogawa scope')
		self.channel1_data = self.yokogawa.data_calc(1,start,stop)			#self.request_wave(1,start,stop)
		print ('Reading Channel 2 data from Yokogawa scope')
		self.channel2_data = self.yokogawa.data_calc(2,start,stop)			#self.request_wave(2,start,stop)
		print ('Reading Channel 3 data from Yokogawa scope')
		self.channel3_data = self.yokogawa.data_calc(3,start,stop)			#self.request_wave(3,start,stop)
		print ('Reading Channel 4 data from Yokogawa scope')
		self.channel4_data = self.yokogawa.data_calc(4,start,stop)			#self.request_wave(4,start,stop)
		print ('Writing to file')
		#f = open(f_name, 'w')
		#writer = csv.writer(f)
		# write a row to the csv file
		#writer.writerow(self.channel1_data)
		#writer.writerow(self.channel2_data)
		#writer.writerow(self.channel3_data)
		#writer.writerow(self.channel4_data)
		#f.close()
	
	def add_increment(self,sample_nr):
		dT = (sample_nr-self.prev_sample)*self.sample_time		
		if (sample_nr == self.prev_sample or dT==0):
			self.current_speed = 100
		else:
			self.current_speed=60/(1024*dT)
		self.prev_sample=sample_nr
		
	
	def process_encoder_increments(self):
		#velocity is calculatied in motor rotot [rev/min]
		# 1 rev =1024 increments
		# timebase is get from scope sample rate
		#######
		# 1 step - calculate increment duration in [s]
		# 2 step  V= 60/(1024*t)
		self.inc_nr = 0
		self.prev_sample = 0
		enc_quadrant = 0
		#for i in range (int(float(self.yokogawa.request_length()))-100):
		for i in range (int(len(self.channel1_data))):
			ch1=self.channel1_data[i]
			ch2=self.channel2_data[i]

			if ( enc_quadrant==0):
				#ch1&ch2 =0
				if ch1>0.4 and ch2<0.4 :
					enc_quadrant=1
					self.add_increment(i)
				if ch1<0.4 and ch2>0.4 :
					enc_quadrant=3
					self.add_increment(i)
				if ch1>0.4 and ch2>0.4 :
					enc_quadrant=2
					self.add_increment(i)					
			elif( enc_quadrant == 1):
				#ch1=5v ch2=0
				if ch1>0.4 and ch2>0.4 :
					enc_quadrant=2
					self.add_increment(i)
				if ch1<0.4 and ch2>0.4 :
					enc_quadrant=3
					self.add_increment(i)
				if ch1<0.4 and ch2<0.4 :
					enc_quadrant=0
					self.add_increment(i)
			elif( enc_quadrant == 2):
				#ch1=5v ch2=5v ToDo
				if ch1>0.4 and ch2<0.4 :
					enc_quadrant=1
					self.add_increment(i)
				if ch1<0.4 and ch2>0.4 :
					enc_quadrant=3
					self.add_increment(i)
				if ch1<0.4 and ch2<0.4 :
					enc_quadrant=0
					self.add_increment(i)
			elif( enc_quadrant == 3):
				#ch1=0V ch2=5v ToDo
				if ch1>0.4 and ch2<0.4 :
					enc_quadrant=1
					self.add_increment(i)
				if ch1>0.4 and ch2>0.4 :
					enc_quadrant=2
					self.add_increment(i)
				if ch1<0.4 and ch2<0.4 :
					enc_quadrant=0
					self.add_increment(i)						
			self.motor_speed.append(self.current_speed)
			self.t.append(self.sample_time*i)
			
			
	def tst(self):
		print ('start scope acquisition')
		self.acq()
		print ('process increment data and calculate velocity')
		self.process_encoder_increments()
		# plot data 
		fig, axs = plt.subplots(2, 1)
		axs[0].plot(self.t, self.motor_speed, self.t, self.channel4_data)
		#axs[0].set_xlim(0, 2)
		axs[0].set_xlabel('time')
		axs[0].set_ylabel('velocity and U_l1')
		axs[0].grid(True)
		#cxy, f = axs[1].cohere(s1, s2, 256, 1. / dt)
		#axs[1].set_ylabel('coherence')
		fig.tight_layout()
		plt.show()
		
	