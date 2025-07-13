import enum
from typing import List

from sqlmodel import Column
from sqlmodel import Enum
from sqlmodel import Field
from sqlmodel import JSON
from sqlmodel import Relationship
from sqlmodel import SQLModel


class UserProgramLink(SQLModel, table=True):
    user_id: int | None = Field(default=None, foreign_key="user.id", primary_key=True)
    program_id: int | None = Field(
        default=None, foreign_key="program.id", primary_key=True
    )


class User(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    slack_id: str = Field(index=True, unique=True)
    admin: bool = Field(default=False)

    programs: list["Program"] = Relationship(
        back_populates="users", link_model=UserProgramLink
    )


class Program(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    name: str = Field(index=True)
    mcg_channels: List[str] = Field(default_factory=list, sa_column=Column(JSON))
    full_channels: List[str] = Field(default_factory=list, sa_column=Column(JSON))
    verification_required: bool = Field(default=False)
    webhook: str = Field(index=True)
    approved: bool = Field(default=False)
    xoxc_token: str | None = None
    xoxd_token: str | None = None
    api_key: str | None = None

    users: list[User] = Relationship(
        back_populates="programs", link_model=UserProgramLink
    )
    signups: list["Signup"] = Relationship(back_populates="program")


class Settings(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    global_verification: bool = Field(default=False)


class SignupStage(enum.Enum):
    INVITED = "invited"
    ACCEPTED = "accepted"
    PROMOTED = "promoted"
    DEACTIVATED = "deactivated"


class Signup(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    slack_id: str | None
    status: SignupStage = Field(
        sa_column=Column(Enum(SignupStage), nullable=False, index=True)
    )
    email: str = Field(index=True, unique=True)
    ip: str | None = Field(default=None, index=True)

    program_id: int = Field(foreign_key="program.id")
    program: Program = Relationship(back_populates="signups")
