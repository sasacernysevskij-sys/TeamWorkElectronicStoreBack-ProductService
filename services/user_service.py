from models.user import User


class UserService:
    def get_users(self, db, skip=0, limit=10):
        users = db.query(User).offset(skip).limit(limit).all()

        return [
            {
                "id": user.id,
                "name": user.name,
                "surname": user.surname,
                "email": user.email,
                "phone": user.phone,
                "role": user.role,
                "created_at": str(user.created_at)
            }
            for user in users
        ], 200