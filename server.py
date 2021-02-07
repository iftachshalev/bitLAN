import sys, os
from queue import Queue

sys.path.append(os.path.abspath('.'))
from communication import Communication

from_sock_buff = Queue()
from_comp_buff = Queue()
port = 12345
frame_size = 32

com = Communication(from_sock_buff, from_comp_buff, port, frame_size)
com.listen()

for i in range(100):
    from_comp_buff.put('hello from server: {}'.format(i).encode())
    print(from_sock_buff.get())

com.close()