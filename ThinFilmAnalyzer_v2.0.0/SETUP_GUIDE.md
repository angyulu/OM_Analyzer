# Thin Film Analyzer - Setup Guide for Team Members

This guide will help you install and run the Thin Film Coverage Analyzer application on your Windows computer.

## Step 1: Install Python

1. **Download Python:**
   - Go to https://www.python.org/downloads/
   - Click the yellow "Download Python 3.12.x" button (or latest version)
   - Save the installer file to your Downloads folder

2. **Install Python:**
   - Double-click the downloaded installer file
   - **IMPORTANT:** Check the box that says "Add Python to PATH" at the bottom of the installer window
   - Click "Install Now"
   - Wait for installation to complete (may take 2-5 minutes)
   - Click "Close" when done

3. **Verify Installation:**
   - Press `Windows Key + R` on your keyboard
   - Type `cmd` and press Enter
   - In the black window that appears, type: `python --version`
   - You should see something like "Python 3.12.x"
   - Type `exit` and press Enter to close the window

## Step 2: Install Application Dependencies

1. **Open the application folder:**
   - Navigate to the folder where you received this application
   - You should see files including `install.bat`, `run_app.bat`, and this guide

2. **Run the installer:**
   - Double-click `install.bat`
   - A black window will appear showing installation progress
   - Wait until you see "Installation complete!" (may take 2-5 minutes)
   - Press any key to close the window

## Step 3: Run the Application

1. **Launch the application:**
   - Double-click `run_app.bat`
   - The application window will open in a few seconds

2. **First-time use:**
   - If you see any Windows Firewall popup, click "Allow access"

## Using the Application

### Loading Images

1. Click "Load Image" button
2. Select a .tif microscopy image
3. The image will appear with detected flakes highlighted in red

### Understanding the Results

- **Red overlay:** Shows detected flake regions
- **Coverage percentage:** Displayed at the top (e.g., "Coverage: 15.23%")
- **Processing time:** Shows how long the detection took

### Tuning Detection Parameters

The application is pre-configured with optimal settings, but you can adjust:

**Adaptive Threshold (enabled by default):**
- **Adaptive Block Size (default: 200):** Size of local region for background estimation
  - Larger values = smoother background estimation
  - Should be larger than your largest flake

- **Adaptive C (default: 5):** Minimum brightness difference to detect flakes
  - Lower values (3-5) = detect thinner flakes (more sensitive)
  - Higher values (10-15) = only detect thicker flakes (less sensitive)

**Other Parameters:**
- **Threshold:** Manual threshold value (only works if "Use Adaptive Threshold" is unchecked)
- **Noise Reduction:** Enable to reduce image noise before detection
- **Blur Kernel:** Size of blur filter (larger = more smoothing)
- **Morphological Close/Open:** Clean up small holes and noise in detection

### Processing Multiple Images

1. Use "Previous" and "Next" buttons to navigate through images in the same folder
2. Each image is processed with the current parameter settings
3. Results update automatically when you change parameters

## Troubleshooting

### Problem: "python is not recognized as an internal or external command"
**Solution:** Python was not added to PATH during installation. Reinstall Python and make sure to check "Add Python to PATH"

### Problem: "No module named 'PyQt6'" or similar errors
**Solution:** Dependencies were not installed correctly. Run `install.bat` again

### Problem: Application window is too small/large
**Solution:** The window is resizable - drag the edges to adjust size

### Problem: Detection is missing flakes or detecting too much
**Solution:**
- For missing flakes: Lower the "Adaptive C" value (try 3-5)
- For over-detection: Raise the "Adaptive C" value (try 10-15)
- Adjust "Adaptive Block Size" to match your image characteristics

### Problem: Application crashes or freezes
**Solution:**
1. Close the application
2. Run `run_app.bat` again
3. If problem persists, contact the development team

## Contact

If you encounter any issues not covered in this guide, please contact:
- [Your name/email here]

## Advanced: Running from Command Line

If you're comfortable with command line, you can run:
```
cd C:\Users\Ang-Yu Lu\python_virtual\platform\OM_Analyzer\OM_V0
python thin_film_analyzer/main.py
```

## File Locations

- **Application files:** `thin_film_analyzer/` folder
- **Test images:** `thin_film_analyzer/tests/Images/` folder
- **Your images:** Load from any location using "Load Image" button
