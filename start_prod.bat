@echo off
setlocal enabledelayedexpansion

REM Usage: start_prod.bat [CONDA_ENV_NAME]
REM If CONDA_ENV_NAME not provided, tries to use 'predyktor' then 'base'.

set PORT=%PORT%
if "%PORT%"=="" set PORT=8010

REM Fix MKL threading issues that can cause crashes
@echo off
REM Minimal start_prod.bat - robust backend starter using conda run or python
setlocal

REM Usage: start_prod.bat [CONDA_ENV_NAME]
set PORT=%PORT%
if "%PORT%"=="" set PORT=8010

set CONDA_ENV=%1
if "%CONDA_ENV%"=="" set CONDA_ENV=predyktor

echo Starting backend on http://127.0.0.1:%PORT% using environment: %CONDA_ENV%

REM Ensure working directory is repository root
cd /d "C:\kurs_ai\zadania_domowe\predyktor_react"

REM Move to backend and start uvicorn
pushd backend

where conda >nul 2>&1
if errorlevel 1 (
	echo conda not found on PATH - using python from current shell
	python -m uvicorn main:app --host 127.0.0.1 --port %PORT%
) else (
	rem Try to find conda.bat to activate env in this script by checking common locations
	set "CONDA_BAT="
	if exist "%USERPROFILE%\miniconda3\condabin\conda.bat" set "CONDA_BAT=%USERPROFILE%\miniconda3\condabin\conda.bat"
	if exist "%USERPROFILE%\Anaconda3\condabin\conda.bat" if not defined CONDA_BAT set "CONDA_BAT=%USERPROFILE%\Anaconda3\condabin\conda.bat"
	for %%p in ("%ProgramFiles%\conda\condabin\conda.bat" "%ProgramFiles(x86)%\conda\condabin\conda.bat") do if not defined CONDA_BAT if exist %%~p set "CONDA_BAT=%%~p"
	if defined CONDA_BAT (
		if not "%CONDA_BAT%"=="" (
			echo Activating via %CONDA_BAT% and starting uvicorn
			call "%CONDA_BAT%" activate %CONDA_ENV%
			python -m uvicorn main:app --host 127.0.0.1 --port %PORT%
		) else (
			echo conda.bat path empty, attempting conda run
			conda run -n %CONDA_ENV% python -m uvicorn main:app --host 127.0.0.1 --port %PORT%
		)
	) else (
		echo conda.bat not found in common locations, attempting conda run
		conda run -n %CONDA_ENV% python -m uvicorn main:app --host 127.0.0.1 --port %PORT%
	)
)

popd

endlocal
		echo package.json not found in frontend. Skipping frontend build.
