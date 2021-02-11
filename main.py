import sys, os
from queue import Queue
import time
from communication import Communication
import sounddevice as sd
import numpy as np
import json


def output_callback(outdata, frames, time, status):
    if conf['debug']:
        print('out:\t{}\t{}'.format(from_sock_buff.qsize(), status))
    data = from_sock_buff.get()
    outdata[:, 0] = np.frombuffer(data, dtype=conf['data_type'])


def input_callback(indata, frames, time, status):
    if conf['debug']:
        print('in:\t{}\t{}'.format(from_comp_buff.qsize(), status))
    from_comp_buff.put(indata.tobytes())


# read config file
with open('config.json') as json_file:
    conf = json.load(json_file)

# init queue
from_sock_buff = Queue()
from_comp_buff = Queue()

data = b'\x00' * (conf['frame_size'])
for i in range(2):
    from_sock_buff.put(data)

# init communication
com = Communication(from_sock_buff, from_comp_buff, conf['port'], conf['frame_size'])

# get user desision
my_ip = Communication.get_ip()
print('My ID is: ' + my_ip[my_ip.rfind('.') + 1:])
connect_id = input('Enter ID (or blank if server)  >> ')
if connect_id == '':
    print('Wait for connections...')
    com.listen()
    print('Connected by: ' + repr(com.addr))
else:
    print('Connect to: ' + connect_id)
    server_ip = my_ip[:my_ip.rfind('.')] + '.' + connect_id
    com.connect(server_ip)
    print('Connected!')

# init block size
block_size = int(conf['frame_size'] / conf['bytes_per_sample'])

s_out = sd.OutputStream(channels=1,
                        callback=output_callback,
                        dtype=conf['data_type'],
                        blocksize=block_size,
                        samplerate=conf['fs'])

s_in = sd.InputStream(channels=1,
                      callback=input_callback,
                      dtype=conf['data_type'],
                      blocksize=block_size,
                      samplerate=conf['fs'])

# run
with s_out, s_in:
    sd.sleep(int(conf['duration'] * 1000))

# close communication
com.close()
