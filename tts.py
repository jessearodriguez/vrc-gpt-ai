

from numpy import append
import pyttsx3
import pydub 

import sounddevice as sd
import time

import config
import os
#replace with betterprofanity  https://pypi.org/project/better-profanity/




def generate_ttsmp3(text: str, ttsFlag, ttsFlag2):

    engine = pyttsx3.init(driverName='sapi5')
    voices = engine.getProperty('voices')
    engine.setProperty('voice', voices[1].id)

    
    
    engine.setProperty('rate', config.tts_wpm)
    engine.save_to_file(text, 'tts.mp3')
    engine.runAndWait()

    sound = pydub.AudioSegment.from_file("tts.mp3")
    sound = sound.set_frame_rate(48000)

   

    
    data = sound.get_array_of_samples()

    sd.default.device = "Line 1 (Virtual Audio Cable), Windows WASAPI"
    ttsFlag.get()
    sd.play(data)


    sd.wait()
    os.remove("tts.mp3")
    ttsFlag2.get()



def tts_run(queue, ttsFlag, ttsFlag2, ttsEvent):

    print("\nTTS ready\n")
    ttsEvent.set()
    while True:
        if queue.qsize() > 0:
            generate_ttsmp3(queue.get(), ttsFlag, ttsFlag2)
        else:
            time.sleep(.1)





