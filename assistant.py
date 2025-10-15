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
    try:
        engine.say(text)
        engine.runAndWait()
    except Exception as e:
        print("Speech Error:", e)
    time.sleep(min(len(text) * 0.05, 1))  # proportional pause

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
    api_key = "99fd6f3c5e17bab6d49a435e905b5edb"
    words = command.split()
    city = "Hyderabad"
    if "in" in words:
        city_index = words.index("in") + 1
        city = " ".join(words[city_index:])

    url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}&units=metric"
    try:
        response = requests.get(url).json()
        if "main" in response:
            temp = response["main"]["temp"]
            desc = response["weather"][0]["description"]
            speak(f"The weather in {city} is {desc} with {temp} degrees Celsius.")
        elif "message" in response:
            speak(f"Weather error: {response['message']}")
        else:
            speak("Sorry, I couldn't fetch the weather right now.")
    except Exception as e:
        print("DEBUG Weather Error:", e)
        speak("Weather service not available.")

def get_news(command):
    api_key = "b0972deefb514e618c2a15cbd314edef"
    url = f"https://newsapi.org/v2/top-headlines?country=in&apiKey={api_key}"

    categories = ["technology", "sports", "business", "health", "science", "entertainment"]
    for cat in categories:
        if cat in command:
            url = f"https://newsapi.org/v2/top-headlines?country=in&category={cat}&apiKey={api_key}"
            break

    try:
        response = requests.get(url).json()
        if not response or response.get("status") != "ok":
            speak("Sorry, I could not fetch the news right now.")
            return

        articles = response.get("articles", [])
        if not articles:
            speak("No news articles available right now.")
            return

        headlines = [a.get("title") for a in articles[:5] if a.get("title")]
        if not headlines:
            speak("No valid headlines found.")
            return

        speak("Here are the top news headlines.")
        for h in headlines:
            speak(h)

    except Exception as e:
        print("DEBUG News Error:", e)
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
        try:
            filepath = os.path.join(os.getcwd(), "notes.txt")
            with open(filepath, "a", encoding="utf-8", errors="ignore") as f:
                f.write(f"{datetime.datetime.now()}: {note}\n")
            speak("Note saved successfully.")
        except Exception as e:
            print("DEBUG File Error:", e)
            speak("I couldn't save the note due to a file error.")
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
# Main Loop (3 iterations)
# ---------------------------
def run_assistant():
    speak("Hello! I am your assistant. How can I help you?")
    attempts = 0
    max_attempts = 3

    while attempts < max_attempts:
        command = listen()
        attempts += 1

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
            speak("Goodbye! Exiting now.")
            break
        else:
            speak("I can search that for you.")
            pywhatkit.search(command)

        time.sleep(1)

    speak("Goodbye! Exiting now.")

# ---------------------------
# Start (Safe Exit)
# ---------------------------
if __name__ == "__main__":
    try:
        run_assistant()
    except KeyboardInterrupt:
        speak("Assistant stopped.")
    except Exception as e:
        print(f"Runtime Error: {e}")
    finally:
        # Clean exit: stop and delete engine
        try:
            engine.endLoop()
        except Exception:
            pass
        try:
            del engine
        except Exception:
            pass
