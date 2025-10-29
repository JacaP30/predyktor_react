import os
import json
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv
import openai
import pandas as pd
from datetime import datetime
from starlette.middleware.gzip import GZipMiddleware

load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if OPENAI_API_KEY:
    openai.api_key = OPENAI_API_KEY
else:
    openai.api_key = None

app = FastAPI(title="Predyktor Półmaratonu API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# GZip compression for responses (reduces payload size over network)
app.add_middleware(GZipMiddleware, minimum_size=1000)


# Middleware dla CORS i kompresji


class UserText(BaseModel):
    text: str


@app.get("/")
async def root():
    """Główny endpoint API"""
    return {"status": "ok", "message": "Predyktor Półmaratonu API działa!", "version": "1.0.0"}


@app.get("/health")
async def health():
    return {"status": "healthy"}


@app.post('/test')
async def test_endpoint(user_text: UserText):
    """Prosty endpoint do testowania bez AI ani ML"""
    return {"message": "Test OK", "received": user_text.text}


def extract_user_data(user_input: str):
    """Wyciąga dane użytkownika. Zawsze próbuje lokalnego, odpornego parsera,
    a jeśli dostępny jest klucz OpenAI – dodatkowo próbuje LLM i w razie sukcesu zwraca jego wynik.
    """
    import re

    def local_parse(txt: str):
        text = (txt or '').strip()
        # Ujednolicenia: zamień przecinki w separatory słów, ale nie psuj MM:SS
        cleaned = re.sub(r",\s*", " ", text)

        name = None
        age = None
        birth_year = None
        gender = None
        time_5k_minutes = None

        # Imię: pierwsze słowo zaczynające się wielką literą (polskie litery dozwolone)
        for token in re.findall(r"[A-Za-zÀ-ÿĄąĆćĘęŁłŃńÓóŚśŹźŻż]+", cleaned):
            if token and token[0].isupper():
                name = token
                break

        # Czas 5km:
        # 1) Format MM:SS
        m = re.search(r"(\b\d{1,2})\s*[:;]\s*(\d{1,2})\b", cleaned)
        if m:
            mm = int(m.group(1))
            ss = int(m.group(2))
            if 0 <= ss < 60:
                time_5k_minutes = mm + ss / 60.0
        # 2) Liczba minut, np. "26.5 min" / "26,5 min" / "26 min"
        if time_5k_minutes is None:
            m2 = re.search(r"(\d+(?:[\.,]\d+)?)\s*(?:min|m)\b", cleaned, re.IGNORECASE)
            if m2:
                val = m2.group(1).replace(',', '.')
                try:
                    time_5k_minutes = float(val)
                except Exception:
                    time_5k_minutes = None

        # Wiek (np. "35 lat") lub rocznik (np. 1990)
        m_age = re.search(r"\b(\d{1,3})\s*lat\b", cleaned, re.IGNORECASE)
        if m_age:
            try:
                v = int(m_age.group(1))
                if 10 <= v <= 100:
                    age = v
            except Exception:
                pass
        if age is None:
            m_year = re.search(r"\b(19\d{2}|20\d{2})\b", cleaned)
            if m_year:
                try:
                    birth_year = int(m_year.group(1))
                    if 1900 < birth_year <= datetime.now().year:
                        age = datetime.now().year - birth_year
                except Exception:
                    pass

        # Heurystyka dla skróconych zapisów typu: "Jan 55 20" (wiek i czas w minutach)
        if age is None or time_5k_minutes is None:
            # Wyciągnij wszystkie liczby (poza MM:SS, już obsłużone) w kolejności wystąpień
            nums = [n.replace(',', '.') for n in re.findall(r"\b\d+(?:[\.,]\d+)?\b", cleaned)]
            # Jeśli mamy co najmniej jedną liczbę i brak wieku – pierwszą w zakresie 10-100 traktuj jako wiek
            if age is None:
                for n in nums:
                    try:
                        v = float(n)
                        if v.is_integer() and 10 <= int(v) <= 100:
                            age = int(v)
                            break
                    except Exception:
                        pass
            # Jeśli brak czasu i mamy jeszcze jakąś liczbę – weź pierwszą, która nie jest już użyta jako wiek/rocznik
            if time_5k_minutes is None:
                for n in nums:
                    try:
                        v = float(n)
                        if birth_year and int(v) == birth_year:
                            continue
                        if age and v == float(age):
                            continue
                        if v > 0:
                            time_5k_minutes = v
                            break
                    except Exception:
                        pass

        # Płeć z kontekstu lub z imienia
        low = cleaned.lower()
        if any(x in low for x in ['kob', 'ona', 'pani']):
            gender = 'K'
        elif any(x in low for x in ['męż', 'on ', 'pan ']):
            gender = 'M'
        elif name:
            n = name.lower()
            gender = 'K' if n.endswith('a') else 'M'

        return {
            'name': name or None,
            'age': age or None,
            'birth_year': birth_year or None,
            'gender': gender or None,
            'time_5k_minutes': time_5k_minutes or None
        }

    # Najpierw lokalny, odporny parser
    parsed = local_parse(user_input)

    # Następnie (opcjonalnie) LLM – jeśli zwróci sensowny JSON, nadpisz wynik
    if openai.api_key:
        try:
            response = openai.chat.completions.create(
                model="gpt-4",
                messages=[
                    {
                        "role": "system",
                        "content": f"""Jesteś ekspertem w analizie tekstu. Twoim zadaniem jest wyciągnięcie następujących informacji z podanego tekstu:\n1. Imię\n2. Wiek (w latach) lub rok urodzenia\n3. Płeć (M dla mężczyzny, K dla kobiety)\n4. Czas na 5km (w minutach, może być w formacie MM:SS lub jako liczba minut)\nZwróć odpowiedź w formacie JSON:\n{{\n  \"name\": \"imię lub null\",\n  \"age\": liczba_lat lub null,\n  \"birth_year\": rok_urodzenia lub null,\n  \"gender\": \"M\" lub \"K\" lub null,\n  \"time_5k_minutes\": liczba_minut lub null\n}}\nJeśli nie możesz określić płci z tekstu, spróbuj wywnioskować ją z imienia.\nJeśli podano czas w formacie MM:SS, przekonwertuj na minuty (np. 25:30 = 25.5).\nRok bieżący: {datetime.now().year}"""
                    },
                    {"role": "user", "content": f"Tekst użytkownika: {user_input}"},
                ],
                temperature=0.1,
                max_tokens=200,
                timeout=25,
            )
            content = response.choices[0].message.content
            if content:
                try:
                    llm = json.loads(content)
                    return {
                        'name': llm.get('name') or parsed.get('name'),
                        'age': llm.get('age') or parsed.get('age'),
                        'birth_year': llm.get('birth_year') or parsed.get('birth_year'),
                        'gender': llm.get('gender') or parsed.get('gender'),
                        'time_5k_minutes': llm.get('time_5k_minutes') or parsed.get('time_5k_minutes'),
                    }
                except Exception:
                    pass
        except Exception:
            pass

    return parsed


def infer_gender_from_name(name: str):
    try:
        if openai.api_key:
            response = openai.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "Jesteś ekspertem w rozpoznawaniu płci na podstawie imion. Zwróć tylko 'M' dla mężczyzny, 'K' dla kobiety lub 'NIEZNANA' jeśli nie możesz określić płci."},
                    {"role": "user", "content": f"Imię: {name}"},
                ],
                temperature=0.1,
                max_tokens=10,
                timeout=10,
            )
            val = (response.choices[0].message.content or '').strip().upper()
            return val if val in ['M', 'K'] else None
        else:
            if not name:
                return None
            n = name.strip().lower()
            # Prosta heurystyka: imiona kończące się na 'a' najczęściej żeńskie
            if n.endswith('a') or n.endswith('e'):
                return 'K'
            return 'M'
    except Exception:
        return None


