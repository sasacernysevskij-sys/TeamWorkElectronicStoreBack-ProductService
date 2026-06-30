from datetime import datetime, timedelta
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

from models.cart_item import CartItem
from models.product import Product
from models.order import Order
from models.order_item import OrderItem
from models.user import User
from config import SMTP_HOST, SMTP_PORT, SMTP_EMAIL, SMTP_PASSWORD


class OrderService:

    def send_order_email(self, db, user_id, order_id, total_price, items):
        """Отправляет письмо с подтверждением заказа"""
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            return

        items_text = ""
        for item in items:
            items_text += f"- {item['name']}: {item['quantity']} x {item['price']}₴ = {item['subtotal']}₴\n"

        msg = MIMEMultipart()
        msg["Subject"] = f"Замовлення №{order_id} оформлено"
        msg["From"] = SMTP_EMAIL
        msg["To"] = user.email

        body = f"""Дякуємо за замовлення!

Номер замовлення: #{order_id}
Сума: {total_price}₴

Товари:
{items_text}

Статус: new
Очікуйте повідомлення про відправку.

З повагою, M·TAC Shop
"""
        msg.attach(MIMEText(body, "plain", "utf-8"))

        try:
            with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as server:
                server.starttls()
                server.login(SMTP_EMAIL, SMTP_PASSWORD)
                server.sendmail(SMTP_EMAIL, user.email, msg.as_string())
            print(f"Письмо отправлено на {user.email}")
        except Exception as e:
            print(f"Ошибка отправки письма: {e}")

    def create_order(self, db, user_id):
        cart_items = db.query(CartItem).filter(CartItem.user_id == user_id).all()

        if len(cart_items) == 0:
            return {
                "detail": "Корзина пустая"
            }, 400

        try:
            total_price = 0
            products_data = []

            for cart_item in cart_items:
                product = db.query(Product).filter(Product.id == cart_item.product_id).first()

                if product is None:
                    return {
                        "detail": f"Товар с id {cart_item.product_id} не найден"
                    }, 404

                if product.stock < cart_item.quantity:
                    return {
                        "detail": f"Недостаточно товара на складе: {product.name}"
                    }, 400

                subtotal = product.price * cart_item.quantity
                total_price += subtotal

                products_data.append({
                    "cart_item": cart_item,
                    "product": product,
                    "price": product.price,
                    "quantity": cart_item.quantity,
                    "subtotal": subtotal
                })
            order = Order(
                user_id=user_id,
                status="new",
                total_price=total_price
            )

            db.add(order)
            db.flush()

            order_items_response = []

            for item in products_data:
                product = item["product"]
                cart_item = item["cart_item"]

                order_item = OrderItem(
                    order_id=order.id,
                    product_id=product.id,
                    quantity=item["quantity"],
                    price=item["price"]
                )

                db.add(order_item)

                product.stock -= item["quantity"]

                db.delete(cart_item)

                order_items_response.append({
                    "product_id": product.id,
                    "name": product.name,
                    "quantity": item["quantity"],
                    "price": item["price"],
                    "subtotal": item["subtotal"]
                })

            db.commit()
            db.refresh(order)

            # Отправляем письмо
            self.send_order_email(
                db=db,
                user_id=user_id,
                order_id=order.id,
                total_price=total_price,
                items=order_items_response
            )

            return {
                "message": "Заказ успешно создан",
                "order": {
                    "id": order.id,
                    "user_id": order.user_id,
                    "status": order.status,
                    "total_price": order.total_price,
                    "created_at": str(order.created_at),
                    "items": order_items_response
                }
            }, 201

        except Exception:
            db.rollback()
            return {
                "detail": "Ошибка при создании заказа"
            }, 500

    def get_my_orders(self, db, user_id):
        orders = db.query(Order).filter(Order.user_id == user_id).all()

        result = []

        for order in orders:
            order_items = db.query(OrderItem).filter(OrderItem.order_id == order.id).all()

            items = []

            for order_item in order_items:
                product = db.query(Product).filter(Product.id == order_item.product_id).first()

                product_name = None

                if product is not None:
                    product_name = product.name

                items.append({
                    "product_id": order_item.product_id,
                    "name": product_name,
                    "quantity": order_item.quantity,
                    "price": order_item.price,
                    "subtotal": order_item.price * order_item.quantity
                })

            result.append({
                "id": order.id,
                "status": order.status,
                "total_price": order.total_price,
                "created_at": str(order.created_at),
                "items": items
            })

        return result, 200

    def get_all_orders_admin(self, db, skip=0, limit=10):
        orders = (
            db.query(Order)
            .order_by(Order.total_price.desc())
            .offset(skip)
            .limit(limit)
            .all()
        )

        return [
            {
                "id": order.id,
                "user_id": order.user_id,
                "status": order.status,
                "total_price": order.total_price,
                "created_at": str(order.created_at)
            }
            for order in orders
        ], 200

    def get_orders_count_admin(self, db):
        count = db.query(Order).count()

        return {
            "orders_count": count
        }, 200

    def get_last_month_orders_sum_admin(self, db):
        date_from = datetime.utcnow() - timedelta(days=30)

        orders = db.query(Order).filter(Order.created_at >= date_from).all()

        total_sum = 0

        for order in orders:
            total_sum += order.total_price

        return {
            "period": "last_30_days",
            "orders_count": len(orders),
            "total_sum": total_sum
        }, 200

    def get_last_month_orders_admin(self, db, skip=0, limit=10):
        date_from = datetime.utcnow() - timedelta(days=30)

        orders = (
            db.query(Order)
            .filter(Order.created_at >= date_from)
            .order_by(Order.created_at.desc())
            .offset(skip)
            .limit(limit)
            .all()
        )

        return [
            {
                "id": order.id,
                "user_id": order.user_id,
                "status": order.status,
                "total_price": order.total_price,
                "created_at": str(order.created_at)
            }
            for order in orders
        ], 200

    def get_order_items_by_order_id_admin(self, db, order_id):
        order = db.query(Order).filter(Order.id == order_id).first()

        if order is None:
            return {
                "detail": "Заказ не найден"
            }, 404

        order_items = db.query(OrderItem).filter(OrderItem.order_id == order_id).all()

        result = []

        for order_item in order_items:
            product = db.query(Product).filter(Product.id == order_item.product_id).first()

            product_name = None
            article = None

            if product is not None:
                product_name = product.name
                article = product.article

            result.append({
                "id": order_item.id,
                "order_id": order_item.order_id,
                "product_id": order_item.product_id,
                "product_name": product_name,
                "article": article,
                "quantity": order_item.quantity,
                "price": order_item.price,
                "subtotal": order_item.price * order_item.quantity
            })

        return {
            "order": {
                "id": order.id,
                "user_id": order.user_id,
                "status": order.status,
                "total_price": order.total_price,
                "created_at": str(order.created_at)
            },
            "items": result
        }, 200