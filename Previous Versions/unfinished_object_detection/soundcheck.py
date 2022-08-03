import audioop
import time
import pyaudio


def soundcheck(numtargets):
    chunk = 1024
    # opening audio stream
    p = pyaudio.PyAudio()
    playing = False
    stream = p.open(format=pyaudio.paInt16,
                    channels=1,
                    rate=4000,
                    input=True,
                    input_device_index=4,
                    frames_per_buffer=chunk)
    # increments targets whenever sound is detected
    while True:
        data = stream.read(chunk)
        rms = audioop.rms(data, 2)
        if rms > 1000:
            if not playing:
                playing = True
                numtargets.value += 1
        else:
            playing = False
        time.sleep(.01)
