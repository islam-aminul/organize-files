@echo off
setlocal EnableDelayedExpansion

echo Checking for virtual environment...

IF NOT EXIST venv (
    echo Creating virtual environment...
    python -m venv venv
    IF NOT !ERRORLEVEL! EQU 0 (
        echo Error creating virtual environment
        pause
        exit /b 1
    )
    echo Virtual environment created successfully
) ELSE (
    echo Virtual environment already exists
)

echo Activating virtual environment...
call venv\Scripts\activate

echo Checking for installed requirements...
python -c "import PIL, tqdm, tkinter, pytz" 2>nul
IF NOT !ERRORLEVEL! EQU 0 (
    echo Installing requirements...
    python -m pip install --upgrade pip
    pip install -r requirements.txt
    IF NOT !ERRORLEVEL! EQU 0 (
        echo Error installing requirements
        pause
        exit /b 1
    )
    echo Requirements installed successfully
) ELSE (
    echo Requirements already installed
)

echo Checking for ffmpeg...
where ffprobe >nul 2>nul
IF NOT !ERRORLEVEL! EQU 0 (
    echo WARNING: ffprobe ^(part of ffmpeg^) is not found in PATH.
    echo Please install ffmpeg from https://ffmpeg.org/download.html
    echo and add it to your system PATH for full video metadata support.
    echo.
    pause
)

echo Cleaning previous builds...
rd /s /q dist 2>nul
rd /s /q build 2>nul

echo Building executable...
pyinstaller pyinstaller.spec
IF NOT !ERRORLEVEL! EQU 0 (
    echo Error building executable
    pause
    exit /b 1
)

echo.
echo Setup completed successfully!
echo The executable can be found in the dist folder as 'FileOrganizer.exe'
echo.

echo Done! You can find the executable in the dist folder.
pause

endlocal
