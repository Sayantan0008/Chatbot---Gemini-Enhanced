import google.generativeai as genai
import os
from dotenv import load_dotenv
import time
import pyttsx3
import speech_recognition as sr
import webbrowser
import subprocess
import platform
from urllib.parse import quote_plus



load_dotenv()

def speak(text, engine):
    
    """Function to convert text to speech"""
    try:
        # Check if engine is busy
        if not engine._inLoop:
            engine.say(text)
            engine.runAndWait()
    except:
        # Reinitialize engine if there's an error
        try:
            engine.endLoop()
        except:
            pass
        engine = pyttsx3.init()
        voices = engine.getProperty('voices')
        voice_index = 1 if len(voices) > 1 else 0
        engine.setProperty('voice', voices[voice_index].id)
        engine.setProperty('rate', 150)
        engine.say(text)
        engine.runAndWait()

def listen():
    """Function to capture voice input and convert to text"""
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        print("\nAdjusting for ambient noise... Please wait...")
        # Adjust for ambient noise
        recognizer.adjust_for_ambient_noise(source, duration=1)
        
        # Increase the energy threshold for better voice detection
        recognizer.energy_threshold = 4000
        recognizer.dynamic_energy_threshold = True
        
        print("Listening...", end=" ", flush=True)
        try:
            # Increase timeout and phrase time limit for longer phrases
            audio = recognizer.listen(source, timeout=20, phrase_time_limit=10)
            print("Processing...", end=" ", flush=True)
            
            # Use language specification and increase sensitivity
            text = recognizer.recognize_google(audio, 
                                            language='en-US', 
                                            show_all=False)
            print(f"\nYou said: {text}")
            return text
        except sr.WaitTimeoutError:
            print("\nNo speech detected within timeout.")
            return ""
        except sr.UnknownValueError:
            print("\nSorry, I couldn't understand that. Please speak clearly and try again.")
            return ""
        except sr.RequestError as e:
            print(f"\nSorry, there was an error with the speech recognition service: {e}")
            return ""

def open_application(app_name):
    """Function to open applications based on the operating system"""
    app_name = app_name.lower()
    system = platform.system().lower()
    
    # Dictionary of applications
    windows_apps = {
        'chrome' or 'google chrome': r'C:\Program Files\Google\Chrome\Application\chrome.exe',
        'firefox': r'C:\Program Files\Mozilla Firefox\firefox.exe',
        'notepad': 'notepad.exe',
        'calculator': 'calc.exe',
        'explorer': 'explorer.exe',
        'spotify': 'Spotify.exe'
    }
    
    mac_apps = {
        'chrome': 'open -a "Google Chrome"',
        'firefox': 'open -a Firefox',
        'safari': 'open -a Safari',
        'calculator': 'open -a Calculator',
        'finder': 'open -a Finder',
        'spotify': 'open -a Spotify'
    }
    
    # Dictionary of common websites
    websites = {
        'youtube': 'https://www.youtube.com',
        'google': 'https://www.google.com',
        'facebook': 'https://www.facebook.com',
        'twitter' or 'x': 'https://www.x.com',
        'github': 'https://www.github.com',
        'netflix': 'https://www.netflix.com'
    }
    
    try:
        # Check if it's a website request
        if app_name in websites:
            webbrowser.open(websites[app_name])
            return f"Opening {app_name} in your default browser"
            
        # Handle application requests based on OS
        if system == 'windows':  # Windows
            if app_name in windows_apps:
                subprocess.Popen(windows_apps[app_name])
                return f"Opening {app_name}"
        elif system == 'darwin':  # macOS
            if app_name in mac_apps:
                os.system(mac_apps[app_name])
                return f"Opening {app_name}"
        elif system == 'linux':
            subprocess.Popen([app_name])
            return f"Attempting to open {app_name}"
            
        return f"Sorry, I don't know how to open {app_name}"
    except Exception as e:
        return f"Error opening {app_name}: {str(e)}"

def search_and_play_youtube(query):
    """Function to search and play YouTube videos"""
    try:
        # Remove words like 'play', 'search', 'youtube' from the query
        clean_query = query.lower()
        for word in ['play', 'search', 'youtube', 'video', 'for']:
            clean_query = clean_query.replace(word, '').strip()
            
        # Create YouTube search URL
        search_url = f"https://www.youtube.com/results?search_query={quote_plus(clean_query)}"
        
        # Open in default browser
        webbrowser.open(search_url)
        return f"Searching YouTube for '{clean_query}'"
    except Exception as e:
        return f"Error searching YouTube: {str(e)}"




def chatbot():
    # Configure Gemini API
    genai.configure(api_key=os.getenv('GEMINI_API_KEY'))
    
    # Initialize text-to-speech engine
    engine = pyttsx3.init()
    voices = engine.getProperty('voices')
    voice_index = 1 if len(voices) > 1 else 0
    engine.setProperty('voice', voices[voice_index].id)
    engine.setProperty('rate', 150)
    
    # Create a model instance
    model = genai.GenerativeModel('gemini-pro')
    
    # Initial context setting
    initial_prompt = """You are a friendly and helpful AI assistant. 
    Be conversational, show enthusiasm, and engage with the user naturally. 
    Keep responses concise but warm."""
    
    print("\n=== AI Chatbot Started ===")
    print("Say 'bye' to end the conversation.\n")
    
    # Start a chat session with the initial context
    chat = model.start_chat(history=[])
    chat.send_message(initial_prompt)
    
    while True:
        user_input = listen().strip().lower()
        
        if not user_input:
            continue
            
        # Check for exit command
        if user_input == 'bye':
            print("\n Bot: Goodbye! Have a great day! \n")
            speak("Goodbye! Have a great day!", engine)
            return
            
        try:
            # Check for YouTube commands
            if any(word in user_input.lower() for word in ['play', 'search']) and \
                any(word in user_input.lower() for word in ['youtube', 'video']):
                result = search_and_play_youtube(user_input)
                print(f"\n Bot: {result}")
                speak(result, engine)
                continue
                
            # Check for navigation commands
            if any(keyword in user_input for keyword in ['open', 'launch', 'start']):
                for keyword in ['open', 'launch', 'start']:
                    if keyword in user_input:
                        app_name = user_input.split(keyword)[-1].strip()
                        break
                
                result = open_application(app_name)
                print(f"\n Bot: {result}")
                speak(result, engine)
                continue
            
            
            # Regular chat response
            print("  Bot is thinking", end="")
            for _ in range(3):
                time.sleep(0.3)
                print(".", end="", flush=True)
            print("\r", end="")
            
            response = chat.send_message(user_input)
            response_text = response.text
            print(f"\r Bot: {response_text}\n")
            speak(response_text, engine)
            
        except Exception as e:
            error_message = f"Oh no! I ran into an error: {str(e)}"
            print("\n Bot:", error_message)
            speak(error_message, engine)

# Run the chatbot
if __name__ == "__main__":
    try:
        chatbot()
    except KeyboardInterrupt:
        print("\n\n Bot: Goodbye! \n")
