import hashlib
from database import SessionLocal
from models import User
from settings import settings

class AuthManager:
    def __init__(self):
        self.current_user = None
    
    def hash_password(self, password: str) -> str:
        return hashlib.sha256(password.encode()).hexdigest()
    
    def create_admin_user(self):
        with SessionLocal() as session:
            existing_admin = session.query(User).filter_by(username=settings.ADMIN_LOGIN).first()
            if not existing_admin:
                admin_user = User(
                    username=settings.ADMIN_LOGIN,
                    password_hash=self.hash_password(settings.ADMIN_PASSWORD)
                )
                session.add(admin_user)
                session.commit()
                print("Администратор создан")
    
    def login(self, username: str, password: str) -> bool:
        with SessionLocal() as session:
            user = session.query(User).filter_by(username=username, is_active=True).first()
            if user and user.password_hash == self.hash_password(password):
                self.current_user = user
                return True
        return False
    
    def logout(self):
        self.current_user = None
    
    def is_authenticated(self) -> bool:
        return self.current_user is not None
    
    def get_current_user(self):
        return self.current_user