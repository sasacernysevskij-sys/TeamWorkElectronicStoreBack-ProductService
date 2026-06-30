from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from db import engine, Base

from models.user import User
from models.product import Product
from models.cart_item import CartItem
from models.order import Order
from models.order_item import OrderItem
from models.favorite import Favorite

from routes.auth_routes import router as auth_router
from routes.product_routes import router as product_router
from routes.cart_routes import router as cart_router
from routes.order_routes import router as order_router
from routes.user_routes import router as user_router
from routes.favorite_routes import router as favorite_router


app = FastAPI(title="Shop API", version="1.0.0")

# Разрешаем CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Создаём таблицы при старте
Base.metadata.create_all(bind=engine)

# Подключаем роуты
app.include_router(auth_router)
app.include_router(product_router)
app.include_router(cart_router)
app.include_router(order_router)
app.include_router(user_router)
app.include_router(favorite_router)


@app.get("/")
def home():
    return {"message": "API работает!"}