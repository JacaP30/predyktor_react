import React, { useCallback, useMemo, useState } from 'react';
import './App.css';

const STORAGE_MODE = 'predyktor_mode';
const STORAGE_KEY = 'predyktor_openai_api_key';

const DEMO_SAMPLE_RESULT = {
  name: 'Anna',
  age: 32,
  gender: 'K',
  time_5k: 26.5,
  predicted_time_formatted: '01:58:42',
};

function getApiBase() {
  if (process.env.NODE_ENV === 'production') {
    return process.env.REACT_APP_API_BASE || 'https://predyktor-react.onrender.com';
  }
  return process.env.REACT_APP_API_BASE || 'http://localhost:8010';
}

function readStoredAppMode() {
  try {
    const mode = localStorage.getItem(STORAGE_MODE);
    const key = localStorage.getItem(STORAGE_KEY);
    if (mode === 'demo') {
      return { needsSetup: false, isDemo: true, apiKey: null };
    }
    if (mode === 'live' && key && key.trim()) {
      return { needsSetup: false, isDemo: false, apiKey: key.trim() };
    }
  } catch {
    /* ignore */
  }
  return { needsSetup: true, isDemo: false, apiKey: null };
}

function looksLikeOpenAiKey(key) {
  const s = (key || '').trim();
  if (s.length < 20) return false;
  return /^sk-[a-zA-Z0-9_-]+$/.test(s);
}

