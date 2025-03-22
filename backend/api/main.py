from fastapi import FastAPI
from backend.api.routes import chatbot

app = FastAPI()

app.include_router(chatbot.router, prefix="/api")

@app.get("/")
def root():
    return {"message": "Welcome to Azure AI Search RAG Chatbot"}



