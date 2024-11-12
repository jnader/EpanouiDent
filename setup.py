import os
import sys
sys.setrecursionlimit(5000)
from cx_Freeze import setup, Executable

external_airmtp = os.path.join(os.getcwd(), "external", "airmtp")
install_bat = os.path.join(os.getcwd(), "install_scripts", "install.bat")

build_exe_options = {
    "excludes":["tkinter", "PyQt6"],  # Exclude unnecessary modules
    "include_files": [
        install_bat,  # include the install.bat file
        (external_airmtp, "lib/external/airmtp"),  # include the whole external/airmtp directory
    ],
}

# base="Win32GUI" should be used only for Windows GUI app
base = "Win32GUI" if sys.platform == "win32" else None

setup(
    name="EpanouiDent",
    version="0.1",
    author="Joudy Nader",
    author_email="joudynader13@gmail.com",
    description="Utility software for dentists",
    options={"build_exe": build_exe_options},
    executables=[Executable("main.py", base=base)],
)
