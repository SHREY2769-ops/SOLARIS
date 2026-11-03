@echo off
cd /d "%~dp0"
if not exist .env (
  copy .env.example .env >nul
  echo A settings file will open. Paste your Gemini key after GEMINI_API_KEY= then save and close it.
  notepad .env
)
if not exist .venv\Scripts\python.exe (
  echo First-time setup. This takes a minute or two...
  py -3.12 -m venv .venv
  if errorlevel 1 python -m venv .venv
  .venv\Scripts\python.exe -m pip install --upgrade pip
  .venv\Scripts\python.exe -m pip install -r requirements.txt
)
.venv\Scripts\python.exe app.py
pause
