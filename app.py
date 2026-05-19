from flask import Flask, render_template, request, redirect, url_for, session

app = Flask(__name__)
# Required for cart to work (secret key)
app.secret_key = "my_simple_ecommerce_123"

# Sample products
products = [
    {
        "id": 1,
        "name": "Basic T-Shirt",
        "price": 15.99,
        "desc": "Comfortable casual daily wear",
        "img": "tshirt.jpg"
    },
    {
        "id": 2,
        "name": "Sports Shoes",
        "price": 49.99,
        "desc": "Lightweight running shoes",
        "img": "shoes.jpg"
    },
    {
        "id": 3,
        "name": "Casual Bag",
        "price": 25.50,
        "desc": "Large capacity student bag",
        "img": "bag.jpg"
    }
]

# Helper: Get product by ID
def get_product_by_id(product_id):
    return next((p for p in products if p["id"] == product_id), None)

# Homepage
@app.route('/')
def home():
    return render_template("index.html")

# Show all products
@app.route('/products')
def show_products():
    return render_template("products.html", items=products)

# ADD TO CART (CORE LOGIC HERE)
@app.route('/add-to-cart/<int:product_id>')
def add_to_cart(product_id):
    product = get_product_by_id(product_id)

    if not product:
        return redirect(url_for('show_products'))

    # Initialize cart if empty
    if 'cart' not in session:
        session['cart'] = []

    # Add product to cart
    session['cart'].append(product)
    # Save session
    session.modified = True

    return redirect(url_for('cart_page'))

# Add this function BEFORE the cart routes
@app.route('/product/<int:product_id>')
def product_detail(product_id):
    product = get_product_by_id(product_id)
    if not product:
        return redirect(url_for('show_products'))
    return render_template('product_detail.html', product=product)
# Cart page
@app.route('/cart')
def cart_page():
    cart_items = session.get('cart', [])
    total = sum(item['price'] for item in cart_items)
    return render_template('cart.html', items=cart_items, total=total)

# Clear cart
@app.route('/clear-cart')
def clear_cart():
    session.pop('cart', None)
    return redirect(url_for('cart_page'))

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=10000)