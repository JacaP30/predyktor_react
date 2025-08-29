# Predyktor Czasu Półmaratonu

Aplikacja do przewidywania czasu ukończenia półmaratonu na podstawie danych wprowadzonych przez użytkownika.

## Technologie

- **Frontend:** React, CSS
- **Backend:** FastAPI, Python
- **AI:** GPT-4 (OpenAI)
- **ML:** PyCaret, joblib

## Funkcjonalności

- 🤖 Analiza tekstu przez GPT-4
- 🏃‍♂️ Przewidywanie czasu półmaratonu
- 📱 Responsywny design
- 🎯 Walidacja danych

## Deployment na Netlify

### Automatyczny deployment:

1. **Połącz z GitHub:**
   - Wgraj kod do repozytorium GitHub
   - Połącz Netlify z repozytorium

2. **Konfiguracja Netlify:**
   - Build command: `cd frontend && npm install && npm run build`
   - Publish directory: `frontend/build`

3. **Zmienne środowiskowe:**
   ```
   REACT_APP_API_BASE=https://your-backend-url.herokuapp.com
   NODE_VERSION=18
   ```

### Backend deployment (Heroku/Railway):

1. **Przygotuj backend:**
   ```bash
   pip install -r backend/requirements.txt
   ```

2. **Dodaj Procfile:**
   ```
   web: uvicorn backend.main:app --host 0.0.0.0 --port $PORT
   ```

3. **Zmienne środowiskowe backendu:**
   ```
   OPENAI_API_KEY=your_openai_key
   PORT=8000
   ```

## Rozwój lokalny

```bash
# Backend
cd backend
pip install -r requirements.txt
python ../run_server.py

# Frontend
cd frontend
npm install
npm start
```

## Struktura projektu

```
├── backend/
│   ├── main.py
│   └── requirements.txt
├── frontend/
│   ├── src/
│   ├── public/
│   └── package.json
├── model/
│   └── app_zad_dom_9_regressor.pkl
└── netlify.toml
```
