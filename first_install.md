First installation steps:

# Windows:
- Press `Win + R` and type `cmd`. Command prompt should open.
- Type the following:
```
setx EPANOUIDENT_DEFAULT_PATH <folder_containing_all_patients_folders>
```

- In the command prompt, also type:
```
curl --create-dirs -L -o "%HOMEPATH%/.u2net/u2net.onnx" "https://github.com/danielgatis/rembg/releases/download/v0.0.0/u2net.onnx"
```