def parse_time_5k(value):
    if value is None:
        return None
    try:
        v = float(value)
        return v if v > 0 else None
    except Exception:
        pass
    try:
        text = str(value).strip()
        if ':' in text:
            mm, ss = text.split(':')
            mm, ss = int(mm), int(ss)
            if mm >= 0 and 0 <= ss < 60:
                return mm + ss/60.0
    except Exception:
        return None
    return None


def format_time(seconds: float) -> str:
    seconds = float(seconds)
    h = int(seconds // 3600)
    m = int((seconds % 3600) // 60)
    s = int(seconds % 60)
    return f"{h:02d}:{m:02d}:{s:02d}"


# model path
MODEL_PATH = 'app_zad_dom_9_regressor'  # PyCaret expects name without .pkl extension

def load_model():
    """Załaduj wytrenowany model regresji PyCaret"""
    try:
        # Import PyCaret functions
        from pycaret.regression import load_model as pycaret_load_model

        # Najpierw spróbuj załadować model zapisany przez PyCaret po nazwie
        try:
            model = pycaret_load_model(MODEL_PATH)
            return model
        except Exception:
            # Spróbuj pliku .pkl obok pliku main.py
            alt = MODEL_PATH if MODEL_PATH.endswith('.pkl') else MODEL_PATH + '.pkl'
            alt_path = os.path.join(os.path.dirname(__file__), alt)
            if os.path.isfile(alt_path):
                try:
                    model = pycaret_load_model(alt_path)
                    return model
                except Exception as e:
                    print(f"Error loading model from .pkl: {e}")
                    return None
            else:
                print(f"Model not found: {alt_path}")
                return None
    except Exception as e:
        print(f"Error loading model: {e}")
        return None


def predict_half_marathon_time(model, gender, age, time_5k):
    """Przewiduj czas półmaratonu na podstawie danych użytkownika - używa PyCaret"""
    try:
        from pycaret.regression import predict_model as pycaret_predict_model
        
        # Oblicz rok urodzenia z wieku
        birth_year = datetime.now().year - age
        
        # Kodowanie płci: M=1, K=0 (zgodnie z treningiem)
        gender_encoded = 1 if gender == 'M' else 0
        
        # Przygotuj dane wejściowe zgodnie z formatem z notebooka
        # Model oczekuje: 'Średni Czas na 5 km', 'Rocznik', 'Płeć_LE'
        input_data = pd.DataFrame([{
            'Średni Czas na 5 km': time_5k,  # czas w sekundach
            'Rocznik': birth_year,
            'Płeć_LE': gender_encoded
        }])
        
        # Dokonaj predykcji używając PyCaret
        prediction_df = pycaret_predict_model(model, data=input_data)
        prediction = prediction_df['prediction_label'].iloc[0]
        
        return prediction
        
    except Exception as e:
        print(f"Error in prediction: {e}")
        return None


@app.post('/analyze')
async def analyze(user_text: UserText):
    text = (user_text.text or '').strip()
    if not text:
        return {"error": "Brak tekstu wejściowego"}

    data = extract_user_data(text)
    if not data:
        return {"error": "Nie udało się przetworzyć danych. Doprecyzuj treść."}

    name = data.get('name')
    age = data.get('age')
    birth_year = data.get('birth_year')
    gender = data.get('gender')
    time_5k = data.get('time_5k_minutes')

    if not age and birth_year:
        age = datetime.now().year - int(birth_year)
    if not gender and name:
        gender = infer_gender_from_name(name)

    t5_min = parse_time_5k(time_5k)

    missing = []
    if not name:
        missing.append('imię')
    if not age:
        missing.append('wiek')
    if not gender:
        missing.append('płeć')
    if t5_min is None:
        missing.append('czas na 5km (MM:SS lub minuty)')

    if missing:
        return {
            "error": (
                "Brakuje lub niepoprawne dane: "
                + ", ".join(missing)
            ),
            "data": data
        }

    # Ładuj model
    model = load_model()
    if model is None:
        # Zwróć przyjazny fallback zamiast błędu - umożliwia testowanie frontend bez modelu
        # Proste oszacowanie: tempo 5km -> przewidywany czas półmaratonu (21.0975 km)
        try:
            # użyj t5_min (minuty) - konwertuj na sekundy
            if t5_min is None:
                raise ValueError('Brak czasu 5km do obliczeń')
            time_5k_seconds_local = t5_min * 60.0
            pace_seconds_per_km = time_5k_seconds_local / 5.0
            predicted_time = pace_seconds_per_km * 21.0975 * 1.05  # dodaj 5% zapasu
        except Exception:
            return {"error": "Model niedostępny i nie można obliczyć fallbacku"}
        return {
            'name': name,
            'age': int(age) if age is not None else None,
            'birth_year': (datetime.now().year - int(age)) if age is not None else None,
            'gender': gender,
            'time_5k': float(t5_min) if t5_min is not None else 0.0,
            'predicted_time_seconds': float(predicted_time),
            'predicted_time_formatted': format_time(predicted_time),
            'note': 'Fallback prediction (model missing)'
        }
    
    # Konwersja czasu 5km na sekundy (już wiemy że t5_min nie jest None)
    time_5k_seconds = t5_min * 60 # type: ignore
    
    # Predykcja używając PyCaret (identycznie jak w Streamlit)
    predicted_time = predict_half_marathon_time(model, gender, age, time_5k_seconds)
    
    if predicted_time is None:
        return {"error": "Błąd podczas predykcji"}

    return {
        'name': name,
        'age': int(age), # type: ignore
        'birth_year': datetime.now().year - int(age), # type: ignore
        'gender': gender,
        'time_5k': float(t5_min) if t5_min is not None else 0.0,
        'predicted_time_seconds': float(predicted_time),
        'predicted_time_formatted': format_time(predicted_time),
    }


# API endpoints only - frontend będzie na Netlify
