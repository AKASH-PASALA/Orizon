import os
import re
import time
import subprocess
import webbrowser
import tempfile
import datetime

import sounddevice as sd
import soundfile as sf
import speech_recognition as sr
import pyttsx3
import ollama
import file_manager
import computer_control



# ---------------- CONFIGURATION ----------------

MODEL = "qwen2.5:3b"
SAMPLE_RATE = 16000
RECORD_SECONDS = 5

recognizer = sr.Recognizer()
speaker = pyttsx3.init()

speaker.setProperty("rate", 175)
speaker.setProperty("volume", 1.0)


# ---------------- VOICE OUTPUT ----------------
def speak(text):
    print(f"\nOrizon: {text}\n")

    engine = None

    try:
        engine = pyttsx3.init("sapi5")
        engine.setProperty("rate", 165)
        engine.setProperty("volume", 1.0)

        engine.say(text)
        engine.runAndWait()

    except Exception as error:
        print(f"VOICE ERROR: {error}")

    finally:
        if engine is not None:
            try:
                engine.stop()
            except Exception:
                pass

            del engine

        time.sleep(0.5)
# ---------------- SPEECH INPUT ----------------

def listen():
    print("Listening... Speak your command!")

    audio_data = sd.rec(
        int(RECORD_SECONDS * SAMPLE_RATE),
        samplerate=SAMPLE_RATE,
        channels=1,
        dtype="int16"
    )

    sd.wait()

    filename = None

    try:
        with tempfile.NamedTemporaryFile(
            suffix=".wav", delete=False
        ) as temp:
            filename = temp.name

        sf.write(filename, audio_data, SAMPLE_RATE)

        with sr.AudioFile(filename) as source:
            audio = recognizer.record(source)

        text = recognizer.recognize_google(audio)

        text = text.lower().strip()

        print(f"You: {text}")

        return text

    except sr.UnknownValueError:
        print("Couldn't understand the recording.")
        return ""

    except sr.RequestError as error:
        print(f"Speech recognition service error: {error}")
        return ""

    except Exception as error:
        print(f"Audio error: {error}")
        return ""

    finally:
        if filename and os.path.exists(filename):
            os.remove(filename)


# ---------------- COMMAND NORMALIZATION ----------------

def normalize_command(text):
    text = text.lower().strip()

    # Remove common variations of the wake word.
    wake_words = [
        "orizon",
        "horizon",
        "origin",
        "orison",
        "orazin"
    ]

    for word in wake_words:
        text = re.sub(
            rf"\b{word}\b",
            " ",
            text,
            count=1
        )
        break

    text = re.sub(r"[^\w\s]", " ", text)
    text = re.sub(r"\s+", " ", text)
    

    return text.strip()


# ---------------- TASK EXECUTION ----------------

