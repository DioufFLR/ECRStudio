#!/usr/bin/env python3
"""Build ECRStudio as a standalone Windows .exe using PyInstaller."""

import subprocess
import sys

def build():
    cmd = [
        sys.executable, "-m", "PyInstaller",
        "--onefile",
        "--windowed",
        "--name", "ECRStudio",
        "main.py",
    ]
    print(f"Running: {' '.join(cmd)}")
    subprocess.run(cmd, check=True)
    print("\nBuild complete! Executable is in dist/ECRStudio.exe")

if __name__ == "__main__":
    build()
