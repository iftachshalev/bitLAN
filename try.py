import sounddevice as sd
from scipy.io.wavfile import write

fs = 44100
seconds = 3
myrecording = sd.rec(int(seconds * fs), samplerate=fs, channels=2)
sd.wait()
write('output.wav', fs, myrecording)
print(bytes(myrecording))
