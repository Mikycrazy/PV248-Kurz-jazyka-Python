from scipy.io import wavfile
from numpy.fft import rfft
import numpy as np
import math

A4 = 440
C0 = A4*pow(2, -4.75)
name = ["c","cis","d","es","e","f","fis","g","gis","a","bes","b"]

def pitch(freq):
    h = round(12*math.log2(freq/C0))
    octave = h // 12
    n = h % 12
    p = name[n]
    if octave == 3:
       return p
    if octave < 3:
        p = p.title()
    if octave < 2:
        p = p + ('\'' * (3 - octave))
    if octave > 3:
        p = p + (',' * (octave - 3))
    return p


print(pitch(440))

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
   
    top = []
    for i in range(3):
        if len(sort) > 0:
            item = sort[0]
            top.append(item)
            sort = [x for x in sort if abs(x[0] - item[0]) > 1]

    top_freq = [pitch(x[0]) for x in top]
    if len(top_freq) > 0:
        start = round(((windows_idx + 1) * 0.1), 1)
        end = round(((windows_idx + 1) * 0.1) + 0.1, 1)
        print(f'{start}-{end} {top_freq}')
