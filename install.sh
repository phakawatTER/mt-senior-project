#!/bin/bash
rm -rf dist # remove prev version #dist
rm -rf build # remove prev version of build
pyinstaller control.spec # freeze the code
python TCLChanger.py # change TCL version
