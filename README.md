# 🎬 Subtitle Translator

Beautiful desktop application for translating Japanese drama subtitles into multiple languages with AI-powered natural language processing.

<div align="center">

![Status](https://img.shields.io/badge/status-production%20ready-success)
![Platform](https://img.shields.io/badge/platform-Windows%20%7C%20macOS%20%7C%20Linux-blue)
![License](https://img.shields.io/badge/license-MIT-green)

</div>

---

## ✨ Features

### 🎨 Beautiful UI

- **Modern Apple-inspired design** with glass morphism effects
- **Real-time progress tracking** with detailed status updates
- **Intuitive interface** - no technical knowledge required

### 🌍 Multi-Language Support

Translate to **7 languages** optimized for Asian audiences:

- 🇮🇳 **Hinglish** (Hindi + English)
- 🇵🇭 **Taglish** (Tagalog + English)
- 🇻🇳 **Vietnamese** (Tiếng Việt)
- 🇹🇭 **Thai** (ภาษาไทย)
- 🇲🇾 **Malay** (Bahasa Melayu)
- 🇪🇸 **Spanish** (Español)
- 🇮🇩 **Indonesian** (Bahasa Indonesia)

### 🤖 AI Models

Choose from **4 OpenAI models** based on your needs:

- **GPT-4o Mini** - Fast & cost-effective
- **GPT-5 Mini** - Balanced quality
- **GPT-4o** - High quality
- **GPT-5** - Premium quality

### ⚡ Performance

- **Parallel processing** for multiple files and languages
- **Smart batching** for optimal API usage
- **Progress tracking** for long-running translations

### 🛡️ Production-Grade Reliability

- ✅ **Automatic retry** with exponential backoff
- ✅ **Error recovery** for rate limits, timeouts, and network issues
- ✅ **Post-translation validation** with detailed reports
- ✅ **Batch retranslation** for failed files
- ✅ **Comprehensive error logging**
- ✅ **7/7 tests passing**

---

## 🚀 Quick Start

### Prerequisites

Before you begin, ensure you have:

| Requirement        | Version | Download                                                    |
| ------------------ | ------- | ----------------------------------------------------------- |
| **Node.js**        | v16+    | [nodejs.org](https://nodejs.org)                            |
| **Python**         | 3.8+    | [python.org](https://www.python.org)                        |
| **OpenAI API Key** | -       | [platform.openai.com](https://platform.openai.com/api-keys) |

### Installation

1. **Clone or download** this repository

2. **Install Node dependencies:**

   ```bash
   npm install
   ```

3. **Install Python dependencies:**

   ```bash
   pip install -r requirements.txt
   ```

4. **Start the application:**
   ```bash
   npm start
   ```

That's it! The app will open and you're ready to translate.

> 💡 **First time?** Check out [QUICKSTART.md](electron/docs/QUICKSTART.md) for a detailed walkthrough.

---

## 📖 Usage Guide

### Step 1: Configure API Key

1. Open the app
2. Enter your OpenAI API key in the "API Configuration" section
3. Toggle the eye icon to show/hide your key
4. The key is auto-saved securely for future use

### Step 2: Select AI Model

Choose based on your needs:

- **GPT-4o Mini** → Best for quick, cost-effective translations
- **GPT-5 Mini** → Balanced quality and speed
- **GPT-4o** → High-quality translations
- **GPT-5** → Premium quality (highest cost)

### Step 3: Choose Translation Mode

- **Parallel Languages** → Translate all languages per file simultaneously (faster)
- **Parallel Files** → Process multiple SRT files at once (faster)
- **Both enabled** → Maximum speed (recommended for large batches)

### Step 4: Select Folders

- **Source Folder** → Folder containing your `.srt` files
- **Output Folder** → Where translated files will be saved

> ⚠️ Source and output folders must be different

### Step 5: Pick Target Languages

- Click language cards to select/deselect
- Use "Select All" or "Clear" buttons for bulk selection
- Select as many languages as you need

### Step 6: Start Translation

1. Click **"Start Translation"**
2. Monitor real-time progress
3. View status updates and error messages
4. Wait for automatic validation to complete

### Step 7: Review Results

- Translated files are organized in language-specific subfolders
- Check validation results for any issues
- Use **"Retranslate Failed Files"** button if needed

---

## 📂 Output Structure

```
output-folder/
├── HINGLISH/
│   ├── episode_01_HINGLISH.srt
│   └── episode_02_HINGLISH.srt
├── VIETNAMESE/
│   ├── episode_01_VIETNAMESE.srt
│   └── episode_02_VIETNAMESE.srt
└── THAI/
    ├── episode_01_THAI.srt
    └── episode_02_THAI.srt
```

---

## 🔧 Advanced Features

### Error Handling & Recovery

The app includes production-grade error handling:

#### Automatic Retry Logic

- **Rate Limits (429)** → Auto-retry with exponential backoff (1s, 2s, 4s, 8s)
- **Timeouts** → Automatic retry up to 3 times
- **Connection Errors** → Smart reconnection attempts
- **API Errors** → Detailed error categorization and reporting

#### Error Tracking

- Real-time error display in the UI
- Failed file list with language-specific details
- Comprehensive JSON error logs in `python/logs/`
- One-click batch retranslation

### Validation System

After each translation:

1. ✅ **Automatic validation** runs
2. 📊 **Results displayed** per language
3. ⚠️ **Failed files identified**
4. 🔄 **Batch retranslation** available

### Translation Quality

Optimized for **Japanese drama subtitles**:

- Preserves honorifics (San, Kun, Sama, Chan, etc.)
- Matches emotional tone and context
- Natural, conversational language
- Cultural nuance preservation

---

## 📦 Building Executables

Create standalone installers for distribution:

### Windows

```bash
npm run build:win
```

Output: `dist/Subtitle-Translator-Setup.exe`

### macOS

```bash
npm run build:mac
```

Output: `dist/Subtitle-Translator.dmg`

### Linux

```bash
npm run build:linux
```

Output: `dist/Subtitle-Translator.AppImage`

### All Platforms

```bash
npm run build
```

---

## 🧪 Testing

Run the comprehensive test suite:

```bash
python python/test_suite.py
```

**Test Coverage:**

- ✅ Error handler functionality
- ✅ Error logging with file tracking
- ✅ Recovery strategies
- ✅ SRT parsing with edge cases
- ✅ File operations
- ✅ Validation logic
- ✅ JSON serialization

**Current Status:** 7/7 tests passing ✅

---

## 🛠️ Troubleshooting

### Common Issues

<details>
<summary><b>❌ "Python not found" Error</b></summary>

**Solution:** Verify Python installation and PATH configuration

```bash
python --version
# or
python3 --version
```

If not found, download and install from [python.org](https://www.python.org/downloads/) and ensure "Add to PATH" is checked during installation.

</details>

<details>
<summary><b>❌ "Module not found" Error</b></summary>

**Solution:** Install Python dependencies

```bash
pip install -r requirements.txt
# or if pip is not found
python -m pip install -r requirements.txt
```

</details>

<details>
<summary><b>❌ API Key Not Working</b></summary>

**Check the following:**

- ✅ Key is valid at [OpenAI Platform](https://platform.openai.com/api-keys)
- ✅ Account has available credits
- ✅ Key starts with `sk-`
- ✅ No extra spaces before/after the key
- ✅ Internet connection is stable

</details>

<details>
<summary><b>❌ App Won't Start</b></summary>

**Try these steps:**

1. **Clear and reinstall dependencies:**

   ```bash
   rm -rf node_modules
   npm install
   ```

2. **Clear Electron cache:**

   ```bash
   # Windows
   rmdir /s %APPDATA%\subtitle-translator

   # macOS/Linux
   rm -rf ~/Library/Application\ Support/subtitle-translator
   ```

3. **Check Node.js version:**
   ```bash
   node --version  # Should be v16+
   ```

</details>

<details>
<summary><b>❌ Translation Fails</b></summary>

**Verify:**

- ✅ Source folder contains `.srt` files
- ✅ API key is correctly entered
- ✅ Internet connection is active
- ✅ OpenAI API status (check [status.openai.com](https://status.openai.com))
- ✅ Check error logs in `python/logs/translation_errors.log`

</details>

<details>
<summary><b>⚠️ Some Files Failed Validation</b></summary>

**Solution:**

1. Check validation results to see which files failed
2. Click **"Retranslate Failed Files"** button
3. App will automatically retry with error recovery
4. Validation runs again after retranslation

</details>

---

## 📚 Documentation

### User Guides

- 📘 [Quickstart Guide](electron/docs/QUICKSTART.md) - Detailed 10-minute setup
- 📗 [Production README](electron/docs/PRODUCTION_README.md) - Complete user manual
- 📕 [Error Reference](electron/docs/ERROR_REFERENCE.md) - Error codes and solutions
- ✅ [Production Checklist](PRODUCTION_CHECKLIST.md) - Pre-deployment checklist

### Developer Guides

- 🔧 [Deployment Guide](electron/docs/DEPLOYMENT_GUIDE.md) - Build and distribute
- 📝 [Implementation Summary](electron/docs/IMPLEMENTATION_SUMMARY.md) - Technical overview

### Code Documentation

- **Error Handling:** [python/error_handler.py](python/error_handler.py)
- **Translation Logic:** [python/translator.py](python/translator.py)
- **SRT Parsing:** [python/srt_utils.py](python/srt_utils.py)
- **Validation:** [python/validation_utils.py](python/validation_utils.py)

---

## 📁 Project Structure

```
subtitle-translator/
├── electron/
│   ├── main.js              # Electron main process
│   ├── preload.js           # Secure IPC bridge
│   └── docs/                # Documentation
├── src/
│   ├── index.html           # App HTML
│   └── app.js               # React UI
├── python/
│   ├── translator.py        # Core translation logic
│   ├── translator_bridge.py # Electron-Python bridge
│   ├── error_handler.py     # Error management
│   ├── srt_utils.py         # SRT parsing
│   ├── validation_utils.py  # Validation logic
│   └── logs/                # Error logs
├── package.json             # Node dependencies
├── requirements.txt         # Python dependencies
└── README.md                # This file
```

---

## 🎨 Customization

### Adding New Languages

1. **Edit** [python/translator.py](python/translator.py):

   ```python
   LANG_STYLE_PRESETS = {
       "your_language": {
           "name": "Your Language",
           "description": "Natural conversational Your Language",
           # ... style settings
       }
   }
   ```

2. **Edit** [src/app.js](src/app.js):

   ```javascript
   const languages = [
     {
       code: "your_language",
       name: "Your Language",
       flag: "🇫🇷",
       desc: "Description",
     },
     // ... other languages
   ];
   ```

3. **Restart** the application

### Changing UI Theme

Edit [src/app.js](src/app.js) Tailwind classes:

```javascript
// Purple theme (current)
className: "bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900";

// Blue theme
className: "bg-gradient-to-br from-slate-900 via-blue-900 to-slate-900";

// Green theme
className: "bg-gradient-to-br from-slate-900 via-emerald-900 to-slate-900";
```

### Updating Model Prices

Edit [python/translator.py](python/translator.py):

```python
MODEL_PRICES = {
    "gpt-4o-mini": {
        "input": 0.00000015,  # per token
        "output": 0.00000060, # per token
    },
    # ... update other models
}
```

---

## 💡 Tips & Best Practices

### 🎯 Translation Quality

- Use **GPT-4o** or **GPT-5** for best results with Japanese dramas
- Test with 1-2 files before batch processing
- Review validation results after translation

### 💰 Cost Optimization

- Start with **GPT-4o Mini** to estimate quality
- Use parallel processing for faster completion
- Process similar content in batches

### 🗂️ File Management

- Keep source files organized in one folder
- Use descriptive file names
- Backup original files before processing

### ⚡ Performance

- Enable both parallel options for maximum speed
- Close unnecessary applications during large batch processing
- Ensure stable internet connection

---

## 🤝 Contributing

Contributions are welcome! Here's how:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

---

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

---

## 🙏 Acknowledgments

- **OpenAI** for GPT models
- **Electron** for cross-platform desktop framework
- **React** for UI framework
- **TailwindCSS** for beautiful styling

---

## 👨‍💻 Author

**Robinson Minj**

Created with ❤️ for Japanese drama fans worldwide

---

## 📞 Support

Having issues? Need help?

1. Check the [Troubleshooting](#-troubleshooting) section
2. Review [Error Reference](electron/docs/ERROR_REFERENCE.md)
3. Check error logs in `python/logs/`
4. Open the dev console (Ctrl+Shift+I / Cmd+Option+I) for detailed errors

---

<div align="center">

**🎉 Happy Translating! 🎬✨**

Made for translating Japanese dramas with love and precision

[⭐ Star this repo](../../) | [🐛 Report Bug](../../issues) | [💡 Request Feature](../../issues)

</div>
