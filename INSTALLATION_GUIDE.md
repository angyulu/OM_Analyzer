# Installation Guide - Thin Film Analyzer v2.1.1

This guide will help you install and set up the Thin Film Analyzer on your computer.

## Table of Contents

- [Prerequisites](#prerequisites)
- [Installation Steps](#installation-steps)
  - [Windows](#windows-installation)
  - [macOS](#macos-installation)
  - [Linux](#linux-installation)
- [Running the Application](#running-the-application)
- [Troubleshooting](#troubleshooting)
- [Uninstallation](#uninstallation)

---

## Prerequisites

### Python 3.10 or Higher

The application requires Python 3.10 or higher to be installed on your system.

#### Checking if Python is Installed

**Windows:**
```cmd
python --version
```

**macOS/Linux:**
```bash
python3 --version
```

If Python is installed, you should see output like `Python 3.10.x` or higher.

#### Installing Python

If Python is not installed or the version is too old:

**Windows:**
1. Download Python from [python.org/downloads](https://www.python.org/downloads/)
2. Run the installer
3. **IMPORTANT:** Check "Add Python to PATH" during installation
4. Click "Install Now"
5. Restart your Command Prompt after installation

**macOS:**
- Using Homebrew (recommended):
  ```bash
  brew install python@3.10
  ```
- Or download from [python.org/downloads](https://www.python.org/downloads/)

**Linux (Ubuntu/Debian):**
```bash
sudo apt update
sudo apt install python3 python3-pip python3-venv
```

**Linux (Fedora):**
```bash
sudo dnf install python3 python3-pip
```

---

## Installation Steps

### Windows Installation

1. **Extract the ZIP file**
   - Right-click `ThinFilmAnalyzer_v2.1.1.zip`
   - Select "Extract All..."
   - Choose a destination folder (e.g., `C:\ThinFilmAnalyzer`)

2. **Open Command Prompt**
   - Navigate to the extracted folder
   - You can also open Command Prompt by:
     - Holding Shift and right-clicking in the folder
     - Select "Open PowerShell window here" or "Open command window here"

3. **Run the installer**
   ```cmd
   install.bat
   ```

4. **Wait for installation to complete**
   - The installer will download and install all required packages
   - This may take 2-5 minutes depending on your internet connection
   - You'll see a "Installation complete!" message when done

5. **Done!**
   - You can now run the application (see [Running the Application](#running-the-application))

### macOS Installation

1. **Extract the ZIP file**
   - Double-click `ThinFilmAnalyzer_v2.1.1.zip`
   - The folder will be automatically extracted

2. **Open Terminal**
   - Open the Terminal application (Applications → Utilities → Terminal)
   - Navigate to the extracted folder:
     ```bash
     cd /path/to/ThinFilmAnalyzer_v2.1.1
     ```
   - Tip: You can drag the folder from Finder into Terminal to auto-type the path

3. **Make scripts executable**
   ```bash
   chmod +x install.sh run_app.sh
   ```

4. **Run the installer**
   ```bash
   ./install.sh
   ```

5. **Wait for installation to complete**
   - The installer will download and install all required packages
   - This may take 2-5 minutes depending on your internet connection
   - You'll see a "Installation complete!" message when done

6. **Done!**
   - You can now run the application (see [Running the Application](#running-the-application))

### Linux Installation

1. **Extract the ZIP file**
   ```bash
   unzip ThinFilmAnalyzer_v2.1.1.zip
   cd ThinFilmAnalyzer_v2.1.1
   ```

2. **Make scripts executable**
   ```bash
   chmod +x install.sh run_app.sh
   ```

3. **Run the installer**
   ```bash
   ./install.sh
   ```

4. **Wait for installation to complete**
   - The installer will download and install all required packages
   - This may take 2-5 minutes depending on your internet connection
   - You'll see a "Installation complete!" message when done

5. **Done!**
   - You can now run the application (see [Running the Application](#running-the-application))

---

## Running the Application

### Windows

Double-click `run_app.bat` or run in Command Prompt:
```cmd
run_app.bat
```

### macOS/Linux

In Terminal:
```bash
./run_app.sh
```

Or double-click `run_app.sh` (may need to set default application to Terminal)

---

## Troubleshooting

### Python Not Found

**Error:** `python: command not found` or `Python is not installed`

**Solution:**
- Make sure Python is installed (see [Prerequisites](#prerequisites))
- **Windows:** Ensure "Add Python to PATH" was checked during installation
  - If not, reinstall Python with this option checked
  - Or manually add Python to PATH in System Environment Variables
- **macOS/Linux:** Use `python3` command instead of `python`

### Permission Denied (macOS/Linux)

**Error:** `Permission denied` when running scripts

**Solution:**
```bash
chmod +x install.sh run_app.sh
```

### Module Not Found

**Error:** `No module named 'PyQt6'` or similar

**Solution:**
- Run the installer again:
  - **Windows:** `install.bat`
  - **macOS/Linux:** `./install.sh`
- If the error persists, try manual installation:
  ```bash
  pip install -r requirements.txt
  ```
  or on macOS/Linux:
  ```bash
  pip3 install -r requirements.txt
  ```

### Application Doesn't Start

**Symptoms:** Window opens briefly and closes, or no window appears

**Solution:**
1. Run the application from Command Prompt/Terminal to see error messages
2. Check if all dependencies are installed:
   ```bash
   pip list
   ```
3. Look for missing packages from `requirements.txt`
4. Reinstall dependencies using `install.bat` or `./install.sh`

### Display/Graphics Issues

**Symptoms:** Blank window, garbled graphics, or crashes when loading images

**Solution:**
- **Windows:** Update your graphics drivers
- **macOS:** Make sure you're running macOS 10.14 (Mojave) or later
- **Linux:** Install additional graphics libraries:
  ```bash
  sudo apt install libxcb-xinerama0 libxcb-cursor0
  ```

### Qt Platform Plugin Error

**Error:** `Could not find the Qt platform plugin "windows"`

**Solution:**
- Reinstall PyQt6:
  ```bash
  pip uninstall PyQt6
  pip install PyQt6
  ```

---

## Uninstallation

### Windows

1. Delete the entire `ThinFilmAnalyzer_v2.1.1` folder
2. That's it! The application doesn't install anything system-wide

### macOS/Linux

```bash
rm -rf ThinFilmAnalyzer_v2.1.1
```

### Cleaning Up Python Packages (Optional)

If you want to remove the installed Python packages (only do this if you're not using them elsewhere):

```bash
pip uninstall PyQt6 opencv-python scikit-image Pillow numpy scipy pandas
```

Or on macOS/Linux:
```bash
pip3 uninstall PyQt6 opencv-python scikit-image Pillow numpy scipy pandas
```

---

## Need More Help?

- Check the [USER_GUIDE.md](USER_GUIDE.md) for application usage instructions
- Report issues on GitHub: https://github.com/angyulu/OM_Analyzer/issues
- Review the [README.md](README.md) for general information

