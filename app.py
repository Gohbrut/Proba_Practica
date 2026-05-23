from flask import Flask, render_template, request, redirect, url_for, session, flash

from db_manager import db, Product, User
from scheduler import start_scheduler
from scraper import scrape_products
from sqlalchemy import cast, Float

import os
import re
import pandas as pd
import pdfplumber

from flask import send_file
from flask import render_template


app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///products.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = 'example_secret_key'


db.init_app(app)


with app.app_context():
    db.create_all()


start_scheduler(app)


def check_login():
    """Check if user is logged in"""
    return 'user_id' in session


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username'].strip()
        password = request.form['password'].strip()
        password_confirm = request.form['password_confirm'].strip()

        if not username or not password:
            flash('Username and password are required', 'error')
            return redirect(url_for('register'))

        if password != password_confirm:
            flash('Passwords do not match', 'error')
            return redirect(url_for('register'))

        # Check if user already exists
        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
            flash('Username already exists', 'error')
            return redirect(url_for('register'))

        # Create new user
        new_user = User(username=username)
        new_user.set_password(password)
        
        db.session.add(new_user)
        db.session.commit()

        flash('Registration successful! Please log in.', 'success')
        return redirect(url_for('login'))

    return render_template('register.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username'].strip()
        password = request.form['password'].strip()

        if not username or not password:
            flash('Username and password are required', 'error')
            return redirect(url_for('login'))

        # Find user
        user = User.query.filter_by(username=username).first()

        if not user or not user.check_password(password):
            flash('Invalid username or password', 'error')
            return redirect(url_for('login'))

        # Set session
        session['user_id'] = user.id
        session['username'] = user.username
        flash(f'Welcome back, {user.username}!', 'success')
        return redirect(url_for('index'))

    return render_template('login.html')


@app.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out', 'success')
    return redirect(url_for('login'))


@app.route('/')
def index():
    if not check_login():
        return redirect(url_for('login'))

    # Get query parameters
    name_filter = request.args.get('name_filter', '').strip()
    sort_option = request.args.get('sort', 'name')
    
    # Start with base query
    query = Product.query
    
    # Apply name filter if provided
    if name_filter:
        query = query.filter(Product.name.ilike(f'%{name_filter}%'))
    
    # Apply sorting
    if sort_option == 'price_asc':
        query = query.order_by(cast(Product.price, Float))
    elif sort_option == 'price_desc':
        query = query.order_by(cast(Product.price, Float).desc())
    else:  # default to name
        query = query.order_by(Product.name)
    
    products = query.all()
    return render_template('index.html', products=products, name_filter=name_filter, sort_option=sort_option)


@app.route('/scrape')
def manual_scrape():
    if not check_login():
        return redirect(url_for('login'))
    
    scrape_products(app)
    return redirect(url_for('index'))


@app.route('/edit/<int:product_id>', methods=['GET', 'POST'])
def edit_product(product_id):
    if not check_login():
        return redirect(url_for('login'))
    
    product = Product.query.get_or_404(product_id)

    if request.method == 'POST':
        product.name = request.form['name']
        product.price = request.form['price']
        product.description = request.form['description']
        product.image_url = request.form['image_url']

        # New ffields for bonus task
        product.price_ron = request.form['price_ron']
        product.conversion_rate = float(request.form['conversion_rate'])

        db.session.commit()

        return redirect(url_for('index'))

    return render_template('edit.html', product=product)


@app.route('/delete/<int:product_id>')
def delete_product(product_id):
    if not check_login():
        return redirect(url_for('login'))
    
    product = Product.query.get_or_404(product_id)

    db.session.delete(product)
    db.session.commit()

    return redirect(url_for('index'))

@app.route('/upload-pdf', methods=['GET', 'POST'])
def upload_pdf():
    if not check_login():
        return redirect(url_for('login'))

    if request.method == 'POST':

        pdf_file = request.files['pdf']

        if not pdf_file:
            return "No file uploaded"

        upload_folder = "uploads"

        os.makedirs(upload_folder, exist_ok=True)

        pdf_path = os.path.join(
            upload_folder,
            pdf_file.filename
        )

        pdf_file.save(pdf_path)

        extracted_products = []

        with pdfplumber.open(pdf_path) as pdf:

            full_text = ""

            for page in pdf.pages:

                text = page.extract_text()

                if text:
                    full_text += text + "\n"

        lines = full_text.splitlines()

        for line in lines:

            print(line)

            if "RON" in line and "H87" in line:

                try:

                    parts = line.split()

                    print(parts)

                    # [
                    # '1',
                    # '172812F',
                    # 'COMUTATOR',
                    # 'PORNIRE',
                    # 'FEBI',
                    # '251.96',
                    # 'RON',
                    # '-1',
                    # '-1',
                    # 'H87',
                    # '19',
                    # '-251.96'
                    # ]

                    cod_produs = parts[1]

                    pret_unitar = parts[-7]

                    moneda = parts[-6]

                    cantitate = parts[-5]

                    denumire = " ".join(parts[2:-7])

                    extracted_products.append({
                        "Cod produs": cod_produs,
                        "Denumire produs": denumire,
                        "Pret unitar": pret_unitar,
                        "Moneda": moneda,
                        "Cantitate": cantitate
                    })

                except Exception as e:
                    print("Parsing error:", e)

        if not extracted_products:
            return "No products found"

        df = pd.DataFrame(extracted_products)

        csv_filename = os.path.splitext(pdf_file.filename)[0] + ".csv"

        csv_path = os.path.join(
            upload_folder,
            csv_filename
        )

        df.to_csv(csv_path, index=False)

        return send_file(
            csv_path,
            as_attachment=True
        )

    return render_template("upload_pdf.html")

if __name__ == '__main__':
    app.run(debug=True)