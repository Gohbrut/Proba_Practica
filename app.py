from flask import Flask, render_template, request, redirect, url_for

from db_manager import db, Product
from scheduler import start_scheduler
from scraper import scrape_products

import os
import re
import pandas as pd
import pdfplumber

from flask import send_file
from flask import render_template


app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///products.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False


db.init_app(app)


with app.app_context():
    db.create_all()


start_scheduler(app)


@app.route('/')
def index():
    products = Product.query.all()
    return render_template('index.html', products=products)


@app.route('/scrape')
def manual_scrape():
    scrape_products(app)
    return redirect(url_for('index'))


@app.route('/edit/<int:product_id>', methods=['GET', 'POST'])
def edit_product(product_id):
    product = Product.query.get_or_404(product_id)

    if request.method == 'POST':
        product.name = request.form['name']
        product.price = request.form['price']
        product.description = request.form['description']
        product.image_url = request.form['image_url']

        db.session.commit()

        return redirect(url_for('index'))

    return render_template('edit.html', product=product)


@app.route('/delete/<int:product_id>')
def delete_product(product_id):
    product = Product.query.get_or_404(product_id)

    db.session.delete(product)
    db.session.commit()

    return redirect(url_for('index'))

@app.route('/upload-pdf', methods=['GET', 'POST'])
def upload_pdf():

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