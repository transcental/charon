from piccolo.engine import engine_finder
from piccolo.engine import PostgresEngine


async def connect():
    """
    Open a connection to the database.
    """
    engine = engine_finder()
    if engine is None:
        raise ValueError("No engine found. Please check your configuration.")
    if not isinstance(engine, PostgresEngine):
        raise ValueError("The engine is not a PostgresEngine instance.")
    await engine.start_connection_pool()


async def disconnect():
    """
    Close the connection to the database.
    """
    engine = engine_finder()
    if engine is None:
        raise ValueError("No engine found. Please check your configuration.")
    if not isinstance(engine, PostgresEngine):
        raise ValueError("The engine is not a PostgresEngine instance.")
    await engine.close_connection_pool()
