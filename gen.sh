#!/bin/bash
source .qtcreator/Python_3_13_3venv/bin/activate
pyside6-uic form.ui -o ui_form.py
pyside6-uic about.ui -o ui_about.py