import sys, os
from queue import Queue
import time
from communication import Communication
import sounddevice as sd
import numpy as np
import json
from pyroomacoustics.denoise.spectral_subtraction import apply_spectral_sub

CHANNELS = 1  # support only 1
SELF_LOOP_FLAG = True
DENOISE_FLAG = True

factor = 0
delta = 0.001
iters = 100


def callback(indata, outdata, frames, time, status):
    if conf['debug']:
        print('mic => {}\tspk => {}\t{}'.format(from_mic_buff.qsize(), to_speaker_buff.qsize(), status))
        print('mic => {:.2f}\tspk => {:.2f}'.format(time.inputBufferAdcTime, time.outputBufferDacTime))

    # try get frame from queue. zeros if empty
    try:
        output_data_bytes = to_speaker_buff.get_nowait()
    except:
        print('output_data_bytes is empty')
        output_data_bytes = b'\x00' * conf['frame_size']

    # send data to speakers
    outdata[:, 0] = np.frombuffer(output_data_bytes, dtype=conf['data_type'])

    # get data from mic
    if DENOISE_FLAG:
        tmp_fct = factor
        for i in range(iters):
            std_up = np.std(indata - (tmp_fct + delta) * outdata)
            std_dn = np.std(indata - (tmp_fct - delta) * outdata)
            if std_up > std_dn:
                tmp_fct -= delta
            else:
                tmp_fct += delta
        print(tmp_fct)
        to_sock_data = indata - tmp_fct * outdata
        # to_sock_data = indata - factor * outdata
        from_mic_buff.put(np.round(to_sock_data).astype(conf['data_type']).tobytes())

    #     d = 1
    #     in_sig = indata / d
    #     denoised_signal = apply_spectral_sub(in_sig[:, 0], nfft=512,
    #                                          db_reduc=10, lookback=5,
    #                                          beta=20, alpha=3)
    #     denoised_data = denoised_signal * d
    #     from_mic_buff.put(np.round(denoised_data).astype(conf['data_type']).tobytes())
    else:
        from_mic_buff.put(indata.tobytes())

# read config file
with open('config.json') as json_file:
    conf = json.load(json_file)

# init queue
to_speaker_buff = Queue()
from_mic_buff = Queue()

# init communication
com = Communication(to_speaker_buff, from_mic_buff, conf['port'], conf['frame_size'])

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
            from_mic_buff.put(to_speaker_buff.get())
else:
    print('Connect to: ' + connect_id)
    server_ip = my_ip[:my_ip.rfind('.')] + '.' + connect_id
    com.connect(server_ip)
    print('Connected!')

# init block size
sample_per_byte = int(round(int(conf['data_type'][3:])/8))
block_size = int(conf['frame_size'] / sample_per_byte)

print('sample_per_byte', sample_per_byte, 'block_size', block_size)

# scnr = Subspace(frame_len=2*block_size, mu=10, lookback=10, skip=2, thresh=0.01)

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
