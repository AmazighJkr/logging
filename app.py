from flask import Flask, request, jsonify, session, redirect, url_for
from flask_mysqldb import MySQL
from flask_bcrypt import Bcrypt
from flask_cors import CORS

app = Flask(__name__)
CORS(app)
bcrypt = Bcrypt(app)
app.secret_key = 'your_secret_key'  # Keep this secure!

# MySQL Database Configuration
app.config["MYSQL_HOST"] = "sql7.freesqldatabase.com"
app.config["MYSQL_USER"] = "sql7762208"
app.config["MYSQL_PASSWORD"] = "MqFJpHymhB"
app.config["MYSQL_DB"] = "sql7762208"
app.config["MYSQL_PORT"] = 3306

mysql = MySQL(app)

# Redirect to login page
@app.route('/')
def home():
    return redirect(url_for('login'))

# Login Route
@app.route('/login', methods=['POST'])
def login():
    data = request.json
    username = data.get('username')
    password = data.get('password')

    cur = mysql.connection.cursor()
    
    # Check if user is a company
    cur.execute("SELECT companyId, password FROM company WHERE username = %s", (username,))
    company = cur.fetchone()

    if company and bcrypt.check_password_hash(company[1], password):
        session['user'] = {'id': company[0], 'role': 'company'}
        return jsonify({'redirect': 'company_dashboard'})

    # Check if user is a client
    cur.execute("SELECT clientId, password FROM client WHERE username = %s", (username,))
    client = cur.fetchone()

    if client and bcrypt.check_password_hash(client[1], password):
        session['user'] = {'id': client[0], 'role': 'client'}
        return jsonify({'redirect': 'client_dashboard'})

    return jsonify({'error': 'Invalid username or password'}), 401

# Client Dashboard Data
@app.route('/client_dashboard', methods=['GET'])
def client_dashboard():
    if 'user' not in session or session['user']['role'] != 'client':
        return jsonify({'error': 'Unauthorized'}), 403

    client_id = session['user']['id']
    
    cur = mysql.connection.cursor()
    cur.execute("SELECT date, price FROM purchase WHERE clientId = %s", (client_id,))
    purchases = cur.fetchall()
    cur.close()

    purchase_list = [{'date': p[0], 'price': p[1]} for p in purchases]
    return jsonify({'purchases': purchase_list})

# Company Dashboard Data
@app.route('/company_dashboard', methods=['GET'])
def company_dashboard():
    if 'user' not in session or session['user']['role'] != 'company':
        return jsonify({'error': 'Unauthorized'}), 403

    cur = mysql.connection.cursor()
    cur.execute("SELECT productCode, productName, salePrice, saleTime FROM sale")
    sales = cur.fetchall()
    cur.close()

    sales_list = [{'product': s[1], 'code': s[0], 'price': s[2], 'time': s[3]} for s in sales]
    return jsonify({'sales': sales_list})

# Update Prices
@app.route('/update_prices', methods=['POST'])
def update_prices():
    if 'user' not in session or session['user']['role'] != 'company':
        return jsonify({'error': 'Unauthorized'}), 403

    data = request.json
    updated_prices = data.get('prices', [])

    cur = mysql.connection.cursor()
    for item in updated_prices:
        cur.execute("UPDATE sale SET salePrice = %s WHERE productCode = %s", (item['new_price'], item['code']))

    mysql.connection.commit()
    cur.close()
    return jsonify({'message': 'Prices updated successfully'})

if __name__ == '__main__':
    app.run(debug=True)

if __name__ == '__main__':
    db.create_all()
    app.run(debug=True)
