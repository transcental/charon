import re

from slack_bolt.async_app import AsyncAck
from slack_sdk.web.async_client import AsyncWebClient
from sqlalchemy import select
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.ext.asyncio import AsyncSession

from charon.utils.config import config
from charon.utils.env import env
from charon.utils.logging import send_heartbeat
from charon.utils.models import Program
from charon.utils.models import User
from charon.utils.models import UserProgramLink
from charon.views.modals.new_program_submitted import get_new_program_submitted_modal


async def new_invite_program_modal(ack: AsyncAck, event: dict, client: AsyncWebClient):
    view = event["view"]
    values = view["state"]["values"]
    program_name = values["program_name"]["program_name"]["value"]
    program_managers = values["program_managers"]["program_managers"]["selected_users"]
    mcg_channels = values["mcg_channels"]["mcg_channels"]["selected_channels"]
    full_channels = values["full_channels"]["full_channels"]["selected_channels"]
    webhook = values["webhook"]["webhook"]["value"]
    checkboxes = values["checkboxes"]["checkboxes"]["selected_options"]
    xoxc_token = values["xoxc_token"]["xoxc_token"]["value"]
    xoxd_token = values["xoxd_token"]["xoxd_token"]["value"]
    docs_read = "docs" in [c["value"] for c in checkboxes]
    verification_required = "verification" in [c["value"] for c in checkboxes]

    user_id = event["user"]["id"]
    errors = {}

    if not program_name:
        errors["program_name"] = "Program name is required."
    if not program_managers:
        errors["program_managers"] = "At least one program manager is required."
    elif user_id not in program_managers:
        errors["program_managers"] = "You must be a program manager."
    if not mcg_channels:
        errors["mcg_channels"] = "At least one MCG channel is required."
    if not full_channels:
        errors["full_channels"] = "At least one full channel is required."
    if not webhook:
        errors["webhook"] = "Webhook URL is required."
    if not re.match(
        r"https?:\/\/(www\.)?[-a-zA-Z0-9@:%._\+~#=]{1,256}\.[a-zA-Z0-9()]{1,6}\b([-a-zA-Z0-9()@:%_\+.~#?&//=]*)",
        webhook,
    ):
        errors["webhook"] = "Invalid webhook URL format."
    if xoxc_token and not xoxd_token:
        errors["xoxd_token"] = "XOXD token is required if XOXC token is provided."
    if xoxd_token and not xoxc_token:
        errors["xoxc_token"] = "XOXC token is required if XOXD token is provided."
    if not docs_read:
        errors["checkboxes"] = (
            "You must read the documentation before creating a program."
        )

    if errors:
        await ack(response_action="errors", errors=errors)
        return

    program = Program(
        name=program_name,
        mcg_channels=mcg_channels,
        full_channels=full_channels,
        webhook=webhook,
        xoxc_token=xoxc_token or None,
        xoxd_token=xoxd_token or None,
        verification_required=verification_required,
        approved=False,
    )
    async with AsyncSession(env.db) as session:
        session.add(program)
        await session.commit()
        await session.refresh(program)

        for manager_slack_id in program_managers:
            stmt = insert(User).values(slack_id=manager_slack_id)
            stmt = stmt.on_conflict_do_nothing(index_elements=["slack_id"])
            await session.execute(stmt)

            stmt = select(User).where(User.slack_id == manager_slack_id)
            result = await session.execute(stmt)
            user = result.scalar_one()

            stmt = insert(UserProgramLink).values(
                user_id=user.id, program_id=program.id
            )
            stmt = stmt.on_conflict_do_nothing(index_elements=["user_id", "program_id"])
            await session.execute(stmt)

        program_id = program.id
        await session.commit()

        await send_heartbeat(
            f":neodog_nom_stick: New program created: {program_name} (ID: {program_id})",
            client=client,
        )
        new_view = get_new_program_submitted_modal()
        await ack(
            {
                "response_action": "update",
                "view": new_view,
            }
        )
        text = f"""
New program created: *{program_name}* (ID: {program_id})
Managers: {", ".join(f"<@{manager_slack_id}>" for manager_slack_id in program_managers)}
MCG Channels: {", ".join(f"<#{channel}>" for channel in mcg_channels)}
Full Channels: {", ".join(f"<#{channel}>" for channel in full_channels)}
Verification Required: {"Yes" if verification_required else "No"}
Webhook: {webhook}
Custom User: {"Yes" if xoxc_token and xoxd_token else "No"}
        """
        blocks = [
            {"type": "section", "text": {"type": "mrkdwn", "text": text}},
            {"type": "divider"},
            {
                "type": "actions",
                "elements": [
                    {
                        "type": "button",
                        "text": {"type": "plain_text", "text": "Approve"},
                        "style": "primary",
                        "action_id": "approve_program",
                        "value": str(program_id),
                    },
                    {
                        "type": "button",
                        "text": {"type": "plain_text", "text": "Reject"},
                        "style": "danger",
                        "action_id": "reject_program",
                        "value": str(program_id),
                    },
                ],
            },
        ]
        await client.chat_postMessage(
            channel=config.slack.applications_channel,
            blocks=blocks,
            text=f"New program created: {program_name}",
        )
