@echo off
start cmd /k python broker.py
timeout /t 1 >nul
start cmd /k python player.py
start cmd /k python player.py