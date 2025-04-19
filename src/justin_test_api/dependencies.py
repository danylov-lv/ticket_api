from .db.base import sessionmanager


async def get_async_session():
    async with sessionmanager.session() as session:
        yield session
