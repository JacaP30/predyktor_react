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

## Deployment na DigitalOcean App Platform

### Automatyczny deployment:

1. **Wejdź na DigitalOcean:**
   - [cloud.digitalocean.com/apps](https://cloud.digitalocean.com/apps)
   - Kliknij "Create App"

2. **Konfiguracja źródła:**
   - Wybierz GitHub
   - Wybierz repo `predyktor_react`
   - Branch: `main`

3. **Ustawienia aplikacji:**
   - **Backend:**
     - Source Directory: `backend-deploy`
     - Build Command: `pip install -r requirements.txt`
     - Run Command: `uvicorn main:app --host 0.0.0.0 --port $PORT`
     - HTTP Port: 8080
   
   - **Frontend:**
     - Source Directory: `frontend`
     - Build Command: `npm install && npm run build`
     - Output Directory: `build`

4. **Zmienne środowiskowe:**
   ```
   OPENAI_API_KEY=your_openai_key
   PORT=8080
   ```

### Alternatywnie - Docker deployment:

```bash
# Build i push do DigitalOcean Container Registry
doctl registry create your-registry
docker build -t your-registry/backend ./backend-deploy
docker push your-registry/backend
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
