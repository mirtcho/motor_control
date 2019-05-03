import numpy as np
from scipy import signal
from matplotlib import pyplot as plt

from scipy.signal import fir_filter_design as ffd
from scipy.signal import filter_design as ifd

import math as m

def test():
	# setup some of the required parameters
	Fs = 1e9           # sample-rate defined in the question, down-sampled

	# remez (fir) design arguements
	Fpass = 10e6       # passband edge
	Fstop = 11.1e6     # stopband edge, transition band 100kHz
	Wp = Fpass/(Fs)    # pass normalized frequency
	Ws = Fstop/(Fs)    # stop normalized frequency

	# iirdesign agruements
	Wip = (Fpass)/(Fs/2)
	Wis = (Fstop+1e6)/(Fs/2)
	Rp = 1             # passband ripple
	As = 62            # stopband attenuation

	# Create a FIR filter, the remez function takes a list of 
	# "bands" and the amplitude for each band.
	taps = 4096
	br = ffd.remez(taps, [0, Wp, Ws, .5], [1,0], maxiter=10000) 

	# The iirdesign takes passband, stopband, passband ripple, 
	# and stop attenuation.
	bc, ac = ifd.iirdesign(Wip, Wis, Rp, As, ftype='ellip')  
	bb, ab = ifd.iirdesign(Wip, Wis, Rp, As, ftype='cheby2') 
	print bc
	print ac
	mfreqz(bc,ac)
	w, h = signal.freqs(bc, ac, 1000)
	fig = plt.figure()
	ax = fig.add_subplot(1, 1, 1)
	ax.semilogx(w / (2*np.pi), 20 * np.log10(np.maximum(abs(h), 1e-5)))
	ax.set_title('Chebyshev Type II bandpass frequency response')
	ax.set_xlabel('Frequency [Hz]')
	ax.set_ylabel('Amplitude [dB]')
	ax.axis((10, 1000000, -100, 10))
	ax.grid(which='both', axis='both')
	plt.show()

def mfreqz(b,a):
    w,h = signal.freqz(b,a)
    h_dB = 20 * np.log10 (abs(h))
    plt.subplot(211)
    plt.plot(w/max(w),h_dB)
    plt.ylim(-150, 5)
    plt.ylabel('Magnitude (db)')
    plt.xlabel(r'Normalized Frequency (x$\pi$rad/sample)')
    plt.title(r'Frequency response')
    plt.subplot(212)
    h_Phase = np.unwrap(np.arctan2(np.imag(h),np.real(h)))
    plt.plot(w/max(w),h_Phase)
    plt.ylabel('Phase (radians)')
    plt.xlabel(r'Normalized Frequency (x$\pi$rad/sample)')
    plt.title(r'Phase response')
    plt.subplots_adjust(hspace=0.5)
    plt.show()

class pwm():
	def gen_signal(self,Am=0.5,f1=1.0,ns=400):
		self.x=range(0,ns)
		self.signal=range(0,ns)
		for i in range(0,ns):
			self.signal[i] = Am+Am*m.sin(2*m.pi*f1*i/ns)

	def gen_pwm(self,ns=400,n_pwm=400*1024):
		self.xx=range(0,n_pwm)		
		self.pwm_signal = range(0,n_pwm)
		self.z_signal = range(0,n_pwm) 
		self.f_cpx = range (0,n_pwm)
		self.fz_cpx= range (0,n_pwm)
		for i in range(0,ns):
			t_on = self.signal[i]*n_pwm/ns
			zSample = self.signal[i]
			for j in range (0,n_pwm/ns):
				self.z_signal[i*n_pwm/ns+j] = zSample
				if (j<=t_on):
					self.pwm_signal[i*n_pwm/ns+j] = 1.0
				else:
					self.pwm_signal[i*n_pwm/ns+j] = 0.0
		plt.plot(self.xx,self.pwm_signal,self.z_signal)
		plt.title("time domain analog and pwm signal")
		plt.show()
		# do fft()
		self.f_cpx = np.fft.fft(self.pwm_signal)
		self.fz_cpx= np.fft.fft(self.z_signal)
		#plt.plot(self.xx,(self.f_cpx.real**2 + self.f_cpx.imag**2)**0.5/n_pwm,(self.fz_cpx.real**2+self.fz_cpx.imag**2)**0.5/n_pwm)
		plt.plot(self.xx,(self.f_cpx.real**2 + self.f_cpx.imag**2)**0.5/n_pwm)
		plt.title("PWM signal spectrum")
		plt.show()
		plt.plot(self.xx,(self.fz_cpx.real**2+self.fz_cpx.imag**2)**0.5/n_pwm)
		plt.title("Z signal sectrum")
		plt.show()
		plt.plot(self.xx,(self.f_cpx.real**2 + self.f_cpx.imag**2)**0.5/n_pwm,(self.fz_cpx.real**2+self.fz_cpx.imag**2)**0.5/n_pwm)
		plt.title("Spectrum PWM and Z signals")
		plt.show()


	def create(self,f1=1.0,f_pwm=400.0):
		ns=400
		npwm=1024*ns #pwm time resolution=1024
		gen_signal(0.5,f1,ns)
		gen_pwm(ns,npwm)
		show()



