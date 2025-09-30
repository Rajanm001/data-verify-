@echo off
echo Starting GetGSA Server...
echo ========================

cd /d "C:\Users\Rajan mishra Ji\abhi"

echo Activating virtual environment...
call ".venv\Scripts\activate.bat"

echo.
echo Starting GetGSA AI Analysis Server...
echo Server will be available at: http://127.0.0.1:8001
echo.
echo Press Ctrl+C to stop the server
echo.

python -m uvicorn main:app --host 127.0.0.1 --port 8001

pause