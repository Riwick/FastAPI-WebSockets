from typing import Callable
from fastapi import WebSocket
from sqlalchemy import insert

from models import Message
from database import async_session_factory


class ConnectionManager:
    def __init__(self):
        self.active_connections: list[WebSocket] = []

    @staticmethod
    async def add_messages_to_db(message: str, async_session_factory: Callable):
        async with async_session_factory() as session:
            stmt = insert(Message).values(message=message)
            await session.execute(stmt)
            await session.commit()

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def send_personal_message(self, message: str, websocket: WebSocket):
        await websocket.send_text(message)

    async def broadcast(self, message: str, add_to_db: bool):
        if add_to_db:
            await ConnectionManager.add_messages_to_db(message, async_session_factory)

        for connection in self.active_connections:
            await connection.send_text(message)


manager = ConnectionManager()
