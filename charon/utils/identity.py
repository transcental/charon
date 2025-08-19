from enum import Enum

from charon.env import env


class VerificationStatus(Enum):
    NOT_FOUND = "not_found"
    NEEDS_SUBMISSION = "needs_submission"
    PENDING = "pending"
    REJECTED = "rejected"
    VERIFIED_ELIGIBLE = "verified_eligible"
    VERIFIED_BUT_OVER_18 = "verified_but_over_18"

    def __str__(self):
        return self.value

    @classmethod
    def from_string(cls, value: str):
        for status in cls:
            if status.value == value:
                return status
        raise ValueError(f"Unknown VerificationStatus: {value}")


async def check_identity(slack_id: str) -> VerificationStatus:
    api_endpoint = (
        f"https://identity.hackclub.com/api/external/check?slack_id={slack_id}"
    )

    async with env.http.get(api_endpoint) as response:
        if response.status != 200:
            raise Exception(f"Failed to check identity: {response.status}")

        data = await response.json()
        if not data.get("ok", False):
            raise Exception(f"Identity API error: {data.get('error', 'Unknown error')}")

        status = data.get("result")
        if not status:
            return VerificationStatus.NOT_FOUND

        return VerificationStatus.from_string(status)
