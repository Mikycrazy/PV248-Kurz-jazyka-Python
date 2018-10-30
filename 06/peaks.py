from scipy.io import wavfile
from numpy.fft import rfft
import numpy as np

fs, data = wavfile.read('SineWave_440Hz.wav') #sampleRate, #data
n = len(data) # 132300 number of samples
a = n / fs #fs = 44100 a = 3000ms


cn = np.abs(rfft(data))


