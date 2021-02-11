import sys, os
from queue import Queue
import time
from communication import Communication
import sounddevice as sd
import numpy as np
import json
from asyncio import QueueEmpty

CHANNELS = 1  # support only 1
SELF_LOOP_FLAG = True


def callback(indata, outdata, frames, time, status):
    if conf['debug']:
        print('mic => {}\tspk => {}\t({})'.format(from_comp_buff.qsize(), from_sock_buff.qsize(), status))

    # try get frame from queue. zeros if empty
    try:
        output_data_bytes = from_sock_buff.get_nowait()
    except:
        output_data_bytes = b'\x00' * conf['frame_size']

    # send data to speakers
    outdata[:, 0] = np.frombuffer(output_data_bytes, dtype=conf['data_type'])

    # get data from mic
    from_comp_buff.put(indata.tobytes())

# read config file
with open('config.json') as json_file:
    conf = json.load(json_file)

# init queue
from_sock_buff = Queue()
from_comp_buff = Queue()

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

    # For Test
    # Server pass all data to client as is
    if SELF_LOOP_FLAG:
        while True:
            from_comp_buff.put(from_sock_buff.get())
else:
    print('Connect to: ' + connect_id)
    server_ip = my_ip[:my_ip.rfind('.')] + '.' + connect_id
    com.connect(server_ip)
    print('Connected!')

# init block size
block_size = int(conf['frame_size'] / conf['bytes_per_sample'])

s = sd.Stream(channels=CHANNELS,
              callback=callback,
              dtype=conf['data_type'],
              blocksize=block_size,
              samplerate=conf['fs'])
# run
with s:
    sd.sleep(int(conf['duration'] * 1000))

# close communication
com.close()
