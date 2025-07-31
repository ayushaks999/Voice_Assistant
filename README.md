# 🗣️ Voice Assistant Project

### 🚀 Overview
This project is a **Voice Assistant** that performs a variety of tasks, including:
- Answering general questions
- Playing music directly from YouTube
- Fetching live weather updates for any location
- Setting reminders with notifications
- Real-time voice-based interaction

It uses **Flask** for the backend and a dynamic **chat-based UI** for seamless interaction.

---

### ✨ Features
- **Voice Input and Output**: Listens and responds with synthesized speech.
- **Music Playback**: Plays YouTube music via `yt-dlp` and `VLC`.
- **Weather Updates**: Fetches live weather using Open-Meteo API.
- **Reminder System**: Notifies users at preset times.
- **Interactive Chat UI**: Displays user-assistant conversations.

---

### 📸 Screenshot

![Voice Assistant UI](images/screenshot.png)
> Add your screenshot image to the `images/` folder.

---

---

### ⚙️ Installation

#### 🧱 Prerequisites
- Python 3.8 or higher
- Packages listed in `requirements.txt`

#### 📦 Setup Instructions

1. Create and activate a virtual environment:
   ```bash
   conda create -p ./env python==3.11 -y
   conda activate ./env  # On Windows: .\env\Scripts\activate
