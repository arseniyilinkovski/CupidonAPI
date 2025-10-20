from fastapi import HTTPException
from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from src.database.models import Scopes, UserScopeLink


async def create_scope(session: AsyncSession, name: str, desc: str):
    existing = await session.scalar(
        select(Scopes).where(Scopes.name == name)
    )
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Скоуп уже существует"
        )
    new_scope = Scopes(name=name, description=desc)
    session.add(new_scope)
    await session.commit()
    return {
        "message": f"Скоуп {name} добавлен"
    }


async def assign_scopes_to_user(session: AsyncSession, scopes_names: list[str], user_id: int):
    for scope_name in scopes_names:
        scope = await session.scalar(
            select(Scopes).where(Scopes.name == scope_name)
        )
        if not scope:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Скоуп {scope_name} не найден"
            )
        existing_link = await session.scalar(
            select(UserScopeLink).where(
                UserScopeLink.user_id == user_id,
                UserScopeLink.scope_id == scope.id
            )
        )
        if existing_link:
            return {
                "message": f"Скоуп {scope_name} уже назначен"
            }
        link = UserScopeLink(user_id=user_id, scope_id=scope.id)
        session.add(link)
    await session.commit()


async def remove_scopes_from_user(session: AsyncSession, user_id: int, scopes_names: list[str]):
    for scope_name in scopes_names:
        scope = await session.scalar(select(Scopes).where(Scopes.name == scope_name))
        if not scope:
            raise HTTPException(status_code=404, detail="Скоуп не найден")

        await session.execute(
            delete(UserScopeLink).where(
                UserScopeLink.user_id == user_id,
                UserScopeLink.scope_id == scope.id
            )
        )
        await session.commit()
        return {"message": f"Скоуп '{scope_name}' удалён у пользователя {user_id}"}


async def get_user_scopes(session: AsyncSession, user_id: int) -> list[str]:
    result = await session.scalars(
        select(Scopes.name).join(UserScopeLink).where(UserScopeLink.user_id == user_id)
    )
    return list(result)




