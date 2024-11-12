@echo off
REM Install EpanouiDent: First Installation Steps

REM Step 1: Prompt the user for the folder path containing all patient folders
set /p EPANOUIDENT_DEFAULT_PATH=Enter the folder path containing all patients folders: 

REM Step 2: Set the environment variable EPANOUIDENT_DEFAULT_PATH
setx EPANOUIDENT_DEFAULT_PATH "%EPANOUIDENT_DEFAULT_PATH%"

REM Step 3: Download the u2net.onnx model file
curl --create-dirs -L -o "%HOMEPATH%\.u2net\u2net.onnx" "https://github.com/danielgatis/rembg/releases/download/v0.0.0/u2net.onnx"

REM Completion message
echo Installation complete! EpanouiDent is now set up.
pause
