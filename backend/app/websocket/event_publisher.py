from app.websocket.connection_manager import ws_manager
from app.core.redis_client import redis_client

class EventPublisher:
    @staticmethod
    async def publish(event_type: str, data: dict):
        """Publishes real-time telemetry events to both local WebSockets and Redis Pub/Sub."""
        await ws_manager.broadcast(event_type, data)
        await redis_client.publish("flowforge_events", {"event": event_type, "data": data})

event_publisher = EventPublisher()
