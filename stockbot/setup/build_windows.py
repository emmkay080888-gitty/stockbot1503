#!/usr/bin/env python3
"""Windows build script - packages the Stock Signal Bot as a standalone executable.

Usage:
    python setup/build_windows.py          # Build the exe
    python setup/build_windows.py --installer  # Build + NSIS installer

Requires:
    pip install pyinstaller
    (optional) NSIS installed at C:/Program Files/NSIS/
"""

import os
import sys
import shutil
import subprocess
from pathlib import Path

ROOT = Path(__file__).parent.parent
DIST_DIR = ROOT / "dist"
BUILD_DIR = ROOT / "build"


def clean():
    """Clean previous builds."""
    for d in [DIST_DIR, BUILD_DIR]:
        if d.exists():
            shutil.rmtree(d)
    print("✓ Cleaned previous builds")


def build_exe():
    """Build standalone executable using PyInstaller."""
    print("Building Stock Signal Bot executable...")

    # Create launcher script that starts Streamlit
    launcher = ROOT / "run_app.py"
    if not launcher.exists():
        launcher.write_text(
            r'''#!/usr/bin/env python3
"""Launcher for the packaged Stock Signal Bot app."""
import os
import sys
import webbrowser
import threading
import time
from pathlib import Path

# Ensure we're in the right directory
os.chdir(Path(__file__).parent)

# Import and run the Streamlit app
from streamlit.web import cli as stcli

def open_browser():
    time.sleep(2)
    webbrowser.open("http://localhost:8501")

if __name__ == "__main__":
    threading.Thread(target=open_browser, daemon=True).start()
    sys.argv = ["streamlit", "run", "app.py", "--server.port=8501", "--server.headless=false"]
    sys.exit(stcli.main())
'''
        )

    # PyInstaller command
    cmd = [
        "pyinstaller",
        "--name=StockBot",
        "--onefile",
        "--windowed",  # No console window
        # NOTE: PyInstaller uses ';' as separator on ALL platforms
        "--add-data", "app.py;.",
        "--add-data", "config.py;.",
        "--add-data", "pages;pages",
        "--add-data", "data;data",
        "--add-data", "analysis;analysis",
        "--add-data", "signals;signals",
        "--add-data", "output;output",
        "--add-data", "utils;utils",
        "--add-data", "pwa;pwa",
        "--hidden-import=streamlit",
        "--hidden-import=pandas",
        "--hidden-import=pandas_ta",
        "--hidden-import=yfinance",
        "--hidden-import=plotly",
        "--hidden-import=numpy",
        "--hidden-import=requests",
        "--hidden-import=dotenv",
        "--hidden-import=rich",
        "--collect-all=streamlit",
        "--collect-all=pandas",
        "--collect-all=pandas_ta",
        "--collect-all=yfinance",
        "--collect-all=plotly",
        str(launcher),
    ]

    result = subprocess.run(cmd, cwd=ROOT, capture_output=True, text=True)

    if result.returncode == 0:
        print("✓ Build successful!")
        exe_path = DIST_DIR / "StockBot.exe"
        if exe_path.exists():
            print(f"  Executable: {exe_path}")
            print(f"  Size: {exe_path.stat().st_size / 1024 / 1024:.1f} MB")
    else:
        print("✗ Build failed!")
        print(result.stderr[-2000:] if result.stderr else result.stdout[-2000:])

    return result.returncode


def build_nsis_installer():
    """Build an NSIS installer wrapping the executable."""
    nsis_script = ROOT / "setup" / "installer.nsi"
    
    if not nsis_script.exists():
        print("✗ NSIS script not found at setup/installer.nsi")
        return 1

    # Check for NSIS
    nsis_paths = [
        "C:/Program Files/NSIS/makensis.exe",
        "C:/Program Files (x86)/NSIS/makensis.exe",
    ]
    
    makensis = None
    for p in nsis_paths:
        if Path(p).exists():
            makensis = p
            break

    if not makensis:
        print("✗ NSIS not found. Install from https://nsis.sourceforge.io/")
        print("  Then run: makensis setup/installer.nsi")
        return 1

    cmd = [makensis, str(nsis_script)]
    result = subprocess.run(cmd, cwd=ROOT, capture_output=True, text=True)

    if result.returncode == 0:
        print("✓ NSIS installer built!")
        installer = DIST_DIR / "StockBot_Setup.exe"
        if installer.exists():
            print(f"  Installer: {installer}")
            print(f"  Size: {installer.stat().st_size / 1024 / 1024:.1f} MB")
    else:
        print("✗ NSIS build failed!")
        print(result.stderr[-1000:] if result.stderr else result.stdout[-1000:])

    return result.returncode


def main():
    import argparse
    parser = argparse.ArgumentParser(description="Build Stock Signal Bot for Windows")
    parser.add_argument("--installer", action="store_true", help="Also build NSIS installer")
    parser.add_argument("--no-clean", action="store_true", help="Skip cleaning previous builds")
    args = parser.parse_args()

    if not args.no_clean:
        clean()

    ret = build_exe()
    if ret != 0:
        sys.exit(ret)

    if args.installer:
        ret = build_nsis_installer()
        if ret != 0:
            sys.exit(ret)

    print("\n✅ Build complete!")
    print(f"   Output directory: {DIST_DIR}")


if __name__ == "__main__":
    main()
