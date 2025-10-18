import random
import string
import os
import qrcode
import json
import google.generativeai as genai
from flask import Blueprint, render_template, redirect, url_for, flash, request, abort, current_app, jsonify
from flask_login import login_user, logout_user, login_required, current_user
from .forms import RegistrationForm, LoginForm, MenuForm, RestaurantForm
from .models import User, Restaurant, Menu
from .extensions import db

main = Blueprint('main', __name__,template_folder='../templates')


def generate_unique_qr_id(length=8):
    """지정된 길이의 고유한 QR 코드 ID를 생성합니다."""
    while True:
        new_id = ''.join(random.choices(string.ascii_uppercase + string.digits, k=length))
        if not Restaurant.query.filter_by(qr_code_id=new_id).first():
            return new_id

def create_qr_code(qr_id, data):
    """주어진 ID와 데이터로 QR 코드를 생성하고 저장합니다."""
    qr_folder = os.path.join(current_app.static_folder, 'qr_codes')
    os.makedirs(qr_folder, exist_ok=True)
    
    qr_path = os.path.join(qr_folder, f'{qr_id}.png')

    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_H,
        box_size=10,
        border=4,
    )
    qr.add_data(data)
    qr.make(fit=True)

    img = qr.make_image(fill_color="black", back_color="white")
    img.save(qr_path)


@main.route('/')
def home_page():
    return render_template('index.html')

@main.route('/menu/<qr_code_id>')
def public_menu_page(qr_code_id):
    restaurant = Restaurant.query.filter_by(qr_code_id=qr_code_id).first_or_404()
    menus = restaurant.menus.all()
    return render_template('public_menu.html', restaurant=restaurant, menus=menus)

@main.route('/api/menu-info', methods=['POST'])
def menu_info_api():
    data = request.get_json()
    if not data:
        return jsonify({'error': 'No input data provided'}), 400

    menu_name = data.get('menu_name')
    description = data.get('description')
    language = data.get('language', 'en')

    api_key = os.environ.get('GEMINI_API_KEY')
    if not api_key:
        return jsonify({'error': 'GEMINI_API_KEY 환경 변수가 설정되지 않았습니다.'}), 500

    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel("gemini-2.5-flash")

        prompt = f"""You are a helpful assistant for a restaurant menu. Perform several tasks and respond ONLY with a valid JSON object that can be parsed by Python's json.loads().
The target language is: {language}.
The Korean food name is: \"{menu_name}\".

Tasks:
1.  **Transliterate the Korean food name** into the phonetic script of the target language. For example, for Japanese, use Katakana. If direct transliteration is not feasible, use the Revised Romanization of Korean.
2.  **Translate the restaurant's special note** into the target language. The note is: \"{description}\".
3.  **Provide a brief, interesting, one-sentence description** of the food in the target language.
4.  **Provide main ingredients, how to eat,Allergy precautions ** of the food in the target language.
5.  **Provide an allergy precaution if possible, or if consumption of the food may cause a problem** of the food in the target language.
6.  **Translate the header '우리 가게 만의 특별한 점'** into the target language.
7.  **Translate the header '음식 정보'** into the target language.

Your response must be a JSON object with five keys: 'transliterated_name', 'translated_description', 'food_info', 'header_special_point', and 'header_food_info'. Do not wrap it in markdown.

Example for Japanese (language='ja') and menu_name='김치찌개':
{{
    "transliterated_name": "キムチチゲ",
    "translated_description": "Translated text here.",
    "food_info": "A brief description of the food here.",
    "header_special_point": "当店だけの特別な点",
    "header_food_info": "食べ物情報"
}}
"""

        response = model.generate_content(prompt)
        result = json.loads(response.text)
        return jsonify(result)

    except Exception as e:
        # Gemini API 호출 또는 JSON 파싱 중 발생한 모든 오류를 처리합니다.
        return jsonify({'error': f'API 호출 또는 데이터 처리 중 오류 발생: {str(e)}'}), 500


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
    return render_template('restaurants.html', restaurants=current_user.restaurants)

