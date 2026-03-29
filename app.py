import os
from flask import Flask, session, redirect, url_for, request, render_template, abort, jsonify

import stripe
import base64
import json
import hashlib
import requests
# ------------------- TELEGRAM -------------------
TELEGRAM_BOT_TOKEN = "8587678939:AAEPhzJHAgCNIdLudispbfkgISMyaKiFYbs"
TELEGRAM_CHAT_ID = "1885493899"

def send_telegram(message):
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    params = {"chat_id": TELEGRAM_CHAT_ID, "text": message, "parse_mode": "HTML"}
    response = requests.post(url, params=params)
    print("Telegram response:", response.text)

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", os.urandom(24))
template_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'templates')
static_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static')
app.template_folder = template_dir
app.static_folder = static_dir

# ------------------- STRIPE -------------------
stripe.api_key = os.environ.get("STRIPE_SECRET_KEY")
STRIPE_PUBLIC_KEY = os.environ.get("STRIPE_PUBLIC_KEY")

# ------------------- LIQPAY -------------------
LIQPAY_PUBLIC_KEY = "sandbox_i28736764684"
LIQPAY_PRIVATE_KEY = "sandbox_Ph5aKw5bEOknDA2tKoFAgI5d0BNisSHI5hfNB9NK"

class LiqPay:
    def __init__(self, public_key, private_key):
        self.public_key = public_key
        self.private_key = private_key

    def cnb_form(self, data):
        data['public_key'] = self.public_key
        json_data = json.dumps(data)
        data_base64 = base64.b64encode(json_data.encode('utf-8')).decode('utf-8')
        sign = base64.b64encode(
            hashlib.sha1((self.private_key + data_base64 + self.private_key).encode('utf-8')).digest()
        ).decode('utf-8')
        form = f'''
        <form method="POST" action="https://www.liqpay.ua/api/3/checkout" accept-charset="utf-8">
            <input type="hidden" name="data" value="{data_base64}" />
            <input type="hidden" name="signature" value="{sign}" />
            <button type="submit" class="btn btn-warning w-100">Оплатити LiqPay</button>
        </form>
        '''
        return form

liqpay = LiqPay(LIQPAY_PUBLIC_KEY, LIQPAY_PRIVATE_KEY)

# ------------------- ТОВАРИ -------------------
products = [
    {
        "id": 1,
        "name": "Vintage Wash Denim",
        "price": 1190,
        "img": [
            "https://i.postimg.cc/wMMt4jw1/avif.avif",
            "https://i.postimg.cc/SNJQhM7p/avif.avif",
            "https://i.postimg.cc/tRtMtC6j/avif.avif"
        ],
        "category": "jeans"
    },
    {
        "id": 2,
        "name": "Washed Vintage Tee",
        "price": 790,
        "img": [
            "https://i.postimg.cc/pLXbn51t/avif.avif",
            "https://i.postimg.cc/qqRdGPM5/avif.avif"
        ],
        "category": "tshirt"
    },
    {
        "id": 3,
        "name": "Street Basic Hoodie",
        "price": 1200,
        "img": [
            "https://i.postimg.cc/0NSLf9M2/avif.avif",
            "https://i.postimg.cc/vZ1hjQ4h/avif.avif"
        ],
        "category": "hoodie"
    },
    {
        "id": 4,
        "name": "Vintage Fade Hoodie",
        "price": 750,
        "img": [
            "https://i.postimg.cc/3xkj4BWv/avif.avif",
            "https://i.postimg.cc/kXGv6nFv/avif.avif",
            "https://i.postimg.cc/SKF6vcFx/avif.avif"
        ],
        "category": "hoodie"
    },
    {
        "id": 5,
        "name": "Minimal Logo Tee",
        "price": 900,
        "img": [
            "https://i.postimg.cc/mDmhyv5C/avif.avif",
            "https://i.postimg.cc/KY2TNFLd/avif.avif",
            "https://i.postimg.cc/4NvhBybg/avif.avif"
        ],
        "category": "tshirt"
    },
    {
        "id": 6,
        "name": "Baldwin Fit Tee",
        "price": 790,
        "img": [
            "https://img.kwcdn.com/product/open/5b5012960e7646ac9cb8787dd60facf0-goods.jpeg?imageView2/2/w/800/q/70/format/avif",
            "https://i.postimg.cc/fbCVfdMY/avif.avif"
        ],
        "category": "tshirt"
    },
    {
        "id": 7,
        "name": "Alley Denim",
        "price": 900,
        "img": [
            "https://i.postimg.cc/2SntLr1g/avif.avif",
            "https://i.postimg.cc/g0g0ZPKM/avif.avif",
            "https://i.postimg.cc/4nR4g4JN/avif.avif",
            "https://i.postimg.cc/9QttR1Nt/avif.avif"
        ],
        "category": "jeans"
    },

    {
        "id": 8,
        "name": "Trap Zone zip",
        "price": 1200,
        "img": [
            "https://i.postimg.cc/MKcD2XgR/avif.avif",
            "https://i.postimg.cc/mZ1wKtvX/avif.avif"

        ],
        "category": "hoodie"
    },
    {
        "id": 9,
        "name": "Night Grip",
        "price": 750,
        "img": [
            "https://i.postimg.cc/8C3vbbPn/avif.avif",
            "https://i.postimg.cc/gkJYYbKq/avif.avif",
            "https://i.postimg.cc/ncCtyYFf/avif.avif"
        ],
        "category": "hoodie"
    },
    {
        "id": 10,
        "name": "Walk with God",
        "price": 900,
        "img": [
            "https://i.postimg.cc/tg1Z7Vtr/avif.avif",
            "https://i.postimg.cc/mkTg3cCk/avif.avif"
        ],
        "category": "tshirt"
    },
    {
        "id": 11,
        "name": "Hood Pass",
        "price": 900,
        "img": [
            "https://i.postimg.cc/W15YTxXM/avif.avif"
        ],
        "category": "Hood Pass"
    },
    {
        "id": 12,
        "name": "",
        "price": 100,
        "img": [
            ""
        ],
        "category": "accessories"
    }
]

