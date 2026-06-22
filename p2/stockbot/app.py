#!/usr/bin/env python3
"""Stock Signal Bot - Streamlit GUI

Run with: streamlit run app.py
"""

import streamlit as st
import sys
import os
from pathlib import Path

ROOT = Path(__file__).parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

st.set_page_config(
    page_title="Stock Signal Bot",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="collapsed",
)

from config import STRATEGY_WEIGHTS, SCREENING, TA_PARAMS
from utils.auth import is_logged_in, get_current_user, verify_remember_token, apply_preferences, _load_users, is_admin
from utils.markets import get_market_list, get_current_market_key, set_market, get_market_config


# ─── Auto-Login from Remember Me (query params from localStorage) ───
params = st.query_params
if "auto_user" in params and "auto_token" in params:
    auto_user = params["auto_user"]
    auto_token = params["auto_token"]
    if auto_user and auto_token and verify_remember_token(auto_user, auto_token):
        if not is_logged_in():
            users = _load_users()
            if auto_user in users:
                u = users[auto_user]
                st.session_state["user"] = {
                    "username": auto_user,
                    "name": u.get("name", auto_user),
                    "email": u.get("email", ""),
                }
                apply_preferences(auto_user)
    # Clear any stale logged_out flag so JS can save the new session
    if "logged_out" in st.query_params:
        del st.query_params["logged_out"]
    # Note: auto_user/auto_token params intentionally left in URL so
    # browser JS can save them to localStorage.


# ─── GitHub OAuth Callback ────────────────────────────────────────────
# When GitHub redirects back with ?code=xxx&state=yyy, exchange the code
# for a token, fetch the user profile, and log them in.
if "code" in st.query_params and "state" in st.query_params \
   and not st.session_state.get("github_oauth_done"):
    from utils.oauth_github import handle_callback
    handle_callback()


# ─── Custom Sound Files (base64 embedded) ──────────────────────────
import base64

SOUNDS_DIR = ROOT / "sounds"

def _load_sound(filename: str) -> str | None:
    """Load a sound file and return as base64 data URI, or None if not found."""
    try:
        for ext in [".mp3", ".wav", ".ogg"]:
            path = SOUNDS_DIR / (filename + ext)
            if path.exists():
                mime = {".mp3": "audio/mpeg", ".wav": "audio/wav", ".ogg": "audio/ogg"}[ext]
                data = path.read_bytes()
                b64 = base64.b64encode(data).decode()
                return f"data:{mime};base64,{b64}"
    except Exception:
        pass  # Fall back to generated sounds if file read fails
    return None

# Encode sound files as data URIs for the browser
CHIME_DATA = _load_sound("chime") or ""
CLICK_DATA = _load_sound("click") or ""

