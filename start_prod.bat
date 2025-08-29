@echo off
setlocal

REM Set default port if not already set
if "%PORT%"=="" set PORT=8010

REM Run Uvicorn
echo Starting FastAPI server on http://127.0.0.1:%PORT%
uvicorn backend.main:app --host 127.0.0.1 --port %PORT%

endlocal
