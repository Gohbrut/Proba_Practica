from flask_sqlalchemy import SQLAlchemy


db = SQLAlchemy()

# Class responsible for defining the "Product" Database.
class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    name = db.Column(db.String(255), unique=True, nullable=False)
    price = db.Column(db.String(100))
    description = db.Column(db.Text)
    image_url = db.Column(db.Text)

    def __repr__(self):
        return f"<Product {self.name}>"