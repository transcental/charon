from sqlalchemy import make_url
from sqlalchemy.ext.asyncio import create_async_engine

from charon.utils.config import config


async def connect():
    """
    Return an SQLAlchemy async engine.
    """

    connection_string = make_url(config.database_url.encoded_string())
    connection_string = connection_string.set(drivername="postgresql+asyncpg")

    return create_async_engine(connection_string)
