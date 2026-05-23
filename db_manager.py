from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash


db = SQLAlchemy()

# Class responsible for defining the "User" Database.
class User(db.Model):
    __tablename__ = 'user'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)

    def set_password(self, password):
        """Hash and set the password"""
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        """Check if the password matches the hash"""
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f"<User {self.username}>"

# Class responsible for defining the "Product" Database.
class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    name = db.Column(db.String(255), unique=True, nullable=False)
    price = db.Column(db.String(100))
    price_ron = db.Column(db.String(100))
    conversion_rate = db.Column(db.Float)
    description = db.Column(db.Text)
    image_url = db.Column(db.Text)

    def __repr__(self):
        return f"<Product {self.name}>"