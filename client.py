import sys, os
from queue import Queue
import time
from communication import Communication

sys.path.append(os.path.abspath('.'))

from_sock_buff = Queue()
from_comp_buff = Queue()
port = 12345
frame_size = 32

com = Communication(from_sock_buff, from_comp_buff, port, frame_size)
com.connect('192.168.1.206')

for i in range(100):
    from_comp_buff.put('hello from client: {}'.format(i).encode())
    print(from_sock_buff.get())
    time.sleep(0.2)