from flask import Flask, request, jsonify, session, redirect, url_for, render_template
from flask_mysqldb import MySQL
from flask_bcrypt import Bcrypt
from flask_cors import CORS

app = Flask(__name__, template_folder=".")  # Look for HTML files in the same directory
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

# Serve Login Page
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template('login.html')  # Ensure 'login.html' exists in the same folder as `app.py`
    
    data = request.json
    username = data.get('username')
    password = data.get('password')

    if not username or not password:
        return jsonify({'error': 'Username and password are required'}), 400

    cur = mysql.connection.cursor()

    # Check if user is a company
    cur.execute("SELECT companyId, password FROM companies WHERE username = %s", (username,))
    company = cur.fetchone()

    if company:
        db_password = company[1]
        if db_password == password:  # Compare directly (NO HASHING)
            session['user'] = {'id': company[0], 'role': 'company'}
            return jsonify({'redirect': '/company_dashboard'})

    # Check if user is a client
    cur.execute("SELECT clientId, password FROM clients WHERE username = %s", (username,))
    client = cur.fetchone()

    if client:
        db_password = client[1]
        if db_password == password:  # Compare directly (NO HASHING)
            session['user'] = {'id': client[0], 'role': 'client'}
            return jsonify({'redirect': '/client_dashboard'})

    return jsonify({'error': 'Invalid username or password'}), 401

# Serve Client Dashboard
@app.route('/client_dashboard', methods=['GET'])
def client_dashboard():
    if 'user' not in session or session['user']['role'] != 'client':
        return redirect(url_for('login'))

    client_id = session['user']['id']
    
    cur = mysql.connection.cursor()
    cur.execute("SELECT date, price FROM purchase WHERE clientId = %s", (client_id,))
    purchases = cur.fetchall()
    cur.close()

    return render_template('client_dashboard.html', purchases=purchases)

# Serve Company Dashboard
@app.route('/company_dashboard', methods=['GET'])
def company_dashboard():
    if 'user' not in session or session['user']['role'] != 'company':
        return redirect(url_for('login'))

    cur = mysql.connection.cursor()
    cur.execute("SELECT productCode, productName, salePrice, saleTime FROM sale1")
    sales = cur.fetchall()
    cur.close()

    return render_template('company_dashboard.html', sales=sales)

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
