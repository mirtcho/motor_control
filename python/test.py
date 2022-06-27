from bench_tools import Yokogawa as Yokogawa

import numpy as np
import matplotlib.pyplot as plt


class Test:
	def __init__(self,ip='10.0.0.74'):
		self.yokogawa = Yokogawa(ip)		
		
	def acq(self):
		self.sample_time=float(self.yokogawa.request_xscale())*10/float(self.yokogawa.request_length())
		self.acq_len=int(float(self.yokogawa.request_length()))
		self.motor_speed = np.empty(self.acq_len)
		self.motor_lpf_speed = np.empty(self.acq_len)
		self.motor_lpf2_speed = np.empty(self.acq_len)
		self.motor_lpf_delta = np.empty(self.acq_len)
		#
		self.t = np.empty(self.acq_len)
		self.channel1_data = np.empty(self.acq_len)
		self.channel2_data = np.empty(self.acq_len)
		self.channel3_data = np.empty(self.acq_len)
		self.channel4_data = np.empty(self.acq_len)		
		#calculate speed LPF filter 
		self.lpf_freq_hz  =6000 #6KHz
		self.lpf2_freq_hz = 300
		sample_freq_hz=1/self.sample_time
		self.lpf_freq_norm=self.lpf_freq_hz/sample_freq_hz
		self.lpf_freq2_norm=self.lpf2_freq_hz/sample_freq_hz		
		print ('sample time =', self.sample_time )		
		start = 0				#1
		stop  = self.acq_len  	#24999000		
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
		if (sample_nr == self.prev_sample or dT<3e-6):
			if (dT==0):
				self.current_speed = 8000 #2000rpm mechanical
			else:
				#glitch skip it
				self.nr_of_glitch+=1
				return
		else:
			self.current_speed=60/(2048*dT)
		self.prev_sample=sample_nr
		
	def sub_increment(self,sample_nr):
		dT = (sample_nr-self.prev_sample)*self.sample_time		
		if (sample_nr == self.prev_sample or dT<3e-6):
			if (dT==0):
				self.current_speed = -8000 #2000rpm mechanical
			else:
				#glitch skip it
				self.nr_of_glitch+=1
				return
		else:
			self.current_speed=-60/(2048*dT)
		self.prev_sample=sample_nr
		
	def process_encoder_increments(self):
		#velocity is calculatied in motor rotor [rev/min]
		# 1 rev =1024 increments
		# timebase is get from scope sample rate
		#######
		# 1 step - calculate increment duration in [s]
		# 2 step  V= 60/(1024*t)
		self.inc_nr = 0
		self.prev_sample = 0
		self.current_speed = 0
		enc_quadrant = 0
		self.nr_of_glitch = 0
		current_lpf_speed = 0
		current_lpf2_speed = 0
		current_lpf_delta = 0
		#for i in range (int(float(self.yokogawa.request_length()))-100):
		for i in range (int(len(self.channel1_data))):
			ch1=self.channel1_data[i]
			ch2=self.channel2_data[i]
			TH_HIGH =1.8
			TH_LOW = 0.6
			if ( enc_quadrant==0):
				#ch1&ch2 =0
				if ch1>TH_HIGH and ch2<TH_LOW :
					enc_quadrant=1
					self.add_increment(i)
				if ch1<TH_LOW and ch2>TH_HIGH :
					enc_quadrant=3
					self.sub_increment(i)
				#if ch1>TH_HIGH and ch2>TH_HIGH :
				#	enc_quadrant=2
				#	self.add_increment(i)					
			elif( enc_quadrant == 1):
				#ch1=5v ch2=0
				if ch1>TH_HIGH and ch2>TH_HIGH :
					enc_quadrant=2
					self.add_increment(i)
				#if ch1<TH_LOW and ch2>TH_HIGH :
				#	enc_quadrant=3
				#	self.add_increment(i)
				if ch1<TH_LOW and ch2<TH_LOW :
					enc_quadrant=0
					self.sub_increment(i)
			elif( enc_quadrant == 2):
				#ch1=5v ch2=5v ToDo
				if ch1>TH_HIGH and ch2<TH_LOW :
					enc_quadrant=1
					self.sub_increment(i)
				if ch1<TH_LOW and ch2>TH_HIGH :
					enc_quadrant=3
					self.add_increment(i)
				#if ch1<TH_LOW and ch2<0.4 :
				#	enc_quadrant=0
				#	self.add_increment(i)
			elif( enc_quadrant == 3):
				#ch1=0V ch2=5v ToDo
				#if ch1>TH_HIGH and ch2<TH_LOW :
				#	enc_quadrant=1
				#	self.add_increment(i)
				if ch1>TH_HIGH and ch2>TH_HIGH :
					enc_quadrant=2
					self.sub_increment(i)
				if ch1<TH_LOW and ch2<TH_LOW :
					enc_quadrant=0
					self.add_increment(i)						
			current_lpf_speed  += self.lpf_freq_norm*(self.current_speed-current_lpf_speed)
			current_lpf2_speed +=self.lpf_freq2_norm*(self.current_speed-current_lpf2_speed)
			current_lpf_delta = current_lpf_speed-current_lpf2_speed
			self.motor_speed[i]     = self.current_speed
			self.motor_lpf_speed[i] = current_lpf_speed
			self.motor_lpf2_speed[i]= current_lpf2_speed
			self.motor_lpf_delta[i] = current_lpf_delta
			self.t[i]               = self.sample_time*i
	
	def tst(self):
		print ('start scope acquisition')
		self.acq()
		print ('process increment data and calculate velocity')
		self.process_encoder_increments()
		# plot data 
		fig, axs = plt.subplots(2, 1)
		#axs[0].plot(self.t[5000:], self.motor_speed[5000:], self.t[5000:], self.motor_lpf_speed[5000:])		
		axs[0].plot( self.t[5000:], self.motor_lpf_speed[5000:])
		axs[1].plot(self.t[5000:], self.channel1_data[5000:],self.t[5000:], self.channel2_data[5000:],self.t[5000:], self.channel4_data[5000:])
		#axs[0].set_xlim(0, 2)
		axs[0].set_xlabel('time[s]')
		axs[0].set_ylabel('speed & speed_lpf[rpm]')
		axs[0].grid(True)

		axs[1].set_xlabel('time[s]')
		axs[1].set_ylabel('I_l1[A] & U_l1[V]')
		axs[1].grid(True)
		#cxy, f = axs[1].cohere(s1, s2, 256, 1. / dt)
		#axs[1].set_ylabel('coherence')
		fig.tight_layout()
		plt.show()
		
	def tst2(self):
		print ('start scope acquisition')
		self.acq()
		print ('process increment data and calculate velocity')
		self.process_encoder_increments()
		#plot data
		fig, ax1 = plt.subplots()
		ax1.plot(self.t[5000:], self.motor_lpf_speed[5000:], color='red')
		ax2 = ax1.twinx()
		ax2.plot(self.t[5000:], self.channel4_data[5000:], color='blue')
		fig.tight_layout()
		plt.show()
		#next figure
		fig, ax1 = plt.subplots()
		ax1.plot(self.t[5000:], self.motor_lpf2_speed[5000:], color='red')
		ax2 = ax1.twinx()
		ax2.plot(self.t[5000:], self.channel4_data[5000:], color='blue')
		fig.tight_layout()
		plt.show()
		#3-th graph
		fig, ax1 = plt.subplots()
		ax1.plot(self.t[5000:], self.motor_lpf_delta[5000:], color='red')
		ax2 = ax1.twinx()
		ax2.plot(self.t[5000:], self.channel4_data[5000:], color='blue')
		fig.tight_layout()

		plt.show()
		