from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.security import verify_password, get_password_hash, create_access_token
from app.core.exceptions import FlowForgeException
from app.models.user import User, UserRole
from app.schemas.auth import UserRegister, UserLogin, Token, UserResponse
from app.repositories.user_repo import UserRepository

class AuthService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.user_repo = UserRepository(db)

    async def register(self, data: UserRegister) -> Token:
        existing = await self.user_repo.get_by_email(data.email)
        if existing:
            raise FlowForgeException("User with this email already exists", status_code=400)
        
        hashed = get_password_hash(data.password)
        user = User(
            email=data.email,
            hashed_password=hashed,
            full_name=data.full_name,
            role=data.role or UserRole.USER
        )
        created = await self.user_repo.create(user)
        token_str = create_access_token(created.id, role=created.role.value)
        return Token(access_token=token_str, user=UserResponse.model_validate(created))

    async def login(self, data: UserLogin) -> Token:
        user = await self.user_repo.get_by_email(data.email)
        if not user or not verify_password(data.password, user.hashed_password):
            raise FlowForgeException("Invalid email or password", status_code=401)
        if not user.is_active:
            raise FlowForgeException("User account is disabled", status_code=403)
        
        token_str = create_access_token(user.id, role=user.role.value)
        return Token(access_token=token_str, user=UserResponse.model_validate(user))
