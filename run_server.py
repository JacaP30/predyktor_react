#!/usr/bin/env python
import os
import sys

# Dodaj katalog backend do ścieżki
backend_path = os.path.join(os.path.dirname(__file__), 'backend')
sys.path.insert(0, backend_path)

# Zmień katalog roboczy na backend
os.chdir(backend_path)

# Importuj i uruchom aplikację
from main import app
import uvicorn

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8010, reload=True)  # Zmienione na port 8010
