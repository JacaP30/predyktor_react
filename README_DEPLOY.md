## Deploy guide (short)

1. Build frontend locally (optional):
   cd frontend && npm ci && npm run build

2. Build Docker image and run locally:
   docker build -t <DOCKERHUB_USER>/predyktor:latest .
   docker run -p 8010:8010 --env PORT=8010 <DOCKERHUB_USER>/predyktor:latest

3. Push to DockerHub and deploy to DigitalOcean App Platform or any container host.

Notes:
- If PyCaret import fails in image due to native libs, consider using a conda-based image and installing dependencies via conda-forge.
