from typing import Annotated

from fastapi import Depends
from fastapi import HTTPException
from fastapi.security import HTTPAuthorizationCredentials
from fastapi.security import HTTPBearer

from charon.db.tables import Program

security = HTTPBearer()


async def check_auth(
    credentials: Annotated[HTTPAuthorizationCredentials, Depends(security)],
) -> Program:
    """
    Check if the provided credentials are valid.
    """
    program = (
        await Program.objects()
        .where(Program.api_key == credentials.credentials)
        .first()
    )
    if not program:
        raise HTTPException(status_code=401, detail="Invalid API key")
    return program
