import speech_recognition as sr
import pyttsx3
import pywhatkit
import datetime
import wikipedia
import pyjokes
import webbrowser
import requests
import logging
from geopy.geocoders import Nominatim


logging.basicConfig(level=logging.INFO)

listener = sr.Recognizer()
engine = pyttsx3.init()
voices = engine.getProperty('voices')
engine.setProperty('voice', voices[1].id)

def talk(text):
    engine.say(text)
    engine.runAndWait()

def wish_user():
    hour = datetime.datetime.now().hour
    if 0 <= hour < 12:
        greeting = "Hello sir, Good Morning"
    elif 12 <= hour < 18:
        greeting = "Hello sir, Good Afternoon"
    else:
        greeting = "Hello sir, Good Evening"
    
    talk(greeting)
    print(greeting)

wish_user()

def take_command():
    with sr.Microphone() as source:
        print("Listening...")
        listener.adjust_for_ambient_noise(source)  # Adjust for ambient noise
        try:
            voice = listener.listen(source)
            command = listener.recognize_google(voice)
            command = command.lower()
            if 'luna' in command:
                command = command.replace('luna', '').strip()
            return command
        except sr.UnknownValueError:
            talk("Sorry, I didn't catch that. Please repeat.")
            return ""
        except sr.RequestError as e:
            talk(f"There is a problem with the speech recognition service: {e}")
            return ""
        except Exception as e:
            talk(f"An unexpected error occurred: {e}")
            return ""

def get_location_from_ip():
    try:
        response = requests.get('http://ip-api.com/json/')
        data = response.json()
        if data['status'] == 'success':
            return data['lat'], data['lon']
    except requests.RequestException as e:
        logging.error(f"Error fetching location: {e}")
    return None, None

def get_directions_web(start_location, end_location):
    google_maps_url = f"https://www.google.com/maps/dir/?api=1&origin={start_location}&destination={end_location}"
    webbrowser.open(google_maps_url)

def search_wikipedia(query):
    """Search Wikipedia and handle errors."""
    try:
        return wikipedia.summary(query, sentences=1)
    except wikipedia.exceptions.DisambiguationError:
        return f"Multiple results found for {query}. Be more specific."
    except wikipedia.exceptions.PageError:
        return f"Sorry, no information found for {query}."

def search_nearby_hospitals(lat, lng):
    search_query = f"nearby hospitals near {lat},{lng}"
    url = f"https://www.google.com/search?q={search_query}"
    webbrowser.open(url)
    return ["Searching for nearby hospitals..."]

def run_luna():
    command = take_command()
    if not command:
        return
    print(f"Command: {command}")

    if 'play' in command:
        song = command.replace('play', '').strip()
        talk(f"Playing {song}")
        pywhatkit.playonyt(song)

    elif 'news' in command:
        webbrowser.open_new_tab("https://timesofindia.indiatimes.com/home/headlines")
        talk("Opening Times of India. Have a reading.")

    elif 'show my location' in command:
        talk("Fetching your location...")
        lat, lng = get_location_from_ip()
        if lat and lng:
            google_maps_url = f"https://www.google.com/maps?q={lat},{lng}"
            talk("Showing your location on Google Maps.")
            print(f"Your current location: {lat}, {lng}")
            webbrowser.open(google_maps_url)
        else:
            talk("Unable to get location. Please check your internet connection.")

    elif 'open youtube' in command:
        talk("Taking you to YouTube")
        webbrowser.open("https://www.youtube.com")

    elif 'open google' in command:
        talk("Taking you to Google")
        webbrowser.open("https://www.google.com")

    elif 'time' in command:
        time = datetime.datetime.now().strftime('%I:%M %p')
        talk(f"Current time is {time}")

    elif 'who is' in command:
        person = command.replace('who is', '').strip()
        info = search_wikipedia(person)
        talk(info)

    elif 'what is' in command:
        item = command.replace('what is', '').strip()
        info = search_wikipedia(item)
        talk(info)

    elif 'joke' in command:
        talk(pyjokes.get_joke())

    elif 'search' in command:
        search_query = command.replace('search', '').strip()
        url = f"https://google.com/search?q={search_query}"
        webbrowser.open(url)
        talk("Here is your search result.")

    elif 'what is your name' in command:
        talk("My name is Luna.")

    elif 'directions from' in command and 'to' in command:
        try:
            parts = command.split('directions from')[1].split('to')
            start = parts[0].strip()
            end = parts[1].strip()
            talk(f"Getting directions from {start} to {end}.")
            get_directions_web(start, end)
        except IndexError:
            talk("Sorry, I couldn't understand the locations properly.")

    elif 'nearby hospitals' in command:
        talk("Fetching your location to find nearby hospitals...")
        lat, lng = get_location_from_ip()
        if lat and lng:
            hospitals = search_nearby_hospitals(lat, lng)
            for hospital in hospitals:
                talk(hospital)
                print(hospital)
        else:
            talk("Unable to get location. Please check your internet connection.")

    elif 'you may go' in command:
        talk("Goodbye, sir. You can call me anytime.")
        return "exit"
    elif 'bye' in command:
        talk("Goodbye, sir. You can call me anytime.")
        return "exit"

    else:
        talk("Sorry, I didn't understand. Please repeat.")

while True:
    if run_luna() == "exit":
        break