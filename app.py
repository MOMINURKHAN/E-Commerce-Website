from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

app = Flask(__name__)
app.secret_key = "my_simple_ecommerce_123"

# DATABASE
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# LOGIN
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# MODELS
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    orders = db.relationship('Order', backref='user', lazy=True)

class Order(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    fullname = db.Column(db.String(200))
    address = db.Column(db.String(500))
    phone = db.Column(db.String(20))
    total = db.Column(db.Float, nullable=False)
    date = db.Column(db.DateTime, default=datetime.utcnow)
    items = db.Column(db.Text, nullable=False)

# PRODUCTS
products = [
    {"id": 1, "name": "Basic T-Shirt", "price": 15.99, "category": "Clothing", "desc": "Soft cotton casual t-shirt.", "img": "tshirt.jpg"},
    {"id": 2, "name": "Sports Shoes", "price": 49.99, "category": "Shoes", "desc": "Lightweight running shoes.", "img": "shoes.jpg"},
    {"id": 3, "name": "Casual Bag", "price": 25.50, "category": "Bags", "desc": "Spacious daily use bag.", "img": "bag.jpg"},
    {"id": 4, "name": "Sunglasses", "price": 12.99, "category": "Accessories", "desc": "UV protection stylish glasses.", "img": "sunglasses.jpg"},
    {"id": 5, "name": "Watch", "price": 35.99, "category": "Accessories", "desc": "Classic analog wrist watch.", "img": "watch.jpg"},
    {"id": 6, "name": "Cap", "price": 9.99, "category": "Accessories", "desc": "Breathable cotton sport cap.", "img": "cap.jpg"},
    {"id": 7, "name": "Backpack", "price": 39.99, "category": "Bags", "desc": "Large travel backpack.", "img": "backpack.jpg"},
    {"id": 8, "name": "Wallet", "price": 18.50, "category": "Accessories", "desc": "Leather stylish wallet.", "img": "wallet.jpg"},
    {"id": 9, "name": "Water Bottle", "price": 8.99, "category": "Accessories", "desc": "Steel water bottle.", "img": "bottle.jpg"},
    {"id": 10, "name": "Hoodie", "price": 29.99, "category": "Clothing", "desc": "Warm winter hoodie.", "img": "hoodie.jpg"},
    {"id": 11, "name": "Socks Pack", "price": 5.99, "category": "Clothing", "desc": "5 pair soft cotton socks.", "img": "socks.jpg"}
]

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

def get_product_by_id(product_id):
    return next((p for p in products if p["id"] == product_id), None)

# HOME
@app.route('/')
def home():
    categories = list(set(p['category'] for p in products))
    return render_template("index.html", categories=categories)

# SHOP
@app.route('/products')
def show_products():
    return render_template("products.html", items=products)

@app.route('/category/<category_name>')
def category_page(category_name):
    filtered = [p for p in products if p['category'] == category_name]
    return render_template("products.html", items=filtered, category=category_name)

# SEARCH & FILTER
@app.route('/search')
def search():
    query = request.args.get('q', '').lower()
    results = [p for p in products if query in p['name'].lower() or query in p['desc'].lower()]
    return render_template("products.html", items=results, query=query)

@app.route('/filter-price')
def filter_price():
    min_p = float(request.args.get('min', 0))
    max_p = float(request.args.get('max', 1000))
    filtered = [p for p in products if min_p <= p['price'] <= max_p]
    return render_template("products.html", items=filtered)

# PRODUCT DETAIL
@app.route('/product/<int:product_id>')
def product_detail(product_id):
    product = get_product_by_id(product_id)
    if not product:
        return redirect(url_for('show_products'))
    related = [p for p in products if p['category'] == product['category'] and p['id'] != product_id][:4]
    return render_template('product_detail.html', product=product, related=related)

# CART
@app.route('/add-to-cart/<int:product_id>')
def add_to_cart(product_id):
    product = get_product_by_id(product_id)
    if not product:
        return redirect(url_for('show_products'))
    if 'cart' not in session:
        session['cart'] = []
    session['cart'].append(product)
    session.modified = True
    return redirect(url_for('cart_page'))

@app.route('/cart')
def cart_page():
    cart_items = session.get('cart', [])
    total = sum(item['price'] for item in cart_items)
    return render_template("cart.html", items=cart_items, total=total)

@app.route('/remove-from-cart/<int:index>')
def remove_from_cart(index):
    if 'cart' in session:
        cart = session['cart']
        if 0 <= index < len(cart):
            cart.pop(index)
            session['cart'] = cart
    return redirect(url_for('cart_page'))

@app.route('/clear-cart')
def clear_cart():
    session.pop('cart', None)
    return redirect(url_for('cart_page'))

# CHECKOUT & ORDER
@app.route('/checkout')
@login_required
def checkout():
    cart_items = session.get('cart', [])
    total = sum(i['price'] for i in cart_items)
    return render_template("checkout.html", items=cart_items, total=total)

@app.route('/payment', methods=["GET","POST"])
@login_required
def payment():
    if request.method=="POST":
        name = request.form.get("fullname")
        phone = request.form.get("phone")
        address = request.form.get("address")
        cart = session.get('cart', [])
        total = sum(i['price'] for i in cart)
        items_str = ", ".join([i['name'] for i in cart])
        order = Order(user_id=current_user.id, fullname=name, address=address, phone=phone, total=total, items=items_str)
        db.session.add(order)
        db.session.commit()
        return render_template("payment.html")
    return redirect(url_for("checkout"))

@app.route('/order-success')
@login_required
def order_success():
    session.pop('cart', None)
    return render_template("success.html")

# USER DASHBOARD
@app.route('/dashboard')
@login_required
def dashboard():
    orders = Order.query.filter_by(user_id=current_user.id).order_by(Order.date.desc()).all()
    return render_template("dashboard.html", orders=orders)

# LOGIN / SIGNUP
@app.route('/login', methods=['GET','POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        user = User.query.filter_by(email=email).first()
        if user and check_password_hash(user.password, password):
            login_user(user)
            return redirect(url_for('home'))
        else:
            return "Invalid email or password"
    return render_template('login.html')

@app.route('/signup', methods=['GET','POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = generate_password_hash(request.form['password'])
        new_user = User(username=username, email=email, password=password)
        db.session.add(new_user)
        db.session.commit()
        return redirect(url_for('login'))
    return render_template('signup.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('home'))

# PAGES
@app.route('/about')
def about():
    return render_template("about.html")

@app.route('/contact')
def contact():
    return render_template("contact.html")

# CREATE DB
with app.app_context():
    db.create_all()

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=10000)