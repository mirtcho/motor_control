import hid

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
  
def read_sample():
  wr=b'\x00\x00\x86\x66'
  rr.write(wr)
  r1 = rr.read(8)
  r2 = rr.read(8)
  r3 = rr.read(8)  
  #print('#',x,'.',r1,r2,r3)
  digit1 = decode1(r1[3])
  digit2 = decode1(r1[4])
  digit3 = decode1(r1[5])
  digit4 = decode1(r1[6])
  digit5 = decode1(r1[7])
  digit6 = decode1(r2[0])
  #print ('decode=',d1,d2,d3,d4,d5,d6 )
  decimal_position = find_decimal_point(r1[3],r1[4],r1[5],r1[6])
  result = (digit1*100000+digit2*10000+digit3*1000+digit4*100+digit5*10+digit6)/(10**decimal_position)
  return result

def test ():
  hid.enumerate()
  rr=hid.Device(0x820,1)
  for x in range(6):
    print (x,'=',read_sample())

