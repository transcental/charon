from slack_bolt.async_app import AsyncAck
from slack_sdk.web.async_client import AsyncWebClient

from charon.utils.logging import send_heartbeat
from charon.views.modals.new_program import get_new_program_modal


async def new_invite_program_cmd(ack: AsyncAck, body: dict, client: AsyncWebClient):
    await ack()
    user_id = body["user_id"]
    await send_heartbeat(f"registering new invite program - {user_id}")
    view = get_new_program_modal(user_id=user_id)
    await client.views_open(
        trigger_id=body["trigger_id"],
        view=view,
    )
