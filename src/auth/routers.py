from fastapi import APIRouter, Depends, Form, Query
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi.security import OAuth2PasswordRequestForm
from fastapi import Request
from fastapi.responses import HTMLResponse


from src.auth.dependencies import get_async_session
from src.auth.schemas import UserAdd, UserLogin, FormUserLogin, ResetPasswordRequest, ForgotPasswordRequest
from src.auth.service import add_user_to_db, login_user_from_db, refresh_access_token_in_db, logout_user_from_db, \
    confirm_user_email, get_current_user, forgot_password_in_db, reset_password_in_db, reset_all_user_refresh_tokens

auth_router = APIRouter()


@auth_router.post("/reg")
async def reg_user(
        user: UserAdd,
        session: AsyncSession = Depends(get_async_session)
):
    return await add_user_to_db(user, session)


@auth_router.post("/login")
async def login_user(
        form_data: OAuth2PasswordRequestForm = Depends(),
        session: AsyncSession = Depends(get_async_session)
):
    user_data = UserLogin(email=form_data.username, password=form_data.password)

    return await login_user_from_db(user_data, session)


@auth_router.post("/refresh")
async def refresh_access_token(
        request: Request,
        session: AsyncSession = Depends(get_async_session)
):
    token = request.cookies.get("refresh_token")
    return await refresh_access_token_in_db(token, session)


@auth_router.post("/logout")
async def logout_user(
        request: Request,
        session: AsyncSession = Depends(get_async_session)
):
    token = request.cookies.get("refresh_token")
    return await logout_user_from_db(token, session)


@auth_router.get("/me")
async def get_my_posts(user_id: str = Depends(get_current_user)):
    return {"message": f"Posts for user {user_id}"}


@auth_router.get("/confirm")
async def confirm_email(
        token: str,
        session: AsyncSession = Depends(get_async_session)
):
    return await confirm_user_email(token, session)


@auth_router.post("/forgot-password")
async def forgot_password(
        user_data: ForgotPasswordRequest,
        session: AsyncSession = Depends(get_async_session)
):
    return await forgot_password_in_db(user_data.email, session)


@auth_router.post("/reset-password")
async def reset_password(
        reset_data: ResetPasswordRequest,
        session: AsyncSession = Depends(get_async_session)
):
    return await reset_password_in_db(reset_data, session)


@auth_router.get("/reset-password-page", response_class=HTMLResponse)
async def get_reset_password_form(token: str = Query(...)):
    print(f"Received token: {token}")
    return f"""
    <!DOCTYPE html>
    <html>
        <head>
            <title>Сброс пароля</title>
            <meta charset="UTF-8">
            <style>
                body {{
                    font-family: Arial, sans-serif;
                    max-width: 500px;
                    margin: 50px auto;
                    padding: 20px;
                }}
                .form-group {{
                    margin-bottom: 15px;
                }}
                label {{
                    display: block;
                    margin-bottom: 5px;
                }}
                input[type="password"] {{
                    width: 100%;
                    padding: 8px;
                    border: 1px solid #ddd;
                    border-radius: 4px;
                    box-sizing: border-box;
                }}
                button {{
                    background-color: #007bff;
                    color: white;
                    padding: 10px 20px;
                    border: none;
                    border-radius: 4px;
                    cursor: pointer;
                }}
                button:hover {{
                    background-color: #0056b3;
                }}
                .message {{
                    margin-top: 15px;
                    padding: 10px;
                    border-radius: 4px;
                }}
                .success {{
                    background-color: #d4edda;
                    color: #155724;
                    border: 1px solid #c3e6cb;
                }}
                .error {{
                    background-color: #f8d7da;
                    color: #721c24;
                    border: 1px solid #f5c6cb;
                }}
            </style>
        </head>
        <body>
            <h2>Сброс пароля</h2>
            <form id="resetForm">
                <input type="hidden" id="token" value="{token}">
                <div class="form-group">
                    <label for="new_password">Новый пароль:</label>
                    <input type="password" id="new_password" required minlength="6">
                </div>
                <div class="form-group">
                    <label for="confirm_password">Подтвердите пароль:</label>
                    <input type="password" id="confirm_password" required minlength="6">
                </div>
                <button type="submit">Сбросить пароль</button>
            </form>

            <div id="message"></div>

            <script>
                document.getElementById('resetForm').addEventListener('submit', async (e) => {{
                    e.preventDefault();

                    const token = document.getElementById('token').value;
                    const newPassword = document.getElementById('new_password').value;
                    const confirmPassword = document.getElementById('confirm_password').value;
                    const messageDiv = document.getElementById('message');

                    // Очищаем предыдущие сообщения
                    messageDiv.innerHTML = '';
                    messageDiv.className = '';

                    // Валидация
                    if (newPassword.length < 6) {{
                        showMessage('Пароль должен быть не менее 6 символов', 'error');
                        return;
                    }}

                    if (newPassword !== confirmPassword) {{
                        showMessage('Пароли не совпадают', 'error');
                        return;
                    }}

                    showMessage('Отправка запроса...', '');

                    try {{
                        const response = await fetch('/auth/reset-password', {{
                            method: 'POST',
                            headers: {{
                                'Content-Type': 'application/json',
                            }},
                            body: JSON.stringify({{
                                token: token,
                                new_password: newPassword
                            }})
                        }});

                        const result = await response.json();

                        if (response.ok) {{
                            showMessage('Пароль успешно изменен! Перенаправление на страницу входа...', 'success');
                            setTimeout(() => {{
                                window.location.href = '/auth/login';
                            }}, 3000);
                        }} else {{
                            showMessage('Ошибка: ' + result.detail, 'error');
                        }}
                    }} catch (error) {{
                        showMessage('Ошибка сети. Попробуйте еще раз.', 'error');
                        console.error('Network error:', error);
                    }}
                }});

                function showMessage(text, type) {{
                    const messageDiv = document.getElementById('message');
                    messageDiv.innerHTML = text;
                    messageDiv.className = type ? 'message ' + type : 'message';
                }}
            </script>
        </body>
    </html>
    """


@auth_router.get("/exit_all")
async def exit_all(
        user = Depends(get_current_user),
        session: AsyncSession = Depends(get_async_session)
):
    return await reset_all_user_refresh_tokens(user["user"], session)