# Build the Sound + Remember Me JS script with data URIs injected
_SOUND_SCRIPT = """<script>
(function(){
// ── Custom sound data (injected as base64) ─────────────────────
var CHIME_URL = '$CHIME$';
var CLICK_URL = '$CLICK$';
var hasCustomChime = CHIME_URL.length > 0;
var hasCustomClick = CLICK_URL.length > 0;

// ── Sound Effects (HTML5 Audio + Web Audio API fallback) ──────
var audioCtx = null;
function initAudio(){
    if(!audioCtx) {
        audioCtx = new (window.AudioContext||window.webkitAudioContext)();
    }
    if(audioCtx.state==='suspended') audioCtx.resume();
}

function playChime(){
    try {
        if(hasCustomChime){
            var a = new Audio(CHIME_URL);
            a.volume = 0.6;
            a.play().catch(function(){});
            return;
        }
        // Fallback: Web Audio API generated chime
        initAudio();
        var now = audioCtx.currentTime;
        [523.25, 659.25, 783.99, 1046.5].forEach(function(f, i){
            var o = audioCtx.createOscillator();
            var g = audioCtx.createGain();
            o.type = 'sine';
            o.frequency.value = f;
            g.gain.setValueAtTime(0.15 - i*0.02, now + i*0.1);
            g.gain.exponentialRampToValueAtTime(0.001, now + i*0.1 + 0.8);
            o.connect(g); g.connect(audioCtx.destination);
            o.start(now + i*0.1); o.stop(now + i*0.1 + 0.8);
        });
    } catch(e){}
}

function playClick(){
    try {
        if(hasCustomClick){
            var a = new Audio(CLICK_URL);
            a.volume = 0.5;
            a.play().catch(function(){});
            return;
        }
        // Fallback: Web Audio API generated click
        initAudio();
        var o = audioCtx.createOscillator();
        var g = audioCtx.createGain();
        o.type = 'sine';
        o.frequency.value = 600 + Math.random()*300;
        g.gain.setValueAtTime(0.06, audioCtx.currentTime);
        g.gain.exponentialRampToValueAtTime(0.001, audioCtx.currentTime + 0.08);
        o.connect(g); g.connect(audioCtx.destination);
        o.start(); o.stop(audioCtx.currentTime + 0.08);
        var o2 = audioCtx.createOscillator();
        var g2 = audioCtx.createGain();
        o2.type = 'triangle';
        o2.frequency.value = 400 + Math.random()*200;
        g2.gain.setValueAtTime(0.03, audioCtx.currentTime);
        g2.gain.exponentialRampToValueAtTime(0.001, audioCtx.currentTime + 0.05);
        o2.connect(g2); g2.connect(audioCtx.destination);
        o2.start(); o2.stop(audioCtx.currentTime + 0.05);
    } catch(e){}
}

// Play chime on first user interaction
var firstInteraction = true;
document.addEventListener('pointerdown', function(){
    if(firstInteraction){
        firstInteraction = false;
        setTimeout(playChime, 100);
    }
}, {once: true});

// Click sounds
document.addEventListener('click',function(e){
    if(e.target.closest('button')||e.target.closest('a')||
       e.target.closest('[role="button"]')||e.target.closest('label')){
        playClick();
    }
});

// ── Remember Me: save, restore & cleanup ─────────────────────
(function(){
    var p = new URLSearchParams(window.location.search);
    // Clear localStorage on explicit logout
    if(p.get('logged_out')==='1'){
        localStorage.removeItem('stockbot_remember');
    }
    // Save query params to localStorage (only on non-logout pages)
    var u = p.get('auto_user');
    var t = p.get('auto_token');
    if(u && t && p.get('logged_out')!=='1'){
        localStorage.setItem('stockbot_remember', JSON.stringify({user:u, token:t}));
    }
    // Restore: redirect with saved params if not already have them
    var saved = localStorage.getItem('stockbot_remember');
    if(saved && !u && !t && p.get('logged_out')!=='1'){
        try {
            var data = JSON.parse(saved);
            if(data && data.user && data.token){
                window.location.href = window.location.pathname +
                    '?auto_user=' + encodeURIComponent(data.user) +
                    '&auto_token=' + encodeURIComponent(data.token);
            }
        } catch(e){}
    }
})();
})();
</script>

<!-- PWA Meta Tags -->
<meta name="description" content="Multi-strategy stock market signal consolidation bot">
<meta name="theme-color" content="#7c4dff">
<meta name="apple-mobile-web-app-capable" content="yes">
<meta name="apple-mobile-web-app-status-bar-style" content="black-translucent">
<meta name="apple-mobile-web-app-title" content="StockBot">
<link rel="manifest" href="/manifest.json">
<link rel="apple-touch-icon" href="/icons/icon-192.png">
<meta name="mobile-web-app-capable" content="yes">
""".replace("$CHIME$", CHIME_DATA).replace("$CLICK$", CLICK_DATA)
st.markdown(_SOUND_SCRIPT, unsafe_allow_html=True)


