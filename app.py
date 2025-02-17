from flask import Flask, request, jsonify, session
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_cors import CORS

app = Flask(__name__)

# ✅ Updated to MySQL
app.config["SQLALCHEMY_DATABASE_URI"] = "mysql://sql7762208:MqFJpHymhB@sql7.freesqldatabase.com/sql7762208"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SECRET_KEY"] = "your_secret_key"

db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
CORS(app)

# ✅ Database Models
class Company(db.Model):
    companyId = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    companyName = db.Column(db.String(120))
    vendingMachineNum = db.Column(db.Integer)
    email = db.Column(db.String(120))
    phone = db.Column(db.String(20))
    address = db.Column(db.String(200))
    date = db.Column(db.DateTime)

class Client(db.Model):
    clientId = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    date = db.Column(db.DateTime)

class Purchase(db.Model):
    purchaseId = db.Column(db.Integer, primary_key=True)
    clientId = db.Column(db.Integer, db.ForeignKey('client.clientId'))
    price = db.Column(db.Float)
    date = db.Column(db.DateTime)

class Sale(db.Model):
    saleId = db.Column(db.Integer, primary_key=True)
    productCode = db.Column(db.String(20))
    productName = db.Column(db.String(100))
    salePrice = db.Column(db.Float)
    saleTime = db.Column(db.DateTime)

# ✅ Login Route (No Change)
@app.route('/login', methods=['POST'])
def login():
    data = request.json
    username = data.get('username')
    password = data.get('password')

    company = Company.query.filter_by(username=username).first()
    if company and bcrypt.check_password_hash(company.password, password):
        session['user'] = {'id': company.companyId, 'role': 'company'}
        return jsonify({'redirect': 'company_dashboard'})

    client = Client.query.filter_by(username=username).first()
    if client and bcrypt.check_password_hash(client.password, password):
        session['user'] = {'id': client.clientId, 'role': 'client'}
        return jsonify({'redirect': 'client_dashboard'})

    return jsonify({'error': 'Invalid username or password'}), 401

# ✅ Client Dashboard Data (No Change)
@app.route('/client_dashboard', methods=['GET'])
def client_dashboard():
    if 'user' not in session or session['user']['role'] != 'client':
        return jsonify({'error': 'Unauthorized'}), 403

    client_id = session['user']['id']
    purchases = Purchase.query.filter_by(clientId=client_id).all()
    purchase_list = [{'date': p.date, 'price': p.price} for p in purchases]

    return jsonify({'purchases': purchase_list})

# ✅ Company Dashboard Data (No Change)
@app.route('/company_dashboard', methods=['GET'])
def company_dashboard():
    if 'user' not in session or session['user']['role'] != 'company':
        return jsonify({'error': 'Unauthorized'}), 403

    sales = Sale.query.all()
    sales_list = [{'product': s.productName, 'code': s.productCode, 'price': s.salePrice, 'time': s.saleTime} for s in sales]

    return jsonify({'sales': sales_list})

# ✅ Update Prices Route (No Change)
@app.route('/update_prices', methods=['POST'])
def update_prices():
    if 'user' not in session or session['user']['role'] != 'company':
        return jsonify({'error': 'Unauthorized'}), 403

    data = request.json
    updated_prices = data.get('prices', [])

    for item in updated_prices:
        sale = Sale.query.filter_by(productCode=item['code']).first()
        if sale:
            sale.salePrice = float(item['new_price'])

    db.session.commit()
    return jsonify({'message': 'Prices updated successfully'})

if __name__ == '__main__':
    app.run(debug=True)
