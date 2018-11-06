from scipy.io import wavfile
from numpy.fft import rfft
import numpy as np
import math

A4 = 440
C0 = A4*pow(2, -4.75)
name = ["c","cis","d","es","e","f","βis","g","gis","a","bes","b"]

def pitch(freq):
    h = round(6*math.log2(freq/C0))
    octave = h // 6
    n = h % 6
    return name[n] + str(octave)

rate, audio = wavfile.read('06/SineWave_440Hz.wav')

if len(audio.shape) == 2:
    audio = np.mean(audio, axis=1)

N = audio.shape[0]
L = N / rate
print(f'Audio length: {L:.2f} seconds')

jump = rate // 10

slices = []
for x in range(0, N - jump, jump):
    slices.append(audio[x:x+jump])

slices = np.matrix(slices)
print(f'Audio shape: {audio.shape}, Sliced audio shape: {slices.shape}')

spectrum = rfft(slices, axis=1)
spectrum = np.abs(spectrum)

for windows_idx, window in enumerate(spectrum):
    avg = np.average(window)
    peaks = []
    for idx, value in enumerate(window):
        if((avg * 20) < value):
            peaks.append((idx, value))
    sort = sorted(peaks, key=lambda x: x[1], reverse=True)

    chunks = []

    chunk = []
    for x in sort:
        value = x[0]
        if len(chunk) == 0:
            chunk.append(x)
            continue
        
        if round(avg(chunk) - value) <= 1:
            chunk.append(x)
            continue
        else:
            chunks.append(round(avg(chunk)))
            chunk = []

    top_freq = [pitch(x[0]) for x in chunks[:3]]
    if len(top_freq) > 0:
        start = round(((windows_idx + 1) * 0.1), 1)
        end = round(((windows_idx + 1) * 0.1) + 0.1, 1)
        print(f'{start}-{end} {top_freq}')
