<<<<<<< HEAD
<![CDATA[<div align="center">

```
  ██████╗ ███████╗██╗   ██╗████████╗ █████╗ 
  ██╔══██╗██╔════╝██║   ██║╚══██╔══╝██╔══██╗
  ██║  ██║█████╗  ██║   ██║   ██║   ███████║
  ██║  ██║██╔══╝  ╚██╗ ██╔╝   ██║   ██╔══██║
  ██████╔╝███████╗ ╚████╔╝    ██║   ██║  ██║
  ╚═════╝ ╚══════╝  ╚═══╝     ╚═╝   ╚═╝  ╚═╝
```

**Your personal AI assistant — like Jarvis, but with an Indian soul.**

[![Python](https://img.shields.io/badge/Python-3.10%2B-blue?logo=python)](https://python.org)
[![Gemini](https://img.shields.io/badge/Powered%20by-Google%20Gemini-orange?logo=google)](https://aistudio.google.com)
[![Platform](https://img.shields.io/badge/Platform-Windows-blue?logo=windows)](https://www.microsoft.com/windows)
[![License](https://img.shields.io/badge/License-MIT-green)](LICENSE)
=======
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
>>>>>>> 768fd87ff8ad6a354d60ed22e1d2ebf622e29f68

</div>

---

<<<<<<< HEAD
## ✨ What is Devta?

**Devta** is an always-on, voice-first AI assistant that runs entirely on your Windows laptop. It listens for your wake word, responds intelligently using Google's Gemini AI, and can actually *do things* on your computer — open apps, take screenshots, search the web, manage files, and more. It also proactively monitors your browser activity and sends you helpful suggestions as toast notifications.

> **Say "Hello Devta" or "Bhai Devta" to wake it up. Say "Devta stop" to go silent.**

---

## 🚀 Features

| Feature | Details |
|---|---|
| 🎙️ **Always-on Wake Word** | Offline detection using [Vosk](https://alphacephei.com/vosk/) — `Hello Devta`, `Bhai Devta`, `Hey Devta` |
| 🧠 **Dual AI Brain** | Gemini 2.0 Flash Lite for fast replies; auto-escalates to Gemini 2.5 Flash for complex tasks |
| 🗣️ **Voice + Text** | Full STT (SpeechRecognition/Vosk) + TTS (pyttsx3) with a dark-themed Tkinter chat UI |
| 🖥️ **System Control** | Open/close apps, volume control, screenshots, clipboard ops, file read/write, shell commands, shutdown/restart |
| 🌐 **Web Integration** | Google Search, open URLs, browser context monitoring |
| 💡 **Proactive Suggestions** | Browser monitor sends smart AI-generated tips as Windows toast notifications |
| 🔇 **Silent Mode** | Say `Devta stop` to pause all suggestions; `Devta resume` to bring them back |
| 🔐 **Private & Local** | Runs on your machine; only Gemini API calls touch the internet |

---

## 🗂️ Project Structure

```
devta-ai/
├── main.py              # 🎯 Entry point & orchestrator
├── brain.py             # 🧠 Gemini AI interface (Flash + Pro hybrid)
├── speech.py            # 🗣️  STT (Vosk/SpeechRecognition) + TTS (pyttsx3)
├── wake_word.py         # 👂 Offline wake-word listener (Vosk)
├── system_control.py    # 🖥️  Windows system actions executor
├── browser_monitor.py   # 🌐 Active browser tab monitor
├── notifier.py          # 🔔 Windows toast notification sender
├── ui.py                # 💻 Tkinter dark-theme chat interface
├── config.py            # ⚙️  All configuration & prompts
├── setup.bat            # 📦 One-click setup script
├── start_devta.bat      # ▶️  Launch shortcut
├── requirements.txt     # 📋 Python dependencies
├── .env.example         # 🔑 API key template
└── vosk_model/          # 🔊 Offline speech recognition model
=======
# Devta AI

**Devta** is a voice-first AI assistant for Windows that runs locally on your laptop.
It listens for a wake word, understands voice commands, and performs real actions on your computer such as opening applications, searching the web, taking screenshots, and managing files.

The assistant uses **Google Gemini** for intelligent responses while keeping most processing local.

Wake words:

```
Hello Devta
Bhai Devta
Hey Devta
```

Stop phrase:

```
Devta stop
```

---

# Features

### Voice Interaction

* Wake word detection using **Vosk (offline)**
* Speech-to-text via **SpeechRecognition / Vosk**
* Text-to-speech using **pyttsx3**

### AI Intelligence

* Uses **Gemini 2.0 Flash Lite** for fast responses
* Automatically escalates to **Gemini 2.5 Flash** for complex queries
* Maintains conversation context

### System Control

Devta can directly control your system:

* Open or close applications
* Take screenshots
* Check battery status
* Control volume
* Run shell commands
* Manage clipboard
* Create and read files
* Lock, shutdown, or restart the system

### Web Integration

* Open URLs
* Perform Google searches
* Monitor active browser tabs
* Generate helpful suggestions

### Desktop Interface

* Dark themed **Tkinter chat UI**
* Voice and text interaction supported

### Notifications

* Windows toast notifications for suggestions
* Smart tips based on browser activity

---

# Project Structure

```
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
>>>>>>> 768fd87ff8ad6a354d60ed22e1d2ebf622e29f68
```

---

<<<<<<< HEAD
## 🛠️ Quick Start

### Prerequisites
- **Windows 10/11**
- **Python 3.10+** — [Download here](https://python.org/downloads)
- **A free Gemini API key** — [Get one in 30 seconds](https://aistudio.google.com/) (no credit card needed)
- A working **microphone**

### 1. Clone the repository
```bash
=======
# Requirements

* Windows 10 or Windows 11
* Python 3.10 or higher
* Microphone
* Gemini API Key

Get a Gemini API key from
https://aistudio.google.com/

---

# Installation

### 1 Clone the repository

```
>>>>>>> 768fd87ff8ad6a354d60ed22e1d2ebf622e29f68
git clone https://github.com/yourusername/devta-ai.git
cd devta-ai
```

<<<<<<< HEAD
### 2. Run the one-click setup
```batch
setup.bat
```
This will:
- ✅ Check your Python version
- ✅ Create a virtual environment
- ✅ Install all dependencies
- ✅ Prompt you to paste your Gemini API key
- ✅ Generate the `start_devta.bat` launch shortcut

### 3. Download the Vosk model
Download [vosk-model-small-en-us-0.15](https://alphacephei.com/vosk/models) and place its contents inside the `vosk_model/` folder.

### 4. Start Devta
```batch
start_devta.bat
```
Or directly:
```bash
=======
### 2 Run setup

```
setup.bat
```

The setup script will:

* create a virtual environment
* install dependencies
* request your Gemini API key
* prepare the start script

### 3 Download Vosk model

Download:

```
vosk-model-small-en-us-0.15
```

From:
https://alphacephei.com/vosk/models

Extract it inside:

```
vosk_model/
```

---

# Running Devta

You can start the assistant using:

```
start_devta.bat
```

or

```
>>>>>>> 768fd87ff8ad6a354d60ed22e1d2ebf622e29f68
python main.py
```

---

<<<<<<< HEAD
## ⚙️ Configuration

All settings are in [`config.py`](config.py). Key options:

| Setting | Default | Description |
|---|---|---|
| `WAKE_WORDS` | `hello devta`, `bhai devta`, ... | Phrases that activate Devta |
| `STOP_PHRASE` | `devta stop` | Silences proactive suggestions |
| `GEMINI_FLASH_MODEL` | `gemini-2.0-flash-lite` | Primary model (fast, high quota) |
| `GEMINI_PRO_MODEL` | `gemini-2.5-flash` | Escalation model for complex queries |
| `TTS_RATE` | `175` | Text-to-speech speed (words/min) |
| `NOTIFICATION_INTERVAL_SECONDS` | `30` | How often browser is checked |
| `MAX_CONVERSATION_HISTORY` | `20` | Conversation turns kept in memory |

### Environment Variables (`.env`)
```env
GEMINI_API_KEY=your_gemini_api_key_here
=======
# Configuration

Configuration settings are located in:

```
config.py
```

Important parameters:

| Setting                       | Description                      |
| ----------------------------- | -------------------------------- |
| WAKE_WORDS                    | Phrases that activate Devta      |
| STOP_PHRASE                   | Phrase that disables suggestions |
| GEMINI_FLASH_MODEL            | Default AI model                 |
| GEMINI_PRO_MODEL              | Model used for complex tasks     |
| TTS_RATE                      | Speech speed                     |
| NOTIFICATION_INTERVAL_SECONDS | Browser monitoring interval      |
| MAX_CONVERSATION_HISTORY      | Number of stored messages        |

Environment variables are defined in:

```
.env
```

Example:

```
GEMINI_API_KEY=your_api_key_here
>>>>>>> 768fd87ff8ad6a354d60ed22e1d2ebf622e29f68
```

---

<<<<<<< HEAD
## 🎙️ Voice Commands

| Say... | What happens |
|---|---|
| `Hello Devta` / `Bhai Devta` | Devta wakes up and listens for your command |
| `Open Chrome` | Opens Google Chrome |
| `Take a screenshot` | Saves a screenshot to your Desktop |
| `What's my battery?` | Reports battery level and charging status |
| `Search for Python tutorials` | Opens Google Search in your browser |
| `Devta stop` | Pauses proactive suggestions (Silent Mode) |
| `Devta resume` | Resumes proactive suggestions |

### Auto Model Escalation
Queries containing keywords like `write code`, `debug`, `analyze`, `research`, `explain in detail`, `essay`, or `calculate` automatically use the more powerful **Gemini 2.5 Flash** model.

---

## 🧩 System Actions Supported

Devta's AI can trigger these actions on your PC via special JSON blocks in its responses:

| Action | Description |
|---|---|
| `open_app` / `close_app` | Launch or kill any application |
| `web_search` / `open_url` | Open browser searches or URLs |
| `screenshot` | Capture and save screen |
| `volume_up/down/mute` | Control system volume |
| `get_system_info` | CPU, RAM, Disk usage |
| `get_time` / `get_battery` | Time and battery status |
| `copy_to_clipboard` / `get_clipboard` | Clipboard operations |
| `create_file` / `read_file` | File I/O |
| `run_command` | Execute shell commands |
| `lock_screen` / `shutdown` / `restart` | Power management |

---

## 🤝 Contributing

Pull requests are welcome! For major changes, please open an issue first to discuss what you'd like to change.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
=======
# Example Voice Commands

Open Chrome

```
Hello Devta
Open Chrome
```

Take a screenshot

```
Hello Devta
Take a screenshot
```

Search the web

```
Hello Devta
Search for Python tutorials
```

Check battery

```
Hello Devta
What's my battery status
```

Stop notifications

```
Devta stop
```

Resume notifications

```
Devta resume
```

---

# Supported System Actions

| Action              | Function              |
| ------------------- | --------------------- |
| open_app            | Launch an application |
| close_app           | Close an application  |
| web_search          | Perform Google search |
| open_url            | Open website          |
| screenshot          | Capture screen        |
| volume_up/down/mute | Control volume        |
| get_system_info     | CPU RAM Disk info     |
| get_time            | Current system time   |
| get_battery         | Battery status        |
| copy_to_clipboard   | Copy text             |
| get_clipboard       | Retrieve clipboard    |
| create_file         | Create file           |
| read_file           | Read file             |
| run_command         | Run shell command     |
| lock_screen         | Lock Windows          |
| shutdown            | Shutdown system       |
| restart             | Restart system        |

---

# Contributing

Contributions are welcome.

Steps:

1. Fork the repository
2. Create a new branch

```
git checkout -b feature-name
```

3. Commit changes

```
git commit -m "Add feature"
```

4. Push to branch

```
git push origin feature-name
```

>>>>>>> 768fd87ff8ad6a354d60ed22e1d2ebf622e29f68
5. Open a Pull Request

---

<<<<<<< HEAD
## 📄 License

This project is licensed under the MIT License — see the [LICENSE](LICENSE) file for details.

---

## 🙏 Acknowledgements

- [Google Gemini](https://deepmind.google/technologies/gemini/) — AI brain
- [Vosk](https://alphacephei.com/vosk/) — Offline speech recognition
- [pyttsx3](https://pyttsx3.readthedocs.io/) — Offline text-to-speech
- [SpeechRecognition](https://pypi.org/project/SpeechRecognition/) — Audio capture
- Inspired by J.A.R.V.I.S from the Marvel universe 🦾

---

<div align="center">
  <sub>Built with ❤️ and a lot of "Haan bolo, main sun raha hoon!"</sub>
</div>
]]>
=======
# License

This project is licensed under the MIT License.

See the LICENSE file for details.

---

# Credits

Technologies used:

* Google Gemini
* Vosk Speech Recognition
* pyttsx3
* SpeechRecognition

Inspired by the concept of JARVIS.

---

Built by Anand Raj Tripathi
>>>>>>> 768fd87ff8ad6a354d60ed22e1d2ebf622e29f68
