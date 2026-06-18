@echo off
cd /d "%~dp0"
@echo on
call "C:\Program Files\QGIS 3.40.5\bin\python-qgis-ltr.bat" -m PyQt5.pyrcc_main -o resources.py resources.qrc
