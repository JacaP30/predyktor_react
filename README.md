# Predyktor Czasu Półmaratonu

Aplikacja wykorzystująca AI (GPT-4) i model uczenia maszynowego (PyCaret) do przewidywania czasu ukończenia półmaratonu na podstawie danych użytkownika.

## Architektura

- **Frontend**: React.js z responsywnym designem
- **Backend**: FastAPI z integracją OpenAI GPT-4
- **Model ML**: PyCaret regressor (scikit-learn)
- **Deployment**: DigitalOcean App Platform

## Funkcje

1. **Analiza tekstu naturalnego**: GPT-4 wyciąga dane użytkownika z dowolnego tekstu
2. **Przewidywanie**: Model ML przewiduje czas półmaratonu na podstawie:
   - Wieku/roku urodzenia
   - Płci
   - Czasu na 5km
3. **Interface**: Przyjazny interface w języku polskim

## Uruchomienie lokalne

### Backend
```bash
cd backend
conda activate kurs_ai  # Wymagane środowisko conda
pip install -r requirements.txt
uvicorn main:app --host 127.0.0.1 --port 8010 --reload
```

### Frontend (development)
```bash
cd frontend
npm install
npm start
```

### Production (Full Stack)
```bash
# Opcja 1: Użyj skryptu batch (Windows - automatycznie aktywuje środowisko)
start_prod.bat

# Opcja 2: Użyj Python script (wymaga ręcznej aktywacji środowiska)
conda activate kurs_ai
python run_server.py

# Opcja 3: Zbuduj frontend i uruchom backend
cd frontend && npm run build && cd ..
conda activate kurs_ai && python run_server.py
```

## Konfiguracja

- **Backend**: `.env` z kluczem OpenAI
- **Frontend**: `.env` z adresem API (localhost:8010)
- **Production**: `.env.production` z adresem produkcyjnym

## Struktura plików

```
├── backend/
│   ├── main.py                      # FastAPI backend
│   ├── requirements.txt             # Zależności Python
│   ├── app_zad_dom_9_regressor.pkl  # Model ML
│   └── .env                         # Konfiguracja backend
├── frontend/
│   ├── src/
│   │   ├── App.js                   # React komponent
│   │   ├── App.css                  # Stylowanie
│   │   └── images/background.png    # Obraz tła
│   ├── build/                       # Zbudowana aplikacja
│   ├── .env                         # Konfiguracja frontend (dev)
│   ├── .env.production              # Konfiguracja frontend (prod)
│   └── package.json
├── run_server.py                    # Skrypt uruchomieniowy
├── start_prod.bat                   # Skrypt Windows
└── struktura.txt                    # Dokumentacja struktury
```
\
## Wdrożenie

Zobacz instrukcję wdrożenia na DigitalOcean w `DEPLOY_DIGITALOCEAN.md` i krótką instrukcję w `README_DEPLOY.md`.

Plik `Dockerfile` w repo tworzy wielostopniowy obraz (buduje frontend i instaluje backend). Możesz zbudować obraz lokalnie i wypchnąć do DockerHub, a następnie użyć DigitalOcean App Platform do jego uruchomienia.
