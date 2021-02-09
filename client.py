import sys, os
from queue import Queue
import time
from communication import Communication
import sounddevice as sd
import numpy as np
duration = 30


def input_callback(indata, frames, time, status):
    from_comp_buff.put(indata.tobytes())
    print(from_comp_buff.qsize())


def output_callback(outdata, frames, time, status):
    print(from_sock_buff.qsize())
    data = from_sock_buff.get()
    outdata[:, 0] = np.frombuffer(data, dtype=np.int32)


sys.path.append(os.path.abspath('.'))

from_sock_buff = Queue()
from_comp_buff = Queue()
port = 12345
frame_size = 2048
block_size = int(frame_size / 4)

com = Communication(from_sock_buff, from_comp_buff, port, frame_size)
com.connect('192.168.1.153')

s_out = sd.OutputStream(channels=1, callback=output_callback, dtype='int32',  blocksize=block_size, samplerate=8000)
s_in = sd.InputStream(channels=1, callback=input_callback, dtype='int32', blocksize=block_size, samplerate=8000)

time.sleep(duration)

s_out.close()
s_in.close()

com.close()
