import base64
import json

from fastapi import Depends, HTTPException, Request

from backend.app.core.config import settings


def get_current_user(request: Request) -> dict:
    if settings.auth_dev_bypass and not settings.is_production:
        return {"id": "dev-user", "name": "Developer", "email": "dev@local"}

    principal = request.headers.get("X-MS-CLIENT-PRINCIPAL")
    if not principal:
        raise HTTPException(status_code=401, detail="Not authenticated")

    try:
        decoded = base64.b64decode(principal)
        return json.loads(decoded)
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid authentication token")
