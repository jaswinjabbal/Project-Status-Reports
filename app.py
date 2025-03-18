from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify
import mysql.connector
import json
from sshtunnel import SSHTunnelForwarder
import random
import string
import logging
logging.basicConfig(level=logging.DEBUG)
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from models import User 
from werkzeug.security import check_password_hash, generate_password_hash

#INTEGRATION
from utils.digikey_tools import get_product_details, load_token
from utils.query_helpers import filter_parts, sort_parts, tag_part, get_product_details, insert_part, use_refresh_token, get_distinct_values, count_filtered_parts


app = Flask(__name__)
app.secret_key = 'your_secret_key_here_1234567890'

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# SSH and MySQL Configuration
ssh_config = {
    'ssh_address_or_host': ('lusherengineeringservices.com', 22),  # SSH Host and Port
    'ssh_username': 'ecen404team45',                                # SSH Username
    'ssh_password': 'ecen404$592H#!cx',                          # SSH Password
    'remote_bind_address': ('127.0.0.1', 3306)                    # MySQL Host and Port on the remote server
}

mysql_config = {
    'user': 'ecen404team45',               # MySQL Username
    'password': 'ecen404$592H#!cx',   # MySQL Password
    'database': 'lusher engineering parts database',          # Replace with your DB name
    'connection_timeout' : 10 
}

#########################

# Function to connect to DB through SSH tunnel
def create_db_connection():
    tunnel = SSHTunnelForwarder(
        ssh_address_or_host=ssh_config['ssh_address_or_host'],
        ssh_username=ssh_config['ssh_username'],
        ssh_password=ssh_config['ssh_password'],
        remote_bind_address=ssh_config['remote_bind_address'],
        local_bind_address=('127.0.0.1', 3307)
    )
    tunnel.start()

    conn = mysql.connector.connect(
        host='127.0.0.1',
        port=3307,
        user=mysql_config['user'],
        password=mysql_config['password'],
        database=mysql_config['database']
    )

    return conn, tunnel
# Helper function: Safely close resources
def cleanup(cursor, conn, tunnel):
    if cursor: cursor.close()
    if conn: conn.close()
    if tunnel: tunnel.stop()

#----------------------Auth----------------------#

@login_manager.user_loader
def load_user(user_id):
    conn, tunnel = create_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, username, password_hash FROM users WHERE id = %s", (user_id,))
    row = cursor.fetchone()
    cleanup(cursor, conn, tunnel)
    if row:
        return User(id=row[0], username=row[1], password_hash=row[2])
    return None

#--------------------AUTH ROUTES-----------------#
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        hashed_pw = generate_password_hash(password)

        conn, tunnel = create_db_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("INSERT INTO users (username, password_hash) VALUES (%s, %s)", (username, hashed_pw))
            conn.commit()
            flash('Registration successful! Please login.')
            return redirect(url_for('login'))
        except mysql.connector.IntegrityError:
            flash('Username already exists. Choose another.')
        finally:
            cleanup(cursor, conn, tunnel)
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        conn, tunnel = create_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT id, username, password_hash FROM users WHERE username = %s", (username,))
        user_data = cursor.fetchone()
        cleanup(cursor, conn, tunnel)

        if user_data and check_password_hash(user_data[2], password):
            user = User(user_data[0], user_data[1], user_data[2])
            login_user(user)
            return redirect(url_for('index'))
        flash('Invalid credentials')
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

#-----------------------ROUTES--------------------#
#Home page displaying parts table
@app.route('/')
@login_required
def index():
    page = request.args.get('page', 1, type=int)
    per_page = 10
    offset = (page - 1) * per_page

    conn, tunnel = create_db_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("SELECT COUNT(*) as total FROM partInfo")
    total_parts = cursor.fetchone()['total']

    cursor.execute("SELECT * FROM partInfo LIMIT %s OFFSET %s", (per_page, offset))
    data = cursor.fetchall()

    has_next = (offset + per_page) < total_parts

    cleanup(cursor, conn, tunnel)
    return render_template('index.html', data=data, page=page, has_next=has_next)

@app.route('/filter', methods=['GET', 'POST'])
@login_required
def filter():
    data = []
    if request.method == 'POST':
        category = request.form['category']
        value = request.form['value']
        try:
            conn, tunnel = create_db_connection()
            cursor = conn.cursor(dictionary=True)
            query = f"SELECT * FROM partInfo WHERE `{category}` = %s"
            cursor.execute(query, (value,))
            data = cursor.fetchall()
            cleanup(cursor, conn, tunnel)
        except Exception as e:
            flash(f"Error during filtering: {e}")
    return render_template('filter.html', data=data)


