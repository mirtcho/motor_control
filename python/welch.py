import numpy as np
from scipy import signal
import matplotlib.pyplot as plt
import test as t

def w_file():
  f=t.fast_file()
  ch1=f.load('IL1_dac48KHz.pkl')
  ch2=f.load('IL2_dac48KHz.pkl')
  ch3=f.load('IL3_dac48KHz.pkl')
  ch4=f.load('IL1_currentprobe48KHz.pkl')

  Fs=2500000

  freq, Pch1_den = signal.welch(ch1, Fs, nperseg=1024*64)
  freq, Pch2_den = signal.welch(ch2, Fs, nperseg=1024*64)
  freq, Pch3_den = signal.welch(ch3, Fs, nperseg=1024*64)
  freq, Pch4_den = signal.welch(ch4, Fs, nperseg=1024*64)

  plt.semilogy(freq, Pch1_den, freq, Pch2_den, freq, Pch3_den)
  plt.show()
  
def plt_welch():
  t1 = t.Test()
  t1.acq()
  f=t.fast_file()
  f.save('Iq5ApereVolt_offse0_Fs625KT200sec_noise277_3k5.pkl'     ,t1.channel1_data)
  f.save('Id5ApereVolt_offset-46A_Fs625KT200sec_noise277_3k5.pkl' ,t1.channel2_data)
  f.save('CtrOutId_0_01_offset-0_5_Fs625KT200sec_noise277_3k5.pkl',t1.channel3_data)
  f.save('CtrOutIq_0_01_offset-0_0_Fs625KT200sec_noise277_3k5.pkl',t1.channel4_data)
  Fs = 625000 #10sec/div 125Msamples
  fft_len=256*1024
  freq, Pch1_den = signal.welch(t1.channel1_data, Fs, nperseg=fft_len)
  freq, Pch2_den = signal.welch(t1.channel2_data, Fs, nperseg=fft_len)
  freq, Pch3_den = signal.welch(t1.channel3_data, Fs, nperseg=fft_len)
  freq, Pch4_den = signal.welch(t1.channel4_data, Fs, nperseg=fft_len)
  plt.semilogy(freq, Pch1_den, label='Iq')
  plt.semilogy(freq, Pch2_den, label='Id')
  plt.semilogy(freq, Pch3_den, label='CtrId')
  plt.semilogy(freq, Pch4_den, label='CtrIq')
  plt.legend()
  plt.show()

def plt_file():
  f=t.fast_file()
  channel1_data = f.load('Iq5ApereVolt_offse0_Fs625KT200sec_noise277_1k0.pkl')
  channel2_data = f.load('Id5ApereVolt_offset-46A_Fs625KT200sec_noise277_1k0.pkl')
  channel3_data = f.load('CtrOutId_0_01_offset-0_5_Fs625KT200sec_noise277_1k0.pkl')
  channel4_data = f.load('CtrOutIq_0_01_offset-0_0_Fs625KT200sec_noise277_1k0.pkl')
  Fs = 625000 #20sec/div 125Msamples 200sec captured data
  fft_len=256*1024
  freq, Pch1_den = signal.welch(channel1_data, Fs, nperseg=fft_len)
  freq, Pch2_den = signal.welch(channel2_data, Fs, nperseg=fft_len)
  freq, Pch3_den = signal.welch(channel3_data, Fs, nperseg=fft_len)
  freq, Pch4_den = signal.welch(channel4_data, Fs, nperseg=fft_len)
  #plt.semilogy(freq, Pch1_den, label='Iq')
  plt.semilogy(freq, Pch2_den, label='Id')
  plt.semilogy(freq, Pch3_den, label='CtrOutId')
  #plt.semilogy(freq, Pch4_den, label='CCtrOutIq')
  plt.legend()
  plt.show()
  #new graph with transfer function plant
  plt.title('Sensitivity plot - CTR+ Plant')
  plt.semilogy(freq, Pch2_den/Pch3_den, label='Id')
  plt.show()
  
def plt_4k_vs_1k():
  f=t.fast_file()
  channel1_data_1k = f.load('Iq5ApereVolt_offse0_Fs625KT200sec_noise277_1k0.pkl')
  channel2_data_1k = f.load('Id5ApereVolt_offset-46A_Fs625KT200sec_noise277_1k0.pkl')
  channel3_data_1k = f.load('CtrOutId_0_01_offset-0_5_Fs625KT200sec_noise277_1k0.pkl')
  channel4_data_1k = f.load('CtrOutIq_0_01_offset-0_0_Fs625KT200sec_noise277_1k0.pkl')
  channel1_data_4k = f.load('Iq5ApereVolt_offse0_Fs625KT200sec_noise277_3k5.pkl')
  channel2_data_4k = f.load('Id5ApereVolt_offset-46A_Fs625KT200sec_noise277_3k5.pkl')
  channel3_data_4k = f.load('CtrOutId_0_01_offset-0_5_Fs625KT200sec_noise277_3k5.pkl')
  channel4_data_4k = f.load('CtrOutIq_0_01_offset-0_0_Fs625KT200sec_noise277_3k5.pkl')
  Fs = 625000 #20sec/div 125Msamples
  fft_len=256*1024
  freq, Pch1_den_1k = signal.welch(channel1_data_1k, Fs, nperseg=fft_len)
  freq, Pch2_den_1k = signal.welch(channel2_data_1k, Fs, nperseg=fft_len)
  freq, Pch3_den_1k = signal.welch(channel3_data_1k, Fs, nperseg=fft_len)
  freq, Pch4_den_1k = signal.welch(channel4_data_1k, Fs, nperseg=fft_len)
  freq, Pch1_den_4k = signal.welch(channel1_data_4k, Fs, nperseg=fft_len)
  freq, Pch2_den_4k = signal.welch(channel2_data_4k, Fs, nperseg=fft_len)
  freq, Pch3_den_4k = signal.welch(channel3_data_4k, Fs, nperseg=fft_len)
  freq, Pch4_den_4k = signal.welch(channel4_data_4k, Fs, nperseg=fft_len)  
  #new graph with transfer function plant
  plt.title('Sensitivity plot - CTR+ Plant')
  plt.semilogy(freq, Pch2_den_1k/Pch3_den_1k, label='1k')
  plt.semilogy(freq, Pch2_den_4k/Pch3_den_4k, label='4k')
  plt.legend()
  plt.show()