def execute_command(command):

    command = normalize_command(command)

    # Remove polite phrases.
    command = re.sub(
        r"\b(please|can you|could you|would you|will you)\b",
        " ",
        command
    )

    command = re.sub(r"\s+", " ", command).strip()

    print(f"Command detected: {command}")

    # NOTEPAD
    if "notepad" in command and any(
        word in command for word in ["open", "start", "launch"]
    ):
        subprocess.Popen(["notepad.exe"])
        speak("Opening Notepad, Boss.")
        return True

    # CALCULATOR
    if "calculator" in command and any(
        word in command for word in ["open", "start", "launch"]
    ):
        subprocess.Popen(["calc.exe"])
        speak("Opening Calculator, Boss.")
        return True

    # BROWSER
    if any(word in command for word in [
        "browser", "google", "website", "web browser"
    ]) and any(word in command for word in [
        "open", "start", "launch"
    ]):
        webbrowser.open("https://www.google.com")
        speak("Opening your browser, Boss.")
        return True

    # YOUTUBE
    if "youtube" in command and any(
        word in command for word in ["open", "start", "launch"]
    ):
        speak("Opening YouTube, Boss.")

        time.sleep(1)

        webbrowser.open("https://www.youtube.com")
        return True

    # TIME
    if "time" in command:
        current_time = datetime.datetime.now().strftime("%I:%M %p")
        speak(f"Boss, the time is {current_time}.")
        return True

    # DATE
    if "date" in command or "today" in command:
        current_date = datetime.datetime.now().strftime(
            "%A, %d %B %Y"
        )
        speak(f"Boss, today is {current_date}.")
        return True

    # EXIT
    if any(phrase in command for phrase in [
        "shutdown orizon",
        "stop orizon",
        "exit assistant",
        "close assistant"
    ]):
        speak("Going offline, Boss.")
        return False
    # FILE EXPLORER
        if "file explorer" in command and any(
            word in command for word in ["open", "start", "launch"]
        ):
            subprocess.Popen(["explorer.exe"])
            speak("Opening File Explorer, Boss.")
            return True
    
        # DOWNLOADS FOLDER
        if "downloads" in command and any(
            word in command for word in ["open", "show", "go to"]
        ):
            downloads = os.path.join(
                os.path.expanduser("~"),
                "Downloads"
            )
            os.startfile(downloads)
            speak("Opening your Downloads folder, Boss.")
            return True
    
        # VS CODE
        if any(word in command for word in [
            "vs code", "visual studio code"
        ]) and any(
            word in command for word in ["open", "start", "launch"]
        ):
            subprocess.Popen(["code"])
            speak("Opening Visual Studio Code, Boss.")
            return True
        # CREATE FOLDER
    if command.startswith("create folder "):
        folder_name = command[len("create folder "):].strip()

        result = file_manager.create_folder(folder_name)
        speak(result)
        return True

    # CREATE TEXT FILE
    if command.startswith("create file "):
        file_name = command[len("create file "):].strip()

        result = file_manager.create_file(file_name)
        speak(result)
        return True

    # OPEN DOWNLOADS FOLDER
    if command in ["open downloads", "show downloads"]:
        downloads = os.path.join(
            os.path.expanduser("~"),
            "Downloads"
        )

        if os.path.isdir(downloads):
            speak("Opening your Downloads folder, Boss.")
            os.startfile(downloads)
        else:
            speak("Boss, I couldn't find your Downloads folder.")

        return True

    # OPEN ORIZON FILE WORKSPACE
    if command in [
        "open my files",
        "open orizon files",
        "open my workspace"
    ]:
        speak("Opening your Orizon files, Boss.")
        file_manager.open_folder()
        return True

    # SEARCH FOR A FILE
    if command.startswith("search file "):
        file_name = command[len("search file "):].strip()

        result = file_manager.search_file(file_name)
        speak(result)
        return True

    # READ A TEXT FILE
    if command.startswith("read file "):
        file_name = command[len("read file "):].strip()

        result = file_manager.read_text_file(file_name)
        speak(result)
        return True

    # LIST FILES
    if command in [
        "list my files",
        "list files",
        "show my files"
    ]:
        result = file_manager.list_files()
        speak(result)
        return True
        # ==============================
    # APPLICATION CONTROL
    # ==============================

    # OPEN GOOGLE CHROME
    if "chrome" in command and any(
        word in command for word in ["open", "start", "launch"]
    ):
        chrome_paths = [
            os.path.expandvars(
                r"%PROGRAMFILES%\Google\Chrome\Application\chrome.exe"
            ),
            os.path.expandvars(
                r"%PROGRAMFILES(X86)%\Google\Chrome\Application\chrome.exe"
            ),
            os.path.expandvars(
                r"%LOCALAPPDATA%\Google\Chrome\Application\chrome.exe"
            )
        ]

        chrome = next(
            (path for path in chrome_paths if os.path.isfile(path)),
            None
        )

        if chrome:
            speak("Opening Google Chrome, Boss.")
            subprocess.Popen([chrome])
        else:
            speak(
                "Boss, I couldn't find Google Chrome. "
                "Please check whether it is installed."
            )

        return True

    # OPEN WINDOWS SETTINGS
    if "settings" in command and any(
        word in command for word in ["open", "start", "launch"]
    ):
        speak("Opening Windows Settings, Boss.")
        os.startfile("ms-settings:")
        return True

    # OPEN TASK MANAGER
    if "task manager" in command and any(
        word in command for word in ["open", "start", "launch"]
    ):
        speak("Opening Task Manager, Boss.")
        subprocess.Popen(["taskmgr.exe"])
        return True

    # OPEN COMMAND PROMPT
    if "command prompt" in command and any(
        word in command for word in ["open", "start", "launch"]
    ):
        speak("Opening Command Prompt, Boss.")
        subprocess.Popen(["cmd.exe"])
        return True

    # OPEN FILE EXPLORER
    if "file explorer" in command and any(
        word in command for word in ["open", "start", "launch"]
    ):
        speak("Opening File Explorer, Boss.")
        subprocess.Popen(["explorer.exe"])
        return True
        # ==============================
    # KEYBOARD AND MOUSE AUTOMATION
    # ==============================

    # TYPE TEXT
    if command.startswith("type "):
        text_to_type = command[len("type "):].strip()

        if text_to_type:
            speak("Typing now, Boss.")
            result = computer_control.type_text(text_to_type)
            speak(result)

        return True

    # PRESS ENTER
    if command in ["press enter", "hit enter"]:
        result = computer_control.press_key("enter")
        speak(result)
        return True

    # PRESS ESCAPE
    if command in ["press escape", "press esc"]:
        result = computer_control.press_key("escape")
        speak(result)
        return True

    # PRESS TAB
    if command == "press tab":
        result = computer_control.press_key("tab")
        speak(result)
        return True

    # SAVE DOCUMENT
    if command in ["save", "save document", "press control s"]:
        speak("Saving, Boss.")
        result = computer_control.save_document()
        return True

    # SWITCH WINDOW
    if command in ["switch window", "change window", "next window"]:
        result = computer_control.switch_window()
        speak(result)
        return True

    # COPY SELECTED CONTENT
    if command in ["copy", "copy selected text"]:
        result = computer_control.copy_selected()
        speak(result)
        return True

    # PASTE CONTENT
    if command in ["paste", "paste content"]:
        result = computer_control.paste_content()
        speak(result)
        return True

    # TAKE SCREENSHOT
    if command in ["take screenshot", "capture screen", "screenshot"]:
        speak("Taking a screenshot, Boss.")
        result = computer_control.take_screenshot()
        speak(result)
        return True

    return None


