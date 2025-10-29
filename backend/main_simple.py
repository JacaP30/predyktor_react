from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

app = FastAPI(title="Simple Test API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class UserText(BaseModel):
    text: str

@app.get("/")
async def root():
    return {"message": "Simple API works!"}

@app.get("/health")
async def health():
    return {"status": "healthy"}

@app.post('/analyze')
async def analyze(user_text: UserText):
    return {
        "message": f"Received: {user_text.text}",
        "status": "success"
    }
