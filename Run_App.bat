@echo off
REM Anaconda ke base environment ko automatically activate karne ke liye
call D:\Anaconda3\Scripts\activate.bat D:\Anaconda3

REM Ab aapki GUI app ko sahi environment mein run karega
python "%~dp0app_gui.py"

pause