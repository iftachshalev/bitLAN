import sounddevice as sd
from scipy.io.wavfile import write
from playsound import playsound
from threading import Thread
import time


def play_sound():
    playsound('output.wav')


def play_sound2():
    playsound('output2.wav')


fs = 44100
seconds = 3
myrecording = sd.rec(int(seconds * fs), samplerate=fs, channels=2)
sd.wait()
write('output.wav', fs, myrecording)
thread = Thread(target=play_sound)
thread.start()
print("f")
myrecording = sd.rec(int(seconds * fs), samplerate=fs, channels=2)
sd.wait()
write('output2.wav', fs, myrecording)
thread = Thread(target=play_sound2)
thread.start()
print("f")
