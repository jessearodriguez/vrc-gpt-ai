import pyaudio
mic = pyaudio.PyAudio()
info = mic.get_host_api_info_by_index(0)
numdevices = info.get('deviceCount')

for i in range(0, numdevices):
    if (mic.get_device_info_by_host_api_device_index(0, i).get('maxInputChannels')) > 0:
        print("Input Device id ", i, " - ", mic.get_device_info_by_host_api_device_index(0, i).get('name'))

import pyttsx3

engine = pyttsx3.init()
voices = engine.getProperty('voices')


engine.setProperty('voice', voices[1].id)
#engine.say('The quick brown fox jumped over the lazy dog.')
#engine.runAndWait()


import sounddevice as sd

print(sd.query_devices())

"""while True:



    inputtext = input("Enter message: ")
    response = requests.post("http://127.0.0.1:7860/run/textgen", json={
    "data": [
        inputtext,
        config.maxtok,
        True,
        config.maxtok,
        config.temperature,
        config.top_p,
        config.typical_p,
        config.repetition_penalty,
        config.top_k,
        config.min_length,
        config.no_repeat_ngram,
        config.num_beams,
        config.penalty_alpha,
        config.length_penalty,
        config.early_stopping,
        config.chatter_name,
        config.ai_name,
        config.context,
        config.stop_gen,
        config.memory,
    ]}).json()
    requests.post("http://127.0.0.1:7860/run/textgen", json={
    "data": [
        inputtext,
        config.maxtok,
        True,
        config.maxtok,
        config.temperature,
        config.top_p,
        config.typical_p,
        config.repetition_penalty,
        config.top_k,
        config.min_length,
        config.no_repeat_ngram,
        config.num_beams,
        config.penalty_alpha,
        config.length_penalty,
        config.early_stopping,
        config.chatter_name,
        config.ai_name,
        config.context,
        config.stop_gen,
        config.memory,
    ]}).json()
    requests.post("http://127.0.0.1:7860/run/textgen", json={
    "data": [
        inputtext,
        config.maxtok,
        True,
        config.maxtok,
        config.temperature,
        config.top_p,
        config.typical_p,
        config.repetition_penalty,
        config.top_k,
        config.min_length,
        config.no_repeat_ngram,
        config.num_beams,
        config.penalty_alpha,
        config.length_penalty,
        config.early_stopping,
        config.chatter_name,
        config.ai_name,
        config.context,
        config.stop_gen,
        config.memory,
    ]}).json()
    #The api seems to require multiple requests before it can be called again
    


    
    data = response["data"]
    jsondata = json.dumps(data, indent=2)

    
    index = len(data[0]) -1 if len(data[0]) > 0 else 0

    result = re.sub('<[^<]+?>', '', data[0][index][1])
    
    print(html.unescape(result))
    print("\n\n")
"""