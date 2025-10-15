import speech_recognition as sr
import pyttsx3
import pywhatkit
import datetime
import time
import requests
import wikipedia
import pyjokes
import os

# ---------------------------
# Text-to-Speech setup
# ---------------------------
engine = pyttsx3.init()
voices = engine.getProperty('voices')
engine.setProperty('voice', voices[1].id)   # 0 = male, 1 = female
engine.setProperty('rate', 170)

def speak(text):
    print("Assistant:", text)
    engine.say(text)
    engine.runAndWait()
    time.sleep(3)  # small pause for smoother interaction

# ---------------------------
# Speech Recognition setup
# ---------------------------
def listen():
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        print("🎤 Listening...")
        recognizer.adjust_for_ambient_noise(source, duration=0.5)
        try:
            audio = recognizer.listen(source, phrase_time_limit=7)
        except sr.WaitTimeoutError:
            print("⏳ No speech detected")
            return ""
    try:
        command = recognizer.recognize_google(audio)
        command = command.lower()
        print("You said:", command)
        return command
    except sr.UnknownValueError:
        speak("Sorry, I didn't catch that.")
        return ""
    except sr.RequestError:
        speak("Speech recognition service error.")
        return ""

# ---------------------------
# Features
# ---------------------------
def tell_time():
    current_time = datetime.datetime.now().strftime("%I:%M %p")
    speak("The time is " + current_time)

def tell_date():
    today = datetime.date.today().strftime("%B %d, %Y")
    speak("Today's date is " + today)

def play_song(command):
    song = command.replace("play", "").strip()
    if song:
        speak("Playing " + song)
        pywhatkit.playonyt(song)
    else:
        speak("Please tell me which song to play.")

def get_weather(command):
    api_key = "99fd6f3c5e17bab6d49a435e905b5edb"  # ✅ your weather API key
    
    # Extract city from command
    words = command.split()
    city = "Hyderabad"  # default
    if "in" in words:
        city_index = words.index("in") + 1
        if city_index < len(words):
            city = words[city_index]

    url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}&units=metric"
    try:
        response = requests.get(url).json()
        # print("DEBUG Weather API response:", response)  # debug

        if "main" in response:
            temp = response["main"]["temp"]
            desc = response["weather"][0]["description"]
            speak(f"The weather in {city} is {desc} with {temp} degrees Celsius.")
        elif "message" in response:
            speak(f"Weather error: {response['message']}")
        else:
            speak("Sorry, I couldn't fetch the weather right now.")
    except Exception as e:
        print("DEBUG Error:", e)
        speak("Weather service not available.")

def get_news(command):
    api_key = "b0972deefb514e618c2a15cbd314edef"  # ✅ your news API key
    
    # Default top headlines
    url = f"https://newsapi.org/v2/top-headlines?country=in&apiKey={api_key}"
    
    # Category-based search
    if "technology" in command:
        url = f"https://newsapi.org/v2/top-headlines?country=in&category=technology&apiKey={api_key}"
    elif "sports" in command:
        url = f"https://newsapi.org/v2/top-headlines?country=in&category=sports&apiKey={api_key}"
    elif "business" in command:
        url = f"https://newsapi.org/v2/top-headlines?country=in&category=business&apiKey={api_key}"
    elif "health" in command:
        url = f"https://newsapi.org/v2/top-headlines?country=in&category=health&apiKey={api_key}"
    elif "science" in command:
        url = f"https://newsapi.org/v2/top-headlines?country=in&category=science&apiKey={api_key}"
    elif "entertainment" in command:
        url = f"https://newsapi.org/v2/top-headlines?country=in&category=entertainment&apiKey={api_key}"

    try:
        response = requests.get(url).json()
        print("DEBUG News API response:", response)  # debug

        if "articles" in response and response["articles"]:
            headlines = [article["title"] for article in response["articles"][:5]]
            speak("Here are the top news headlines.")
            for h in headlines:
                speak(h)
        elif "message" in response:
            speak(f"News error: {response['message']}")
        else:
            speak("Sorry, I couldn't fetch the news right now.")
    except Exception as e:
        print("DEBUG Error:", e)
        speak("News service not available.")

def search_wikipedia(command):
    query = command.replace("wikipedia", "").strip()
    try:
        result = wikipedia.summary(query, sentences=2)
        speak(result)
    except:
        speak("Sorry, I couldn't find that on Wikipedia.")

def tell_joke():
    joke = pyjokes.get_joke()
    speak(joke)

def take_note():
    speak("What should I write down?")
    note = listen()
    if note:
        with open("notes.txt", "a") as f:
            f.write(f"{datetime.datetime.now()}: {note}\n")
        speak("Note saved.")
    else:
        speak("I didn't hear anything to save.")

def open_app(command):
    if "notepad" in command:
        speak("Opening Notepad.")
        os.system("notepad")
    elif "calculator" in command:
        speak("Opening Calculator.")
        os.system("calc")
    elif "chrome" in command:
        speak("Opening Chrome.")
        os.system("start chrome")
    else:
        speak("I don't know how to open that yet.")

# ---------------------------
# Main Loop
# ---------------------------
def run_assistant():
    speak("Hello! I am your assistant. How can I help you?")
    while True:
        command = listen()

        if command == "":
            continue

        if "time" in command:
            tell_time()
        elif "date" in command:
            tell_date()
        elif "play" in command:
            play_song(command)
        elif "weather" in command:
            get_weather(command)
        elif "news" in command:
            get_news(command)
        elif "wikipedia" in command:
            search_wikipedia(command)
        elif "joke" in command:
            tell_joke()
        elif "note" in command or "remember" in command:
            take_note()
        elif "open" in command:
            open_app(command)
        elif "stop" in command or "exit" in command or "quit" in command:
            speak("Goodbye!")
            break
        elif command != "":
            speak("I can search that for you.")
            pywhatkit.search(command)

        time.sleep(1)

# ---------------------------
# Start
# ---------------------------
if __name__ == "__main__":
    run_assistant()