for index, product in enumerate(products, start=1):
    if "id" not in product:
        product["id"] = index

# ------------------- Виправлення Jinja2 -------------------
for product in products:
    product['images'] = product['img']

# ------------------- ДОПОМІЖНІ -------------------
def get_cart_data():
    cart = session.get("cart", {})
    items = []
    total = 0
    for pid, qty in cart.items():
        product = next((p for p in products if p["id"] == int(pid)), None)
        if product:
            subtotal = product["price"] * qty
            total += subtotal
            items.append({"product": product, "qty": qty, "subtotal": subtotal})
    return items, total

def get_cart_count():
    return sum(session.get("cart", {}).values())

@app.before_request
def initialize_cart():
    if "cart" not in session:
        session["cart"] = {}

# ------------------- ФУНКЦІЇ -------------------
@app.route("/")
def index():
    return render_template("index.html", products=products, cart_count=get_cart_count())

@app.route("/category/<string:category_name>")
def category_page(category_name):
    filtered_products = [p for p in products if p["category"].lower() == category_name.lower()]
    if not filtered_products:
        abort(404)
    return render_template("category.html", products=filtered_products,
                           category_name=category_name.capitalize(),
                           cart_count=get_cart_count())

@app.route("/product/<int:product_id>")
def product_page(product_id):
    product = next((p for p in products if p["id"] == product_id), None)
    if not product:
        abort(404)
    return render_template("product.html", product=product, cart_count=get_cart_count())

@app.route("/add/<int:product_id>", methods=["POST"])
def add_to_cart(product_id):
    cart = session.get("cart", {})
    pid = str(product_id)
    cart[pid] = cart.get(pid, 0) + 1
    session["cart"] = cart
    return redirect(request.referrer or url_for("index"))

@app.route("/quick_add/<int:product_id>", methods=["POST"])
def quick_add(product_id):
    cart = session.get("cart", {})
    pid = str(product_id)
    cart[pid] = cart.get(pid, 0) + 1
    session["cart"] = cart
    session.modified = True
    return jsonify({"success": True, "cart_count": sum(cart.values())})

@app.route("/update/<int:product_id>", methods=["POST"])
def update_cart(product_id):
    cart = session.get("cart", {})
    pid = str(product_id)
    action = request.form.get("action")
    if action == "plus":
        cart[pid] = cart.get(pid, 0) + 1
    elif action == "minus":
        if cart.get(pid, 0) > 1:
            cart[pid] -= 1
        else:
            cart.pop(pid, None)
    session["cart"] = cart
    return redirect(url_for("view_cart"))

@app.route("/clear", methods=["POST"])
def clear_cart():
    session["cart"] = {}
    return redirect(url_for("view_cart"))

@app.route("/cart")
def view_cart():
    items, total = get_cart_data()
    return render_template("cart.html", cart_items=items, total=total, cart_count=get_cart_count())

