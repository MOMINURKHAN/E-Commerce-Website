from flask import Flask, render_template, request, redirect, url_for, session
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

# ------------------------------
# MODELS
# ------------------------------
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    is_admin = db.Column(db.Boolean, default=False)
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

class Wishlist(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    product_id = db.Column(db.Integer, nullable=False)

class Review(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    rating = db.Column(db.Integer, nullable=False)
    comment = db.Column(db.Text)
    date = db.Column(db.DateTime, default=datetime.utcnow)
    user = db.relationship('User', backref='reviews')

# ------------------------------
# PRODUCTS (25 PRODUCTS)
# ------------------------------
products = [
    {"id": 1, "name": "Basic Cotton T-Shirt", "price": 14.99, "category": "Clothing", "desc": "Soft, breathable, regular fit.", "img": "tshirt.jpg"},
    {"id": 2, "name": "Running Sports Shoes", "price": 54.99, "category": "Shoes", "desc": "Lightweight, comfortable for running.", "img": "shoes.jpg"},
    {"id": 3, "name": "Casual Shoulder Bag", "price": 27.50, "category": "Bags", "desc": "Spacious, stylish daily use bag.", "img": "bag.jpg"},
    {"id": 4, "name": "UV Protection Sunglasses", "price": 13.99, "category": "Accessories", "desc": "Stylish sunglasses with UV protection.", "img": "sunglasses.jpg"},
    {"id": 5, "name": "Analog Wrist Watch", "price": 38.99, "category": "Accessories", "desc": "Classic design, long battery life.", "img": "watch.jpg"},
    {"id": 6, "name": "Sports Cotton Cap", "price": 8.99, "category": "Accessories", "desc": "Breathable, adjustable size.", "img": "cap.jpg"},
    {"id": 7, "name": "Large Travel Backpack", "price": 42.99, "category": "Bags", "desc": "Waterproof, durable, large capacity.", "img": "backpack.jpg"},
    {"id": 8, "name": "Genuine Leather Wallet", "price": 19.50, "category": "Accessories", "desc": "Slim, stylish, card slots.", "img": "wallet.jpg"},
    {"id": 9, "name": "Steel Water Bottle", "price": 9.49, "category": "Accessories", "desc": "Cold & hot insulation.", "img": "bottle.jpg"},
    {"id": 10, "name": "Winter Warm Hoodie", "price": 31.99, "category": "Clothing", "desc": "Soft fleece inside, warm.", "img": "hoodie.jpg"},
    {"id": 11, "name": "Cotton Socks 5 Pair", "price": 6.49, "category": "Clothing", "desc": "Soft, stretchable, comfortable.", "img": "socks.jpg"},
    {"id": 12, "name": "Denim Jeans", "price": 34.99, "category": "Clothing", "desc": "Regular fit, durable fabric.", "img": "jeans.jpg"},
    {"id": 13, "name": "Leather Belt", "price": 11.99, "category": "Accessories", "desc": "Genuine leather, adjustable.", "img": "belt.jpg"},
    {"id": 14, "name": "Formal Shoes", "price": 49.99, "category": "Shoes", "desc": "For office, party, casual wear.", "img": "formalshoes.jpg"},
    {"id": 15, "name": "Laptop Sleeve Bag", "price": 22.99, "category": "Bags", "desc": "Protective, lightweight.", "img": "laptopbag.jpg"},
    {"id": 16, "name": "Wireless Earbuds", "price": 29.99, "category": "Gadgets", "desc": "Good sound, long battery.", "img": "earbuds.jpg"},
    {"id": 17, "name": "Phone Cover", "price": 12.99, "category": "Gadgets", "desc": "Shockproof, stylish design.", "img": "phonecover.jpg"},
    {"id": 18, "name": "Sunglasses Sport", "price": 15.99, "category": "Accessories", "desc": "For cycling, running, outdoor.", "img": "sportsunglass.jpg"},
    {"id": 19, "name": "Polo Shirt", "price": 18.99, "category": "Clothing", "desc": "Smart fit, casual wear.", "img": "polo.jpg"},
    {"id": 20, "name": "Jacket Windbreaker", "price": 39.99, "category": "Clothing", "desc": "Windproof, rainproof, lightweight.", "img": "jacket.jpg"},
    {"id": 21, "name": "Travel Duffel Bag", "price": 35.99, "category": "Bags", "desc": "For travel, gym, luggage.", "img": "duffel.jpg"},
    {"id": 22, "name": "Canvas Shoes", "price": 29.99, "category": "Shoes", "desc": "Casual, comfortable, stylish.", "img": "canvasshoes.jpg"},
    {"id": 23, "name": "Hair Band", "price": 4.99, "category": "Accessories", "desc": "Elastic, for sports & daily use.", "img": "hairband.jpg"},
    {"id": 24, "name": "Key Chain", "price": 3.99, "category": "Accessories", "desc": "Stylish metal key ring.", "img": "keychain.jpg"},
    {"id": 25, "name": "Face Mask Pack 10", "price": 5.99, "category": "Health", "desc": "Disposable, breathable, safe.", "img": "mask.jpg"}
]

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

def get_product_by_id(product_id):
    return next((p for p in products if p["id"] == product_id), None)

# ------------------------------
# HOME & CATEGORIES
# ------------------------------
@app.route('/')
def home():
    categories = list(set(p['category'] for p in products))
    return render_template("index.html", categories=categories)

@app.route('/products')
def show_products():
    return render_template("products.html", items=products)

@app.route('/category/<category_name>')
def category_page(category_name):
    filtered = [p for p in products if p['category'] == category_name]
    return render_template("products.html", items=filtered, category=category_name)

# ------------------------------
# SEARCH & FILTER
# ------------------------------
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

# ------------------------------
# PRODUCT DETAIL
# ------------------------------
@app.route('/product/<int:product_id>')
def product_detail(product_id):
    product = get_product_by_id(product_id)
    if not product:
        return redirect(url_for('show_products'))
    
    # Get reviews for this product
    reviews = Review.query.filter_by(product_id=product_id).all()
    
    return render_template('product_detail.html', product=product, reviews=reviews)
#-----------------------
# WISHLIST
#-----------------------    
@app.route('/add-to-wishlist/<int:product_id>')
@login_required
def add_to_wishlist(product_id):
    exists = Wishlist.query.filter_by(user_id=current_user.id, product_id=product_id).first()
    if not exists:
        w = Wishlist(user_id=current_user.id, product_id=product_id)
        db.session.add(w)
        db.session.commit()
    return redirect(url_for('wishlist_page'))

@app.route('/wishlist')
@login_required
def wishlist_page():
    w = Wishlist.query.filter_by(user_id=current_user.id).all()
    prods = [get_product_by_id(x.product_id) for x in w]
    return render_template('wishlist.html', products=prods)

@app.route('/remove-wishlist/<int:product_id>')
@login_required
def remove_wishlist(product_id):
    item = Wishlist.query.filter_by(user_id=current_user.id, product_id=product_id).first()
    if item:
        db.session.delete(item)
        db.session.commit()
    return redirect(url_for('wishlist_page'))

#------------------------------
# Reivew
#------------------------------
@app.route('/add-review/<int:product_id>', methods=['POST'])
@login_required
def add_review(product_id):
    r = request.form.get('rating')
    c = request.form.get('comment')
    rev = Review(product_id=product_id, user_id=current_user.id, rating=r, comment=c)
    db.session.add(rev)
    db.session.commit()
    return redirect(f'/product/{product_id}')

# ------------------------------
# CART
# ------------------------------
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

# ------------------------------
# CHECKOUT & ORDER
# ------------------------------
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
        
        return redirect(url_for('order_success'))
    
    return redirect(url_for("checkout"))

@app.route('/order-success')
@login_required
def order_success():
    session.pop('cart', None)
    return render_template("success.html")

# ------------------------------
# USER PROFILE
# ------------------------------
@app.route('/profile', methods=['GET','POST'])
@login_required
def profile():
    if request.method == 'POST':
        new_name = request.form['username']
        new_pass = request.form['password']
        
        current_user.username = new_name
        if new_pass:
            current_user.password = generate_password_hash(new_pass)
        
        db.session.commit()
        return redirect(url_for('dashboard'))
    
    return render_template('profile.html')

# ------------------------------
# USER DASHBOARD
# ------------------------------
@app.route('/dashboard')
@login_required
def dashboard():
    orders = Order.query.filter_by(user_id=current_user.id).order_by(Order.date.desc()).all()
    return render_template("dashboard.html", orders=orders)

# ------------------------------
# ADMIN PANEL
# ------------------------------
@app.route('/admin')
@login_required
def admin_panel():
    if not current_user.is_admin:
        return "Access Denied! Only admin can enter"
    all_users = User.query.all()
    all_orders = Order.query.order_by(Order.date.desc()).all()
    return render_template("admin.html", users=all_users, orders=all_orders)

@app.route('/make-admin/<int:user_id>')
@login_required
def make_admin(user_id):
    if not current_user.is_admin:
        return "No permission"
    user = User.query.get(user_id)
    if user:
        user.is_admin = True
        db.session.commit()
    return redirect(url_for('admin_panel'))

# ------------------------------
# LOGIN / SIGNUP / LOGOUT
# ------------------------------
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

# ------------------------------
# PAGES
# ------------------------------
@app.route('/about')
def about():
    return render_template("about.html")

@app.route('/contact')
def contact():
    return render_template("contact.html")

# ------------------------------
# CREATE DATABASE
# ------------------------------
with app.app_context():
    db.create_all()
# ------------------------------
# AUTO ADMIN - PERMANENT FIX
# ------------------------------
with app.app_context():
    db.create_all()
    # AUTO MAKE YOU ADMIN FOREVER
    admin_email = "khanmominul527@gmail.com"
    admin_user = User.query.filter_by(email=admin_email).first()
    if admin_user:
        admin_user.is_admin = True
        db.session.commit()
        print("✅ AUTO ADMIN ENABLED FOR YOUR ACCOUNT")

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=10000, debug= True)