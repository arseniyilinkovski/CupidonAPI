from fastapi import HTTPException
from jose import jwt, JWTError
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from src.admin.utils import generate_admin_promotion_token
from src.auth.utils import send_confirmation_email
from src.config import settings
from src.database.models import Users, Scopes, UserScopeLink


async def add_admin_to_db(token: str, session: AsyncSession):
    try:

        payload = jwt.decode(token, settings.get_secret_key(), settings.get_algorithm())
        user_id = int(payload.get("sub"))
        scope = payload.get("scope")
        if scope != "admin":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Invalid scope"
            )
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid token"
        )
    user = await session.scalar(
        select(Users).where(Users.id == user_id)
    )
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Пользователь не найден"
        )

    admin_scope = await session.scalar(
        select(Scopes).where(Scopes.name == "admin")
    )
    print(admin_scope.id)
    if not admin_scope:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Admin scope not found"
        )

    scopes = await session.scalars(
        select(UserScopeLink).where(
            UserScopeLink.user_id == user_id,
            UserScopeLink.scope_id == admin_scope.id
        )
    )
    print(list(scopes))
    # if scopes:
    #     return {
    #         "message": "Пользователь уже админ"
    #     }

    link = UserScopeLink(user_id=user_id, scope_id=admin_scope.id)
    session.add(link)
    await session.commit()
    return {
        "message": f"User {user.email} promoted to admin"
    }


async def get_admin_promote_link_service(user):
    token = generate_admin_promotion_token(user.id)
    await send_confirmation_email(
        user.email,
        token,
        "Стать администратором",
        "Чтобы стать администратором, перейдите по ссылке",
        "/admin/promote-admin"
    )
    return {
        "message": "Дальнейшие указания отправлены на почту"
    }
