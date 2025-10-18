from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, IntegerField, TextAreaField
from wtforms.validators import DataRequired, Email, EqualTo, Length, ValidationError
from .models import User, Restaurant

from wtforms import StringField, PasswordField, SubmitField, IntegerField, TextAreaField, BooleanField
from wtforms.validators import DataRequired, Email, EqualTo, Length, ValidationError
from .models import User, Restaurant

class LoginForm(FlaskForm):
    username = StringField('사용자 이름', validators=[DataRequired()])
    password = PasswordField('비밀번호', validators=[DataRequired()])
    remember_me = BooleanField('로그인 유지')
    submit = SubmitField('로그인')

class RegistrationForm(FlaskForm):
    username = StringField('사용자 이름', validators=[DataRequired(), Length(min=4, max=20)])
    email = StringField('이메일', validators=[DataRequired(), Email()])
    password = PasswordField('비밀번호', validators=[DataRequired(), Length(min=6)])
    password2 = PasswordField('비밀번호 확인', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('회원가입')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('이미 존재하는 사용자 이름입니다. 다른 이름을 사용해주세요.')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('이미 등록된 이메일 주소입니다. 다른 이메일을 사용해주세요.')

class RestaurantForm(FlaskForm):
    name = StringField('식당 이름', validators=[DataRequired(), Length(max=100)])
    qr_code_id = StringField('QR 코드 ID', validators=[DataRequired(), Length(min=5, max=20)])
    submit = SubmitField('식당 생성')

    def validate_qr_code_id(self, qr_code_id):
        restaurant = Restaurant.query.filter_by(qr_code_id=qr_code_id.data).first()
        if restaurant:
            raise ValidationError('이미 존재하는 QR 코드 ID입니다. 다른 ID를 사용해주세요.')

class MenuForm(FlaskForm):
    name_ko = StringField('메뉴 이름 (한국어)', validators=[DataRequired(), Length(max=100)])
    description_ko = TextAreaField('메뉴 설명 (한국어)')
    price = IntegerField('가격', validators=[DataRequired()])
    submit = SubmitField('메뉴 추가')
