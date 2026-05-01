@echo off
cd /d "%~dp0"
"C:\Users\sinha\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe" app.py >> server.log 2>&1
