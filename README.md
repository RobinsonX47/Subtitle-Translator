# 🎬 Subtitle Translator Desktop App

Beautiful desktop application for translating Japanese drama subtitles into multiple languages with AI-powered translation.

## ✨ Features

- 🎨 **Modern Apple-inspired UI** with glass morphism effects
- 🌍 **7 Languages**: Hinglish, Taglish, Vietnamese, Thai, Malay, Spanish, Indonesian
- 🤖 **Multiple AI Models**: GPT-4o Mini, GPT-5 Mini, GPT-4o, GPT-5
- 💰 **Cost Estimation** before translation
- 📊 **Real-time Progress** tracking
- 🔐 **Secure API Key** storage
- 📁 **Easy Folder Selection** with native dialogs
- 💾 **Auto-save Settings**

---

## 📋 Prerequisites

- **Node.js** (v16 or higher) - [Download here](https://nodejs.org/)
- **Python 3.8+** - [Download here](https://www.python.org/downloads/)
- **OpenAI API Key** - [Get one here](https://platform.openai.com/api-keys)

---

## 🚀 Installation

### Step 1: Clone or Download the Project

```bash
# If you have git
git clone <your-repo-url>
cd subtitle-translator

# Or just extract the ZIP file
```

### Step 2: Install Node.js Dependencies

```bash
npm install
```

### Step 3: Install Python Dependencies

```bash
pip install -r requirements.txt
```

Or if you're using Python 3:

```bash
pip3 install -r requirements.txt
```

### Step 4: Project Structure

Make sure your project has this structure:

```
subtitle-translator/
├── electron/
│   ├── main.js          ← Electron main process
│   └── preload.js       ← Preload script
├── src/
│   ├── index.html       ← App HTML
│   └── app.js           ← App JavaScript (React)
├── python/
│   ├── translator_bridge.py  ← Python bridge script
│   ├── translator.py         ← Translation logic (your enhanced version)
│   ├── srt_utils.py          ← SRT parsing utilities
│   ├── archive_utils.py      ← Archive extraction (optional)
│   └── .env                  ← Environment variables (optional)
├── package.json
├── requirements.txt
└── README.md
```

---

## 🎮 Running the App

### Development Mode

```bash
npm start
```

Or with dev tools:

```bash
npm run dev
```

---

## 📦 Building the App

### Build for Windows

```bash
npm run build:win
```

The installer will be in `dist/` folder.

### Build for macOS

```bash
npm run build:mac
```

Creates a `.dmg` file in `dist/` folder.

### Build for Linux

```bash
npm run build:linux
```

Creates an AppImage in `dist/` folder.

### Build for All Platforms

```bash
npm run build
```

---

## 📖 How to Use

### 1. **Enter API Key**
   - Get your OpenAI API key from [OpenAI Platform](https://platform.openai.com/api-keys)
   - Paste it in the "OpenAI API Key" field
   - It will be saved securely and auto-filled next time

### 2. **Select Model**
   - Choose from 4 available models
   - **GPT-4o Mini**: Fastest and cheapest
   - **GPT-5 Mini**: Balanced quality and cost
   - **GPT-4o**: High quality
   - **GPT-5**: Premium quality (most expensive)

### 3. **Select Folders**
   - **Source Folder**: Click "Browse" and select the folder containing your `.srt` files
   - **Output Folder**: Click "Browse" and select where translated files should be saved

### 4. **Choose Languages**
   - Click on language cards to select/deselect
   - Or use "Select All" / "Clear" buttons
   - You can select multiple languages at once

### 5. **Calculate Cost**
   - Click "Calculate Cost" to see:
     - Number of files to process
     - Total tokens needed
     - Estimated cost in USD and INR
   - This helps you know the cost before starting

### 6. **Start Translation**
   - Click "Start Translation"
   - Watch the progress bar and status updates
   - You can cancel anytime by clicking "Cancel"

### 7. **Find Your Translations**
   - Go to your Output Folder
   - Each language will have its own subfolder
   - Files will be named with language suffix (e.g., `episode_01_HINGLISH.srt`)

---

## 🎯 Tips for Best Results

### For Japanese Dramas:
- The app is optimized for Japanese drama translation
- Honorifics (San, Kun, Sama, etc.) are preserved
- Emotional tone is matched to the scene
- Natural, conversational language

### Cost Optimization:
- Use **GPT-4o Mini** for faster, cheaper translations
- Use **GPT-5 Mini** for balanced quality
- Use **GPT-4o** or **GPT-5** for highest quality

### File Organization:
- Keep all your SRT files in one folder
- Make sure files are named clearly
- The app processes all `.srt` files it finds

---

## 🛠️ Troubleshooting

### "Python not found" Error

**Solution**: Make sure Python is installed and in your PATH:

```bash
python --version
# or
python3 --version
```

If not installed, download from [python.org](https://www.python.org/downloads/)

### "Module not found" Error

**Solution**: Install Python dependencies:

```bash
pip install -r requirements.txt
```

### API Key Not Working

**Solutions**:
- Check if the key is valid at [OpenAI Platform](https://platform.openai.com/api-keys)
- Make sure you have credits in your OpenAI account
- Check if the key has the correct permissions

### App Won't Start

**Solutions**:
1. Delete `node_modules` and reinstall:
   ```bash
   rm -rf node_modules
   npm install
   ```

2. Clear Electron cache:
   ```bash
   # Windows
   rmdir /s %APPDATA%\subtitle-translator
   
   # Mac/Linux
   rm -rf ~/Library/Application\ Support/subtitle-translator
   ```

### Translation Fails

**Check**:
- Source folder contains `.srt` files
- API key is correct
- You have internet connection
- OpenAI API is not rate-limited

---

## 🔧 Advanced Configuration

### Changing Model Prices

Edit `python/translator.py` and update the `MODEL_PRICES` dictionary:

```python
MODEL_PRICES = {
    "gpt-4o-mini": {
        "input": 0.0000007,
        "output": 0.0000007,
    },
    # ... other models
}
```

### Adding New Languages

1. Add language to `python/translator.py` in `LANG_STYLE_PRESETS`
2. Add language to `src/app.js` in the `languages` array
3. Restart the app

---

## 📝 Project Files

### Core Files You Can Modify:

- **`python/translator.py`** - Translation logic and language styles
- **`python/translator_bridge.py`** - Bridge between Electron and Python
- **`src/app.js`** - UI logic and state management
- **`electron/main.js`** - Electron window and IPC handlers

### Files to Keep As-Is:

- **`electron/preload.js`** - Security bridge
- **`src/index.html`** - HTML structure
- **`package.json`** - Dependencies

---

## 🎨 Customization

### Change App Colors

Edit `src/app.js` and modify the Tailwind classes:

```javascript
// Current gradient
className="bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900"

// Change to blue theme
className="bg-gradient-to-br from-slate-900 via-blue-900 to-slate-900"
```

### Change App Icon

1. Create icons:
   - `assets/icon.ico` (Windows)
   - `assets/icon.icns` (macOS)
   - `assets/icon.png` (Linux)

2. Update `package.json` build section

---

## 📄 License

MIT License - feel free to use and modify!

---

## 🤝 Support

If you encounter issues:

1. Check the troubleshooting section above
2. Make sure all dependencies are installed
3. Check the console for error messages (open with Ctrl+Shift+I or Cmd+Option+I)

---

## 🎉 Enjoy Your App!

You now have a professional subtitle translation app! Perfect for translating Japanese dramas into multiple languages with beautiful, natural results.

**Happy Translating! 🎬✨**