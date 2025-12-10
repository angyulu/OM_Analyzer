# Thin Film Analyzer - Quick Reference Card

## Getting Started (First Time Only)

1. Install Python from https://www.python.org/downloads/
   - **IMPORTANT:** Check "Add Python to PATH" during installation
2. Double-click `install.bat` and wait for completion
3. Double-click `run_app.bat` to start the application

## Daily Use

**Launch:** Double-click `run_app.bat`

## Basic Operations

| Action | How To |
|--------|--------|
| Load image | Click "Load Image" button |
| Next/Previous image | Click "Next" or "Previous" buttons |
| View results | Check coverage percentage at top |
| Save screenshot | (Use Windows Snipping Tool or Print Screen) |

## Parameter Tuning

### Main Parameters (99% of users only need these)

| Parameter | What It Does | When to Change |
|-----------|--------------|----------------|
| **Adaptive C** | Sensitivity for thin flakes | Missing flakes? Lower to 3-4<br>Too much detected? Raise to 10-15 |
| **Adaptive Block Size** | Size of local region | Usually keep at 200<br>Make larger than your biggest flake |

### Advanced Parameters (rarely needed)

| Parameter | Default | Purpose |
|-----------|---------|---------|
| Blur Kernel | 3 | Noise reduction (larger = more blur) |
| Morph Close | 2 | Fill small holes |
| Morph Open | 2 | Remove small noise spots |

## Common Problems & Solutions

| Problem | Solution |
|---------|----------|
| Missing thin flakes | Lower "Adaptive C" to 3-4 |
| Detecting too much (false positives) | Raise "Adaptive C" to 10-15 |
| Bright circle in center | Enable "Use Adaptive Threshold" |
| Missing flakes in corners | Enable "Use Adaptive Threshold" |
| Noisy detection | Increase "Blur Kernel" to 5 |
| Small holes in flakes | Increase "Morph Close" to 3-4 |

## Understanding Results

- **Coverage:** Percentage of image covered by flakes
- **Red overlay:** Shows what the software detected as flakes
- **Processing time:** How long detection took

## File Formats Supported

- TIFF (.tif, .tiff) ✓
- PNG (.png) ✓
- JPEG (.jpg, .jpeg) ✓
- Bitmap (.bmp) ✓

## Tips for Best Results

1. **Use consistent imaging conditions** - Same microscope settings for all images
2. **Avoid manual adjustments** - Use default parameters when possible
3. **Check a few images first** - Verify detection accuracy before batch processing
4. **Keep Adaptive Threshold enabled** - It handles uneven lighting automatically
5. **Adaptive C = 5 works for most cases** - Only change if clearly needed

## Keyboard Shortcuts

- `Ctrl+O` - Open image
- `Ctrl+Q` - Exit application

## When to Contact Support

- Application won't start after following setup guide
- Python installation issues
- Consistent detection problems across all images
- Need help choosing parameters for specific sample types

## Where to Get Help

See `SETUP_GUIDE.md` for detailed troubleshooting

---

**Remember:** The default settings (Adaptive Threshold ON, C=5, Block Size=200) work for most cases. Only adjust if you see obvious problems!
