# pip install pysinewave

from pysinewave import SineWave
from time import sleep

sinewave = SineWave(pitch = 10)
sinewave.play()
for p in range(10, 20):
    sinewave.set_pitch(p)
    sleep(.5)
sinewave.
sinewave.set_volume(0.01)
sleep(.5)
sinewave.stop()