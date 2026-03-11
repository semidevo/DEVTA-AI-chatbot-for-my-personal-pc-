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

</div>

---

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
```

---

## 🛠️ Quick Start

### Prerequisites
- **Windows 10/11**
- **Python 3.10+** — [Download here](https://python.org/downloads)
- **A free Gemini API key** — [Get one in 30 seconds](https://aistudio.google.com/) (no credit card needed)
- A working **microphone**

### 1. Clone the repository
```bash
git clone https://github.com/yourusername/devta-ai.git
cd devta-ai
```

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
python main.py
```

---

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
```

---

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
5. Open a Pull Request

---

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
