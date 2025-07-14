from fastapi.responses import JSONResponse

from charon.db.tables import Person
from charon.env import env


async def health():
    try:
        await env.slack_client.api_test()
        slack_healthy = True
    except Exception:
        slack_healthy = False

    try:
        await Person.objects().first()
        db_healthy = True
    except Exception:
        db_healthy = False

    return JSONResponse(
        content={
            "healthy": slack_healthy,
            "slack": slack_healthy,
            "database": db_healthy,
        }
    )