# ------------------- Checkout -------------------
@app.route("/checkout", methods=["GET", "POST"])
def checkout():
    cart_items, total = get_cart_data()
    if not cart_items:
        return redirect(url_for("index"))

    success = False
    name = phone = city = warehouse = ""

    if request.method == "POST":
        name = request.form.get("name")
        phone = request.form.get("phone")
        city = request.form.get("city")
        warehouse = request.form.get("warehouse")
        payment = request.form.get("payment")

        if not name or not phone or not city or not warehouse:
            return "Заповніть всі поля"

        success = True
        session["cart"] = {}

        # ---------- Telegram ----------
        message = f"🛒 <b>Нове замовлення!</b>\n"
        message += f"Ім'я: {name}\n"
        message += f"Телефон: {phone}\n"
        message += f"Місто: {city}\n"
        message += f"Відділення: {warehouse}\n\nТовари:\n"
        for item in cart_items:
            message += f"{item['product']['name']} x{item['qty']} = {item['subtotal']} грн\n"
        message += f"Всього: {total} грн"

        send_telegram(message)

    return render_template("checkout.html",
                           success=success,
                           cart_items=cart_items,
                           total=total,
                           name=name,
                           phone=phone,
                           city=city,
                           warehouse=warehouse,
                           stripe_public_key=STRIPE_PUBLIC_KEY)

# ------------------- Купівля одного товару -------------------
@app.route("/buy/<int:product_id>", methods=["GET", "POST"])
def buy_now(product_id):
    product = next((p for p in products if p["id"] == product_id), None)
    if not product:
        abort(404)

    success = False
    name = phone = city = warehouse = ""

    if request.method == "POST":
        name = request.form.get("name")
        phone = request.form.get("phone")
        city = request.form.get("city")
        warehouse = request.form.get("warehouse")

        if not name or not phone or not city or not warehouse:
            return "Заповніть всі поля"

        success = True

        message = f"🛒 <b>Нове замовлення!</b>\n"
        message += f"Ім'я: {name}\n"
        message += f"Телефон: {phone}\n"
        message += f"Місто: {city}\n"
        message += f"Відділення: {warehouse}\n"
        message += f"Товар: {product['name']}\n"
        message += f"Ціна: {product['price']} грн"

        send_telegram(message)

    return render_template("checkout.html",
                           success=success,
                           product=product,
                           single=True,
                           name=name,
                           phone=phone,
                           city=city,
                           warehouse=warehouse,
                           stripe_public_key=STRIPE_PUBLIC_KEY)

# ------------------- Stripe -------------------
@app.route("/create-checkout-session", methods=["POST"])
def create_checkout_session():
    product_id = request.json.get("product_id")
    if product_id:
        product = next((p for p in products if p["id"] == int(product_id)), None)
        if not product:
            return jsonify({"error": "Товар не знайдено"}), 404
        line_items = [{
            'price_data': {
                'currency': 'uah',
                'product_data': {'name': product["name"]},
                'unit_amount': product["price"] * 100,
            },
            'quantity': 1,
        }]
    else:
        items, _ = get_cart_data()
        line_items = [{
            'price_data': {
                'currency': 'uah',
                'product_data': {'name': item['product']['name']},
                'unit_amount': item['product']['price'] * 100,
            },
            'quantity': item['qty'],
        } for item in items]

    session_stripe = stripe.checkout.Session.create(
        payment_method_types=["card"],
        line_items=line_items,
        mode='payment',
        success_url="http://localhost:5000/success",
        cancel_url="http://localhost:5000/cancel",
    )
    return jsonify({'id': session_stripe.id})

# ------------------- LiqPay -------------------
@app.route("/liqpay-pay", methods=["POST"])
def liqpay_pay():
    product_id = request.form.get("product_id")
    if product_id:
        product = next((p for p in products if p["id"] == int(product_id)), None)
        if not product:
            return "Товар не знайдено", 404
        amount = product["price"]
        description = f"Оплата {product['name']}"
    else:
        _, total = get_cart_data()
        amount = total
        description = "Оплата кошика товарів"

    data = {
        "action": "pay",
        "amount": amount,
        "currency": "UAH",
        "description": description,
        "order_id": "order_" + str(os.urandom(4).hex()),
        "version": "3",
        "sandbox": 1
    }

    html = liqpay.cnb_form(data)
    return html

@app.route("/success")
def success():
    return "Оплата пройшла успішно!"

@app.route("/cancel")
def cancel():
    return "Оплата була скасована."


@app.route('/catalog')
def catalog():
    return render_template('catalog.html', products=products, cart_count=get_cart_count())

@app.route('/contacts')
def contacts():
    return render_template('contacts.html')


@app.route("/update/<int:product_id>", methods=["POST"])
def update_carts(product_id):
    cart = session.get("cart", {})
    pid = str(product_id)
    action = request.form.get("action")
    if action == "plus":
        cart[pid] = cart.get(pid, 0) + 1
    elif action == "minus":
        if cart.get(pid, 0) > 1:
            cart[pid] -= 1
        else:
            cart.pop(pid, None)
    elif action == "remove":   # додай цю гілку
        cart.pop(pid, None)
    session["cart"] = cart
    return redirect(url_for("view_cart"))


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)