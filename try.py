import sounddevice as sd


duration = 10


def callback(indata, outdata, frames, time, status):
    outdata[:] = indata


with sd.Stream(channels=2, callback=callback):
    sd.sleep(int(duration * 1000))
