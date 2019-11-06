
from datetime import datetime
from myShop import db, login_manager
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

wish_list = db.Table("wish_list",
                     db.Column("item_id", db.Integer, db.ForeignKey("item.id")),
                     db.Column("wish_id", db.Integer, db.ForeignKey("wishes.id")))     
    

class Wishes(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    items = db.relationship("Item", secondary=wish_list, backref=db.backref("wishes", lazy="dynamic"), lazy="dynamic")
    
    def __repr__(self):
        return f"Wishes('{self.id}','{self.user_id}', '{self.item_id}')"

class Cart(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    quantity = db.Column(db.Integer, nullable=False, default=0)
    items = db.relationship("Item", backref="cart", lazy="dynamic")
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    
    def __repr__(self):
        return f"Cart('{self.id}','{self.quantity}', '{self.user_id}')"

class Item(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    item_name = db.Column(db.String(120), nullable=False)
    description = db.Column(db.String(380), nullable=False)
    price = db.Column(db.Numeric(10,2), nullable=False)
    stock_level = db.Column(db.Integer, nullable=False, default=0)
    image_file = db.Column(db.String(60), nullable=False, default="default.jpg")
    info_website = db.Column(db.String(320))
    cart_id = db.Column("Cart", db.ForeignKey("cart.id"))
    def __repr__(self):
        return f"Item('{self.item_name}','{self.description}', '{self.price}', '{self.stock_level}', '{self.info_website}', '{self.cart_id}')"
    
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128))
    password = db.Column(db.String(60), nullable=False)
    first_name = db.Column(db.String(60), nullable=False)
    last_name = db.Column(db.String(60), nullable=False)
    active = db.Column(db.Boolean, nullable=False, default=True)
    user_cart = db.relationship("Cart", backref="user", uselist=False)
    wishlist = db.relationship("Wishes", backref="user", uselist=False)
    
    def __repr__(self):
        return f"User('{self.email}', '{self.first_name}', '{self.last_name}', '{self.active}')"
    
    @property
    def password(self):
        raise AttributeError("Password is not a readable attribute")
    
    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    @property
    def is_active(self):
        return self.active
    
    @property
    def is_authenticated(self):
        return True
     
    @property
    def is_anonymous(self):
        return False

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))