function App() {
  const API_BASE = useMemo(() => getApiBase(), []);

  const initial = useMemo(() => readStoredAppMode(), []);
  const [needsSetup, setNeedsSetup] = useState(initial.needsSetup);
  const [isDemo, setIsDemo] = useState(initial.isDemo);
  const [apiKey, setApiKey] = useState(initial.apiKey || '');

  const [userInput, setUserInput] = useState('');
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);
  const [loading, setLoading] = useState(false);

  const [setupKeyInput, setSetupKeyInput] = useState('');
  const [setupError, setSetupError] = useState(null);
  const [setupValidating, setSetupValidating] = useState(false);

  const persistLiveMode = useCallback((key) => {
    const k = key.trim();
    localStorage.setItem(STORAGE_MODE, 'live');
    localStorage.setItem(STORAGE_KEY, k);
    setApiKey(k);
    setIsDemo(false);
    setNeedsSetup(false);
    setSetupError(null);
    setSetupKeyInput('');
  }, []);

  const chooseDemo = useCallback(() => {
    try {
      localStorage.setItem(STORAGE_MODE, 'demo');
      localStorage.removeItem(STORAGE_KEY);
    } catch {
      /* ignore */
    }
    setApiKey('');
    setIsDemo(true);
    setNeedsSetup(false);
    setSetupError(null);
    setSetupKeyInput('');
    setResult(null);
    setError(null);
  }, []);

  const openSetupAgain = useCallback(() => {
    try {
      localStorage.removeItem(STORAGE_MODE);
      localStorage.removeItem(STORAGE_KEY);
    } catch {
      /* ignore */
    }
    setNeedsSetup(true);
    setIsDemo(false);
    setApiKey('');
    setResult(null);
    setError(null);
    setSetupKeyInput('');
    setSetupError(null);
  }, []);

  const validateKeyOnServer = useCallback(
    async (key) => {
      const res = await fetch(`${API_BASE}/validate-openai-key`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ api_key: key.trim() }),
      });
      if (!res.ok) {
        throw new Error(
          res.status === 404
            ? 'Serwer nie obsługuje walidacji klucza (zaktualizuj backend).'
            : `Błąd serwera: ${res.status}`,
        );
      }
      const data = await res.json();
      if (!data.valid) {
        throw new Error(data.error || 'Nieprawidłowy klucz API.');
      }
    },
    [API_BASE],
  );

  const handleSetupSubmit = async (e) => {
    e.preventDefault();
    const raw = setupKeyInput.trim();
    setSetupError(null);

    if (!looksLikeOpenAiKey(raw)) {
      setSetupError(
        'Nieprawidłowy format klucza. Klucz OpenAI zwykle zaczyna się od sk- i zawiera tylko znaki alfanumeryczne, myślniki i podkreślenia.',
      );
      return;
    }

    setSetupValidating(true);
    try {
      await validateKeyOnServer(raw);
      persistLiveMode(raw);
    } catch (err) {
      setSetupError(err.message || 'Walidacja nie powiodła się.');
    } finally {
      setSetupValidating(false);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (isDemo) return;
    if (!userInput.trim()) {
      setError('Proszę podać informacje o sobie!');
      return;
    }

    setLoading(true);
    setError(null);
    setResult(null);

    try {
      const controller = new AbortController();
      const timeoutId = setTimeout(() => controller.abort(), 60000);

      const headers = {
        'Content-Type': 'application/json',
      };
      if (apiKey) {
        headers['X-OpenAI-API-Key'] = apiKey;
      }

      const response = await fetch(`${API_BASE}/analyze`, {
        method: 'POST',
        headers,
        body: JSON.stringify({ text: userInput }),
        signal: controller.signal,
      });

      clearTimeout(timeoutId);

      if (!response.ok) {
        throw new Error(`Błąd serwera: ${response.status}`);
      }

      const data = await response.json();

      if (data.error) {
        setError(data.error);
      } else {
        setResult(data);
      }
    } catch (err) {
      if (err.name === 'AbortError') {
        setError('Przekroczono limit czasu. Spróbuj ponownie.');
      } else {
        setError(`Błąd połączenia: ${err.message}`);
      }
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="App">
      {needsSetup && (
        <div className="setup-overlay" role="dialog" aria-modal="true" aria-labelledby="setup-title">
          <div className="setup-card">
            <h2 id="setup-title">Wybierz sposób korzystania</h2>
            <p className="setup-intro">
              Aby uruchomić analizę z ulepszeniami OpenAI (LLM), podaj swój klucz API. Możesz też wejść w tryb demo —
              zobaczysz interfejs i przykładowy wynik, bez wysyłania danych do analizy.
            </p>
            <form onSubmit={handleSetupSubmit} className="setup-form">
              <label htmlFor="openai-key" className="setup-label">
                Klucz API OpenAI
              </label>
              <input
                id="openai-key"
                type="password"
                autoComplete="off"
                className="setup-input"
                value={setupKeyInput}
                onChange={(ev) => setSetupKeyInput(ev.target.value)}
                placeholder="sk-..."
                disabled={setupValidating}
              />
              {setupError && <p className="setup-error">{setupError}</p>}
              <button type="submit" className="setup-primary" disabled={setupValidating || !setupKeyInput.trim()}>
                {setupValidating ? 'Sprawdzam klucz…' : 'Zapisz klucz i kontynuuj'}
              </button>
            </form>
            <button type="button" className="setup-secondary" onClick={chooseDemo} disabled={setupValidating}>
              Tryb demo (tylko podgląd)
            </button>
          </div>
        </div>
      )}

      <div className="container">
        <div className="top-bar">
          {isDemo ? (
            <span className="mode-badge mode-badge-demo">Tryb demo</span>
          ) : (
            <span className="mode-badge mode-badge-live">Pełna funkcja</span>
          )}
          {!needsSetup && (
            <button type="button" className="link-button" onClick={openSetupAgain}>
              Zmień tryb / klucz
            </button>
          )}
        </div>

        <h1>🏃‍♂️ Predyktor Czasu Półmaratonu</h1>

        {isDemo && (
          <div className="demo-banner">
            <strong>Tryb demo:</strong> przycisk analizy jest wyłączony. Poniżej znajduje się przykładowy wynik — po
            podaniu klucza API w ustawieniach startowych odblokujesz prawdziwą analizę.
          </div>
        )}

        <div className="info-box">
          <h3>Opowiedz o sobie, żeby uzyskać prawdopodobny czas ukończenia półmaratonu:</h3>
          <p>
            <strong>Podaj następujące informacje w dowolnej formie:</strong>
          </p>
          <ul>
            <li>
              <strong>Imię</strong>, <strong>Wiek</strong>, <strong>Czas na 5km</strong>, <strong>Płeć</strong> (jeśli
              chcesz)
            </li>
          </ul>
          <p>
            <strong>Przykłady:</strong>
          </p>
          <ul>
            <li>&quot;Nazywam się Kasia, urodziłam się w 1990 roku, biegam 5 km w 26.5 minuty&quot;</li>
            <li>&quot;Jestem Anna, mam 28 lat i biegam 5 km w 24 minuty&quot;</li>
            <li>&quot;Marek, 35 lat, czas na 5km: 22:45&quot;</li>
            <li>Możesz też po prostu &quot;Janek 75 25&quot; 😉</li>
          </ul>
        </div>

        <form onSubmit={handleSubmit} className="form">
          <textarea
            value={userInput}
            onChange={(e) => setUserInput(e.target.value)}
            placeholder="Napisz coś o sobie..."
            className="input-field"
            rows="4"
            readOnly={isDemo}
            disabled={isDemo}
          />
          <button
            type="submit"
            disabled={loading || !userInput.trim() || isDemo}
            className="submit-button"
            title={isDemo ? 'Włącz pełną funkcję, podając klucz API przy starcie' : ''}
          >
            {loading ? '🔍 Analizuję...' : '🔍 Analizuj i przewiduj czas półmaratonu'}
          </button>
        </form>

        {error && (
          <div className="error">
            <h3>❌ Błąd:</h3>
            <p>{error}</p>
          </div>
        )}

        {isDemo && !result && (
          <div className="result demo-sample">
            <p className="demo-sample-label">Przykładowy wynik (nie pochodzi z Twojego wpisu):</p>
            <h2>🔍 Dane wyciągnięte przez AI:</h2>
            <div className="data-grid">
              <div className="data-item">
                <strong>Imię:</strong> {DEMO_SAMPLE_RESULT.name}
              </div>
              <div className="data-item">
                <strong>Wiek:</strong> {DEMO_SAMPLE_RESULT.age} lat
              </div>
              <div className="data-item">
                <strong>Płeć:</strong> {DEMO_SAMPLE_RESULT.gender === 'M' ? 'Mężczyzna' : 'Kobieta'}
              </div>
              <div className="data-item">
                <strong>Czas 5km:</strong> {DEMO_SAMPLE_RESULT.time_5k} min
              </div>
            </div>
            <div className="prediction">
              <h2>🏃‍♂️ Przewidywany czas półmaratonu:</h2>
              <div className="predicted-time">{DEMO_SAMPLE_RESULT.predicted_time_formatted}</div>
            </div>
          </div>
        )}

        {result && (
          <div className="result">
            <h2>🔍 Dane wyciągnięte przez AI:</h2>
            <div className="data-grid">
              <div className="data-item">
                <strong>Imię:</strong> {result.name}
              </div>
              <div className="data-item">
                <strong>Wiek:</strong> {result.age} lat
              </div>
              <div className="data-item">
                <strong>Płeć:</strong> {result.gender === 'M' ? 'Mężczyzna' : 'Kobieta'}
              </div>
              <div className="data-item">
                <strong>Czas 5km:</strong> {result.time_5k} min
              </div>
            </div>

            <div className="prediction">
              <h2>🏃‍♂️ Przewidywany czas półmaratonu:</h2>
              <div className="predicted-time">{result.predicted_time_formatted}</div>
            </div>

            <div className="motivation">
              <p>💪 Powodzenia w treningu! Pamiętaj, że regularne treningi są kluczem do sukcesu.</p>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

export default App;
