# RapidBot Setup Guide

A simple step-by-step guide to install RapidBot on a new Windows PC.

---

## Step 1: Install Python

1. Open your web browser and go to: **https://www.python.org/downloads/**
2. Click the big yellow **"Download Python"** button
3. Run the downloaded file
4. ⚠️ **IMPORTANT**: Check the box that says **"Add Python to PATH"** at the bottom
5. Click **"Install Now"**
6. Wait for installation to complete, then click **"Close"**

---

## Step 2: Install Tesseract OCR

1. Open **PowerShell** (search "PowerShell" in Start menu)
2. Copy and paste this command, then press Enter:
   ```
   winget install UB-Mannheim.TesseractOCR
   ```
3. Type **Y** and press Enter when asked to agree
4. Wait for installation to complete

---

## Step 3: Download RapidBot

1. Get the RapidBot folder from your source (USB, cloud, etc.)
2. Copy the entire `rapidbot` folder to your computer
3. Remember where you put it (e.g., `C:\rapidbot`)

---

## Step 4: Install Python Libraries

1. Open **PowerShell**
2. Navigate to the rapidbot folder:
   ```
   cd C:\rapidbot
   ```
3. Create a virtual environment:
   ```
   python -m venv .venv
   ```
4. Activate it:
   ```
   .\.venv\Scripts\Activate.ps1
   ```
5. Install required libraries:
   ```
   pip install pyautogui opencv-python pytesseract pillow pywin32 requests websocket-client numpy
   ```
6. Wait for all packages to install

---

## Step 5: Run RapidBot

1. Open **PowerShell**
2. Go to the rapidbot folder:
   ```
   cd C:\rapidbot
   ```
3. Activate the virtual environment:
   ```
   .\.venv\Scripts\Activate.ps1
   ```
4. Start the app:
   ```
   python app.py
   ```

---

## Quick Start (After Setup)

Every time you want to run RapidBot:

1. Open PowerShell
2. Run these commands:
   ```
   cd C:\rapidbot
   .\.venv\Scripts\Activate.ps1
   python app.py
   ```

---

## Troubleshooting

### "Python is not recognized"
→ Reinstall Python and make sure to check **"Add Python to PATH"**

### "Tesseract not found" or OCR errors
→ Run this in PowerShell: `winget install UB-Mannheim.TesseractOCR --force`

### "Script cannot be run" error
→ Run this in PowerShell (as Administrator):
```
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

---

## Need Help?

If you get stuck, take a screenshot of the error message and ask for help!
