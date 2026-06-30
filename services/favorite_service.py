from models.favorite import Favorite
from models.product import Product

class FavoriteService:

    def add_to_favorites(self, db, user_id, product_id):
        # Проверка существует ли товар
        product = db.query(Product).filter(Product.id == product_id).first()
        if product is None:
            return {"detail": "Товар не найден"}, 404

        # Проверка не добавлен ли уже
        existing = db.query(Favorite).filter(
            Favorite.user_id == user_id,
            Favorite.product_id == product_id
        ).first()
        if existing:
            return {"detail": "Товар уже в избранном"}, 400

        favorite = Favorite(user_id=user_id, product_id=product_id)
        db.add(favorite)
        db.commit()
        db.refresh(favorite)

        return {
            "id": favorite.id,
            "user_id": favorite.user_id,
            "product_id": favorite.product_id
        }, 201

    def get_favorites(self, db, user_id):
        favorites = db.query(Favorite).filter(Favorite.user_id == user_id).all()

        items = []
        for fav in favorites:
            product = db.query(Product).filter(Product.id == fav.product_id).first()
            if product is None:
                continue
            items.append({
                "favorite_id": fav.id,
                "product_id": product.id,
                "name": product.name,
                "price": product.price,
                "image_url": product.image_url,
                "rating": product.rating,
                "product_type": product.product_type,
                "stock": product.stock,
                "article": product.article,
                "description": product.description
            })

        return {"items": items}, 200

    def remove_from_favorites(self, db, user_id, product_id):
        favorite = db.query(Favorite).filter(
            Favorite.user_id == user_id,
            Favorite.product_id == product_id
        ).first()

        if favorite is None:
            return {"detail": "Товар не найден в избранном"}, 404

        db.delete(favorite)
        db.commit()
        return {"detail": "Товар удалён из избранного"}, 200

    def clear_favorites(self, db, user_id):
        db.query(Favorite).filter(Favorite.user_id == user_id).delete()
        db.commit()
        return {"detail": "Все товары удалены из избранного"}, 200