import pytest
import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.core.database import init_db
from app.core.broker import broker

@pytest.fixture(autouse=True)
async def setup_test_db():
    await init_db()
    await broker.connect()
    yield
    await broker.disconnect()