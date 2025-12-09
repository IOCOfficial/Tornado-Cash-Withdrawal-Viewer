# Tornado Cash Withdrawal Viewer - Setup Guide

A step-by-step guide for new users on **macOS** and **Windows**.

---

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Get an Etherscan API Key](#get-an-etherscan-api-key)
3. [Download the Tool](#download-the-tool)
4. [Installation & Setup](#installation--setup)
   - [macOS Setup](#macos-setup)
   - [Windows Setup](#windows-setup)
5. [Running the Tool](#running-the-tool)
6. [Usage Examples](#usage-examples)
7. [Troubleshooting](#troubleshooting)

---

## Prerequisites

### What You Need

| Requirement | Description |
|-------------|-------------|
| **Python 3.8+** | Programming language runtime |
| **Etherscan API Key** | Free API key from Etherscan |
| **Internet Connection** | Required to query the blockchain |

---

## Get an Etherscan API Key

Before using the tool, you need a free Etherscan API key.

### Step 1: Create an Etherscan Account

1. Go to [https://etherscan.io/register](https://etherscan.io/register)
2. Fill in your email and create a password
3. Verify your email address

### Step 2: Generate an API Key

1. Log in to Etherscan
2. Go to [https://etherscan.io/myapikey](https://etherscan.io/myapikey)
3. Click **"Add"** to create a new API key
4. Give it a name (e.g., "Tornado Viewer")
5. Click **"Create New API Key"**
6. **Copy and save your API key** - you'll need it later

> ⚠️ **Keep your API key private.** Don't share it publicly.

---

## Download the Tool

### Option 1: Download ZIP (Easiest)

1. Go to the GitHub repository
2. Click the green **"Code"** button
3. Click **"Download ZIP"**
4. Extract the ZIP file to a folder of your choice

### Option 2: Git Clone

If you have Git installed:

```bash
git clone https://github.com/YOUR_USERNAME/tornado_cash_viewer.git
cd tornado_cash_viewer
```

---

## Installation & Setup

Choose your operating system:

- [macOS Setup](#macos-setup)
- [Windows Setup](#windows-setup)

---

## macOS Setup

### Step 1: Check if Python is Installed

1. Open **Terminal** (press `Cmd + Space`, type "Terminal", press Enter)

2. Check Python version:
   ```bash
   python3 --version
   ```

3. If you see `Python 3.x.x`, you're good! Skip to [Step 3](#step-3-navigate-to-the-tool-folder).

4. If you see "command not found", continue to Step 2.

### Step 2: Install Python (if needed)

#### Option A: Download from Python.org (Recommended)

1. Go to [https://www.python.org/downloads/](https://www.python.org/downloads/)
2. Click **"Download Python 3.x.x"** (latest version)
3. Open the downloaded `.pkg` file
4. Follow the installation wizard
5. Restart Terminal and verify:
   ```bash
   python3 --version
   ```

#### Option B: Install via Homebrew

If you have Homebrew installed:
```bash
brew install python3
```

### Step 3: Navigate to the Tool Folder

1. In Terminal, navigate to where you extracted/downloaded the tool:
   ```bash
   cd ~/Downloads/tornado_cash_viewer
   ```
   
   Or drag the folder into Terminal after typing `cd `:
   ```bash
   cd /path/to/tornado_cash_viewer
   ```

### Step 4: Make the Script Executable

```bash
chmod +x run.sh
```

### Step 5: Run the Tool

```bash
./run.sh
```

### Step 6: Enter Your API Key

On first run, you'll be prompted:
```
════════════════════════════════════════════════════════════
ETHERSCAN API KEY SETUP
════════════════════════════════════════════════════════════

No API key found. You need an Etherscan API key to use this tool.
Get a free API key at: https://etherscan.io/apis

Enter your Etherscan API key: 
```

1. Paste your Etherscan API key
2. Press Enter
3. The key will be validated and saved automatically

**You're ready to go!** 🎉

---

## Windows Setup

### Step 1: Check if Python is Installed

1. Open **Command Prompt** (press `Win + R`, type "cmd", press Enter)

2. Check Python version:
   ```cmd
   python --version
   ```

3. If you see `Python 3.x.x`, skip to [Step 3](#step-3-navigate-to-the-tool-folder-1).

4. If you see "'python' is not recognized", continue to Step 2.

### Step 2: Install Python (if needed)

1. Go to [https://www.python.org/downloads/](https://www.python.org/downloads/)

2. Click **"Download Python 3.x.x"** (latest version)

3. **IMPORTANT:** Run the installer and check these boxes:
   - ✅ **"Add Python to PATH"** (at the bottom of the installer)
   - ✅ "Install for all users" (optional)

4. Click **"Install Now"**

5. After installation, **close and reopen Command Prompt**

6. Verify installation:
   ```cmd
   python --version
   ```

### Step 3: Navigate to the Tool Folder

1. Open **Command Prompt**

2. Navigate to where you extracted the tool:
   ```cmd
   cd C:\Users\YourName\Downloads\tornado_cash_viewer
   ```
   
   Or use the full path to wherever you saved it.

### Step 4: Create Virtual Environment & Install Dependencies

Since Windows doesn't run `.sh` files directly, run these commands:

```cmd
:: Create virtual environment
python -m venv venv

:: Activate the virtual environment
venv\Scripts\activate

:: Install dependencies
pip install -r requirements.txt
```

### Step 5: Run the Tool

```cmd
python tornado_viewer.py
```

### Step 6: Enter Your API Key

On first run, you'll be prompted:
```
════════════════════════════════════════════════════════════
ETHERSCAN API KEY SETUP
════════════════════════════════════════════════════════════

No API key found. You need an Etherscan API key to use this tool.
Get a free API key at: https://etherscan.io/apis

Enter your Etherscan API key:
```

1. Paste your Etherscan API key
2. Press Enter
3. The key will be validated and saved automatically

**You're ready to go!** 🎉

### Windows: Running the Tool in the Future

Each time you want to run the tool:

```cmd
cd C:\Users\YourName\Downloads\tornado_cash_viewer
venv\Scripts\activate
python tornado_viewer.py
```

Or create a batch file (see [Troubleshooting](#create-a-windows-batch-file)).

---

## Running the Tool

### Interactive Mode (Recommended for Beginners)

Just run the tool without any arguments:

**macOS:**
```bash
./run.sh
```

**Windows:**
```cmd
python tornado_viewer.py
```

You'll see the main menu:
```
╔════════════════════════════════════════════════════════════════════════════╗
║            TORNADO CASH WITHDRAWAL VIEWER                                  ║
║                       intelligenceonchain.com                              ║
╚════════════════════════════════════════════════════════════════════════════╝

  Options:
    1. View Tornado Cash Withdrawals
    2. Change API Key
    3. Exit

  Select option (1-3):
```

### Command Line Mode (For Advanced Users)

Run queries directly from the terminal:

**macOS:**
```bash
./run.sh --last-7d
./run.sh --last-30d --pools 10,100 --export results.csv
```

**Windows:**
```cmd
python tornado_viewer.py --last-7d
python tornado_viewer.py --last-30d --pools 10,100 --export results.csv
```

---

## Usage Examples

### Example 1: Analyze Last 7 Days (All Pools)

1. Run the tool
2. Select option `1` (View Tornado Cash Withdrawals)
3. Select option `1` (All pools)
4. Select option `2` (Last 7 days)
5. Leave export blank (or enter a filename)
6. View results!

### Example 2: Analyze Only 100 ETH Pool (Last 30 Days)

1. Run the tool
2. Select option `1`
3. Select option `4` (100 ETH pool only)
4. Select option `3` (Last 30 days)
5. Enter `withdrawals.csv` to export
6. Results saved to CSV!

### Example 3: Command Line - Quick Query

**macOS:**
```bash
./run.sh --last-24h --pools 100
```

**Windows:**
```cmd
python tornado_viewer.py --last-24h --pools 100
```

### Example 4: Export to CSV

**macOS:**
```bash
./run.sh --last-30d --pools 10,100 --export tornado_results.csv
```

**Windows:**
```cmd
python tornado_viewer.py --last-30d --pools 10,100 --export tornado_results.csv
```

---

## Troubleshooting

### Common Issues

#### "python: command not found" (macOS)

Use `python3` instead of `python`:
```bash
python3 tornado_viewer.py
```

#### "python is not recognized" (Windows)

Python wasn't added to PATH. Either:
1. Reinstall Python and check **"Add Python to PATH"**
2. Or use the full path: `C:\Users\YourName\AppData\Local\Programs\Python\Python3x\python.exe`

#### "Permission denied" (macOS)

Make the script executable:
```bash
chmod +x run.sh
```

#### "No module named requests"

Install dependencies:
```bash
pip install requests
```

Or use the virtual environment:

**macOS:**
```bash
./run.sh  # This handles it automatically
```

**Windows:**
```cmd
venv\Scripts\activate
pip install -r requirements.txt
```

#### API Key Invalid

1. Check for extra spaces when pasting
2. Make sure the key is from [etherscan.io](https://etherscan.io), not another block explorer
3. Wait a few minutes if you just created the key

#### "Connection timeout"

- Check your internet connection
- Etherscan may be temporarily slow - try again in a few minutes

### Create a Windows Batch File

To make running easier on Windows, create a file called `run.bat`:

1. Open Notepad
2. Paste this:
   ```batch
   @echo off
   cd /d "%~dp0"
   call venv\Scripts\activate
   python tornado_viewer.py %*
   pause
   ```
3. Save as `run.bat` in the tornado_cash_viewer folder
4. Double-click `run.bat` to run the tool

### Reset Your API Key

If you need to change your API key:

**macOS:**
```bash
./run.sh --reset-key
```

**Windows:**
```cmd
python tornado_viewer.py --reset-key
```

Or delete the config file:
- **macOS/Linux:** `~/.tornado_viewer/config.json`
- **Windows:** `C:\Users\YourName\.tornado_viewer\config.json`

---

## Getting Help

- **GitHub Issues:** Report bugs or request features
- **intelligenceonchain.com:** More blockchain tools and resources

---

**Happy investigating!** 🔍

*Built by [intelligenceonchain.com](https://intelligenceonchain.com)*
