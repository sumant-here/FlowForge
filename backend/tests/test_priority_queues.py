import pytest
from app.core.broker import broker, Priority

@pytest.mark.asyncio
async def test_priority_queue_consumption_order():
    # Clear queue first
    while await broker.consume_one("queue.low", timeout=0.01):
        pass
    
    await broker.publish_job("queue.low", {"id": "prio_low"}, priority=Priority.LOW)
    await broker.publish_job("queue.low", {"id": "prio_crit"}, priority=Priority.CRITICAL)
    await broker.publish_job("queue.low", {"id": "prio_high"}, priority=Priority.HIGH)

    first = await broker.consume_one("queue.low")
    second = await broker.consume_one("queue.low")
    third = await broker.consume_one("queue.low")

    assert first["id"] == "prio_crit"
    assert second["id"] == "prio_high"
    assert third["id"] == "prio_low"