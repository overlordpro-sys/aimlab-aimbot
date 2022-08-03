import pyaudio
import audioop
import time


from multiprocessing import Process, Value, Manager


def detect_sound(numtargets):
  chunk = 1024
  #opening audio stream
  p = pyaudio.PyAudio()
  playing = False
  stream = p.open(format=pyaudio.paInt16,
                  channels=1,
                  rate=12000,
                  input=True,
                  input_device_index = 4,
                  frames_per_buffer=chunk)
  #increments targets whenever sound is detected
  while True:
      data = stream.read(chunk)
      rms = audioop.rms(data,2)
      if rms > 1000:
          if playing == False:
              playing = True
              numtargets.value+=1
      else:
          playing = False
      time.sleep(.01)
      # print(numtargets.value)
#
if __name__ == '__main__':
    manager = Manager()
    tcount = manager.Value('i', 0)
    detect_sound(tcount)