@main.route('/add_restaurant', methods=['GET', 'POST'])
@login_required
def add_restaurant_page():
    form = RestaurantForm()
    if form.validate_on_submit():
        qr_code_id = generate_unique_qr_id()
        new_restaurant = Restaurant(name=form.name.data, qr_code_id=qr_code_id)
        new_restaurant.owners.append(current_user)
        db.session.add(new_restaurant)
        db.session.commit()

        # QR 코드 생성
        qr_data = url_for('main.public_menu_page', qr_code_id=new_restaurant.qr_code_id, _external=True)
        create_qr_code(new_restaurant.qr_code_id, qr_data)

        flash('새 식당이 추가되고 QR 코드가 생성되었습니다.', 'success')
        return redirect(url_for('main.restaurant_list_page'))
    return render_template('add_restaurant.html', form=form)

@main.route('/restaurant/<int:restaurant_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_restaurant_page(restaurant_id):
    restaurant = Restaurant.query.get_or_404(restaurant_id)
    if current_user not in restaurant.owners:
        abort(403)
    
    form = RestaurantForm(obj=restaurant)
    if form.validate_on_submit():
        restaurant.name = form.name.data
        db.session.commit()
        flash('식당 정보가 수정되었습니다.', 'success')
        return redirect(url_for('main.restaurant_list_page'))
    
    return render_template('edit_restaurant.html', form=form, restaurant=restaurant)

@main.route('/restaurant/<int:restaurant_id>/delete', methods=['POST'])
@login_required
def delete_restaurant(restaurant_id):
    restaurant = Restaurant.query.get_or_404(restaurant_id)
    if current_user not in restaurant.owners:
        abort(403)
    
    # QR 코드 파일 삭제
    qr_code_path = os.path.join(current_app.static_folder, 'qr_codes', f'{restaurant.qr_code_id}.png')
    try:
        if os.path.exists(qr_code_path):
            os.remove(qr_code_path)
    except OSError as e:
        flash(f'QR 코드 파일 삭제 중 오류 발생: {e}', 'danger')

    db.session.delete(restaurant)
    db.session.commit()
    flash('식당이 삭제되었습니다.', 'success')
    return redirect(url_for('main.restaurant_list_page'))

@main.route('/restaurant/<int:restaurant_id>/manage', methods=['GET', 'POST'])
@login_required
def menu_management_page(restaurant_id):
    restaurant = Restaurant.query.get_or_404(restaurant_id)
    if current_user not in restaurant.owners:
        abort(403)

    form = MenuForm()
    if form.validate_on_submit():
        new_menu = Menu(
            name_ko=form.name_ko.data,
            description_ko=form.description_ko.data,
            price=form.price.data,
            restaurant_id=restaurant.id
        )
        db.session.add(new_menu)
        db.session.commit()
        flash('새 메뉴가 추가되었습니다.', 'success')
        return redirect(url_for('main.menu_management_page', restaurant_id=restaurant.id))

    menus = restaurant.menus.all()
    return render_template('menu_management.html', restaurant=restaurant, menus=menus, form=form)

@main.route('/menu/<int:menu_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_menu_page(menu_id):
    menu = Menu.query.get_or_404(menu_id)
    restaurant = menu.restaurant
    if current_user not in restaurant.owners:
        abort(403)

    form = MenuForm(obj=menu)
    if form.validate_on_submit():
        menu.name_ko = form.name_ko.data
        menu.description_ko = form.description_ko.data
        menu.price = form.price.data
        db.session.commit()
        flash('메뉴가 수정되었습니다.', 'success')
        return redirect(url_for('main.menu_management_page', restaurant_id=restaurant.id))

    return render_template('edit_menu.html', form=form, menu=menu)

@main.route('/menu/<int:menu_id>/delete', methods=['POST'])
@login_required
def delete_menu(menu_id):
    menu = Menu.query.get_or_404(menu_id)
    restaurant_id = menu.restaurant.id
    if current_user not in menu.restaurant.owners:
        abort(403)
    
    db.session.delete(menu)
    db.session.commit()
    flash('메뉴가 삭제되었습니다.', 'success')
    return redirect(url_for('main.menu_management_page', restaurant_id=restaurant_id))


