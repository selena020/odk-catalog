from flask import Blueprint, render_template, redirect, url_for, flash, request, abort
from flask_login import login_required, current_user
from models import db, Product, Category
import os
from werkzeug.utils import secure_filename

admin_bp = Blueprint('admin', __name__)

def admin_required(func):
    from functools import wraps
    @wraps(func)
    def decorated_view(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_admin():
            abort(403)
        return func(*args, **kwargs)
    return decorated_view

@admin_bp.route('/dashboard')
@login_required
@admin_required
def dashboard():
    products = Product.query.all()
    return render_template('admin/dashboard.html', products=products)

@admin_bp.route('/product/add', methods=['GET', 'POST'])
@login_required
@admin_required
def add_product():
    if request.method == 'POST':
        # Обработка фото
        photo = request.files.get('photo')
        image_url = None
        
        if photo and photo.filename != '':
            # Создаём безопасное имя файла
            import os
            from werkzeug.utils import secure_filename
            filename = secure_filename(photo.filename)
            # Добавляем время, чтобы имена не повторялись
            import time
            filename = str(int(time.time())) + '_' + filename
            # Сохраняем в папку static/uploads
            photo.save(os.path.join('static/uploads', filename))
            image_url = '/static/uploads/' + filename
        
        product = Product(
            name=request.form['name'],
            category_id=request.form['category_id'],
            thrust_kgf=request.form.get('thrust_kgf') or None,
            power_hp=request.form.get('power_hp') or None,
            application=request.form['application'],
            description=request.form['description'],
            image_url=image_url,
            created_by=current_user.id
        )
        db.session.add(product)
        db.session.commit()
        flash('Двигатель добавлен', 'success')
        return redirect(url_for('admin.dashboard'))
    
    categories = Category.query.all()
    return render_template('admin/product_form.html', categories=categories)

@admin_bp.route('/product/edit/<int:id>', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_product(id):
    product = Product.query.get_or_404(id)
    
    if request.method == 'POST':
        # Обновляем текстовые поля
        product.name = request.form['name']
        product.category_id = request.form['category_id']
        product.thrust_kgf = request.form.get('thrust_kgf') or None
        product.power_hp = request.form.get('power_hp') or None
        product.application = request.form['application']
        product.description = request.form['description']
        
        # Обработка нового фото
        photo = request.files.get('photo')
        if photo and photo.filename != '':
            import os
            from werkzeug.utils import secure_filename
            import time
            
            # Удаляем старое фото, если оно есть
            if product.image_url:
                old_path = os.path.join('static', product.image_url.lstrip('/'))
                if os.path.exists(old_path):
                    os.remove(old_path)
            
            # Сохраняем новое
            filename = secure_filename(photo.filename)
            filename = str(int(time.time())) + '_' + filename
            photo.save(os.path.join('static/uploads', filename))
            product.image_url = '/static/uploads/' + filename
        
        db.session.commit()
        flash('Данные обновлены', 'success')
        return redirect(url_for('admin.dashboard'))
    
    categories = Category.query.all()
    return render_template('admin/product_form.html', product=product, categories=categories)

@admin_bp.route('/product/delete/<int:id>')
@login_required
@admin_required
def delete_product(id):
    product = Product.query.get_or_404(id)
    db.session.delete(product)
    db.session.commit()
    flash('Двигатель удалён', 'success')
    return redirect(url_for('admin.dashboard'))