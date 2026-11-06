@echo off
echo ====================================================
echo  eminakkurt.com AI Agent & MCP Backend Baslatiliyor
echo ====================================================
cd /d "%~dp0"
"C:\Users\Vanora\AppData\Local\Programs\Python\Python312\python.exe" -m uvicorn server:app --host 127.0.0.1 --port 8000 --reload
pause
