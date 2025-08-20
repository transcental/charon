from dataclasses import dataclass
from datetime import datetime
from datetime import timedelta
from datetime import timezone
from io import BytesIO

import numpy as np

from charon.db.tables import Person
from charon.db.tables import Program
from charon.db.tables import Signup
from charon.utils.bucky import upload_file
from charon.utils.graphs.stacked_bar import generate_stacked_bar_chart
from charon.utils.time import is_day

STATUS_COLOURS = {
    "invited": "#FFAB00",
    "joined": "#36C5F0",
    "promoted": "#2EB67D",
    "deactivated": "#E01E5A",
    "errored": "#FF4500",
    "unknown": "#A0A0A0",
}


@dataclass
class ProgramStats:
    name: str
    count: int
    stages: dict[str, int]

    def __str__(self):
        return f"{self.name}: {self.count}"

    def __repr__(self):
        return self.__str__()


async def generate_pie(
    signups: list[Signup], programs: list[Program], is_daytime: bool, days: int = 0
) -> str:
    if days:
        cutoff = datetime.now() - timedelta(days=days)
        signups = [s for s in signups if s.created_at >= cutoff]
    program_stats: list[ProgramStats] = []

    for signup in signups:
        if signup.program_id is None:
            program_name = "Other"
        else:
            program = next((p for p in programs if p.id == signup.program_id), None)
            if not program:
                continue
            program_name = program.name

        stage = (signup.status or "Unknown").lower()

        existing = next((ps for ps in program_stats if ps.name == program_name), None)
        if existing:
            existing.count += 1
            existing.stages[stage] = existing.stages.get(stage, 0) + 1
        else:
            new_stats = ProgramStats(name=program_name, count=1, stages={stage: 1})
            program_stats.append(new_stats)

    all_statuses = sorted(
        {stage for ps in program_stats for stage in ps.stages.keys()},
    )
    status_colours = [STATUS_COLOURS.get(status, "#A0A0A0") for status in all_statuses]

    program_names = [ps.name for ps in program_stats]
    x = np.arange(len(program_names))
    y = []
    for status in all_statuses:
        y.append([ps.stages.get(status, 0) for ps in program_stats])
    y = np.array(y)

    fig = generate_stacked_bar_chart(
        x=x,
        y=y,
        labels=program_names,
        text_colour="black" if is_daytime else "white",
        bg_colour="#FFFFFF" if is_daytime else "#181A1E",
        categories=[status.capitalize() for status in all_statuses],
        colours=status_colours,
        x_axis_label="Programs",
        title=f"User Signups by program{' in the last ' + str(days) + ' days' if days else ''}",
    )

    b = BytesIO()
    fig.savefig(
        b, bbox_inches="tight", pad_inches=0.1, dpi=300, transparent=False, format="png"
    )

    url = await upload_file(
        file=b.getvalue(),
        filename="join_status.png",
        content_type="image/png",
    )

    return (
        url
        or "https://hc-cdn.hel1.your-objectstorage.com/s/v3/888f292372d8450449b41dd18767812c72518449_binoculars.png"
    )


async def render_stats(user: Person | None, tz: timezone):
    is_daytime = is_day(tz)

    signups = await Signup.objects()
    programs = await Program.objects()

    all_time = await generate_pie(
        signups=signups, programs=programs, is_daytime=is_daytime
    )
    week = await generate_pie(
        signups=signups, programs=programs, is_daytime=is_daytime, days=7
    )

    return [
        {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": ":rac_graph: here's some stats on user signups by program! these charts show the number of users who have signed up through each program, both all-time and in the last week. you can use this info to help out in the hack club slack.",
            },
        },
        {
            "type": "image",
            "title": {
                "type": "plain_text",
                "text": "User Signups by Program",
                "emoji": True,
            },
            "image_url": all_time,
            "alt_text": "All-time user signups by program"
            if "cat" in all_time
            else "looks like pat's scrounging around for those signups",
        },
        {
            "type": "image",
            "title": {
                "type": "plain_text",
                "text": "User Signups by Program (Last Week)",
                "emoji": True,
            },
            "image_url": week,
            "alt_text": "User signups by program in the last week"
            if "cat" in week
            else "looks like pat's scrounging around for those signups",
        },
    ]
