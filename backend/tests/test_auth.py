import pytest
import time
from app.core.database import AsyncSessionLocal
from app.services.auth_service import AuthService
from app.schemas.auth import UserRegister, UserLogin

@pytest.mark.asyncio
async def test_register_and_login():
    async with AsyncSessionLocal() as session:
        auth_service = AuthService(session)
        
        email = f"test_{int(time.time() * 1000)}@flowforge.dev"
        # Register
        reg_data = UserRegister(email=email, password="securePassword123!", full_name="Test User")
        token_res = await auth_service.register(reg_data)
        assert token_res.access_token is not None
        assert token_res.user.email == email

        # Login
        login_data = UserLogin(email=email, password="securePassword123!")
        login_res = await auth_service.login(login_data)
        assert login_res.access_token is not None