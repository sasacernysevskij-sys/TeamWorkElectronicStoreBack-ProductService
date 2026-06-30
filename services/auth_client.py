import requests

AUTH_SERVICE_URL = "http://localhost:8001"

def get_current_user(token: str):
    """Проверяет токен через Auth Service и возвращает пользователя"""
    try:
        response = requests.get(
            f"{AUTH_SERVICE_URL}/api/auth/me",
            headers={"Authorization": f"Bearer {token}"}
        )
        if response.status_code == 200:
            return response.json().get("user")
        return None
    except:
        return None

def verify_admin(token: str):
    """Проверяет что пользователь — админ"""
    user = get_current_user(token)
    if user and user.get("role") == "admin":
        return user
    return None