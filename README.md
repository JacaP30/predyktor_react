# Predyktor Czasu Półmaratonu

Aplikacja wykorzystująca AI (GPT-4) i model uczenia maszynowego (PyCaret) do przewidywania czasu ukończenia półmaratonu na podstawie danych użytkownika.

## Architektura

- **Frontend**: React.js z responsywnym designem (Netlify)
- **Backend**: FastAPI z integracją OpenAI GPT-4 (Render)
- **Model ML**: PyCaret regressor (scikit-learn)
- **Deployment**: Netlify + Render

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
├── backend/                         # Backend dla Render
│   ├── main.py                      # FastAPI backend
│   ├── requirements.txt             # Zależności Python
│   ├── app_zad_dom_9_regressor.pkl  # Model ML
│   └── env.example                  # Przykład konfiguracji
├── frontend/                        # Frontend dla Netlify
│   ├── src/
│   │   ├── App.js                   # React komponent
│   │   ├── App.css                  # Stylowanie
│   │   └── images/background.png    # Obraz tła
│   ├── public/
│   │   └── _redirects               # SPA routing dla Netlify
│   └── package.json
├── netlify.toml                     # Konfiguracja Netlify
└── DEPLOY_NETLIFY_RENDER.md         # Instrukcja wdrożenia
```
\
## Wdrożenie

Zobacz szczegółową instrukcję wdrożenia na Netlify + Render w `DEPLOY_NETLIFY_RENDER.md`.

### Szybki start:
1. **Backend**: Wdróż na Render (Python, FastAPI)
2. **Frontend**: Wdróż na Netlify (React, automatyczny build)
3. **Konfiguracja**: Ustaw zmienne środowiskowe (OPENAI_API_KEY)
