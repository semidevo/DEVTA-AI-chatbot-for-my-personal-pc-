<div align="center">

```
██████╗ ███████╗██╗   ██╗████████╗ █████╗
██╔══██╗██╔════╝██║   ██║╚══██╔══╝██╔══██╗
██║  ██║█████╗  ██║   ██║   ██║   ███████║
██║  ██║██╔══╝  ╚██╗ ██╔╝   ██║   ██╔══██║
██████╔╝███████╗ ╚████╔╝    ██║   ██║  ██║
╚═════╝ ╚══════╝  ╚═══╝     ╚═╝   ╚═╝  ╚═╝
```

### Your personal AI assistant — like Jarvis, but with an Indian soul.

![Python](https://img.shields.io/badge/Python-3.10+-blue?logo=python)
![Gemini](https://img.shields.io/badge/Powered%20by-Google%20Gemini-orange?logo=google)
![Platform](https://img.shields.io/badge/Platform-Windows-blue?logo=windows)
![License](https://img.shields.io/badge/License-MIT-green)

</div>

---

# Devta AI

**Devta** is a voice-first AI assistant for Windows that runs locally on your laptop.
It listens for a wake word, understands voice commands, and performs real actions on your computer such as opening applications, searching the web, taking screenshots, and managing files.

The assistant uses **Google Gemini** for intelligent responses while keeping most processing local.
Wake words:

Hello Devta
Bhai Devta
Hey Devta

Stop phrase:

Devta stop
Features
Voice Interaction

Wake word detection using Vosk (offline)

Speech-to-text via SpeechRecognition / Vosk

Text-to-speech using pyttsx3

AI Intelligence

Uses Gemini 2.0 Flash Lite for fast responses

Automatically escalates to Gemini 2.5 Flash for complex queries

Maintains conversation context

System Control

Devta can directly control your system:

Open or close applications

Take screenshots

Check battery status

Control volume

Run shell commands

Manage clipboard

Create and read files

Lock, shutdown, or restart the system

Web Integration

Open URLs

Perform Google searches

Monitor active browser tabs

Generate helpful suggestions

Desktop Interface

Dark themed Tkinter chat UI

Voice and text interaction supported

Notifications

Windows toast notifications for suggestions

Smart tips based on browser activity

Project Structure
devta-ai/
│
├── main.py
├── brain.py
├── speech.py
├── wake_word.py
├── system_control.py
├── browser_monitor.py
├── notifier.py
├── ui.py
├── config.py
│
├── setup.bat
├── start_devta.bat
├── requirements.txt
├── .env.example
│
└── vosk_model/
Requirements

Windows 10 or Windows 11

Python 3.10 or higher

Microphone

Gemini API Key

Get a Gemini API key from
https://aistudio.google.com/

Installation
1 Clone the repository
git clone https://github.com/yourusername/devta-ai.git
cd devta-ai
2 Run setup
setup.bat

The setup script will:

create a virtual environment

install dependencies

request your Gemini API key

prepare the start script

3 Download Vosk model

Download:

vosk-model-small-en-us-0.15

From:
https://alphacephei.com/vosk/models

Extract it inside:

vosk_model/
Running Devta

You can start the assistant using:

start_devta.bat

or

python main.py
Configuration

Configuration settings are located in:

config.py

Important parameters:

Setting	Description
WAKE_WORDS	Phrases that activate Devta
STOP_PHRASE	Phrase that disables suggestions
GEMINI_FLASH_MODEL	Default AI model
GEMINI_PRO_MODEL	Model used for complex tasks
TTS_RATE	Speech speed
NOTIFICATION_INTERVAL_SECONDS	Browser monitoring interval
MAX_CONVERSATION_HISTORY	Number of stored messages

Environment variables are defined in:

.env

Example:

GEMINI_API_KEY=your_api_key_here
Example Voice Commands

Open Chrome

Hello Devta
Open Chrome

Take a screenshot

Hello Devta
Take a screenshot

Search the web

Hello Devta
Search for Python tutorials

Check battery

Hello Devta
What's my battery status

Stop notifications

Devta stop

Resume notifications

Devta resume
Supported System Actions
Action	Function
open_app	Launch an application
close_app	Close an application
web_search	Perform Google search
open_url	Open website
screenshot	Capture screen
volume_up/down/mute	Control volume
get_system_info	CPU RAM Disk info
get_time	Current system time
get_battery	Battery status
copy_to_clipboard	Copy text
get_clipboard	Retrieve clipboard
create_file	Create file
read_file	Read file
run_command	Run shell command
lock_screen	Lock Windows
shutdown	Shutdown system
restart	Restart system
Contributing

Contributions are welcome.

Steps:

Fork the repository

Create a new branch

git checkout -b feature-name

Commit changes

git commit -m "Add feature"

Push to branch

git push origin feature-name

Open a Pull Request

License

This project is licensed under the MIT License.

See the LICENSE file for details.

Credits

Technologies used:

Google Gemini

Vosk Speech Recognition

pyttsx3

SpeechRecognition

Inspired by the concept of JARVIS.

Built by Anand Raj Tripathi
