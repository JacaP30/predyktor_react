import React, { useState } from 'react';
import './App.css';

function App() {
  const [userInput, setUserInput] = useState('');
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);
  const [loading, setLoading] = useState(false);

  // Konfiguracja API dla różnych środowisk
  const getApiBase = () => {
    if (process.env.NODE_ENV === 'production') {
  // When frontend is served from the backend use same origin (relative paths).
  // If you need external API host, set REACT_APP_API_BASE in build env.
  return process.env.REACT_APP_API_BASE || '';
    }
    return process.env.REACT_APP_API_BASE || 'http://localhost:8010';
  };

  const API_BASE = getApiBase();

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!userInput.trim()) {
      setError('Proszę podać informacje o sobie!');
      return;
    }

    setLoading(true);
    setError(null);
    setResult(null);

    try {
      const controller = new AbortController();
      const timeoutId = setTimeout(() => controller.abort(), 25000);

      const response = await fetch(`${API_BASE}/analyze`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
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
      <div className="container">
        <h1>🏃‍♂️ Predyktor Czasu Półmaratonu</h1>
        
        <div className="info-box">
          <h3>Opowiedz o sobie, żeby uzyskać prawdopodobny czas ukończenia półmaratonu:</h3>
          <p><strong>Podaj następujące informacje w dowolnej formie:</strong></p>
          <ul>
            <li><strong>Imię</strong>, <strong>Wiek</strong>, <strong>Czas na 5km</strong>, <strong>Płeć</strong> (jeśli chcesz)</li>
          </ul>
          <p><strong>Przykłady:</strong></p>
          <ul>
            <li>"Nazywam się Kasia, urodziłam się w 1990 roku, biegam 5 km w 26.5 minuty"</li>
            <li>"Jestem Anna, mam 28 lat i biegam 5 km w 24 minuty"</li>
            <li>"Marek, 35 lat, czas na 5km: 22:45"</li>
            <li>Możesz też po prostu "Janek 75 25" 😉</li>
          </ul>
        </div>

        <form onSubmit={handleSubmit} className="form">
          <textarea
            value={userInput}
            onChange={(e) => setUserInput(e.target.value)}
            placeholder="Napisz coś o sobie..."
            className="input-field"
            rows="4"
          />
          <button 
            type="submit" 
            disabled={loading || !userInput.trim()}
            className="submit-button"
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
