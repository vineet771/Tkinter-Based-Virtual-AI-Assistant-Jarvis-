import tkinter as tk
from tkinter import scrolledtext
import speech_recognition as sr
import webbrowser
import pyttsx3
import musicLibrary
import requests
from openai import OpenAI
from gtts import gTTS
import pygame
import os
import threading

recognizer = sr.Recognizer()
engine = pyttsx3.init()
newsapi = "<Your Key Here>"

client = OpenAI(api_key="")  



def speak(text):
    tts = gTTS(text)
    tts.save('temp.mp3')
    pygame.mixer.init()
    pygame.mixer.music.load('temp.mp3')
    pygame.mixer.music.play()

    while pygame.mixer.music.get_busy():
        pygame.time.Clock().tick(10)

    pygame.mixer.music.unload()
    os.remove("temp.mp3")


# AI Response 
def aiProcess(command):
    completion = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are Jarvis, a helpful assistant like Alexa. Respond briefly."},
            {"role": "user", "content": command}
        ]
    )
    return completion.choices[0].message.content


# Command Processor 
def processCommand(c):
    log(f"Command: {c}")
    if "open google" in c.lower():
        webbrowser.open("https://google.com")
        speak("Opening Google")
    elif "open facebook" in c.lower():
        webbrowser.open("https://facebook.com")
        speak("Opening Facebook")
    elif "open youtube" in c.lower():
        webbrowser.open("https://youtube.com")
        speak("Opening YouTube")
    elif "open linkedin" in c.lower():
        webbrowser.open("https://linkedin.com")
        speak("Opening LinkedIn")
    elif c.lower().startswith("play"):
        song = c.lower().split(" ")[1]
        link = musicLibrary.music.get(song, None)
        if link:
            webbrowser.open(link)
            speak(f"Playing {song}")
        else:
            speak("Song not found in library")
    elif "news" in c.lower():
        r = requests.get(f"https://newsapi.org/v2/top-headlines?country=in&apiKey={newsapi}")
        if r.status_code == 200:
            articles = r.json().get('articles', [])
            for article in articles[:5]:
                speak(article['title'])
        else:
            speak("Couldn't fetch news")
    else:
        output = aiProcess(c)
        log(f"Jarvis: {output}")
        speak(output)


# Listen and Process
def listen():
    try:
        with sr.Microphone() as source:
            recognizer.adjust_for_ambient_noise(source)
            log("Listening for 'Jarvis'...")
            audio = recognizer.listen(source, timeout=3, phrase_time_limit=5)
            word = recognizer.recognize_google(audio)

            if word.lower() == "jarvis":
                speak("Yes?")
                log("Jarvis activated.")
                with sr.Microphone() as source:
                    audio = recognizer.listen(source, timeout=5)
                    command = recognizer.recognize_google(audio)
                    processCommand(command)
            else:
                log("Wake word not detected.")
    except Exception as e:
        log(f"Error: {str(e)}")


#  GUI Logging 
def log(message):
    log_box.insert(tk.END, f"{message}\n")
    log_box.see(tk.END)


# Threading Wrapper 
def threaded_listen():
    threading.Thread(target=listen).start()


# GUI Setup
app = tk.Tk()
app.title("Jarvis AI Assistant")
app.geometry("900x700")
app.configure(bg="#121212")

title = tk.Label(app, text="🎙️ Jarvis Voice Assistant", font=("Arial", 16), fg="white", bg="#121212")
title.pack(pady=10)

log_box = scrolledtext.ScrolledText(app, width=60, height=15, bg="#1e1e1e", fg="white", insertbackground="white")
log_box.pack(pady=10)

listen_btn = tk.Button(app, text="🎧 Start Listening", command=threaded_listen, font=("Arial", 12), bg="#4CAF50", fg="white")
listen_btn.pack(pady=10)

exit_btn = tk.Button(app, text="❌ Exit", command=app.quit, font=("Arial", 12), bg="#f44336", fg="white")
exit_btn.pack()

log("Jarvis Initialized...")

app.mainloop()
