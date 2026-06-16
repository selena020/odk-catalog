from flask import Blueprint, render_template, request
from models import Product, Category

catalog_bp = Blueprint('catalog', __name__)

@catalog_bp.route('/')
def list_products():
    # Получаем параметры из адресной строки
    category_id = request.args.get('category', type=int)
    search_query = request.args.get('search', type=str, default='')
    page = request.args.get('page', 1, type=int)  # ← НОМЕР СТРАНИЦЫ (по умолчанию 1)
    per_page = 4  # ← КОЛИЧЕСТВО ДВИГАТЕЛЕЙ НА СТРАНИЦЕ
    
    # Базовый запрос
    query = Product.query
    
    # Фильтр по категории
    if category_id:
        query = query.filter_by(category_id=category_id)
    
    # Поиск по названию
    if search_query:
        query = query.filter(Product.name.ilike(f'%{search_query}%'))
    
    # ПАГИНАЦИЯ
    pagination = query.paginate(page=page, per_page=per_page, error_out=False)
    products = pagination.items  # ← двигатели на текущей странице
    
    # Получаем все категории
    categories = Category.query.all()
    
    return render_template('index.html', 
                         products=products,
                         categories=categories,
                         active_category=category_id,
                         search_query=search_query,
                         pagination=pagination)  # ← передаём объект пагинации в шаблон

@catalog_bp.route('/product/<int:id>')
def product_detail(id):
    product = Product.query.get_or_404(id)
    return render_template('product_detail.html', product=product)