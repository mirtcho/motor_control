import hid

hid.enumerate()
rr=hid.Device(0x820,1)
wr=b'\x00\x00\x86\x66'


def decode (st):
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
  
def test ():
  for x in range(6):
    rr.write(wr)
    r1 = rr.read(8)
    r2 = rr.read(8)
    r3 = rr.read(8)  
    #print('#',x,'.',r1,r2,r3)
    d1=decode(r1[3])
    d2=decode(r1[4])
    d3=decode(r1[5])
    d4=decode(r1[6])
    d5=decode(r1[7])
    d6=decode(r2[0])
    print ('decode=',d1,d2,d3,d4,d5,d6 )
