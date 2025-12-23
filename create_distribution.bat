@echo off
echo ========================================
echo Thin Film Analyzer - Distribution Package Creator
echo ========================================
echo.

REM Set version
set VERSION=2.2.1

REM Create distribution folder name
set DIST_FOLDER=ThinFilmAnalyzer_v%VERSION%

echo Creating distribution folder: %DIST_FOLDER%
echo.

REM Check if distribution folder already exists
if exist "%DIST_FOLDER%" (
    echo WARNING: Distribution folder already exists.
    echo Press Ctrl+C to cancel or
    pause
    echo Removing old distribution folder...
    rmdir /s /q "%DIST_FOLDER%"
)

REM Create main distribution folder
mkdir "%DIST_FOLDER%"

echo Copying application files...

REM Copy main application folder
xcopy /E /I /Y "thin_film_analyzer" "%DIST_FOLDER%\thin_film_analyzer"

REM Copy batch files
copy /Y "install.bat" "%DIST_FOLDER%\"
copy /Y "run_app.bat" "%DIST_FOLDER%\"

REM Copy documentation
copy /Y "SETUP_GUIDE.md" "%DIST_FOLDER%\"
copy /Y "QUICK_REFERENCE.md" "%DIST_FOLDER%\"
copy /Y "README.md" "%DIST_FOLDER%\"
copy /Y "requirements.txt" "%DIST_FOLDER%\"

REM Optional: Copy diagnostic scripts
echo.
echo Do you want to include diagnostic scripts? (Y/N)
set /p INCLUDE_DIAG="Include diagnose_threshold.py and analyze_images.py? "
if /i "%INCLUDE_DIAG%"=="Y" (
    copy /Y "diagnose_threshold.py" "%DIST_FOLDER%\" 2>nul
    copy /Y "analyze_images.py" "%DIST_FOLDER%\" 2>nul
    echo Diagnostic scripts included.
) else (
    echo Diagnostic scripts skipped.
)

REM Clean up __pycache__ folders
echo.
echo Cleaning up Python cache files...
for /d /r "%DIST_FOLDER%" %%d in (__pycache__) do @if exist "%%d" rd /s /q "%%d"
del /s /q "%DIST_FOLDER%\*.pyc" 2>nul

echo.
echo ========================================
echo Distribution package created successfully!
echo ========================================
echo.
echo Folder: %DIST_FOLDER%
echo.
echo Next steps:
echo 1. Review the contents of %DIST_FOLDER%
echo 2. Test on a clean machine if possible
echo 3. Compress to ZIP file: %DIST_FOLDER%.zip
echo 4. Share with your team members
echo.
echo See DISTRIBUTION_CHECKLIST.md for complete distribution guide.
echo.
pause
