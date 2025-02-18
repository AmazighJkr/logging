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
app.config["MYSQL_USER"] = "sql7763333"
app.config["MYSQL_PASSWORD"] = "BtCcUDutUB"
app.config["MYSQL_DB"] = "sql7763333"
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
        return render_template('login.html')  # Ensure 'login.html' exists
    
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
            session['user'] = {'companyId': company[0], 'role': 'company'}  # ✅ FIXED
            return jsonify({'redirect': '/company_dashboard'})

    # Check if user is a client
    cur.execute("SELECT clientId, password FROM clients WHERE username = %s", (username,))
    client = cur.fetchone()

    if client:
        db_password = client[1]
        if db_password == password:  # Compare directly (NO HASHING)
            session['user'] = {'clientId': client[0], 'role': 'client'}  # ✅ Renaming for consistency
            return jsonify({'redirect': '/client_dashboard'})

    return jsonify({'error': 'Invalid username or password'}), 401

# Serve Client Dashboard
@app.route('/client_dashboard', methods=['GET'])
def client_dashboard():
    if 'user' not in session or session['user']['role'] != 'client':
        return redirect(url_for('login'))

    client_id = session['user']['id']
    cur = mysql.connection.cursor()

    # ✅ Fetch purchases from the correct table
    table_name = f"purchases{client_id}"
    cur.execute(f"SELECT date, price FROM {table_name} WHERE clientId = %s", (client_id,))
    purchases = cur.fetchall()

    # ✅ Fetch RFID cards
    cur.execute("SELECT uid, balance FROM users WHERE clientId = %s", (client_id,))
    rfid_cards = [{'uid': row[0], 'balance': row[1]} for row in cur.fetchall()]
    
    cur.close()

    # ✅ Pass the data to the template instead of returning JSON
    return render_template('client_dashboard.html', purchases=purchases, rfid_cards=rfid_cards)

# Serve Company Dashboard
@app.route('/company_dashboard', methods=['GET', 'POST'])
def company_dashboard():
    if 'user' not in session or session['user']['role'] != 'company':
        return redirect(url_for('login'))

    company_id = session['user']['companyId']

    # Get selected vending machine from the form (default: 1)
    machine_id = request.form.get('machine', '1')

    # Correct table format (sales per company, filtered by machine)
    table_name = f"selles{company_id}"

    cur = mysql.connection.cursor()
    
    # Query sales for the selected vending machine
    query = f"SELECT productCode, productName, salePrice, saleTime FROM {table_name} WHERE vendingMachineId = %s"
    cur.execute(query, (machine_id,))
    
    sales = cur.fetchall()
    cur.close()

    return render_template('company_dashboard.html', sales=sales, selected_machine=machine_id)

# Update Prices
@app.route('/update_prices', methods=['POST'])
def update_prices():
    if 'user' not in session or session['user']['role'] != 'company':
        return redirect(url_for('login'))

    company_id = session['user']['companyId']
    machine_id = request.form.get('machine', '1')  # Get selected machine

    table_name = f"selles{company_id}_{machine_id}"  # Dynamic table name

    cur = mysql.connection.cursor()
    for key, value in request.form.items():
        if key.startswith("price_"):  # Filter only price fields
            product_code = key.split("_")[1]
            new_price = value
            query = f"UPDATE {table_name} SET salePrice = %s WHERE productCode = %s"
            cur.execute(query, (new_price, product_code))

    mysql.connection.commit()
    cur.close()
    return redirect(url_for('company_dashboard'))  # Redirect to refresh page

if __name__ == '__main__':
    app.run(debug=True)
