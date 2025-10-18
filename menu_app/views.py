from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required
from .forms import RegistrationForm, LoginForm
from .models import User
from .extensions import db

main = Blueprint('main', __name__,template_folder='../templates')


@main.route('/')
def home_page():
    return render_template('index.html')


@main.route('/login', methods=['GET', 'POST'])
def login_page():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('사용자 이름 또는 비밀번호가 올바르지 않습니다.', 'danger')
            return redirect(url_for('main.login_page'))
        login_user(user, remember=form.remember_me.data)
        flash('로그인되었습니다!', 'success')
        return redirect(url_for('main.restaurant_list_page'))
    return render_template('login.html', form=form)

@main.route('/logout')
@login_required
def logout_page():
    logout_user()
    flash('로그아웃되었습니다.', 'info')
    return redirect(url_for('main.home_page'))

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
@login_required
def restaurant_list_page():
    return "<h1>식당 관리 페이지</h1><p>등록된 식당 목록 및 관리가 표시됩니다.</p>"


