import os

SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-123")
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///shop.db")
JWT_EXPIRATION_HOURS = 24

# SMTP настройки для отправки писем
SMTP_HOST = "smtp.gmail.com"
SMTP_PORT = 587
SMTP_EMAIL = "sasacernysevskij@gmail.com" 
SMTP_PASSWORD = "qrgawqvxbiwobjfj"  