# ---------------- LOCAL AI BRAIN ----------------

def ask_ai(question):

    if not question:
        speak("Yes, Boss? What should I do?")
        return

    try:
        response = ollama.chat(
            model=MODEL,
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are Orizon, a private personal AI assistant. "
                        "Address the user as Boss. "
                        "Be helpful and concise. "
                        "Do not claim to have executed computer actions "
                        "unless a tool actually executed them."
                    )
                },
                {
                    "role": "user",
                    "content": question
                }
            ]
        )

        answer = response["message"]["content"]

        speak(answer)

    except Exception as error:
        print(f"AI error: {error}")
        speak("Boss, I couldn't connect to my local AI brain.")


# ---------------- MAIN LOOP ----------------

def main():

    speak("Orizon is online, Boss.")

    speak("Boss, this is Orizon speaking from the main program.")

    while True:

        text = listen()

        if not text:
            continue

        # Only process commands that include the wake word.
        wake_pattern = r"\b(orizon|horizon|origin|orison|orazin)\b"

        if not re.search(wake_pattern, text):
            continue

        command = re.sub(
            wake_pattern,
            " ",
            text,
            count=1
        )

        command = re.sub(r"\s+", " ", command).strip()

        # Wake word only.
        if not command:
            speak("Yes, Boss. I'm listening.")
            command = listen()

            if not command:
                continue

        result = execute_command(command)

        if result is False:
            break

        if result is None:
            ask_ai(normalize_command(command))

        time.sleep(0.3)

    print("Orizon stopped.")


if __name__ == "__main__":
    try:
        main()

    except KeyboardInterrupt:
        print("\nOrizon stopped, Boss.")