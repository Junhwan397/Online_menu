from .extensions import db
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin  # Flask-Login을 위한 UserMixin 임포트

# 다대다 관계를 위한 연결 테이블
user_restaurants = db.Table(
    'user_restaurants',
    db.Column('user_id', db.Integer, db.ForeignKey('user.id'), primary_key=True),
    db.Column('restaurant_id', db.Integer, db.ForeignKey('restaurant.id'), primary_key=True)
)


# User 모델 (UserMixin 상속)
class User(UserMixin, db.Model):  # UserMixin 추가
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)

    # relationship: Restaurant 테이블과 다대다 연결
    restaurants = db.relationship(
        'Restaurant',
        secondary=user_restaurants,
        lazy='subquery',
        backref=db.backref('owners', lazy=True)
    )

    # 비밀번호 해싱 메서드
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    # 비밀번호 검증 메서드
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f'<User {self.username}>'


# Restaurant 모델
class Restaurant(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    qr_code_id = db.Column(db.String(20), unique=True, nullable=False)

    menus = db.relationship('Menu', backref='restaurant', lazy='dynamic')

    def __repr__(self):
        return f'<Restaurant {self.name}>'


# Menu 모델
class Menu(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    restaurant_id = db.Column(db.Integer, db.ForeignKey('restaurant.id'), nullable=False)

    name_ko = db.Column(db.String(100), nullable=False)
    description_ko = db.Column(db.Text)
    price = db.Column(db.Integer)

    def __repr__(self):
        return f'<Menu {self.name_ko}>'
