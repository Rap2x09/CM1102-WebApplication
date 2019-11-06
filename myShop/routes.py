import os
from flask import render_template, url_for, request, redirect, flash, session
from myShop import app, db
from myShop.models import User, Item, Cart, Wishes, wish_list
from flask_login import login_user, current_user, logout_user, login_required
from myShop.forms import RegistrationForm, LoginForm, CheckoutForm
from myShop.normalise import *

@app.route("/")
@app.route("/home", methods=['GET', 'POST'])
def home():
    select = request.form.get('sort')
    if select == "nameAZ":
        items = Item.query.order_by(Item.item_name).all()
        flash("Items sorted by name A - Z")
    elif select == "nameZA":
        items = Item.query.order_by(Item.item_name.desc()).all()
        flash("Items sorted by name Z - A")
    elif select == "priceAsc":
        items = Item.query.order_by(Item.price).all()
        flash("Sorted Items by price from Lowest - Highest")
    elif select == "priceDesc":
        items = Item.query.order_by(Item.price.desc()).all()
        flash("Sorted Items by price from Highest - Lowest")
    else:
        items = Item.query.all()
    return render_template('home.html', items=items, title='Items', active='home')

@app.route("/sort_by", methods=['GET', 'POST'])
def sort_by():
    
    select = request.form.get('sort')
    if select == "nameAZ":
        sort_items = Item.query.order_by(Item.item_name).all()
    return redirect('/home', items=sort_items)

@app.route("/searh_result", methods=['GET', 'POST'])
def search_result():
    search_items = request.form.get("search_item")
    
    if len(search_items) == 0:
        return redirect('/home')
    
    search_for = normalise_input(search_items)
    
    
    items = Item.query.filter(Item.item_name.like("%" + search_for + "%")).all()
        #flash("Search Result for item \"" + )
    if items:
        title = "Found " + str(len(items)) + " result for \"" + search_items + "\""
        flash("Match found")
    else:
        title = "No result found for \"" + search_items + "\""
        flash("Item Not Found")
    
    return render_template('search_result.html', items=items, title=title)

@app.route("/about")
def about():
    return render_template('about.html', title='About', active='about')

@app.route("/offers")
def offers():
    return render_template('offers.html', title='Offers', active='offers')

@app.route("/contact_us")
def contact_us():
    return render_template('help.html', title='Contact Us', active='contact_us')

