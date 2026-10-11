import asyncio
import json
from typing import AsyncGenerator, Dict, Any, List

class EventBroadcaster:
    """In-memory event hub for Server-Sent Events (SSE) broadcasting to Caregiver UI"""
    def __init__(self):
        self._subscribers: List[asyncio.Queue] = []

    def subscribe(self) -> asyncio.Queue:
        q = asyncio.Queue()
        self._subscribers.append(q)
        return q

    def unsubscribe(self, q: asyncio.Queue) -> None:
        if q in self._subscribers:
            self._subscribers.remove(q)

    async def broadcast(self, event_data: Dict[str, Any]) -> None:
        dead_queues = []
        for q in self._subscribers:
            try:
                await q.put(event_data)
            except Exception:
                dead_queues.append(q)
        for dq in dead_queues:
            self.unsubscribe(dq)

    async def stream_events(self) -> AsyncGenerator[str, None]:
        q = self.subscribe()
        try:
            while True:
                data = await q.get()
                yield f"data: {json.dumps(data)}\n\n"
        except asyncio.CancelledError:
            pass
        finally:
            self.unsubscribe(q)

broadcaster = EventBroadcaster()
