import os
import json
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv
import openai
import pandas as pd
from datetime import datetime
from joblib import load as joblib_load
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class UserText(BaseModel):
    text: str


def extract_user_data(user_input: str):
    try:
        response = openai.chat.completions.create(
            model="gpt-4",
            messages=[
                {
                    "role": "system",
                    "content": f"""Jesteś ekspertem w analizie tekstu. Twoim zadaniem jest wyciągnięcie następujących informacji z podanego tekstu:\n1. Imię\n2. Wiek (w latach) lub rok urodzenia\n3. Płeć (M dla mężczyzny, K dla kobiety)\n4. Czas na 5km (w minutach, może być w formacie MM:SS lub jako liczba minut)\nZwróć odpowiedź w formacie JSON:\n{{\n  \"name\": \"imię lub null\",\n  \"age\": liczba_lat lub null,\n  \"birth_year\": rok_urodzenia lub null,\n  \"gender\": \"M\" lub \"K\" lub null,\n  \"time_5k_minutes\": liczba_minut lub null\n}}\nJeśli nie możesz określić płci z tekstu, spróbuj wywnioskować ją z imienia.\nJeśli podano czas w formacie MM:SS, przekonwertuj na minuty (np. 25:30 = 25.5).\nRok bieżący: {datetime.now().year}"""
                    
                },
                {
                    "role": "user",
                    "content": f"Tekst użytkownika: {user_input}"
                },
            ],
            temperature=0.1,
            max_tokens=200,
            timeout=25,
        )
        content = response.choices[0].message.content
        if not content:
            return None
        return json.loads(content)
    except Exception:
        return None


def infer_gender_from_name(name: str):
    try:
        response = openai.chat.completions.create(
            model="gpt-4",
            messages=[
                {
                    "role": "system",
                    "content": "Jesteś ekspertem w rozpoznawaniu płci na podstawie imion. Zwróć tylko 'M' dla mężczyzny, 'K' dla kobiety lub 'NIEZNANA' jeśli nie możesz określić płci. Bierz pod uwagę imiona z różnych kultur i języków."
                    
                },
                {"role": "user", "content": f"Imię: {name}"},
            ],
            temperature=0.1,
            max_tokens=10,
            timeout=10,
        )
        val = (response.choices[0].message.content or '').strip().upper()
        return val if val in ['M', 'K'] else None
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


# model
MODEL_PATH = os.path.join(
    os.path.dirname(__file__), 'app_zad_dom_9_regressor.pkl'
)
model = joblib_load(os.path.abspath(MODEL_PATH))


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

    # przygotowanie wektora cech jak w treningu:
    # ['Średni Czas na 5 km', 'Rocznik', 'Płeć_LE']
    birth_year_calc = (
        int(birth_year)
        if birth_year
        else (datetime.now().year - int(age))
    )
    plec_le = 1 if str(gender).upper().startswith('M') else 0
    
    # Używamy pandas DataFrame (wymagane przez model PyCaret)
    X = pd.DataFrame([{
        'Średni Czas na 5 km': float(t5_min) * 60.0 if t5_min is not None else 0.0,
        'Rocznik': int(birth_year_calc),
        'Płeć_LE': int(plec_le)
    }])

    pred_seconds = float(model.predict(X)[0])
    return {
        'name': name,
        'age': int(age),
        'birth_year': birth_year_calc,
        'gender': gender,
        'time_5k': float(t5_min) if t5_min is not None else 0.0,
        'predicted_time_seconds': pred_seconds,
        'predicted_time_formatted': format_time(pred_seconds),
    }

# serwowanie builda React gdy istnieje
BUILD_DIR = os.path.abspath(
    os.path.join(os.path.dirname(__file__), '..', 'frontend', 'build')
)
if os.path.isdir(BUILD_DIR):
    app.mount('/', StaticFiles(directory=BUILD_DIR, html=True), name='static')

    @app.get('/{full_path:path}')
    async def serve_react(full_path: str):
        index_path = os.path.join(BUILD_DIR, 'index.html')
        if os.path.isfile(index_path):
            return FileResponse(index_path)
        return {"status": "ok"}
