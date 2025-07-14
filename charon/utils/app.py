from typing import Annotated

from fastapi import Depends
from fastapi import FastAPI
from fastapi import Request
from fastapi.security import HTTPAuthorizationCredentials
from slack_bolt.adapter.fastapi.async_handler import AsyncSlackRequestHandler

from charon.config import config
from charon.env import env
from charon.routes import check_auth
from charon.routes import health
from charon.routes import invite_user
from charon.routes import security
from charon.routes import UserInviteRequest
from charon.utils.slack import app as slack_app

req_handler = AsyncSlackRequestHandler(slack_app)

app = FastAPI(
    debug=True if config.environment != "production" else False,
    lifespan=env.enter,
)


@app.post("/slack/events")
async def slack_events(req: Request):
    return await req_handler.handle(req)


@app.get("/health")
async def health_route():
    return await health()


@app.post("/user/invite")
async def user_invite(
    credentials: Annotated[HTTPAuthorizationCredentials, Depends(security)],
    req: UserInviteRequest,
):
    program = await check_auth(credentials)
    return await invite_user(req, program)
