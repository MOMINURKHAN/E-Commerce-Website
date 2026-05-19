from flask import Flask, render_template, request, redirect, url_for, session

app = Flask(__name__)
app.secret_key = "my_simple_ecommerce_123"

# PRODUCTS WITH CATEGORIES
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

def get_product_by_id(product_id):
    return next((p for p in products if p["id"] == product_id), None)

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

@app.route('/search')
def search():
    query = request.args.get('q', '').lower()
    results = [p for p in products if query in p['name'].lower() or query in p['desc'].lower()]
    return render_template("products.html", items=results, query=query)

@app.route('/product/<int:product_id>')
def product_detail(product_id):
    product = get_product_by_id(product_id)
    if not product:
        return redirect(url_for('show_products'))
    return render_template('product_detail.html', product=product)

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

@app.route('/about')
def about():
    return render_template("about.html")

@app.route('/contact')
def contact():
    return render_template("contact.html")

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=10000)