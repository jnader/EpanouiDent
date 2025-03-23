#!/bin/sh
# Install EpanouiDent: First Installation Steps

# Step 1: Prompt the user for the folder path containing all patient folders
read -r -p "Enter the folder path containing all patients folders: " EPANOUIDENT_DEFAULT_PATH

echo $EPANOUIDENT_DEFAULT_PATH

# Step 2: Set the environment variable EPANOUIDENT_DEFAULT_PATH
echo "export EPANOUIDENT_DEFAULT_PATH=$EPANOUIDENT_DEFAULT_PATH" >> $HOME/.bashrc

# Step 3: Download the u2net.onnx model file
curl --create-dirs -L -o $HOME/.u2net/u2net.onnx https://github.com/danielgatis/rembg/releases/download/v0.0.0/u2net.onnx

# Completion message
echo "Installation complete! EpanouiDent is now setup."
