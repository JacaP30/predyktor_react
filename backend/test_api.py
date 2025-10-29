from fastapi.testclient import TestClient
import main

client = TestClient(main.app)

print('GET /health ->', client.get('/health').json())
print('POST /test ->', client.post('/test', json={'text':'test'}).json())
print('POST /analyze ->', client.post('/analyze', json={'text':'Marek, 35 lat, czas na 5km: 22:45'}).json())
