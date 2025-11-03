import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import status
from unittest.mock import AsyncMock, patch
from src.database.models import Users
from sqlalchemy import select, delete, text
from sqlalchemy.exc import IntegrityError


@patch("src.auth.service.send_confirmation_email", new_callable=AsyncMock)
@patch("src.auth.service.create_access_token", return_value="mocked_token")
@patch("src.auth.service.assign_scopes_to_user", new_callable=AsyncMock)
@patch("src.auth.service.get_user_scopes", return_value=["user:read"])
@pytest.mark.asyncio
async def test_successful_registration(
    mock_scopes,
    mock_assign,
    mock_token,
    mock_email,
    client: AsyncClient,
    test_db_session: AsyncSession
):
    email = "newuser@example.com"

    await test_db_session.execute(delete(Users).where(Users.email == email))
    await test_db_session.commit()

    payload = {
        "email": email,
        "password": "securepassword123"
    }

    response = await client.post("/auth/reg", json=payload)

    assert response.status_code == status.HTTP_200_OK, response.text
    data = response.json()
    assert data["JWT-токен"] == "mocked_token"
    assert data["user"]["email"] == email


@pytest.mark.asyncio
async def test_registration_with_existing_email(client: AsyncClient, test_db_session: AsyncSession):
    user = Users(email="existing@example.com", password="hashed")
    test_db_session.add(user)
    await test_db_session.commit()

    payload = {
        "email": "existing@example.com",
        "password": "newpassword123"
    }

    response = await client.post("/auth/reg", json=payload)

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json()["detail"] == "Пользователь с таким email уже существует"

