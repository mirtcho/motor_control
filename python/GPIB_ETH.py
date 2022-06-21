import socket
import numpy as np
import matplotlib.pyplot as plt

HOST='10.0.0.131'
PORT=1234
buf_len=123400000

s=socket.socket(socket.AF_INET,socket.SOCK_STREAM,socket.IPPROTO_TCP)
a=s.connect((HOST,1234))
r=s.recv(buf_len)
print (r)
#convert string to list
a_list=r.split()
#convert list to numpy
x=np.array(a_list)
#convert string numpy array to floats 
x_float=x.astype(np.float)
mean=np.mean(x_float)
std=np.std(x_float)
plt.plot(y)
plt.show()
s.close()

