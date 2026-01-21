from fastapi import FastAPI, WebSocket
from src.api.websocket import websocket_endpoint

app = FastAPI(title="DevMind AI API")

@app.websocket("/ws/{repo_id}")
async def ws_repo_updates(websocket: WebSocket, repo_id: str):
    await websocket_endpoint(websocket, repo_id)

@app.get("/health")
def health_check():
    return {"status": "ok"}
