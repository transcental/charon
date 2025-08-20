import logging

import pytz

from charon.db.tables import Person
from charon.env import env
from charon.views.home.components import navbar
from charon.views.home.components.stats import render_stats

logger = logging.getLogger(__name__)


async def get_dashboard_view(user: Person | None, slack_id: str):
    tz_string = "Europe/London"
    user_info = await env.slack_client.users_info(user=slack_id)
    slack_user = user_info.get("user", {})

    tz_string = slack_user.get("tz", "Europe/London")
    tz = pytz.timezone(tz_string)
    stats = await render_stats(user, tz)

    btns = navbar.get_buttons(user, "dashboard")
    logger.info(
        f"Generating dashboard view for user {slack_id} with timezone {tz_string}"
    )
    return {
        "type": "home",
        "blocks": [
            {
                "type": "header",
                "text": {
                    "type": "plain_text",
                    "text": ":rac_cute: slack joins!",
                    "emoji": True,
                },
            },
            btns,
            {"type": "divider"},
            *stats,
        ],
    }
