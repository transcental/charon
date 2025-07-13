import enum

from piccolo.columns import Boolean
from piccolo.columns import ForeignKey
from piccolo.columns import JSON
from piccolo.columns import LazyTableReference
from piccolo.columns import M2M
from piccolo.columns import Serial
from piccolo.columns import Varchar
from piccolo.table import Table


class SignupStage(enum.Enum):
    INVITED = "invited"
    ACCEPTED = "accepted"
    JOINED = "joined"
    DEACTIVATED = "deactivated"


class Person(Table):
    id = Serial(primary_key=True)
    slack_id = Varchar(index=True, unique=True)
    admin = Boolean(default=False)

    programs = M2M(LazyTableReference("PersonProgramLink", module_path=__name__))


class Program(Table):
    id = Serial(primary_key=True)
    name = Varchar(index=True)
    mcg_channels = JSON(default=list)
    full_channels = JSON(default=list)
    verification_required = Boolean(default=False)
    webhook = Varchar(index=True)
    approved = Boolean(default=False)
    xoxc_token = Varchar(null=True)
    xoxd_token = Varchar(null=True)
    api_key = Varchar(null=True)

    managers = M2M(LazyTableReference("PersonProgramLink", module_path=__name__))


class PersonProgramLink(Table):
    user_id = ForeignKey(Person)
    program_id = ForeignKey(Program)


class Settings(Table):
    id = Serial(primary_key=True)
    global_verification = Boolean(default=False)


class Signup(Table):
    id = Serial(primary_key=True)
    slack_id = Varchar(null=True)
    status = Varchar(choices=SignupStage, index=True)
    email = Varchar(index=True, unique=True)
    ip = Varchar(null=True, index=True)
    program_id = ForeignKey(Program)
