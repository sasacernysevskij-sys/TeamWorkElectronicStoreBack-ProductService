from models.cart_item import CartItem
from models.product import Product


class CartService:
    def add_to_cart(self, db, user_id, product_id, quantity):
        if quantity <= 0:
            return {
                "detail": "Количество товара должно быть больше 0"
            }, 400

        product = db.query(Product).filter(Product.id == product_id).first()

        if product is None:
            return {
                "detail": "Товар не найден"
            }, 404

        if product.stock < quantity:
            return {
                "detail": "Недостаточно товара на складе"
            }, 400

        cart_item = (
            db.query(CartItem)
            .filter(
                CartItem.user_id == user_id,
                CartItem.product_id == product_id
            )
            .first()
        )

        if cart_item is not None:
            new_quantity = cart_item.quantity + quantity

            if product.stock < new_quantity:
                return {
                    "detail": "Недостаточно товара на складе"
                }, 400

            cart_item.quantity = new_quantity
        else:
            cart_item = CartItem(
                user_id=user_id,
                product_id=product_id,
                quantity=quantity
            )

            db.add(cart_item)

        db.commit()
        db.refresh(cart_item)

        return {
            "id": cart_item.id,
            "user_id": cart_item.user_id,
            "product_id": cart_item.product_id,
            "quantity": cart_item.quantity,
            "product": {
                "id": product.id,
                "name": product.name,
                "price": product.price,
                "stock": product.stock
            }
        }, 201

    def get_cart(self, db, user_id):
        cart_items = db.query(CartItem).filter(CartItem.user_id == user_id).all()

        items = []
        total_price = 0

        for cart_item in cart_items:
            product = db.query(Product).filter(Product.id == cart_item.product_id).first()

            if product is None:
                continue

            subtotal = product.price * cart_item.quantity
            total_price += subtotal

            items.append({
                "cart_item_id": cart_item.id,
                "product_id": product.id,
                "name": product.name,
                "article": product.article,
                "description": product.description,
                "price": product.price,
                "product_type": product.product_type,
                "stock": product.stock,
                "quantity": cart_item.quantity,
                "subtotal": subtotal,
                "image_url": product.image_url
            })

        return {
            "items": items,
            "total_price": total_price
        }, 200

    def clear_cart(self, db, user_id):
        cart_items = db.query(CartItem).filter(CartItem.user_id == user_id).all()

        for cart_item in cart_items:
            db.delete(cart_item)

        db.commit()

        return {
            "message": "Корзина очищена"
        }, 200
    def update_cart_item(self, db, user_id, product_id, quantity):
        if quantity <= 0:
            return {
                "detail": "Количество товара должно быть больше 0"
            }, 400

        product = db.query(Product).filter(Product.id == product_id).first()

        if product is None:
            return {
                "detail": "Товар не найден"
            }, 404

        if product.stock < quantity:
            return {
                "detail": "Недостаточно товара на складе"
            }, 400

        cart_item = (
            db.query(CartItem)
            .filter(
                CartItem.user_id == user_id,
                CartItem.product_id == product_id
            )
            .first()
        )

        if cart_item is None:
            return {
                "detail": "Товар не найден в корзине"
            }, 404

        cart_item.quantity = quantity
        db.commit()
        db.refresh(cart_item)

        return {
            "id": cart_item.id,
            "user_id": cart_item.user_id,
            "product_id": cart_item.product_id,
            "quantity": cart_item.quantity
        }, 200
    def remove_cart_item(self, db, user_id, product_id):
        cart_item = (
            db.query(CartItem)
            .filter(
                CartItem.user_id == user_id,
                CartItem.product_id == product_id
            )
            .first()
        )
        if cart_item is None:
            return {"detail": "Товар не найден в корзине"}, 404
        db.delete(cart_item)
        db.commit()

        return {"detail": "Товар удалён из корзины"}, 200