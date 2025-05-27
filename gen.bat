@echo off
.\.qtcreator\Python_3_13_2venv\Scripts\activate.bat
pyside6-uic form.ui -o ui_form.py
pyside6-uic about.ui -o ui_about.py