from slack_bolt.async_app import AsyncAck
from slack_sdk.web.async_client import AsyncWebClient

from charon.env import env
from charon.events.buttons.approve_reject_program import approve_reject_program_btn
from charon.events.commands.new_program import new_invite_program_cmd
from charon.events.views.new_program import new_invite_program_modal

app = env.app


@app.command("/new-invite-program")
async def new_invite_program(ack: AsyncAck, client: AsyncWebClient, body: dict):
    await new_invite_program_cmd(ack, body, client)


@app.view("create_program_modal")
async def create_program_modal(ack: AsyncAck, body: dict, client: AsyncWebClient):
    await ack()
    await new_invite_program_modal(ack, body, client)


@app.action("approve_program")
@app.action("reject_program")
async def approve_reject_program(
    ack: AsyncAck, body: dict, client: AsyncWebClient, action: dict
):
    await ack()
    await approve_reject_program_btn(ack, body, client, action)
