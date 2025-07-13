def get_new_program_submitted_modal() -> dict:
    return {
        "type": "modal",
        "title": {"type": "plain_text", "text": "Program Submitted"},
        "close": {"type": "plain_text", "text": "Close"},
        "blocks": [
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": "*Program successfully submitted!*\n\nYou'll get a DM when your program is approved with your API key and other details. For now, please read the documentation on GitHub and get your server and onboarding flow set up",
                },
            }
        ],
    }
