from enum import Enum

from piccolo.apps.migrations.auto.migration_manager import MigrationManager
from piccolo.columns.column_types import Varchar


ID = "2025-08-20T10:17:39:188801"
VERSION = "1.27.1"
DESCRIPTION = "Allow null program_id for direct joins"


async def forwards():
    manager = MigrationManager(
        migration_id=ID, app_name="charon", description=DESCRIPTION
    )

    manager.alter_column(
        table_class_name="Signup",
        tablename="signup",
        column_name="status",
        db_column_name="status",
        params={
            "default": "invited",
            "choices": Enum(
                "SignupStage",
                {
                    "INVITED": "invited",
                    "PROMOTED": "promoted",
                    "JOINED": "joined",
                    "DEACTIVATED": "deactivated",
                    "ERRORED": "errored",
                },
            ),
        },
        old_params={
            "default": "",
            "choices": Enum(
                "SignupStage",
                {
                    "INVITED": "invited",
                    "ACCEPTED": "accepted",
                    "JOINED": "joined",
                    "DEACTIVATED": "deactivated",
                },
            ),
        },
        column_class=Varchar,
        old_column_class=Varchar,
        schema=None,
    )

    return manager
