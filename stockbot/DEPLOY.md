# Stock Signal Bot — Deployment & Install Guide

## 📱 Android — Install as a PWA (Add to Home Screen)

The app already has PWA (Progressive Web App) support. To install it on your Android phone:

### Option 1: Deploy to Streamlit Cloud (Free)

1. **Push to GitHub:**
   ```bash
   git add .
   git commit -m "Initial commit"
   git remote add origin https://github.com/YOUR_USER/stock-signal-bot.git
   git push -u origin main
   ```

2. **Deploy on Streamlit Community Cloud:**
   - Go to https://share.streamlit.io
   - Sign in with GitHub
   - Click "New app" → select your repo → branch: `main` → file: `app.py`
   - Click "Deploy"
   - Wait ~2 minutes for the build
   - Your app will be at: `https://YOUR_USER-stock-signal-bot.streamlit.app`

3. **Install on Android:**
   - Open the URL in Chrome on your phone
   - Tap the menu (⋮) → "Add to Home Screen" → "Install"
   - It will now appear as a standalone app with its own icon

4. **To use the PWA wrapper (optional):**
   - Deploy the `pwa/` folder to GitHub Pages or Vercel
   - Update `pwa/index.html` → change `STREAMLIT_URL` to your Streamlit Cloud URL
   - Visit the wrapper URL → "Add to Home Screen"
   - The wrapper shows a splash screen while loading and supports offline fallback

### Option 2: Run Locally + Share on Network

```bash
# Start the app on all network interfaces
cd stockbot && source venv/bin/activate
streamlit run app.py --server.port 8501 --server.address 0.0.0.0
```

- Find your computer's IP (e.g., 192.168.1.100)
- On your phone, open: `http://192.168.1.100:8501`
- Tap Chrome menu → "Add to Home Screen" to install

---

## 🪟 Windows — Installer

### Option 1: Standalone Executable (No Python needed)

Build a portable `.exe` that runs on any Windows machine:

```bash
# On Windows with Python installed:
cd stockbot
pip install pyinstaller
python setup/build_windows.py          # Builds StockBot.exe
python setup/build_windows.py --installer  # Builds + NSIS installer
```

**Output files:**
- `dist/StockBot.exe` — Portable executable (~100-150 MB)
- `dist/StockBot_Setup.exe` — Windows installer (if NSIS is installed)

**Running the EXE:**
- Double-click `StockBot.exe`
- The app opens in your default browser at `http://localhost:8501`
- Close the terminal window to stop the app

### Option 2: NSIS Installer (Professional)

1. Download NSIS: https://nsis.sourceforge.io/Download
2. Install NSIS (default location: `C:/Program Files/NSIS/`)
3. Run: `python setup/build_windows.py --installer`
4. The installer will be at `dist/StockBot_Setup.exe`

The installer creates:
- Start Menu shortcut
- Desktop shortcut
- Add/Remove Programs entry
- All dependencies bundled

### Option 3: Quick Launch (Python required)

```powershell
# From the stockbot directory:
python -m venv venv
.\venv\Scripts\activate
pip install -r requirements.txt
streamlit run app.py
```

Or double-click `run_app.bat` (create this file):

```batch
@echo off
cd /d "%~dp0"
call venv\Scripts\activate.bat
streamlit run app.py --server.port 8501
pause
```

---

## 🔧 Requirements

| Platform | Requirements |
|---|---|
| **Android (PWA)** | Chrome browser, internet connection |
| **Windows (EXE)** | Windows 10+, ~200MB disk space |
| **Windows (dev)** | Python 3.10+, 8GB RAM recommended |

## 📁 Project Structure

```
stockbot/
├── app.py                 # Launch with: streamlit run app.py
├── config.py              # Strategy weights, screening params
├── pages/                 # Streamlit UI pages
├── analysis/              # Technical analysis + strategies
├── data/                  # Data fetching (yfinance + fallback)
├── signals/               # Signal generation + consolidation
├── output/                # CLI reporting
├── utils/                 # Config helpers
├── pwa/                   # PWA files (Android install)
│   ├── index.html         # PWA wrapper page
│   ├── manifest.json      # PWA manifest
│   └── sw.js              # Service worker
└── setup/                 # Build tools
    ├── build_windows.py   # PyInstaller build script
    └── installer.nsi       # NSIS installer script
```

## 🎯 Quick Start

```bash
# 1. Clone or download the project
# 2. Install dependencies
cd stockbot
python -m venv venv
source venv/bin/activate  # Linux/Mac
# .\venv\Scripts\activate  # Windows

pip install -r requirements.txt

# 3. Run the app
streamlit run app.py
```
