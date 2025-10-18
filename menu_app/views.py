from flask import Blueprint, render_template, redirect, url_for, flash, request, abort
from flask_login import login_user, logout_user, login_required, current_user
from .forms import RegistrationForm, LoginForm, MenuForm, RestaurantForm
from .models import User, Restaurant, Menu
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
    return render_template('restaurants.html', restaurants=current_user.restaurants)

@main.route('/add_restaurant', methods=['GET', 'POST'])
@login_required
def add_restaurant_page():
    form = RestaurantForm()
    if form.validate_on_submit():
        new_restaurant = Restaurant(name=form.name.data, qr_code_id=form.qr_code_id.data)
        new_restaurant.owners.append(current_user)
        db.session.add(new_restaurant)
        db.session.commit()
        flash('새 식당이 추가되었습니다.', 'success')
        return redirect(url_for('main.restaurant_list_page'))
    return render_template('add_restaurant.html', form=form)

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


