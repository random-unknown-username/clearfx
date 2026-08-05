import secrets
from passlib.context import CryptContext
from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import Header, HTTPException, Depends
from .models import Creator
from .database import get_db

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_api_key(api_key: str) -> str:
    return pwd_context.hash(api_key)

def verify_api_key_hash(plain_api_key: str, hashed_api_key: str) -> bool:
    return pwd_context.verify(plain_api_key, hashed_api_key)

def generate_api_key() -> str:
    return "cfx_" + secrets.token_urlsafe(32)

async def get_current_creator(x_api_key: str = Header(None), db: AsyncSession = Depends(get_db)) -> Creator:
    if not x_api_key:
        raise HTTPException(status_code=401, detail="API Key missing")
        
    result = await db.execute(select(Creator))
    creators = result.scalars().all()
    for creator in creators:
        if verify_api_key_hash(x_api_key, creator.api_key_hash):
            return creator
            
    raise HTTPException(status_code=401, detail="Invalid API Key")