# ─── Custom CSS ─────────────────────────────────────────────────────
st.markdown("""<style>
    .stApp { background: linear-gradient(135deg, #1a0a2e 0%, #16213e 30%, #0f3460 60%, #1a1a2e 100%); }
    section[data-testid="stSidebar"] {
        background: linear-gradient(180deg, #1a0a2e 0%, #16213e 100%);
        border-right: 1px solid rgba(124, 77, 255, 0.2);
    }
    section[data-testid="stSidebar"] .stButton button {
        background: linear-gradient(135deg, rgba(124,77,255,0.15) 0%, rgba(0,200,83,0.1) 100%);
        border: 1px solid rgba(124,77,255,0.3);
        border-radius: 12px;
        color: #e0e0e0 !important;
        transition: all 0.3s ease;
        padding: 10px 16px;
        margin: 2px 0;
    }
    section[data-testid="stSidebar"] .stButton button:hover {
        background: linear-gradient(135deg, rgba(124,77,255,0.3) 0%, rgba(0,200,83,0.2) 100%);
        border-color: #7c4dff;
        transform: translateX(4px);
        box-shadow: 0 4px 15px rgba(124,77,255,0.3);
    }
    section[data-testid="stSidebar"] .stButton button[kind="primary"] {
        background: linear-gradient(135deg, #7c4dff 0%, #00c853 100%) !important;
        color: white !important;
        border: none !important;
        box-shadow: 0 4px 15px rgba(124,77,255,0.4);
    }
    .main-header {
        background: linear-gradient(135deg, #7c4dff, #00c853, #ff9100);
        -webkit-background-clip: text; -webkit-text-fill-color: transparent;
        font-size: 2.5rem; font-weight: 700; margin-bottom: 0;
    }
    .sub-header { color: #b0bec5; font-size: 1rem; margin-top: 0; }
    .signal-buy { color: #00c853; font-weight: bold; }
    .signal-sell { color: #ff1744; font-weight: bold; }
    .score-high { color: #00c853; font-weight: bold; }
    .score-mid { color: #ffd700; font-weight: bold; }
    .score-low { color: #ff9100; font-weight: bold; }
    div[data-testid="stMetricValue"] { font-size: 1.8rem; color: #7c4dff !important; }
    .st-eb { border-color: rgba(124, 77, 255, 0.2); }
    h1, h2, h3 {
        background: linear-gradient(135deg, #7c4dff, #00c853) !important;
        -webkit-background-clip: text !important; -webkit-text-fill-color: transparent !important;
    }
    .stAlert { border-radius: 12px; border-left: 4px solid #7c4dff; }
    .stDataFrame { border-radius: 12px; overflow: hidden; }

    /* Landing */
    .landing-hero {
        background: linear-gradient(135deg, #1a0a2e 0%, #16213e 50%, #0f3460 100%);
        border: 1px solid rgba(124,77,255,0.3); border-radius: 20px;
        padding: 40px 30px; margin: 10px 0 30px 0; text-align: center;
        position: relative; overflow: hidden;
    }
    .hero-glow {
        position: absolute; top: -50%; left: -50%; width: 200%; height: 200%;
        background: radial-gradient(circle at center, rgba(124,77,255,0.15) 0%, transparent 60%);
        animation: heroGlow 4s ease-in-out infinite;
    }
    @keyframes heroGlow {
        0%, 100% { transform: translate(0, 0); }
        50% { transform: translate(30px, 30px); }
    }
    .hero-badge-live {
        display: inline-block;
        background: linear-gradient(135deg, rgba(0,200,83,0.2), rgba(0,200,83,0.1));
        border: 1px solid rgba(0,200,83,0.4); border-radius: 20px;
        padding: 4px 16px; font-size: 0.7rem; color: #00c853;
        letter-spacing: 2px; margin-bottom: 12px;
        animation: pulseLive 2s ease-in-out infinite;
    }
    @keyframes pulseLive { 0%,100%{opacity:1} 50%{opacity:0.6} }
    .hero-content { position: relative; z-index: 1; }
    .hero-title {
        font-size: 3rem !important; font-weight: 800 !important; margin-bottom: 10px !important;
        background: linear-gradient(135deg, #7c4dff, #00c853, #ff9100) !important;
        -webkit-background-clip: text !important; -webkit-text-fill-color: transparent !important;
    }
    .hero-subtitle { color: #b0bec5; font-size: 1.1rem; margin-bottom: 24px; max-width: 600px; margin: 0 auto 24px; }
    .hero-stats { display: flex; justify-content: center; gap: 16px; margin-bottom: 20px; flex-wrap: wrap; }
    .hero-stat {
        background: linear-gradient(135deg, rgba(124,77,255,0.15), rgba(124,77,255,0.05));
        border: 1px solid rgba(124,77,255,0.3); border-radius: 12px;
        padding: 10px 20px; min-width: 100px; text-align: center;
    }
    .hero-stat-value { display: block; font-size: 1.4rem; font-weight: 700; color: #e0e0e0; }
    .hero-stat-label { display: block; font-size: 0.7rem; color: #78909c; text-transform: uppercase; letter-spacing: 1px; margin-top: 2px; }
    .hero-badges { display: flex; gap: 10px; justify-content: center; flex-wrap: wrap; }
    .badge {
        background: linear-gradient(135deg, rgba(124,77,255,0.2), rgba(0,200,83,0.2));
        border: 1px solid rgba(124,77,255,0.3); border-radius: 20px;
        padding: 6px 16px; font-size: 0.85rem; color: #e0e0e0;
    }
    /* Auth buttons in top-right */
    .auth-bar {
        position: absolute; top: 16px; right: 20px; z-index: 10;
        display: flex; gap: 8px;
    }
    .auth-btn {
        padding: 6px 18px; border-radius: 20px; font-size: 0.8rem;
        font-weight: 600; cursor: pointer; border: none;
        transition: all 0.3s ease; text-decoration: none;
    }
    .auth-btn-login {
        background: transparent;
        border: 1px solid rgba(124,77,255,0.5);
        color: #b0bec5;
    }
    .auth-btn-login:hover { border-color: #7c4dff; color: #e0e0e0; }
    .auth-btn-signup {
        background: linear-gradient(135deg, #7c4dff, #00c853);
        color: white;
    }
    .auth-btn-signup:hover { box-shadow: 0 4px 15px rgba(124,77,255,0.4); transform: translateY(-1px); }
    .auth-btn-user {
        background: linear-gradient(135deg, rgba(124,77,255,0.2), rgba(0,200,83,0.1));
        border: 1px solid rgba(124,77,255,0.3); border-radius: 20px;
        padding: 6px 18px; font-size: 0.8rem; color: #e0e0e0; cursor: pointer;
    }

    /* Ticker */
    .ticker-wrap {
        background: linear-gradient(90deg, rgba(124,77,255,0.1), rgba(0,200,83,0.1));
        border: 1px solid rgba(124,77,255,0.2); border-radius: 12px;
        overflow: hidden; padding: 12px 0; margin: 10px 0 20px 0;
    }
    .ticker { display: flex; animation: scroll 25s linear infinite; white-space: nowrap; }
    @keyframes scroll { 0% { transform: translateX(100%); } 100% { transform: translateX(-100%); } }
    .ticker-item { display: inline-block; padding: 0 24px; font-size: 0.95rem; border-right: 1px solid rgba(124,77,255,0.2); }
    .ticker-price { color: #e0e0e0; margin: 0 4px; }
    .section-title { font-size: 1.6rem !important; font-weight: 700 !important; margin: 30px 0 15px 0 !important; text-align: center; }

    /* Testimonials */
    .testimonial-card {
        background: linear-gradient(135deg, rgba(124,77,255,0.1), rgba(0,200,83,0.05));
        border: 1px solid rgba(124,77,255,0.2); border-radius: 16px;
        padding: 20px; height: 100%; transition: all 0.3s ease;
    }
    .testimonial-card:hover {
        transform: translateY(-4px); box-shadow: 0 8px 25px rgba(124,77,255,0.2); border-color: #7c4dff;
    }
    .testimonial-stars { font-size: 1.1rem; margin-bottom: 8px; }
    .testimonial-text { color: #b0bec5; font-size: 0.9rem; font-style: italic; line-height: 1.5; margin-bottom: 12px; }
    .testimonial-author strong { color: #e0e0e0; display: block; font-size: 0.95rem; }
    .testimonial-author span { color: #78909c; font-size: 0.8rem; }

    /* About */
    .about-card {
        background: linear-gradient(135deg, rgba(124,77,255,0.08), rgba(0,200,83,0.05));
        border: 1px solid rgba(124,77,255,0.2); border-radius: 16px;
        padding: 24px; line-height: 1.8; color: #b0bec5;
    }
    .about-card strong { color: #e0e0e0; }
    .about-card ul { margin: 12px 0; padding-left: 20px; }
    .about-card li { margin: 6px 0; }

    /* Disclaimer */
    .disclaimer {
        background: linear-gradient(135deg, rgba(255,152,0,0.08), rgba(255,23,68,0.05));
        border: 1px solid rgba(255,152,0,0.2); border-radius: 16px;
        padding: 24px; font-size: 0.85rem; line-height: 1.6; color: #90a4ae;
    }
    .disclaimer strong { color: #ff9100; }

    @media (max-width: 768px) {
        .main-header { font-size: 1.6rem; }
        .hero-title { font-size: 2rem !important; }
        .hero-stat { min-width: 80px; padding: 8px 14px; }
        .hero-stat-value { font-size: 1.1rem; }
    }
</style>""", unsafe_allow_html=True)


