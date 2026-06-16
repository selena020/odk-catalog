from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from models import db, User, Role
import secrets

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('catalog.list_products'))

    if request.method == 'POST':
        login_input = request.form['login']
        password = request.form['password']
        user = User.query.filter((User.login == login_input) | (User.email == login_input)).first()
        if user and user.verify_password(password):
            login_user(user)
            flash('Вход выполнен успешно', 'success')
            next_page = request.args.get('next')
            return redirect(next_page or url_for('catalog.list_products'))
        else:
            flash('Неверный логин/email или пароль', 'danger')
    return render_template('login.html')

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('catalog.list_products'))

    if request.method == 'POST':
        login = request.form['login']
        email = request.form['email']
        password = request.form['password']
        confirm = request.form['confirm']

        if password != confirm:
            flash('Пароли не совпадают', 'danger')
        elif User.query.filter_by(login=login).first():
            flash('Логин уже занят', 'danger')
        elif User.query.filter_by(email=email).first():
            flash('Email уже зарегистрирован', 'danger')
        else:
            role_user = Role.query.filter_by(name='user').first()
            new_user = User(login=login, email=email, role_id=role_user.id)
            new_user.set_password(password)
            db.session.add(new_user)
            db.session.commit()
            flash('Регистрация успешна! Теперь войдите.', 'success')
            return redirect(url_for('auth.login'))

    return render_template('register.html')

@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Вы вышли из системы', 'info')
    return redirect(url_for('catalog.list_products'))

# ВОССТАНОВЛЕНИЕ ПАРОЛЯ (без email, просто выводим ссылку в консоль)
@auth_bp.route('/restore', methods=['GET', 'POST'])
def restore_request():
    if current_user.is_authenticated:
        return redirect(url_for('catalog.list_products'))
    
    if request.method == 'POST':
        email = request.form['email']
        user = User.query.filter_by(email=email).first()
        
        if user:
            token = secrets.token_urlsafe(32)
            user.reset_token = token
            db.session.commit()
            
            # Выводим ссылку в консоль (вместо реального email)
            reset_link = url_for('auth.restore_password', token=token, _external=True)
            print(f"\n=== ССЫЛКА ДЛЯ СБРОСА ПАРОЛЯ ===\n{reset_link}\n================================\n")
            flash('Ссылка для сброса пароля выведена в консоль (терминал)', 'info')
        else:
            flash('Email не найден в системе', 'danger')
        
        return redirect(url_for('auth.login'))
    
    return render_template('restore_request.html')

@auth_bp.route('/restore/<token>', methods=['GET', 'POST'])
def restore_password(token):
    user = User.query.filter_by(reset_token=token).first()
    
    if not user:
        flash('Ссылка недействительна или истекла', 'danger')
        return redirect(url_for('auth.login'))
    
    if request.method == 'POST':
        new_password = request.form['password']
        confirm = request.form['confirm']
        
        if new_password == confirm:
            user.set_password(new_password)
            user.reset_token = None
            db.session.commit()
            flash('Пароль успешно изменён! Теперь войдите с новым паролем', 'success')
            return redirect(url_for('auth.login'))
        else:
            flash('Пароли не совпадают', 'danger')
    
    return render_template('restore_password.html', token=token)