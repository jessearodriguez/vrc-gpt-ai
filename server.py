import requests
import json
import re
import html
import os


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



memory = deque([""]*config.memory*2, maxlen=config.memory*2) #FIFO queue to keep track of chat history
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
        listenCD.wait()
        print("Listening...")
        client.send_message("/chatbox/input", ["Listening...", True])
        while listenqueue.qsize() == 0:
            time.sleep(.5)
        stopFlag.put(1)
        heardtext = listenqueue.get()
        censoredText = censorMessage(heardtext)

        print(f"Heard: {heardtext} Thinking...")
        client.send_message("/chatbox/input", [f"Heard: {censoredText} Thinking...", True])

        memory.append(f"You: {heardtext}")

        history = ""
        for sentence in memory:
            if sentence != "":
                history = history + f"\n{sentence}"

        inputtext = f"{config.context} \n {history} \n{config.ai_name}:"
        
        #print(inputtext)
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
        config.memory,
    ]}).json()
        
        data = response["data"][0]
        data = data.splitlines()

        print(data[-1])
        censoredResponse = censorMessage(data[-1])
        ttsqueue.put(censoredResponse[len(config.ai_name)+1:]) #ignore ai name and semicolon in tts reponse
        ttsFlag.put(1)
        while ttsFlag.qsize()>0:
            time.sleep(.05)

        #wait for playback to start before sending message data, but send rn
        ttsFlag2.put(1)#set this flag when tts starts speaking, will be removed by the tts process
        msgarr = wrap(censoredResponse, 143)# splits and wraps text block into <144 sized character chunks in ordre to fit inside the osc chatbox
        
        for block in msgarr:
            client.send_message("/chatbox/input", [block, True])
            time.sleep(len(block.split())/config.tts_wpm/60) #words in block divided by spoken words per second


        #wait for tts to finish
        while ttsFlag2.qsize()>0:
            time.sleep(.05)
        memory.append(data[-1])
        
        stopFlag.get()

        print("Wait...")
        client.send_message("/chatbox/input", ["Wait...", True])


