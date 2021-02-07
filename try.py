import sounddevice as sd
from time import sleep

fs = 8000# 16000, 44100
block_size = 800
duration = 10
delay = 1
sampl_arr = [0]*(fs*delay+block_size)

def callback(indata, outdata, frames, time, status):
    sampl_arr.append(indata)
    outdata[:] = sampl_arr[-1*(fs*delay):-1*(fs*delay)+block_size]
    print(frames, time, status)


with sd.Stream(channels=1, callback=callback, samplerate=fs, blocksize=block_size, ):
    sd.sleep(int(duration * 1000))
