# Norwegian Dictionary Lookup

A lightweight Windows utility that provides instant Norwegian ↔ English translations with a simple hotkey. Perfect for language learners reading Norwegian text!

![Version](https://img.shields.io/badge/version-1.0.0-blue.svg)
![Platform](https://img.shields.io/badge/platform-Windows-lightgrey.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)

## ✨ Features

- **Instant Translations**: Select any word and press `Alt+P+N` ("på norsk") to see translations
- **Bidirectional**: Works for both Norwegian → English and English → Norwegian
- **Non-Intrusive**: Runs silently in the background, no window clutter
- **Smart Popups**: Translation appears near your cursor, automatically positioned on the correct monitor
- **Lexin Dictionary**: Uses the authoritative Norwegian Lexin Bokmål-English dictionary
- **Auto-Updates**: Automatically checks for new versions once per day
- **Lightweight**: Minimal resource usage, starts with Windows

## 🚀 Quick Start

### Installation

1. Download the latest `NorwegianDictionary_Setup.exe` from [Releases](https://github.com/oslo-c/norsk_lookup/releases)
2. Run the installer
3. Choose whether to start automatically with Windows (recommended)
4. The app starts immediately - you're ready to go!

### Usage

1. **Select a word** - Highlight any Norwegian or English word in any application
2. **Press `Alt+P+N`** - The hotkey for "på norsk"
3. **See translation** - A popup appears showing the translation and part of speech
4. **Click anywhere** to dismiss the popup

That's it!

## 📖 Examples

**Norwegian → English:**
```
Select: "hund"
Press: Alt+P+N
Result: hund (noun) → dog
```

**English → Norwegian:**
```
Select: "house"
Press: Alt+P+N
Result: hus (noun) → house
```

**Multiple meanings:**
```
Select: "bank"
Press: Alt+P+N
Result: 
bank (noun) → bank
bank (noun) → bench
```

## 💡 Tips

- Works in **any application**: browsers, Word, PDFs, text editors, etc.
- **Multi-monitor support**: Popup stays on the screen where your cursor is
- **Click anywhere outside** the popup to close it
- **Click on the popup itself** to close it immediately
- If no translation is found, the popup will tell you

## 🔧 How It Works

The app uses:
- **UI Automation API** to capture selected text (no clipboard interference!)
- **Lexin Dictionary API** from Oslo Metropolitan University
- **Windows hotkeys** for global keyboard monitoring
- **Tkinter popups** for clean, styled display windows

## 🛠️ Building from Source

### Prerequisites

- Python 3.8+
- Windows 10/11
- [Inno Setup 6](https://jrsoftware.org/isdl.php) (for creating installer)

### Setup

```bash
# Clone the repository
git clone https://github.com/oslo-c/norsk_lookup.git
cd norsk_lookup

# Create virtual environment
python -m venv .venv
.venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### Development

Run directly with Python:
```bash
cd src
python main.py
```

### Building

Build the executable:
```bash
build_scripts\build_installer.bat
```

Or for a debug build with console output:
```bash
build_scripts\build_debug.bat
```

The installer will be created in `Output\NorwegianDictionary_Setup.exe`

### Clean Build

To remove all build artifacts:
```bash
build_scripts\cleanbuild.bat
```

## 🐛 Troubleshooting

### Hotkey not working?
- Make sure the app is running (check Task Manager for `NorwegianDictionary.exe`)
- Try restarting the application
- Another app might be using the same hotkey combination

### No translation popup appears?
- Ensure you've **highlighted** the text before pressing the hotkey
- Try selecting just a single word
- Check that you have an internet connection (required for dictionary lookups)

### Popup appears on wrong monitor?
- This should be automatic - if it's not working, please report a bug!

### App not starting with Windows?
- Open Task Manager → Startup tab
- Enable "Norwegian Dictionary Lookup"
- Or reinstall and check the startup option

## 🤝 Contributing

Contributions welcome! Feel free to:
- Report bugs
- Suggest features
- Submit pull requests

## 📜 License

MIT License - feel free to use and modify!

## 🙏 Credits

- Dictionary data from [Lexin](https://lexin.oslomet.no/) by Oslo Metropolitan University
- Built with Python, PyInstaller, and Inno Setup
- Inspired by the need for quick translations while reading Norwegian text

## 📞 Support

Having issues? Check the [Issues](https://github.com/YOUR_USERNAME/YOUR_REPO_NAME/issues) page or create a new issue.

---

**Made with ❤️ for Norwegian language learners**

*Lykke til med norsk!* (Good luck with Norwegian!)