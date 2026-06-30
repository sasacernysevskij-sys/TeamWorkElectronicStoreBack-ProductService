from sqlalchemy import Column, Integer, String, Float, Text, DateTime
from datetime import datetime
from db import Base

class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(60), nullable=False)
    article = Column(String(10), unique=True, nullable=False)
    description = Column(Text, nullable=True)
    price = Column(Float, nullable=False)
    product_type = Column(String(30), nullable=False)
    stock = Column(Integer, nullable=False, default=0)
    rating = Column(Float, nullable=True, default=0.0)
    image_url = Column(String(500), nullable=True)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)