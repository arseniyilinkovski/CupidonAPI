from sqlalchemy.ext.asyncio import AsyncSession

from src.auth.schemas import UserAdd
from src.database.models import Users


async def add_user_to_db(user_data: UserAdd, session: AsyncSession):
    user = Users(**user_data.dict())
    session.add(user)
    await session.commit()
    await session.refresh(user)
    return user
