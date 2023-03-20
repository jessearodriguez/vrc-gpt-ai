import requests
import json
import re
import html
import os
import unicodedata

from pythonosc import udp_client

import config

import tts

import multiprocessing

import time
from better_profanity import profanity


from vosper import main as vspr

from collections import deque
from textwrap import wrap


client = udp_client.SimpleUDPClient(config.ip, config.sendport)



memory = deque([], maxlen=int(config.memory*2)) #FIFO queue to keep track of chat history
#need to rewrite this into seperate memory banks
def censorMessage(text:str)->str:

    message = profanity.censor(text, '|')
    newmessage = ""
    group = False
    for char in message:
        if char == '|':
            if not group:
                newmessage = newmessage + ' CENSORED '
                group= True


        else:
            group = False
            newmessage += char
    return newmessage


if __name__ == '__main__':


    print("Setup...")
    client.send_message("/chatbox/input", ["Setting up...", True])


    profanity.load_censor_words()

    listenqueue = multiprocessing.Queue()
    ttsqueue = multiprocessing.Queue()
    ttsFlag = multiprocessing.Queue() #could replace with events eventually
    ttsFlag2 = multiprocessing.Queue()
    stopFlag = multiprocessing.Queue()


    startupListeningEvent = multiprocessing.Event()
    startupTtsEvent = multiprocessing.Event()
    listenCD = multiprocessing.Event()
    

    listenCD.set()

    listnprocess = multiprocessing.Process(target=vspr.vspr_run, args=(listenqueue,stopFlag, startupListeningEvent, listenCD))
    ttsprocess = multiprocessing.Process(target=tts.tts_run, args=(ttsqueue,ttsFlag, ttsFlag2, startupTtsEvent))

    listnprocess.start()
    ttsprocess.start()

    


    startupTtsEvent.wait()#wait for setup to begin
    startupListeningEvent.wait()


    while True: 
        #print(memory)
        listenCD.wait()
        print("Listening...")
        client.send_message("/chatbox/input", ["Listening...", True])
        while listenqueue.qsize() == 0:
            time.sleep(.5)
        stopFlag.put(1)
        heardtext = listenqueue.get()
        censoredText = censorMessage(heardtext)

        if(censoredText.isspace()): continue

        #print(f"Heard: {censoredText} Thinking...")
        client.send_message("/chatbox/input", [f"Heard: {censoredText} Thinking...", True])
        #maybe threading loop to change the elipsese on 'thinking...' ?
        

        history = ""
        for sentence in memory:
            if sentence != "":
                history = history + f"\n{sentence}"
        #history += "\n"
        #print(f"History: \n{history}"){history}
        inputtext = f"{config.context}\n<START>\n{config.example_dialogue}\n{config.chatter_name}: {heardtext}\n{config.ai_name}: "
        print(inputtext)
        params = {
        'max_new_tokens': config.maxtok,
        'do_sample': True,
        'temperature': config.temperature,
        'top_p': config.top_p,
        'typical_p': config.typical_p,
        'repetition_penalty': config.repetition_penalty,
        'top_k': config.top_k,
        'min_length': config.min_length,
        'no_repeat_ngram_size': config.no_repeat_ngram,
        'num_beams': config.num_beams,
        'penalty_alpha': config.penalty_alpha,
        'length_penalty': config.length_penalty,
        'early_stopping': config.early_stopping,
    }

        #for some reason this api needs 2 post requests to return something usefull

        response = requests.post(f"http://{config.ip}:7860/run/textgen", json={
            "data": [
                inputtext,
                1,
                params['do_sample'],
                params['temperature'],
                params['top_p'],
                params['typical_p'],
                params['repetition_penalty'],
                params['top_k'],
                0,
                params['no_repeat_ngram_size'],
                params['num_beams'],
                params['penalty_alpha'],
                params['length_penalty'],
                params['early_stopping'],
            ]
        }).json()
        
        response2 = requests.post(f"http://{config.ip}:7860/run/textgen", json={
            "data": [
                inputtext,
                params['max_new_tokens'],
                params['do_sample'],
                params['temperature'],
                params['top_p'],
                params['typical_p'],
                params['repetition_penalty'],
                params['top_k'],
                params['min_length'],
                params['no_repeat_ngram_size'],
                params['num_beams'],
                params['penalty_alpha'],
                params['length_penalty'],
                params['early_stopping'],
            ]
        }).json()
        


        data = response["data"][0]
        data2 = response2["data"][0]
        #print(data+"\n\n\n")
        #print(data2)
        data = data2


        data = data.splitlines()
        
        
        censoredResponse = html.unescape(censorMessage(unicodedata.normalize('NFKC',html.escape(data[-1]))))
        if (censoredResponse[len(config.ai_name)+1:].isspace()):
            stopFlag.get()
            print("Wait...")
            client.send_message("/chatbox/input", ["Wait...", True])
            continue
        ttsqueue.put(censoredResponse[len(config.ai_name)+1:]) #ignore ai name and semicolon in tts reponse
        ttsFlag.put(1)
        while ttsFlag.qsize()>0:
            time.sleep(.05)

        #wait for playback to start before sending message data, but send rn
        ttsFlag2.put(1)#set this flag when tts starts speaking, will be removed by the tts process
        msgarr = wrap(censoredResponse, 143)# splits and wraps text block into <144 sized character chunks in ordre to fit inside the osc chatbox
        
        for block in msgarr:
            client.send_message("/chatbox/input", [block, True])
            #print(f"sleeptime: {len(block.split())/(config.tts_wpm/60)}, {len(block.split())}, {(config.tts_wpm/60)} ")

            time.sleep(len(block.split())/(config.tts_wpm/60)) #words in block divided by spoken words per second
            time.sleep(.1)


        #wait for tts to finish
        while ttsFlag2.qsize()>0:
            time.sleep(.05)
            
        memory.append(f"{config.chatter_name}: {heardtext}")
        memory.append(data[-1])
        
        stopFlag.get()

        print("Wait...")
        client.send_message("/chatbox/input", ["Wait...", True])