@app.route("/register", methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    
    if form.validate_on_submit():
        user = User(email=form.email.data, password=form.password.data, first_name=form.first_name.data, last_name=form.last_name.data)
        db.session.add(user)
        db.session.commit()
        flash("Your account has been created. You can now log in")
        return redirect(url_for("login"))
    
    return render_template("register.html", title="Register", form=form)

@app.route("/login", methods=['GET', 'POST'])
def login():
    form = LoginForm()
    
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        
        if user is not None and user.verify_password(form.password.data):
            login_user(user)
            if "cart" in session:
                session.pop("cart")
            flash("You are now logged in")
            return redirect(url_for("home"))
        
        flash("Invalid username or password")
        
        return render_template("login.html",title="Login", form=form)
    return render_template("login.html", title="Login", form=form)

@app.route("/logout")
def logout():
    logout_user()
    if "cart" in session:
        session.pop("cart")
    flash("You are now logged out")
    return redirect(url_for("login"))

@app.route("/item/<int:item_id>")
def item(item_id):
    item = Item.query.get_or_404(item_id)
    
    return render_template("item.html", item=item, title=item.item_name)

@app.route("/add_to_cart/<int:item_id>")
def add_to_cart(item_id):
    
    if "cart" not in session:
        session["cart"] = []
    
    session["cart"].append(item_id)    
            
    flash("Item has been added to your shopping cart")
    return redirect("/cart")

@app.route("/cart", methods=['GET', 'POST'])
def cart_display():
    
    if "cart" not in session:
        flash("There is nothing in your cart.")        
        return render_template("cart.html", title="Your Shopping Cart", display_cart={}, total=0, active='cart')
    else:
        items = session["cart"]
        cart = {}        
        total_price = 0
        total_quantity = 0
        
        for item in items:
            cart_item = Item.query.get_or_404(item)            
            total_price += cart_item.price
            
            if cart_item.id in cart:
                if cart_item.stock_level != cart[cart_item.id]["quantity"]:
                    cart[cart_item.id]["quantity"] += 1
                else:                    
                    session["cart"].remove(cart_item.id)
                    flash("You cannot add anymore of this item!")
                    session.modified = True
                    return redirect("/cart")
            else:
                cart[cart_item.id] = {"quantity":1, "item_name":cart_item.item_name, "price":cart_item.price}            
            total_quantity = sum(item["quantity"] for item in cart.values())
        return render_template("cart.html", title="Your Shopping Cart", display_cart = cart, total = total_price, total_quantity = total_quantity, active='cart')
     
    return render_template("cart.html", active='cart')

@app.route("/delete_item/<int:item_id>", methods=["GET", "POST"])
def delete_item(item_id):   
    item = Item.query.get_or_404(item_id)
    message = item.item_name + " has been removed from your shopping cart"
    
    if "cart" not in session:
        session["cart"] = []
        
    session["cart"].remove(item_id)
    
    flash(message)
    
    session.modified = True
    
    return redirect("/cart")

@app.route("/checkout", methods=['GET', 'POST'])
def checkout():
    form = CheckoutForm()
    delivery_charge = 00.00
    subtotal, total_quantity = get_cart_details()
    
    if form.validate_on_submit():
        first_name = form.cfirst_name.data
        last_name = form.clast_name.data
        email = form.cemail.data
        address_line1 = form.address_line1.data
        address_line2 = form.address_line2.data
        post_code = form.post_code.data
        country = form.country.data
        town = form.town.data
        name_on_card = form.name_on_card.data
        card_number = form.card_number.data
        exp_month = form.exp_month.data
        exp_year = form.exp_year.data    
        security_code = form.security_code.data
        flash("Your Order has been processed")
        session.pop("cart")
        
        return redirect(url_for("order_complete"))
    
    if subtotal < 20:
        delivery_charge = 3.99
        
    return render_template("checkout.html", title="Checkout", form=form, total_quantity=total_quantity, subtotal=subtotal, delivery = delivery_charge)

def get_cart_details():
    
    items = session["cart"]
    cart = {}
    
    total_price = 0
    total_quantity = 0
    
    for item in items:
        cart_item = Item.query.get_or_404(item)
        
        total_price += cart_item.price
        
        if cart_item.id in cart:
            if cart_item.stock_level != cart[cart_item.id]["quantity"]:
                cart[cart_item.id]["quantity"] += 1
  
        else:
            cart[cart_item.id] = {"quantity":1, "item_name":cart_item.item_name, "price":cart_item.price}
        
        total_quantity = sum(item["quantity"] for item in cart.values())
        
    return total_price, total_quantity

@app.route("/order_complete", methods=['GET', 'POST'])
def order_complete():
    return render_template('order_complete.html')

@app.route("/add_to_wishlist/<int:item_id>", methods=['GET', 'POST'])
def add_to_wishlist(item_id):
    
    if current_user.is_anonymous:
        flash("Please login to access the wishlist page")
        return redirect('/login')

    item = Item.query.get_or_404(item_id)
    user_wishlist = Wishes.query.filter_by(user_id=current_user.id).all()
    user_wish = Wishes.query.filter_by(user_id=current_user.id).first()
   
    if not user_wishlist:
        db.session.add(Wishes(user_id=current_user.id, items=[item]))
        flash("Item has been added to your wishlist")
        db.session.commit()
    
    else:
        if item in user_wish.items:
            flash("Item is already in your wishlist")
        else:
            user_wish.items.append(item)
            flash("Item has been added to your wishlist")
            db.session.commit()

    return redirect('/wishlist')

@app.route("/wishlist", methods=['GET', 'POST'])
def show_wishlist():
    
    if current_user.is_anonymous:
        flash("Please login to access the wishlist page")
        return redirect('/login')
    
    user_wish = Wishes.query.filter_by(user_id=current_user.id).first()
    
    
    if user_wish is None:
        return render_template('wishlist.html', title='Your Wishlist', user_wish=user_wish)
    wish_items = user_wish.items
    wishlist = [a for a in wish_items]
    
    if wish_items is None or len(wishlist) == 0:
        flash("You don't have anything in your wish list")
        
    return render_template('wishlist.html', title='Your Wishlist', wish_items = wish_items, user_wish=user_wish, wishlist=wishlist)


@app.route("/delete_wish_item/<int:item_id>", methods=["GET", "POST"])
def delete_wish_item(item_id): 
  
    user_wish = Wishes.query.filter_by(user_id=current_user.id).first()

    item = Item.query.get_or_404(item_id)

    user_wish.items.remove(item)
    flash("Item has been removed from your wishlist")
    db.session.commit()

    return redirect('/wishlist')