from flask import Flask, render_template, request, redirect, url_for

from db_manager import db, Product
from scheduler import start_scheduler
from scraper import scrape_products


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


if __name__ == '__main__':
    app.run(debug=True)