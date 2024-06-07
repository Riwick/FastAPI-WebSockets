import select
import uvicorn

from fastapi import Depends, FastAPI, WebSocket, WebSocketDisconnect
from fastapi.templating import Jinja2Templates
from fastapi import Request
from fastapi.middleware.cors import CORSMiddleware

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from database import get_async_session
from models import Message
from utils import manager

app = FastAPI(debug=True)


origins = [
    "http://127.0.0.1:8000"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)


templates = Jinja2Templates(directory="templates")


@app.get("/")
async def get(request: Request):
    return templates.TemplateResponse(request=request, name="chat.html")


@app.get("/last_messages")
async def get_last_messages(session: AsyncSession = Depends(get_async_session)):
    query = select(Message).order_by(Message.id.desc()).limit(5)
    result = await session.execute(query)
    messages = result.all()
    messages_lst = [msg[0].as_dict() for msg in messages]
    return messages_lst


@app.websocket("/ws/{client_id}")
async def websocket_endpoint(websocket: WebSocket, client_id: int):
    await manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            await manager.broadcast(f"Client #{client_id} says: {data}", add_to_db=True)
    except WebSocketDisconnect:
        manager.disconnect(websocket)
        await manager.broadcast(f"Client #{client_id} left the chat", add_to_db=False)


if __name__ == "__main__":
    uvicorn.run("app:app", reload=True)