# ─── Initialize session state ──────────────────────────────────────
if "current_page" not in st.session_state:
    st.session_state.current_page = "landing"


# ─── Sidebar ────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("<h1 style='color: #00ff88;'>📈 Stock Signal Bot</h1>", unsafe_allow_html=True)
    st.markdown("<p style='color: #8892b0; font-size: 0.85rem;'>Multi-strategy signal consolidation</p>", unsafe_allow_html=True)
    st.divider()

    # User section
    if is_logged_in():
        user = get_current_user()
        role_badge = "🛡️" if is_admin() else "👤"
        st.markdown(
            f"<p style='color: {'#ffd700' if is_admin() else '#00c853'}; font-size: 0.85rem;'>"
            f"{role_badge} Logged in as <strong>{user.get('name', 'User')}</strong>"
            f"{' 🛡️ <span style="color:#ffd700;font-size:0.7rem;">ADMIN</span>' if is_admin() else ''}</p>",
            unsafe_allow_html=True,
        )
        if st.button("👤 My Profile", use_container_width=True,
                     type="secondary" if st.session_state.current_page != "profile" else "primary"):
            st.session_state.current_page = "profile"
            st.rerun()
        if is_admin():
            if st.button("🛡️ Admin Dashboard", use_container_width=True,
                         type="secondary" if st.session_state.current_page != "admin" else "primary"):
                st.session_state.current_page = "admin"
                st.rerun()
    else:
        if st.button("🔐 Login", use_container_width=True,
                     type="secondary" if st.session_state.current_page != "login" else "primary"):
            st.session_state.current_page = "login"
            st.rerun()
        if st.button("📝 Sign Up", use_container_width=True,
                     type="secondary" if st.session_state.current_page != "signup" else "primary"):
            st.session_state.current_page = "signup"
            st.rerun()

    st.divider()

    # Navigation
    st.markdown("### Navigation")
    pages = {
        "🏠 Home": "landing",
        "🔮 Magic Call": "magic_call",
        "🔍 Market Scan": "market_scan",
        "📊 Stock Analysis": "stock_analysis",
        "📈 LiveChart": "live_chart",
        "🔄 Backtest": "backtest",
        "⚙️ Settings": "settings",
    }

    for label, page_id in pages.items():
        if st.button(label, use_container_width=True,
                     type="secondary" if st.session_state.current_page != page_id else "primary"):
            st.session_state.current_page = page_id
            st.rerun()

    st.divider()

    # Market exchange selector (global)
    st.markdown("### 🌍 Market")
    market_options = get_market_list()
    current_market = get_current_market_key()
    selected_market = st.selectbox(
        "Select Exchange",
        options=[m["key"] for m in market_options],
        format_func=lambda k: next((m["label"] for m in market_options if m["key"] == k), k),
        index=next((i for i, m in enumerate(market_options) if m["key"] == current_market), 0),
        key="market_selector",
        label_visibility="collapsed",
    )
    if selected_market != current_market:
        set_market(selected_market)
        st.rerun()

    # Show active market context (timezone + currency) — visible on all pages
    mkt_cfg = get_market_config()
    st.markdown(
        f"<div style='background: rgba(124,77,255,0.08); border: 1px solid rgba(124,77,255,0.15); "
        f"border-radius: 8px; padding: 8px 12px; margin: 4px 0;'>"
        f"<div style='color: #78909c; font-size: 0.65rem; text-transform: uppercase; letter-spacing: 1px;'>Active Market</div>"
        f"<div style='color: #e0e0e0; font-size: 0.85rem; font-weight: 600;'>"
        f"{mkt_cfg['emoji']} {mkt_cfg['name']}</div>"
        f"<div style='color: #8892b0; font-size: 0.75rem; display: flex; gap: 12px; margin-top: 2px;'>"
        f"<span>🪙 {mkt_cfg['currency']}</span>"
        f"<span>🕐 {mkt_cfg['timezone']}</span>"
        f"</div></div>",
        unsafe_allow_html=True,
    )

    st.divider()
    st.markdown("<p style='color: #555; font-size: 0.75rem;'>Data: Yahoo Finance<br>Strategies: 7<br>Powered by StockBot</p>", unsafe_allow_html=True)


