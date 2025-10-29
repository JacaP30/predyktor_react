# Wdrożenie na Netlify (Frontend) + Render (Backend)

## Przegląd architektury

- **Frontend (React)**: Netlify
- **Backend (FastAPI)**: Render
- **Model ML**: PyCaret (wbudowany w backend)

## Krok 1: Przygotowanie repozytorium

### Struktura po czyszczeniu:
```
predyktor_react/
├── frontend/                 # React app dla Netlify
│   ├── src/
│   ├── public/
│   ├── package.json
│   └── build/               # Zostanie zbudowany przez Netlify
├── backend/                 # FastAPI app dla Render
│   ├── main.py
│   ├── requirements.txt
│   ├── app_zad_dom_9_regressor.pkl
│   └── env.example
├── netlify.toml            # Konfiguracja Netlify
└── README.md
```

## Krok 2: Wdrożenie Backendu na Render

### 2.1 Przygotowanie
1. Przejdź na [render.com](https://render.com)
2. Zaloguj się i połącz z GitHub

### 2.2 Tworzenie nowego Web Service
1. Kliknij **"New +"** → **"Web Service"**
2. Połącz repozytorium GitHub
3. Wybierz repozytorium `predyktor_react`

### 2.3 Konfiguracja Render
```
Name: predyktor-backend
Environment: Python 3
Build Command: pip install -r backend/requirements.txt
Start Command: cd backend && gunicorn main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:$PORT
```

### 2.4 Zmienne środowiskowe
W sekcji **Environment Variables** dodaj:
```
OPENAI_API_KEY = your_actual_openai_api_key_here
```

### 2.5 Ustawienia zaawansowane
- **Auto-Deploy**: Yes (dla automatycznych aktualizacji)
- **Plan**: Free (dla testów) lub Starter ($7/miesiąc dla produkcji

### 2.6 Wdrożenie
1. Kliknij **"Create Web Service"**
2. Render automatycznie zbuduje i wdroży aplikację
3. Po zakończeniu otrzymasz URL: `https://predyktor-backend.onrender.com`

## Krok 3: Wdrożenie Frontendu na Netlify

### 3.1 Przygotowanie
1. Przejdź na [netlify.com](https://netlify.com)
2. Zaloguj się i połącz z GitHub

### 3.2 Tworzenie nowego site
1. Kliknij **"New site from Git"**
2. Wybierz **"GitHub"** i autoryzuj
3. Wybierz repozytorium `predyktor_react`

### 3.3 Konfiguracja Netlify
Netlify automatycznie wykryje ustawienia z `netlify.toml`:
```
Build command: npm install && npm run build
Publish directory: frontend/build
Base directory: frontend
```

### 3.4 Zmienne środowiskowe (opcjonalne)
W **Site settings** → **Environment variables**:
```
REACT_APP_API_BASE = https://predyktor-backend.onrender.com
```

### 3.5 Wdrożenie
1. Kliknij **"Deploy site"**
2. Netlify automatycznie zbuduje i wdroży frontend
3. Po zakończeniu otrzymasz URL: `https://your-site-name.netlify.app`

## Krok 4: Testowanie

### 4.1 Test backendu
```bash
curl https://predyktor-backend.onrender.com/health
# Powinno zwrócić: {"status": "healthy"}
```

### 4.2 Test frontendu
1. Otwórz URL Netlify w przeglądarce
2. Wprowadź przykładowe dane:
   ```
   "Nazywam się Jan, mam 30 lat, biegam 5km w 25 minut"
   ```
3. Sprawdź czy otrzymujesz przewidywany czas półmaratonu

## Krok 5: Konfiguracja CORS (jeśli potrzebna)

Jeśli wystąpią problemy z CORS, backend już ma skonfigurowane:
```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

## Krok 6: Monitoring i logi

### Render (Backend)
- **Logs**: Dashboard → Web Service → Logs
- **Metrics**: CPU, Memory, Response time
- **Uptime**: Monitor dostępności

### Netlify (Frontend)
- **Deploy logs**: Dashboard → Deploys
- **Analytics**: Włącz w ustawieniach
- **Functions**: Jeśli dodasz serverless functions

## Rozwiązywanie problemów

### Backend nie startuje
1. Sprawdź logi w Render
2. Upewnij się, że `requirements.txt` zawiera wszystkie zależności
3. Sprawdź czy model `app_zad_dom_9_regressor.pkl` jest w folderze `backend/`

### Frontend nie łączy się z backendem
1. Sprawdź URL API w `frontend/src/App.js`
2. Sprawdź czy backend jest dostępny: `https://predyktor-backend.onrender.com/health`
3. Sprawdź CORS w logach przeglądarki

### Model ML nie działa
1. Sprawdź czy plik `.pkl` jest w `backend/`
2. Sprawdź logi backendu w Render
3. Upewnij się, że PyCaret jest zainstalowany

## Koszty

### Render (Backend)
- **Free tier**: 750h/miesiąc, sleep po 15min bezczynności
- **Starter**: $7/miesiąc, zawsze online

### Netlify (Frontend)
- **Free tier**: 100GB bandwidth, 300 build minutes
- **Pro**: $19/miesiąc dla większych projektów

## Aktualizacje

### Automatyczne
- Oba serwisy mają włączone auto-deploy z GitHub
- Push do `main` branch automatycznie wdraża zmiany

### Ręczne
- **Render**: Dashboard → Manual Deploy
- **Netlify**: Dashboard → Trigger Deploy

## Bezpieczeństwo

1. **API Keys**: Nigdy nie commituj kluczy do repozytorium
2. **Environment Variables**: Używaj zmiennych środowiskowych
3. **HTTPS**: Oba serwisy używają HTTPS automatycznie
4. **CORS**: Backend ma skonfigurowane CORS dla wszystkich domen

## Następne kroki

1. Skonfiguruj domenę niestandardową (opcjonalne)
2. Dodaj monitoring i alerty
3. Skonfiguruj CI/CD pipeline
4. Dodaj testy automatyczne
5. Zoptymalizuj wydajność (caching, CDN)
