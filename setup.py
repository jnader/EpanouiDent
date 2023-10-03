import sys
sys.setrecursionlimit(5000)
from cx_Freeze import setup, Executable

# Dependencies are automatically detected, but it might need fine tuning.
build_exe_options = {
    "excludes": ["tkinter", "unittest"],
    "zip_include_packages": ["encodings", "PySide2"],
    "optimize": 1,
}

# base="Win32GUI" should be used only for Windows GUI app
base = "Win32GUI" if sys.platform == "win32" else None

setup(
    name="EpanouiDent",
    version="0.1",
    description="Software for Dentists!",
    options={"build_exe": build_exe_options},
    executables=[Executable("main.py", base=base)],
)