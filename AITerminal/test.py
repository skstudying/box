import os
from dotenv import load_dotenv  
import io 
import azure.cognitiveservices.speech as speechsdk
#from openai import AzureOpenAI
import openai
import time
import datetime  
import threading  
import json, ast
import pygame  
import requests, json
from io import BytesIO 
import tempfile 
import subprocess  


load_dotenv("xiaoxin.env")  

os.environ["OPENAI_API_TYPE"] = os.environ["Azure_OPENAI_API_TYPE1"]
os.environ["OPENAI_API_BASE"] = os.environ["Azure_OPENAI_API_BASE1"]
os.environ["OPENAI_API_KEY"] = os.environ["Azure_OPENAI_API_KEY1"]
os.environ["OPENAI_API_VERSION"] = os.environ["Azure_OPENAI_API_VERSION1"]
BASE_URL=os.environ["OPENAI_API_BASE"]
# API_KEY=os.environ["OPENAI_API_KEY"]
API_KEY = "sk-jE516y7ADSphPxJN7d5f92F8Fb064d3e95A871Cb1c399bBb"
Chat_Deployment=os.environ["Azure_OPENAI_Chat_API_Deployment"]
Whisper_key=os.environ["Azure_Whisper_API_KEY"]
Whisper_endpoint = os.environ["Azure_Whisper_API_Url"]
Azure_speech_key= os.environ["Azure_speech_key"]
Azure_speech_region= os.environ["Azure_speech_region"]
Azure_speech_speaker= os.environ["Azure_speech_speaker"]
WakeupWord = os.environ["WakeupWord"]
WakeupModelFile=os.environ["WakeupModelFile"]
os.environ["AZURE_API_KEY"] =API_KEY
os.environ["AZURE_API_BASE"] =BASE_URL
os.environ["AZURE_API_VERSION"] =os.environ["Azure_OPENAI_API_VERSION1"]

messages = []
openai.api_key =API_KEY
openai.api_base = BASE_URL
openai.api_type = os.environ["OPENAI_API_TYPE"] 
# openai.api_version = os.environ["OPENAI_API_VERSION"]


# Set up Azure Speech-to-Text and Text-to-Speech credentials
speech_key = Azure_speech_key
service_region = Azure_speech_region
speech_config = speechsdk.SpeechConfig(subscription=speech_key, region=service_region)
# Set up Azure Text-to-Speech language 
speech_config.speech_synthesis_language = "zh-CN"
# Set up Azure Speech-to-Text language recognition
speech_config.speech_recognition_language = "zh-CN"
#auto_detect_source_language_config = speechsdk.languageconfig.AutoDetectSourceLanguageConfig(languages=["en-US", "ja-JP","zh-CN"])
lang="zh-CN"
# Set up the voice configuration
speech_config.speech_synthesis_voice_name = Azure_speech_speaker
speech_synthesizer = speechsdk.SpeechSynthesizer(speech_config=speech_config)

# Creates an instance of a keyword recognition model. Update this to
# point to the location of your keyword recognition model.
model = speechsdk.KeywordRecognitionModel(WakeupModelFile)
# The phrase your keyword recognition model triggers on.
keyword = WakeupWord
# Create a local keyword recognizer with the default microphone device for input.
#keyword_recognizer = speechsdk.KeywordRecognizer()
done = False

# Set up the audio configuration
audio_config = speechsdk.audio.AudioConfig(use_default_microphone=True)
# Create a speech recognizer and start the recognition
speech_recognizer = speechsdk.SpeechRecognizer(speech_config=speech_config,  audio_config=audio_config)
unknownCount=0
sysmesg={"role": "system", "content": os.environ["sysprompt_"+lang]}
messages=[]


def getLLMResponse(message):
    i=20
    messages_ai = {"role": "system", "content": message} 
    sysmesg={"role": "system", "content": os.environ["sysprompt_"+lang]}    
    response = openai.ChatCompletion.create(
        model = "gpt-4o",
        messages=[sysmesg]+[messages_ai],
        temperature=0.6,
        max_tokens=500,
        stream=False
    )
    print(response)
    return response.choices[0].message

def get_llm_response(message):
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }
    data = {
        "model": "gpt-4o",  # 确保模型名是正确的
        "messages": [
            {"role": "system", "content": os.getenv(f"sysprompt_zh-CN")},
            {"role": "user", "content": message}
        ],
        "temperature": 0.6,
        "max_tokens": 500
    }
    response = requests.post(f"{BASE_URL}/v1/chat/completions", json=data, headers=headers)
    response_json = response.json()
    
    if 'choices' in response_json and len(response_json['choices']) > 0:
        ai_response_content = response_json['choices'][0]['message']['content']
        return ai_response_content
    else:
        return "Error"

while True:
    user_input = input()
    print(f"You said: {user_input}")

    # Generate a response using OpenAI
    #prompt = f"Q: {user_input}\nA:"
    response = getLLMResponse(user_input)
    #response = user_input
    print(f"AI says: {response}")
    
