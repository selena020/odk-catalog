from app import create_app
from models import db, Role, Category, User, Product

app = create_app()

with app.app_context():
    # СОЗДАЁМ ТАБЛИЦЫ
    db.create_all()

    # РОЛИ
    for role_name in ['guest', 'user', 'admin']:
        if not Role.query.filter_by(name=role_name).first():
            db.session.add(Role(name=role_name))
    db.session.commit()
    print("Роли созданы")

    # АДМИНИСТРАТОР
    admin_role = Role.query.filter_by(name='admin').first()
    if not User.query.filter_by(login='admin').first():
        admin = User(login='admin', email='admin@odk.ru', role_id=admin_role.id)
        admin.set_password('admin123')
        db.session.add(admin)
        db.session.commit()
        print("Администратор создан: login=admin, password=admin123")

    # КАТЕГОРИИ
    categories_data = ['Турбовентиляторные', 'Турбовинтовые', 'Турбовальные', 'Наземные ГТД']
    for cat_name in categories_data:
        if not Category.query.filter_by(name=cat_name).first():
            db.session.add(Category(name=cat_name))
    db.session.commit()
    print("Категории созданы")

    cat_turbofan = Category.query.filter_by(name='Турбовентиляторные').first()
    cat_turboprop = Category.query.filter_by(name='Турбовинтовые').first()
    cat_turboshaft = Category.query.filter_by(name='Турбовальные').first()
    cat_ground = Category.query.filter_by(name='Наземные ГТД').first()

    # ДВИГАТЕЛИ С ФОТО
    products_data = [
        {'category': cat_turbofan, 'name': 'ПД-14', 'thrust_kgf': 14000, 'application': 'МС-21', 'description': 'Турбовентиляторный двигатель 14000 кгс для МС-21.', 'image_url': '/static/uploads/pd14.jpg'},
        {'category': cat_turbofan, 'name': 'ПД-8', 'thrust_kgf': 8000, 'application': 'SJ-100, Бе-200', 'description': 'Двигатель 8000 кгс для импортозамещения SaM146.', 'image_url': '/static/uploads/pd8.jpg'},
        {'category': cat_turbofan, 'name': 'ПС-90А', 'thrust_kgf': 16000, 'application': 'Ту-204/214, Ил-96', 'description': 'Турбовентиляторный двухконтурный двигатель.', 'image_url': '/static/uploads/ps90a.jpg'},
        {'category': cat_turboprop, 'name': 'ТВ7-117СТ-01', 'power_hp': 3000, 'application': 'Ил-114, ТВРС-44 Ладога', 'description': 'Турбовинтовой двигатель 3000 л.с.', 'image_url': '/static/uploads/tv17.jpg'},
        {'category': cat_turboshaft, 'name': 'ВК-650В', 'power_hp': 650, 'application': 'Ансат, Ка-226Т', 'description': 'Турбовальный двигатель 650 л.с.', 'image_url': '/static/uploads/vk650v.jpg'},
        {'category': cat_turboshaft, 'name': 'ВК-1600В', 'power_hp': 1600, 'application': 'Ка-62', 'description': 'Турбовальный двигатель 1600 л.с.', 'image_url': '/static/uploads/vk1600v.jpg'},
        {'category': cat_ground, 'name': 'ГТД-110М', 'thrust_kgf': None, 'power_hp': 156356, 'application': 'Газотурбинные электростанции', 'description': 'Наземный газотурбинный двигатель 115 МВт.', 'image_url': '/static/uploads/gtd110m.jpg'},
    ]

    admin_user = User.query.filter_by(login='admin').first()
    for p in products_data:
        if not Product.query.filter_by(name=p['name']).first():
            product = Product(
                category_id=p['category'].id,
                created_by=admin_user.id,
                name=p['name'],
                thrust_kgf=p.get('thrust_kgf'),
                power_hp=p.get('power_hp'),
                application=p.get('application'),
                description=p.get('description'),
                image_url=p.get('image_url')
            )
            db.session.add(product)
    db.session.commit()
    print("База данных заполнена двигателями с фото!")