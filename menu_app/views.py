from flask import Blueprint, render_template

main = Blueprint('main', __name__,template_folder='../templates')


@main.route('/')
def home_page():
    return render_template('index.html')


@main.route('/login')
def login_page():
    return render_template('login.html')

@main.route('/register')
def register_page():
    return render_template('register.html')


@main.route('/restaurants')
def restaurant_list_page():
    return "<h1>식당 관리 페이지</h1><p>등록된 식당 목록 및 관리가 표시됩니다.</p>"

