@echo off
setlocal

REM Usage: start_dev.bat [CONDA_ENV_NAME]
set CONDA_ENV=%1
if "%CONDA_ENV%"=="" set CONDA_ENV=predyktor

echo Activating conda environment: %CONDA_ENV%
call conda activate %CONDA_ENV% || (
    echo Failed to activate %CONDA_ENV%, falling back to base
    call conda activate base
)

REM Start backend with reload in separate window
start "Backend" cmd /k "cd backend && python -m uvicorn main:app --host 127.0.0.1 --port 8010 --reload"

REM Start frontend dev server
pushd frontend
if exist package.json (
    npm install --no-audit --no-fund
    npm start
) else (
    echo package.json not found in frontend. Cannot start dev server.
)
popd

endlocal
