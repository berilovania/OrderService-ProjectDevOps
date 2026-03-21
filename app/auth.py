import os

from fastapi import HTTPException, Security
from fastapi.security import APIKeyHeader

API_KEY = os.getenv("API_KEY", "")

api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)


async def require_api_key(key: str | None = Security(api_key_header)):
    if not API_KEY:
        return
    if key != API_KEY:
        raise HTTPException(status_code=401, detail="Invalid or missing API key")
