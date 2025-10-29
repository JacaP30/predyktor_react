# Wdrożenie na DigitalOcean App Platform (Docker)

Poniżej znajduje się prosty przewodnik jak wdrożyć tę aplikację na DigitalOcean App Platform używając obrazu Docker zbudowanego z repo.

1. Przygotowania lokalne
   - Upewnij się, że projekt działa lokalnie (backend + frontend):
     - Backend: `cd backend && conda activate predyktor && pip install -r requirements.txt && python -m uvicorn main:app --host 127.0.0.1 --port 8010`
     - Frontend: `cd frontend && npm install && npm run build`

2. Docker
   - Obraz jest zdefiniowany w `Dockerfile` w repozytorium (multi-stage: buduje frontend i instaluje backend).
   - Aby zbudować obraz lokalnie:

```bash
docker build -t <DOCKERHUB_USER>/predyktor:latest .
```

   - Aby przetestować obraz lokalnie:

```bash
docker run -p 8010:8010 --env PORT=8010 <DOCKERHUB_USER>/predyktor:latest
```

3. Push do DockerHub (albo innego rejestru)

```bash
docker login
docker push <DOCKERHUB_USER>/predyktor:latest
```

4. DigitalOcean App Platform
   - Zaloguj się do DigitalOcean.
   - Stwórz nową aplikację (Create App) i wybierz "Container Registry/Repository" lub "Dockerfile in GitHub".
   - Jako image podaj `docker.io/<DOCKERHUB_USER>/predyktor:latest` lub wskaż repo i branch z Dockerfile.
   - Ustaw port aplikacji na `8010`.
   - Dodaj zmienne środowiskowe w panelu (np. `OPENAI_API_KEY`).
   - Wybierz plan (najmniejszy dev droplet powinien wystarczyć do testów).

5. Ustawienia dodatkowe
   - Mount dla statycznych plików nie jest wymagany (frontend jest wbudowany w obraz).
   - Jeśli model PyCaret jest duży i chcesz go załadować, rozważ użycie wolumenu lub hostowanego miejsca na pliki (Spaces) i modyfikację aplikacji, by pobierała model przy starcie.

6. Logi i debug
   - Użyj DigitalOcean Console -> Logs, by przeglądać output uvicorn.
   - Jeżeli musisz uruchomić migrations lub jednorazowe taski, użyj `doctl` albo terminala w panelu.

7. CI/CD (opcjonalne)
   - W pliku `.github/workflows/deploy.yml` jest prosty workflow budujący i wypychający obraz do DockerHub przy push na `main`. Dodaj `DOCKERHUB_USERNAME` i `DOCKERHUB_TOKEN` do repo secrets.

8. Uwagi dotyczące PyCaret i zależności native
   - PyCaret wymaga więcej zależności i czasami lepiej jest budować obraz na bazie `continuumio/miniconda3` i instalować pakiety conda-forge, jeśli pojawią się problemy z binarkami (np. sqlite). Jeśli zauważysz błędy importu `_sqlite3`, rozważ zmianę bazy obrazu i instalację `sqlite`/`libsqlite3` przez apt oraz instalację PyCaret przez conda w Dockerfile.

