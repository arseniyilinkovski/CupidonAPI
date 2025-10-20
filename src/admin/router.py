from fastapi import APIRouter, Depends, Request, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from src.admin.service import add_admin_to_db, get_admin_promote_link_service
from src.auth.dependencies import get_async_session
from src.auth.service import get_current_user
from src.auth.utils import send_confirmation_email

admin_router = APIRouter()


@admin_router.get("/promote-admin")
async def promote_admin(request: Request, session: AsyncSession = Depends(get_async_session)):
    token = request.query_params.get("token")
    if not token:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Токена нет"
        )
    return await add_admin_to_db(token, session)


@admin_router.get("/promote-admin-link")
async def get_promote_admin_token(user=Depends(get_current_user)):
    return await get_admin_promote_link_service(user["user"])


