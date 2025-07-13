from slack_bolt.async_app import AsyncAck
from slack_sdk.web.async_client import AsyncWebClient
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from charon.utils.cryptography import generate_api_key
from charon.utils.env import env
from charon.utils.models import Program


async def approve_reject_program_btn(
    ack: AsyncAck, body: dict, client: AsyncWebClient, action: dict
) -> None:
    """
    Approve a program based on the provided button click event.
    """
    action_id = action["action_id"]
    value = action["value"]
    approved = action_id == "approve_program"

    if approved:
        async with AsyncSession(env.db) as session:
            program = select(Program).where(Program.id == int(value))
            result = await session.execute(program)
            program = result.one()
            program.approved = True
            api_key = generate_api_key()
            program.api_key = api_key
            managers = await program.managers
            session.add(program)
            await session.commit()
            await session.refresh(program)

            for manager in [m.slack_id for m in managers]:
                await env.slack_client.chat_postMessage(
                    channel=manager.slack_id,
                    text=f":white_check_mark: Program *{program.name}* has been approved! :tada:\n\n"
                    f"Your API Key is below, keep it safe!"
                    f"`{api_key}`",
                )
