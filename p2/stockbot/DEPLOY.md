# Stock Signal Bot — Deployment Guide

## ☁️ Deploy to Streamlit Cloud (Free)

This is the recommended way to make your app accessible from anywhere, including installing it as a PWA on your phone.

### Prerequisites

- A GitHub account
- This project **already pushed** to your GitHub repo:
  ```
  https://github.com/emmkay080888-gitty/stockbot1503.git
  ```

### Step 1: Push latest changes to GitHub

```bash
git add p2/stockbot/
git commit -m "Prepare for Streamlit Cloud deployment"
git push origin main
```

### Step 2: Deploy on Streamlit Community Cloud

1. Go to **https://share.streamlit.io**
2. Click **"Sign in with GitHub"** and authorize
3. Click **"New app"**
4. Select your repo: `emmkay080888-gitty/stockbot1503`
5. **Branch:** `main`
6. **Main file path:** `p2/stockbot/app.py`
7. Click **"Deploy"**
8. Wait ~2-3 minutes for the build
9. Your app will be at: `https://stockbot1503.streamlit.app`

### Step 3: Configure Secrets (Optional)

If you want GitHub OAuth login, add secrets in the Streamlit Cloud dashboard:

1. Go to **https://share.streamlit.io**
2. Click on your app → **"⚙️ Settings"** → **"Secrets"**
3. Add the following:

```toml
[github_oauth]
client_id = "your_github_client_id"
client_secret = "your_github_client_secret"
redirect_uri = "https://stockbot1503.streamlit.app"
```

4. To get a GitHub OAuth app client ID:
   - Go to **https://github.com/settings/developers** → **"New OAuth App"**
   - **Homepage URL:** `https://stockbot1503.streamlit.app`
   - **Authorization callback URL:** `https://stockbot1503.streamlit.app`
   - Copy the **Client ID** and generate a **Client Secret**

### Step 4: Set App Settings

In the Streamlit Cloud dashboard, under **"⚙️ Settings"**:

| Setting | Value |
|---|---|
| **Python version** | 3.12 (or latest available) |
| **App file** | `p2/stockbot/app.py` |
| **Auto-restart** | On (deploys new pushes automatically) |

### Important Notes

- **Auth persistence:** User accounts and remember-me tokens are saved to `users.json` on the **ephemeral filesystem**. New registrations will be lost when Streamlit Cloud restarts the app (typically every few hours on the free tier). The pre-seeded `admin` account will persist because it's committed to git.
- **PWA manifest 404:** On Streamlit Cloud, the PWA manifest (`/manifest.json`) and icons are not served from the app URL — you'll see 404s in the browser console. This is cosmetic and doesn't affect functionality. To get full PWA support, use the separate PWA wrapper (Option 2 in the PWA section below).
- **Reports directory:** Report files are written to `/tmp/stockbot_reports/` on Streamlit Cloud and will be lost on restart.
- **Memory limit:** Streamlit Cloud free tier has 1 GB RAM — the stock scanner handles this fine.
- **App sleeps:** After ~3 days of inactivity, the app goes to sleep. Visiting the URL wakes it up (~15 seconds).

---

## 📱 Install as PWA on Android

Once deployed, you can install the app as a native-feeling app on your phone.

### Option 1: Direct (No wrapper)

1. Open `https://stockbot1503.streamlit.app` in **Chrome** on your phone
2. Tap the menu (⋮) → **"Add to Home Screen"**
3. Name it "StockBot" → tap **"Install"**
4. It will now appear as a standalone app with its own icon

### Option 2: With PWA Splash Screen (Recommended)

The `pwa/` folder contains a wrapper page with a splash screen and offline fallback.

1. Deploy `p2/stockbot/pwa/` to **GitHub Pages** or **Vercel** (free)
2. Update `pwa/index.html` → change `STREAMLIT_URL` to your app URL
3. Visit the wrapper URL → **"Add to Home Screen"**
4. The wrapper shows a splash screen while loading and supports offline fallback

**Deploy to Vercel (easiest):**

```bash
cd p2/stockbot/pwa
# Deploy the pwa/ folder with Vercel CLI or drag-and-drop to vercel.com
# Set FRAMEWORK_PRESET = "Static" (no framework)
```

---

## 🐳 Deploy with Docker (Self-Hosted)

```bash
cd p2
docker build -t stockbot -f Dockerfile .
docker run -p 8501:8501 stockbot
```

Or with docker-compose:

```bash
cd p2
docker compose up -d
```

---

## 🪟 Windows Installer

Build a standalone `.exe`:

```bash
cd stockbot
pip install pyinstaller
python setup/build_windows.py
```

---

## 📋 Requirements

| Platform | Requirements |
|---|---|
| **Streamlit Cloud** | GitHub account, Chrome browser |
| **Android (PWA)** | Chrome browser, internet |
| **Docker** | Docker Engine 20+ |
| **Local dev** | Python 3.10+ |

## 🎯 Quick Start (Local)

```bash
cd p2/stockbot
python -m venv venv
source venv/bin/activate   # Linux/Mac
pip install -r requirements.txt
streamlit run app.py
```
