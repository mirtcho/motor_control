import hid
#test post processing relaated imports
from datetime import datetime 
import test as t
import numpy as np
from scipy import signal
import matplotlib.pyplot as plt
import allantools

def decode1 (st):
#decode the 7 segment digit
  st = st & 0xfe
  if st == 0xbe: d = 0
  if st == 0xa0: d = 1
  if st == 0xda: d = 2
  if st == 0xf8: d = 3
  if st == 0xe4: d = 4 #
  if st == 0x7c: d = 5 #
  if st == 0x7e: d = 6 
  if st == 0xa8: d = 7 
  if st == 0xfe: d = 8 # 
  if st == 0xfc or st == 0xec: d = 9 #
  return d

def find_decimal_point(s1,s2,s3,s4):
  position = 0       # no decimal point
  if s1 & 0x01 == 1:
    position = 5
  if s2 & 0x01 == 1:
    position = 4
  if s3 & 0x01 == 1:
    position = 3
  if s4 & 0x01 == 1:
    position = 2
  return position

def get_sign(data):
  if (data & 0x20) == 0:
    sign = 1
  else:
    sign =-1
  return sign  

def read_sample(rr):
##############################################
# Software packet does not match documentation
# Table matching doc and sw packet
# SW byte#       DOC byte nr       Example value   Doc_Field
#  0                 1             0x0             ID
#  1                 3             0x11            Avg,Min,Max,H,C,R,Auto
#  2                 4             0x10            T1,T2,+,-, VFD
#  3                 5             0xbe            Main Digit 1
#  4                 6             0xbf            Main Digit 2
#  5                 7             0xbe            Main Digit 3
#  6                 8             0xbe            Main Digit 4
#  7                 9             0xbe            Main Digit 5
#  8- 50,000 counts 11             0x01
#  8-500,000 counts 11             0xa1            Main Digit 6-500,000 mode


  wr=b'\x00\x00\x86\x66'
  rr.write(wr)
  r1 = rr.read(8) # usb v1.1 HID packets are 8 bytes
  r2 = rr.read(8)
  r3 = rr.read(8)  
  #print('#',x,'.',r1,r2,r3)
  digit1 = decode1(r1[3])
  digit2 = decode1(r1[4])
  digit3 = decode1(r1[5])
  digit4 = decode1(r1[6])
  digit5 = decode1(r1[7])
  try:
    digit6 = decode1(r2[0])
  except:
    digit6=0
  #print ('decode=',d1,d2,d3,d4,d5,d6 )
  decimal_position = find_decimal_point(r1[3],r1[4],r1[5],r1[6])
  sign = get_sign(r1[2])
  result = sign*(digit1*100000+digit2*10000+digit3*1000+digit4*100+digit5*10+digit6)/(10**decimal_position)
  return result

def test (nr_samples=200,file_name='bm869_1.pkl'):
  data = np.empty(nr_samples)
  hid.enumerate()
  rr=hid.Device(0x820,1)  
  start_time = datetime.now() 
  for x in range(nr_samples):
    data[x] = read_sample(rr)
    print (x,'=',data[x])
  end_time = datetime.now()
  time_difference = (end_time - start_time).total_seconds() 
  print("Execution time of program is: ", time_difference, "sec") 
  print("Sample rate =",nr_samples/time_difference,'S/sec')
  f=t.fast_file()
  f.save(file_name, data)
  #dmm1=f.load('mb869_1.pkl')
  
def allan_dev(f_name='bm869_4v8_Vdc.pkl'):
  f=t.fast_file()
  data_set= f.load (f_name)
  Fs = 5
  len = data_set.size
  print ('Sigma=',np.std(data_set),'Begin=',data_set[1],'End=',data_set[len-1])
  # Compute a deviation using the Dataset class
  a = allantools.Dataset(data=data_set)
  a.compute("mdev")
  # New in 2019.7 : write results to file
  #a.write_result("output.dat")
  # Plot it using the Plot class
  b = allantools.Plot()
  # New in 2019.7 : additional keyword arguments are passed to
  # matplotlib.pyplot.plot()
  b.plot(a, errorbars=True, grid=True)
  # You can override defaults before "show" if needed
  b.ax.set_xlabel("Tau (s)")
  b.show()

