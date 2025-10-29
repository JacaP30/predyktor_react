Instrukcja instalacji środowiska dla backendu

Założenia
- System: Windows (instrukcje poniżej są dla PowerShell / Anaconda/Miniconda)
- Masz zainstalowany conda (miniconda/anaconda) lub mamba

Kroki (zalecane: użyj conda-forge dla PyCaret)

1) Utwórz środowisko conda (mamba zalecane dla szybkości):

PowerShell:

```powershell
# jeśli masz mamba
mamba env create -f ..\environment.yml -n predyktor
# lub conda
conda env create -f ..\environment.yml -n predyktor
```

2) Aktywuj środowisko:

```powershell
conda activate predyktor
```

3) Zainstaluj zależności Pythona z pliku backend/requirements.txt (pip):

```powershell
pip install -r backend\requirements.txt
```

Uwaga: PyCaret instaluje sporo pakietów, łącznie z zależnościami natywnymi. Jeśli instalacja PyCaret zgłasza błędy, spróbuj zainstalować najpierw część zależności przez conda:

```powershell
conda install -c conda-forge pycaret
# lub jeśli chcesz kontrolować wersje:
# conda install -c conda-forge pycaret=3.3.2
```

4) (Opcjonalnie) Jeśli pojawi się błąd związany z `_sqlite3` lub brakującą biblioteką DLL:
- Upewnij się, że używasz conda/miniconda (konkretna dystrybucja Pythona zawiera sqlite DLL)
- Możesz spróbować:

```powershell
conda install -c anaconda sqlite
conda install -c conda-forge libsqlite
```

5) Plik .env i klucz OpenAI
- Jeśli chcesz używać funkcji OpenAI, stwórz plik `backend/.env` z zawartością:

```
OPENAI_API_KEY=sk-...
```

6) Uruchom serwer backend i frontend

Backend (z katalogu projektu):

```powershell
python .\run_server.py
```

Frontend (w trybie deweloperskim):

```powershell
Set-Location frontend
npm install
npm start
```

Troubleshooting
- Jeśli `uvicorn` natychmiast się zamyka przy starcie i logi nie pokazują błędu: spróbuj uruchomić aplikację bez reloadera z katalogu `backend`:

```powershell
Set-Location backend
python -m uvicorn main:app --host 127.0.0.1 --port 8010
```

- Jeśli PyCaret zgłasza błędy importu binarek: rozważ instalację przez conda (conda-forge) lub użycie środowiska Docker z przygotowanym obrazem.

Jeśli chcesz, mogę wygenerować plik `environment.yml` bardziej kompletny (z pakietami specyficznymi dla PyCaret) lub przygotować skrypt PowerShell, który automatyzuje instalację i wskazuje dokładne wersje pakietów.
