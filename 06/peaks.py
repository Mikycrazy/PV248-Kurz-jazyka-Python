from scipy.io import wavfile
from numpy.fft import rfft
import numpy as np

rate, audio = wavfile.read('06/SineWave_440Hz.wav')

if len(audio.shape) == 2:
    audio = np.mean(audio, axis=1)

N = audio.shape[0]
L = N / rate
print(f'Audio length: {L:.2f} seconds')

M = rate
audio = audio[:(N // M) * M]
slices = np.matrix(np.split(audio, M))
print(f'Audio shape: {audio.shape}, Sliced audio shape: {slices.shape}')

slices = slices.T
spectrum = rfft(slices, axis=1)
spectrum = np.abs(spectrum)

peaks = []
for window in spectrum:
    avg = np.average(window)
    for idx, value in enumerate(window):
        if((avg * 20) < value):
            peaks.append(idx)

if(len(peaks) > 0):
    a = np.amin(peaks)
    b = np.amax(peaks)
    print(f'low = {a}, high = {b}')
else:
    print('no peaks')

