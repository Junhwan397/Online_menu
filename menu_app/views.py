from flask import Blueprint, render_template, redirect, url_for, flash, request
from .forms import RegistrationForm
from .models import User
from .extensions import db

main = Blueprint('main', __name__,template_folder='../templates')


@main.route('/')
def home_page():
    return render_template('index.html')


@main.route('/login')
def login_page():
    return render_template('login.html')

@main.route('/register', methods=['GET', 'POST'])
def register_page():
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('회원가입이 완료되었습니다! 이제 로그인할 수 있습니다.', 'success')
        return redirect(url_for('main.login_page'))
    return render_template('register.html', form=form)


@main.route('/restaurants')
def restaurant_list_page():
    return "<h1>식당 관리 페이지</h1><p>등록된 식당 목록 및 관리가 표시됩니다.</p>"


