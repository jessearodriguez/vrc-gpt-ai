

from numpy import append
import pyttsx3
import pydub 

import sounddevice as sd
import time

import config
import os
import numpy as np

#replace with betterprofanity  https://pypi.org/project/better-profanity/




def generate_ttsmp3(text: str, ttsFlag, ttsFlag2):
    print(f"tts: {text}")
    engine = pyttsx3.init(driverName='sapi5')
    voices = engine.getProperty('voices')
    engine.setProperty('voice', voices[1].id)

    
    
    engine.setProperty('rate', config.tts_wpm)
    engine.save_to_file(text, 'tts.wav')
    engine.runAndWait()

    sound = pydub.AudioSegment.from_file("tts.wav")
    sound = sound.set_frame_rate(48000)
    
 
   

    
    data = sound.get_array_of_samples()

    sd.default.device = "Line 1 (Virtual Audio Cable), Windows WASAPI"
    ttsFlag.get()
    sd.play(data)


    sd.wait()
    sd.stop()
    os.remove("tts.wav")
    ttsFlag2.get()



def tts_run(queue, ttsFlag, ttsFlag2, ttsEvent):

    print("\nTTS ready\n")
    ttsEvent.set()
    while True:
        if queue.qsize() > 0:
            generate_ttsmp3(queue.get(), ttsFlag, ttsFlag2)
        else:
            time.sleep(.1)





