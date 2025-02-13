from flask import Flask, render_template, request, redirect, url_for, session, jsonify
from flask_mysqldb import MySQL
import pymysql
import os

app = Flask(__name__)
app.secret_key = "your_secret_key"

# Enable CORS
from flask_cors import CORS
CORS(app)

# Database configuration
app.config["MYSQL_HOST"] = "sql7.freesqldatabase.com"
app.config["MYSQL_USER"] = "sql7762208"
app.config["MYSQL_PASSWORD"] = "MqFJpHymhB"
app.config["MYSQL_DB"] = "sql7762208"
app.config["MYSQL_PORT"] = 3306

mysql = MySQL(app)

# Serve Login Page
@app.route("/")
def login_page():
    return render_template("login.html")

# Serve Dashboard Page (Protected)
@app.route("/dashboard")
def dashboard():
    if "user_id" not in session:
        return redirect(url_for("login_page"))
    return render_template("dashboard.html")

# Handle Login
@app.route("/login", methods=["POST"])
def login():
    username = request.form.get("username")
    password = request.form.get("password")

    cursor = mysql.connection.cursor()
    cursor.execute("SELECT userId, username FROM users WHERE username = %s AND password = %s", (username, password))
    user = cursor.fetchone()
    cursor.close()

    if user:
        session["user_id"] = user[0]
        session["username"] = user[1]
        return redirect(url_for("dashboard"))
    else:
        return render_template("login.html", error="Invalid username or password")

# Handle Logout
@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login_page"))

# Fetch Vending Machines
@app.route("/vendingmachines", methods=["GET"])
def get_vending_machines():
    cursor = mysql.connection.cursor()
    cursor.execute("SELECT vendingMachineCode, vendingMachineName FROM vendingmachines")
    machines = cursor.fetchall()
    cursor.close()
    
    return jsonify([{ "code": row[0], "name": row[1] } for row in machines])

if __name__ == "__main__":
    app.run(debug=True)