@app.route('/sort', methods=['GET', 'POST'])
@login_required
def sort():
    page = request.args.get('page', 1, type=int)
    per_page = 10
    offset = (page - 1) * per_page

    category = request.args.get('category')

    # If POST (form submission), update category
    if request.method == 'POST':
        category = request.form.get('category')
        return redirect(url_for('sort', page=1, category=category))  # redirect to GET w/ params

    data = []
    total = 0
    if category:
        valid_columns = ['Manufacturer', 'Supplier', 'Part_Category', 'Cost_1pc', 'Stock']
        if category not in valid_columns:
            flash("Invalid column name selected for sorting.")
            return redirect(url_for('sort'))

        conn, tunnel = create_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute(f"SELECT COUNT(*) as total FROM partInfo")
        total = cursor.fetchone()['total']
        cursor.execute(f"SELECT * FROM partInfo ORDER BY {category} LIMIT %s OFFSET %s", (per_page, offset))
        data = cursor.fetchall()
        cleanup(cursor, conn, tunnel)

    return render_template('sort.html', data=data, page=page, has_next=(offset + per_page < total), selected_category=category)

@app.route('/tag', methods=['GET', 'POST'])
@login_required
def tag():
    if request.method == 'POST':
        part_number = request.form['part_number']
        tag = request.form['tag']
        try:
            conn, tunnel = create_db_connection()
            cursor = conn.cursor()
            query = "UPDATE partInfo SET Tags = %s WHERE Supplier_Part_Number = %s"
            cursor.execute(query, (tag, part_number))
            conn.commit()
            cleanup(cursor, conn, tunnel)
            flash('Tag updated successfully!')
        except Exception as e:
            flash(f"Error during tagging: {e}")
        return redirect(url_for('tag'))
    return render_template('tag_part.html')

#add works
@app.route('/add', methods=['GET', 'POST'])
@login_required
def add():
    if request.method == 'POST':
        part_number = request.form['part_number']
        manufacturer = request.form['manufacturer']
        category = request.form['category']
        cost = request.form['cost']
        try:
            conn, tunnel = create_db_connection()
            cursor = conn.cursor()
            query = ("INSERT INTO partInfo (Supplier_Part_Number, Manufacturer, Part_Category, Cost_1pc) "
                     "VALUES (%s, %s, %s, %s)")
            cursor.execute(query, (part_number, manufacturer, category, cost))
            conn.commit()
            cleanup(cursor, conn, tunnel)
            flash('Part added successfully!')
        except Exception as e:
            flash(f"Error adding part: {e}")
        return redirect(url_for('add'))
    return render_template('add_part.html')

#update works
@app.route('/update', methods=['GET', 'POST'])
@login_required
def update():
    if request.method == 'POST':
        part_number = request.form['part_number']
        new_cost = request.form['new_cost']
        try:
            conn, tunnel = create_db_connection()
            cursor = conn.cursor()
            query = "UPDATE partInfo SET Cost_1pc = %s WHERE Supplier_Part_Number = %s"
            cursor.execute(query, (new_cost, part_number))
            conn.commit()
            cleanup(cursor, conn, tunnel)
            flash('Part updated successfully!')
        except Exception as e:
            flash(f"Error updating part: {e}")
        return redirect(url_for('update'))
    return render_template('update.html')

#search works
@app.route('/search', methods=['GET', 'POST'])
@login_required
def search():
    page = request.args.get('page', 1, type=int)
    per_page = 10
    offset = (page - 1) * per_page
    results = []
    total = 0

    selected_category = request.form.get('category') if request.method == 'POST' else request.args.get('category')
    search_value = request.form.get('value') if request.method == 'POST' else request.args.get('value')

    if request.method == 'POST':
        return redirect(url_for('search', page=1, category=selected_category, value=search_value))

    if selected_category and search_value:
        conn, tunnel = create_db_connection()
        cursor = conn.cursor(dictionary=True)
        results = filter_parts(cursor, selected_category, search_value, per_page, offset)
        total = count_filtered_parts(cursor, selected_category, search_value)
        cleanup(cursor, conn, tunnel)

    return render_template('search.html', results=results, selected_category=selected_category, search_value=search_value,
                           page=page, has_next=(offset + per_page < total))


@app.route('/get_values', methods=['POST'])
@login_required
def get_values():
    category = request.form.get('category')
    valid_columns = ['Manufacturer', 'Supplier', 'Part_Category', 'Stock']
    if category not in valid_columns:
        return {"values": []}

    conn, tunnel = create_db_connection()
    cursor = conn.cursor()
    cursor.execute(f"SELECT DISTINCT `{category}` FROM partInfo")
    values = [row[0] for row in cursor.fetchall()]
    cleanup(cursor, conn, tunnel)
    return {"values": values}


@app.route('/digikey_add', methods=['GET', 'POST'])
@login_required
def digikey_add():
    if request.method == 'POST':
        part_number = request.form['part_number']
        token = load_token()
        product = get_product_details(part_number, token)
        if product:
            # Insert into DB here using create_db_connection()
            flash('Part added successfully via Digikey API')
        else:
            flash('Failed to fetch part info')
        return redirect(url_for('digikey_add'))
    return render_template('digikey_add.html')


if __name__ == '__main__':
    app.run(debug=True)