# ─── Page Router with Auth Gate ─────────────────────────────────────
# Public pages — accessible without login
PUBLIC_PAGES = {"landing", "login", "signup", "forgot_password"}
# Protected pages — require authentication
PROTECTED_PAGES = {"magic_call", "market_scan", "stock_analysis", "live_chart", "backtest", "settings", "profile", "admin"}

page = st.session_state.current_page

# Auth gate: redirect to login if trying to access a protected page without auth
if page in PROTECTED_PAGES and not is_logged_in():
    st.session_state["login_redirect"] = page
    st.session_state.current_page = "login"
    page = "login"
    st.warning("🔒 Please sign in or create an account to access this feature.")

if page == "landing":
    from pages.Landing import show
    show()
elif page == "magic_call":
    from pages.Magic_Call import show
    show()
elif page == "market_scan":
    from pages.Market_Scan import show
    show()
elif page == "stock_analysis":
    from pages.Stock_Analysis import show
    show()
elif page == "live_chart":
    from pages.LiveChart import show
    show()
elif page == "backtest":
    from pages.Backtest import show
    show()
elif page == "settings":
    from pages.Settings import show
    show()
elif page == "login":
    from pages.Login import show
    show()
elif page == "signup":
    from pages.Signup import show
    show()
elif page == "profile":
    from pages.Profile import show
    show()
elif page == "forgot_password":
    from pages.ForgotPassword import show
    show()
elif page == "admin":
    from pages.Admin import show
    show()
