from flask import Flask, request, jsonify, session, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import check_password_hash

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Change this to a secure key
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://username:password@localhost/database_name'
db = SQLAlchemy(app)

class Client(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)

class Company(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)

def verify_user(username, password):
    user = Client.query.filter_by(username=username).first()
    if user and check_password_hash(user.password_hash, password):
        return 'client', user.id
    
    user = Company.query.filter_by(username=username).first()
    if user and check_password_hash(user.password_hash, password):
        return 'company', user.id
    
    return None, None

@app.route('/login', methods=['POST'])
def login():
    data = request.json
    username = data.get('username')
    password = data.get('password')

    role, user_id = verify_user(username, password)
    if role:
        session['user_id'] = user_id
        session['role'] = role
        if role == 'client':
            return jsonify({'redirect': url_for('client_dashboard')})
        else:
            return jsonify({'redirect': url_for('company_dashboard')})
    return jsonify({'error': 'Invalid credentials'}), 401

@app.route('/client_dashboard')
def client_dashboard():
    if 'user_id' in session and session['role'] == 'client':
        return jsonify({'message': 'Client Dashboard'})
    return redirect(url_for('login'))

@app.route('/company_dashboard')
def company_dashboard():
    if 'user_id' in session and session['role'] == 'company':
        return jsonify({'message': 'Company Dashboard'})
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)
