# 🚀 MacroPad Configurator using Arduino Pro Micro

A customizable **MacroPad System** built using an **Arduino Pro Micro** with dual-mode operation:

* 🐍 **Python Running** → Open software/folders directly from button press
* 🔌 **Python Closed** → Arduino works independently as a HID Macro Keyboard

This project was developed for **Microprocessor, Microcontroller and Embedded System** coursework.

---

# 📸 Features

- ✅ 4 Programmable Macro Buttons
- ✅ GUI Configurator using Python Tkinter
- ✅ Custom Key Combination Support
- ✅ Open Software & Folders
- ✅ EEPROM Storage
- ✅ Serial Communication with Arduino
- ✅ Heartbeat Detection between Python ↔ Arduino
- ✅ Standalone Arduino Operation
- ✅ Media Control Keys
- ✅ Copy/Paste Shortcuts
- ✅ Custom Hotkeys
- ✅ Auto Configuration Save

---

# 🛠 Hardware Used

| Component       | Description                |
| --------------- | -------------------------- |
| Microcontroller | Arduino Pro Micro          |
| Push Buttons    | 4                          |
| LEDs            | 2                          |
| USB Cable       | Micro USB                  |
| Resistors       | Optional Pull-up/Pull-down |

---

# 💻 Software Used

| Software            | Purpose                    |
| ------------------- | -------------------------- |
| Python 3            | GUI & Serial Communication |
| Arduino IDE         | Upload Firmware            |
| PySerial            | Serial Communication       |
| Tkinter             | GUI                        |
| HID-Project Library | Keyboard & Media Control   |

---

# 📂 Project Structure

```bash
Project/
│
├── macro.py                     # Main GUI Application
├── sof.py                       # Software/Folder Launcher Module
├── com_find.py                  # COM Port Scanner
├── config.json                  # Button Configuration
├── software_folder_config.json  # Software/Folder Paths
│
└── Arduino_Code.ino             # Arduino Pro Micro Firmware
```

---

# ⚡ How It Works

## 🐍 Mode 1: Python Running

When `macro.py` is running:

* Button press is detected by Arduino
* Arduino sends serial command:

```cpp
PRESS:B1
```

* Python receives the command
* Python opens configured software/folder

Example:

| Button | Action                |
| ------ | --------------------- |
| B1     | Open Chrome           |
| B2     | Open VS Code          |
| B3     | Open Documents Folder |
| B4     | Open Spotify          |

---

## 🔌 Mode 2: Python Closed

When Python application is NOT running:

* Arduino works independently
* Buttons send HID keyboard/media commands

Example:

| Button | Action      |
| ------ | ----------- |
| B1     | Volume Up   |
| B2     | Volume Down |
| B3     | Mute        |
| B4     | Play/Pause  |

---

# 🔄 Heartbeat System

A heartbeat system is implemented between Python and Arduino.

### 💓 Python Sends:

```text
HEARTBEAT
```

### 📥 Arduino Responds:

```text
HEARTBEAT:ACK
```

If heartbeat stops for 2 seconds:

✅ Arduino detects Python disconnected
✅ Heartbeat LED turns OFF
✅ Arduino switches to standalone mode

---

# 🧠 EEPROM Support

Button configurations are stored permanently inside EEPROM.

Even after power loss:

✅ Macro settings remain saved
✅ Arduino works without PC software

---

# 🎮 Supported Actions

## 🎵 Media Controls

* Volume Up
* Volume Down
* Mute
* Play/Pause

---

## ⌨️ Keyboard Shortcuts

Examples:

```text
CTRL + C
CTRL + V
CTRL + SHIFT + ESC
ALT + TAB
WIN + R
```

---

## 🧩 Function Keys

Supported:

```text
F1 → F12
HOME
END
TAB
DELETE
INSERT
ESC
PAGEUP
PAGEDOWN
ENTER
BACKSPACE
PRTSC
```

---

# 🖥 GUI Features

The Python GUI includes:

✅ Button Configuration
✅ Custom Key Setup
✅ Software/Folder Selection
✅ Debug Console
✅ Serial Monitor
✅ Save/Load Configurations
✅ Upload to Arduino

---

# 🔌 COM Port Detection

If Arduino IDE is not installed or COM port is unknown:

Run:

```bash
python com_find.py
```

Example Output:

```text
Scanning for available ports...

Port: COM8
Description: Arduino Pro Micro
✓ This is likely your Arduino on COM8
```

---

# 📦 Required Python Libraries

Install dependencies:

```bash
pip install pyserial
```

Tkinter usually comes preinstalled with Python.

---

# 📚 Required Arduino Libraries

Install from Arduino IDE Library Manager:

## 📌 HID-Project

By NicoHood

Required for:

* Keyboard Emulation
* Media Controls

---

# 🚀 How To Run

## 1️⃣ Upload Arduino Code

* Open Arduino IDE
* Select:

```text
Board: Arduino Leonardo / Pro Micro
```

* Select correct COM port
* Upload firmware

---

## 2️⃣ Find COM Port

Run:

```bash
python com_find.py
```

Update this line in `macro.py`:

```python
PORT = 'COM8'
```

---

## 3️⃣ Run Python GUI

```bash
python macro.py
```

---

# 🔘 Button Pin Connections

| Button | Pin |
| ------ | --- |
| B1     | 9   |
| B2     | 8   |
| B3     | 7   |
| B4     | 6   |

---

# 💡 LED Connections

| LED           | Pin |
| ------------- | --- |
| Status LED    | 13  |
| Heartbeat LED | 2   |

---

# 🧪 Example Use Cases

✅ Open VS Code instantly
✅ Launch Browser
✅ Open Music Folder
✅ Media Controller
✅ Gaming Hotkeys
✅ OBS Stream Controls
✅ Productivity Shortcuts
✅ Coding Macros

---

# 🐛 Troubleshooting

## ❌ Arduino Not Detected

* Check USB cable
* Verify COM port
* Run `com_find.py`

---

## ❌ Python Cannot Connect

Check:

```python
PORT = 'COM8'
```

Use correct COM port.

---

## ❌ Software Not Opening

* Verify file path exists
* Check Debug Console
* Test using "Test B1"

---

## ❌ Buttons Not Working

Check:

* Wiring
* Pull-up configuration
* Baud Rate = 9600

---

# 🔧 Future Improvements

* RGB Lighting
* OLED Display
* Rotary Encoder
* Profile Switching
* Wireless Support
* Web Dashboard
* Dynamic Macros
* Macro Recording

---

# 📖 Technologies Used

* Python
* Arduino C++
* Tkinter
* PySerial
* HID-Project
* EEPROM
* Serial Communication

---

# 👨‍💻 Author

Developed by **Md. Zarif Noor**

Project for:

> Microprocessor, Microcontroller and Embedded System

---

# ⭐ If You Like This Project

Give this repository a ⭐ on GitHub!
