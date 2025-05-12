import requests, json,random,secrets,os,uuid
from datetime import datetime
from dotenv import load_dotenv

from flask import render_template,request,redirect,flash,session,url_for,jsonify
from werkzeug.security import generate_password_hash,check_password_hash
from werkzeug.utils import secure_filename

from flask_mail import Message

from fashapp import app,mail

from fashapp.models import db,Customer,Admin,State,Lga,Payment,Category,Order,Orderdetails,Design,Product,Price,Cart

from fashapp.forms import LoginForm,ProfileForm,ContactForm,DesignForm,CheckoutForm

@app.route('/')
def home_page():
    loggedin_cust=session.get('loggedin')
    if loggedin_cust:
        cust_deets= db.session.query(Customer).get(loggedin_cust)

    else:
        cust_deets= None
    return render_template('user/index.html',cust_deets=cust_deets)


@app.route('/search/')
def search_products():
    query = request.args.get("query", "").strip().lower()  # Get user input & convert to lowercase
    if query:
        filtered_products = [p for p in products if query in p["name"].lower()]
    else:
        filtered_products = products  # Show all if empty search

    return render_template('user/index.html', products=filtered_products)



@app.route('/login/', methods=['POST', 'GET'])
def user_login():
    loginform = LoginForm()
    if request.method == "GET":
        return render_template('user/login.html', loginform=loginform)
    else:
        if loginform.validate_on_submit():
            email = loginform.email.data
            password = loginform.password.data

            record = db.session.query(Customer).filter(Customer.cust_email == email).first()
            if record:  # Email was found
                hashed_password = record.cust_password
                chk = check_password_hash(hashed_password, password)
                if chk:
                    session['loggedin'] = record.cust_id  # Keep for display
                    session['cust_id'] = record.cust_id  # Add this for cart and other actions

                    return redirect("/")
                else:
                    flash('errormsg', "Invalid password")
                    return redirect("/login/")
            else:
                flash('errormsg', "Invalid Email")
                return redirect("/login/")
        else:
            return render_template("user/login.html", loginform=loginform)


@app.route('/register/', methods=['POST','GET'])
def user_register():
    if request.method =='GET':
        return render_template('user/register.html')
    
    else:
        email = request.form.get('custemail')
        password= request.form.get('custpass')
        cpassword =request.form.get('custconfirm')

        firstname=request.form.get('custfirstname')
        lastname=request.form.get('custlname')
        if password != cpassword:
            flash('errormsg','password not matched please try again')

            return redirect('/register/')
        else:
            hashed = generate_password_hash(password)
            c = Customer(cust_firstname=firstname, cust_lname=lastname,cust_password=hashed,cust_email=email)
            db.session.add(c)
            db.session.commit()
            flash('feedback','An account has been created for you, please login')
            return redirect('/login/')
        
@app.route('/about/')
def about_page():
    return render_template('user/about.html')

@app.route('/crepe/')
def crepe_fabric():
    return render_template('user/crepe.html')

@app.route('/satin/')
def satin_fabric():
    return render_template('user/satin.html')

@app.route('/floral/')
def floral_fabric():
    return render_template('user/floral.html')






@app.route("/dashboard/")
def dashboard():
    loggedin_cust = session.get('loggedin')
    if loggedin_cust:
        cust_deets = db.session.query(Customer).get(loggedin_cust)
        if cust_deets:
            # Fetch customer's payments
            paydeets = db.session.query(Payment).filter_by(payment_custid=loggedin_cust).all()

            return render_template("user/dashboard.html", cust_deets=cust_deets, paydeets=paydeets)
        else:
            flash("errormsg", "User not found.")
            return redirect("/login/")
    else:
        flash("errormsg", "You must be logged in to view your dashboard.")
        return redirect("/login/")









@app.route('/profile/', methods=['GET', 'POST'])
def profile():
    pform = ProfileForm()
    loggedin_cust = session.get('loggedin')  # Get user ID from session
    
    if loggedin_cust:
        states = State.query.all()
        paydeets = db.session.query(Payment).filter(
            Payment.payment_custid == loggedin_cust, 
            Payment.payment_status == 'paid'
        ).all()
        
        cust_deets = db.session.query(Customer).get(loggedin_cust)

        if pform.validate_on_submit():
            # Only update details if form submission is valid
            cust_deets.cust_firstname = pform.cust_firstname.data
            cust_deets.cust_lname = pform.cust_lname.data
            cust_deets.cust_email = pform.cust_email.data
            cust_deets.cust_password = pform.cust_password.data  

            file = pform.cust_coverimage.data
            if file and file.filename != '':
                _, ext = os.path.splitext(file.filename)
                rand_str = secrets.token_hex(10)
                filename = f'{rand_str}{ext}'
                file.save(f'fashapp/static/uploads/{filename}')
                cust_deets.cust_coverimage = filename

            db.session.commit()
            flash('feedback', 'Profile details updated successfully!')
            return redirect('/profile/')

        return render_template('user/profile.html', cust_deets=cust_deets, pform=pform, states=states, paydeets=paydeets)
    
    flash("errormsg", "You must be logged in")
    return redirect("/login/")

    


    

@app.route('/profile/<cust_id>/update/', methods=['GET', 'POST'])
def update_profile(cust_id):
    loggedin_cust = session.get('loggedin')  # Get the logged-in user ID
    if loggedin_cust:
        paydeets = db.session.query(Payment).filter(Payment.payment_custid == loggedin_cust,Payment.payment_status == 'paid').all()
        cust_deets = db.session.query(Customer).get(cust_id)  # Get customer details

        if request.method == 'POST':
            cust_firstname = request.form.get('cust_firstname')
            cust_lname = request.form.get('cust_lname')
            cust_email = request.form.get('cust_email')


            #RETRIEVE FILE DATA
            allowed_ext = ['.jpg','.jpeg','.png','.gif']
            file = request.files.get('cust_coverimage')
            _,ext = os.path.splitext(file.filename)
            rand_str = secrets.token_hex(10)
            filename = f'{rand_str}{ext}'
            if ext in allowed_ext:
                filename = f'{rand_str}{ext}'
                file.save(f'fashapp/static/uploads/{filename}')
            else:
                flash('errormsg', 'You cover images must be an image file')
                return redirect("/profile/")


            # Update customer details
            cust_deets.cust_firstname = cust_firstname
            cust_deets.cust_lname = cust_lname
            cust_deets.cust_email = cust_email
            
            cust_deets.cust_coverimage = filename

            db.session.commit()
            flash("Profile details updated successfully!", "feedback")
            return redirect(url_for('update_profile', cust_id=cust_id))

        return render_template('user/profile.html', cust_deets=cust_deets, paydeets=paydeets)

    return redirect(url_for('login'))  # Redirect to login if not logged in
    
    




@app.route('/lgas/get/', methods=['GET', 'POST'])
def get_lgas():
    state_id = request.form.get('state_id')

    if not state_id:
        return '<option value="">Invalid State</option>'

    state = State.query.get(state_id)
    
    if not state:
        return '<option value="">State not found</option>'
    
    lgas = state.lgas  

    if not lgas:
        return '<option value="">No LGAs found</option>'

    result = ''.join([f'<option value="{lga.lga_id}">{lga.lga_name}</option>' for lga in lgas])
    
    return result


   


@app.route('/contact/', methods=['GET','POST'])
def contact():
    contactform =ContactForm()
    if contactform.validate_on_submit():
        fullname =contactform.fullname.data
        email =contactform.email.data
        message =contactform.message.data

        msg =Message(subject='thank you for the email',sender='elekeoluchukwu@moatcohorts.com.ng', recipients=[email])
        msg.html ="<h2 style='background:green;></h2>"
        mail.send(msg)
        flash('feedback', 'Email sent successfully!')
        return redirect('/contact/')

    return render_template('user/contact.html',contactform=contactform)


    


    

@app.route("/category/")
def mycategories():
    loggedin_cust = session.get('loggedin')

    if loggedin_cust:
        cust_deets = Customer.query.get(loggedin_cust)  
        cats = Category.query.all()  

        # Fetch categories the user has already selected
        selected_cats = {d.design_catid for d in Design.query.filter_by(design_custid=loggedin_cust).all()}

        return render_template("user/category.html", cust_deets=cust_deets, cats=cats, selected_cats=selected_cats)
    
    flash("You must be logged in", "danger")
    return redirect(url_for("login"))



@app.route("/category/update/", methods=['POST'])
def update_category():
    loggedin_cust = session.get('loggedin')
    if loggedin_cust:
        cat_list = request.form.getlist("catid")  # Get selected category IDs

        # Fetch existing categories the user has already selected
        existing_cats = {d.design_catid for d in Design.query.filter_by(design_custid=loggedin_cust).all()}

        # Add only new selections (avoid duplicates)
        for c in cat_list:
            if int(c) not in existing_cats:  
                new_design = Design(design_custid=loggedin_cust, design_catid=int(c))
                db.session.add(new_design)

        db.session.commit()
        flash("Categories updated successfully!", "success")  # Flash success message
        return redirect("/category/")
    
    flash("You must be logged in", "danger")
    return redirect(url_for("login"))

@app.route("/logout/")

def logout():
    session.pop("loggedin",None)
    flash('feedback',"you have logged out")
    return redirect("/login/")   

# @app.route('/design/add/', methods=['GET', 'POST'])
# def add_design():
#     form = DesignForm()
#     if form.validate_on_submit():
#         design_id= form.design_id.data
#         design_name = form.design_name.data
#         design_catid = form.design_catid.data
#         design_custid = form.design_custid.data
        
#         # Insert into the database
#         new_design = Design( design_id=design_id, design_name=design_name, design_catid=design_catid, design_custid=design_custid)
#         db.session.add(new_design)
#         db.session.commit()
        
#         return "Design added successfully!"
#     return render_template('user/category.html', form=form)

@app.route("/design/new/", methods=["POST"])
def create_design():
    design_name = request.form.get("design_name")
    design_catid = request.form.get("design_catid")
    design_custid = request.form.get("design_custid")

    print(f"Received: design_name={design_name}, design_catid={design_catid}, design_custid={design_custid}")

    if not design_name:
        flash("Error: Design name cannot be empty", "danger")
        return redirect(request.referrer)

    new_design = Design(design_name=design_name, design_catid=design_catid, design_custid=design_custid)

    try:
        db.session.add(new_design)
        db.session.commit()
        flash("Design added successfully!", "success")
    except Exception as e:
        db.session.rollback()
        flash(f"Database Error: {str(e)}", "danger")

    return redirect("/category/")


# @app.route('/design/<int:design_id>/update/', methods=['GET', 'POST'])
# def update_design(design_id):
#     design = Design.query.get(design_id)
#     form = DesignForm()
#     if form.validate_on_submit():
#         design.design_id = form.design_id.data
#         design.design_name = form.design_name.data
#         design.design_catid = form.design_catid.data
#         design.design_cust_id = form.design_cust_id.data
#         db.session.commit()
#         flash('Design updated successfully!', 'success')
#         return redirect('user/category.html')
#     return render_template('add_design.html', form=form)

@app.route("/design/<int:design_id>/update/", methods=["POST"])
def update_design():
    loggedin_cust = session.get('loggedin')
    
    if loggedin_cust:
        cat_list = request.form.getlist("catid")  # List of selected category IDs
        
        # Ensure at least one category is selected
        if not cat_list:
            flash("Please select at least one category", "danger")
            return redirect(request.referrer)
        
        # Remove only the customer's previous selections (without affecting other data)
        db.session.execute(
            db.text("DELETE FROM design WHERE design_custid = :cust_id"),
            {"cust_id": loggedin_cust}
        )
        db.session.commit()

        # Add new category selections for the customer
        for c in cat_list:
            new_design = Design(design_name="Custom Design", design_custid=loggedin_cust, design_catid=int(c))
            db.session.add(new_design)
        
        try:
            db.session.commit()
            flash("Design categories updated successfully", "success")
        except Exception as e:
            db.session.rollback()
            flash(f"Database Error: {str(e)}", "danger")

        return redirect("/category/")
    else:
        flash("You must be logged in to update your category preferences", "danger")
        return redirect("/login/")




@app.route('/product/<int:pro_id>/details/')
def pro_details(pro_id):
    cust_details = Product.query.get_or_404(pro_id)  # Fetch the product details
    return render_template('user/cust_details.html', cust_details=cust_details)


@app.route('/cart/', methods=['GET'])
def get_cart():
    cust_id = session.get('cust_id')  # Ensure this is the correct key
    cart_items = []
    total_price = 0
    cust_deets = None

    if cust_id:
        # Fix incorrect column filtering
        cust_deets = db.session.query(Customer).filter_by(cust_id=cust_id).first()
        
        # Fetch cart from DB
        cart = db.session.query(Cart).filter_by(cust_id=cust_id).all()
        print(" Cart items from DB:", [item.pro_id for item in cart])  # Debugging
    else:
        # Fetch cart from session
        cart = session.get('cart', [])
        if not isinstance(cart, list):
            session['cart'] = []
            cart = []
        print(" Cart items from session:", cart)  # Debugging

    cart_count = len(cart)

    for item in cart:
        if cust_id:
            product = db.session.query(Product).filter_by(pro_id=item.pro_id).first()
            cart_quantity = item.cart_quantity
        else:
            product = db.session.query(Product).filter_by(pro_id=item['pro_id']).first()
            cart_quantity = item['cart_quantity']

        if product:
            item_total_price = cart_quantity * product.pro_price
            total_price += item_total_price
            cart_items.append({
                'pro_id': product.pro_id,
                'pro_pix': product.pro_pix,
                'cart_id': item.cart_id if cust_id else None,
                'pro_name': product.pro_name,
                'cart_quantity': cart_quantity,
                'pro_price': float(product.pro_price),
                'total_price': float(item_total_price),
            })

    if request.is_json:
        return jsonify({
            'success': True,
            'cart_count': cart_count,
            'cart_items': cart_items,
            'total_price': float(total_price)
        })

    return render_template(
        'user/cart.html',
        cart_items=cart_items,
        total_price=float(total_price),
        cart_count=cart_count,
        cust_deets=cust_deets
    )











@app.route("/add_to_cart/<int:pro_id>", methods=["POST"])
def add_to_cart(pro_id):
    if 'cust_id' not in session:
        return jsonify({"error": "You must be logged in to add items to the cart"}), 401

    myproduct = Product.query.get_or_404(pro_id)
    cart_item = Cart.query.filter_by(cust_id=session['cust_id'], pro_id=pro_id).first()

    if cart_item:
        cart_item.cart_quantity += 1
    else:
        cart_item = Cart(cust_id=session['cust_id'], pro_id=pro_id, cart_quantity=1)
        db.session.add(cart_item)

    db.session.commit()

    return jsonify({
        "message": "Item added to cart successfully!",
        "redirect": "/cart/"  # <-- ADD A VALID REDIRECT URL
    })





 
@app.route('/cart/plus/', methods=['POST'])
def plus_cart():
    cart_id = request.form.get('cart_id', type=int)
    pro_id = request.form.get('pro_id', type=int)
    cust_id = session.get('cust_id')

    if cust_id:
        # Logged-in user: Update cart in database
        cart_item = db.session.query(Cart).filter_by(cart_id=cart_id, cust_id=cust_id).first()
        if cart_item:
            cart_item.cart_quantity += 1
            db.session.commit()
            flash('Item quantity increased!', 'success')
        else:
            flash('Cart item not found!', 'error')
    else:
        # Guest user: Update cart in session
        if 'cart' in session:
            for item in session['cart']:
                if item['pro_id'] == pro_id:
                    item['cart_quantity'] += 1
                    session.modified = True
                    flash('Item quantity increased!', 'success')
                    break
    
    return redirect(url_for('get_cart'))



@app.route('/cart/minus/', methods=['POST'])
def minus_cart():
    cart_id = request.form.get('cart_id', type=int)
    pro_id = request.form.get('pro_id', type=int)
    cust_id = session.get('cust_id')

    if cust_id:
        # Logged-in user: Update cart in database
        cart_item = db.session.query(Cart).filter_by(cart_id=cart_id, cust_id=cust_id).first()
        if cart_item:
            if cart_item.cart_quantity > 1:
                cart_item.cart_quantity -= 1
            else:
                db.session.delete(cart_item)
            db.session.commit()
            flash('Item quantity updated!', 'success')
        else:
            flash('Cart item not found!', 'error')
    else:
        # Guest user: Update cart in session
        if 'cart' in session:
            for item in session['cart']:
                if item['pro_id'] == pro_id:
                    if item['cart_quantity'] > 1:
                        item['cart_quantity'] -= 1
                    else:
                        session['cart'].remove(item)
                    session.modified = True
                    flash('Item quantity updated!', 'success')
                    break
    
    return redirect(url_for('get_cart'))


@app.route('/cart/remove/', methods=['POST'])
def remove_cart():
    cart_id = request.form.get('cart_id', type=int)
    pro_id = request.form.get('pro_id', type=int)
    cust_id = session.get('cust_id')

    if cust_id:
        # Logged-in user: Remove item from database
        cart_item = db.session.query(Cart).filter_by(cart_id=cart_id, cust_id=cust_id).first()
        if cart_item:
            db.session.delete(cart_item)
            db.session.commit()
            flash('Item removed from cart!', 'success')
        else:
            flash('Cart item not found!', 'error')
    else:
        # Guest user: Remove item from session
        if 'cart' in session:
            session['cart'] = [item for item in session['cart'] if item['pro_id'] != pro_id]
            session.modified = True
            flash('Item removed from cart!', 'success')
    
    return redirect(url_for('get_cart'))



@app.route('/checkout/', methods=['GET', 'POST'])
def checkout():
    if 'cust_id' not in session:
        flash('You need to log in to proceed with checkout!', 'error')
        return redirect(url_for('user_login'))
    
    cust_id = session['cust_id']
    cart_items = Cart.query.filter_by(cust_id=cust_id).all()
    
    if not cart_items:
        flash('Your cart is empty!', 'error')
        return redirect(url_for('get_cart'))
    
    checkout_form = CheckoutForm()
    
    # Calculate total price based on product prices and cart quantity
    total_price = sum(item.cart_quantity * item.myproduct.pro_price for item in cart_items if item.myproduct)
    transaction_fee = round(total_price * 0.035, 2)
    final_total = total_price + transaction_fee

    # Check if an order already exists
    order = Order.query.filter_by(order_custid=cust_id, order_status="Pending").first()

    if request.method == 'POST':
        if checkout_form.validate_on_submit():
            if not order:  # Create new order if none exists
                order = Order(
                    order_custid=cust_id,
                    order_totalamt=final_total,
                    order_status='Pending'
                )
                db.session.add(order)
                db.session.flush()  # Get order_id before commit
                db.session.refresh(order)  # Ensure order_id is assigned
                
            try:
                # Store order_id in session before committing cart clear
                session['order_id'] = order.order_id
                
                # Loop through cart items to create order details
                for item in cart_items:
                    if item.myproduct:  # Ensure product exists
                        order_detail = Orderdetails(
                            orderdetails_order_id=order.order_id,
                            orderdetails_pro_id=item.pro_id,  # Correct reference to product ID
                            orderdetails_quantity=item.cart_quantity,
                            orderdetails_amt=item.cart_quantity * item.myproduct.pro_price
                        )
                        db.session.add(order_detail)
                
                db.session.commit()  # Commit order and order details

                #  Create a pending payment record
                new_payment = Payment(
                    payment_custid=cust_id,
                    payment_order_id=order.order_id,
                    payment_amt=order.order_totalamt,  #  Use updated order total
                    payment_status="pending"
                )
                db.session.add(new_payment)
                db.session.commit()

                # Clear the cart after order is placed
                Cart.query.filter_by(cust_id=cust_id).delete()
                db.session.commit()

                flash('Your order has been placed. Proceed to payment.', 'success')
                return redirect(url_for('payment_confirmation'))

            except Exception as e:
                db.session.rollback()  # Rollback on error
                app.logger.error(f"Error processing checkout: {e}")
                flash('There was an error processing your order. Please try again.', 'error')
                return redirect(url_for('checkout'))
        else:
            flash('Please fill out all required fields correctly.', 'error')
    
    return render_template('user/checkout.html', 
                           cart_items=cart_items, 
                           checkoutform=checkout_form, 
                           total_price=total_price, 
                           transaction_fee=transaction_fee, 
                           final_total=final_total,
                           order=order)





products = [
    {"pro_id": 1, "pro_name": "Ankara", "pro_price": 10000,"pro_design_id": 1,"pro_status": "Available", "pro_pix": "/static/pix/cat2.jpg"},
    {"pro_id": 2, "pro_name": "Satin", "pro_price": 12000, "pro_design_id": 2,"pro_status": "Available","pro_pix": "/static/pix/ballg.jpg"},
    {"pro_id": 3, "pro_name": "Summer Outfit", "pro_price": 15000, "pro_design_id": 3,"pro_status": "Available","pro_pix": "/static/pix/sum.jpg"},
    {"pro_id": 4, "pro_name": "Skirt", "pro_price": 15000,"pro_design_id": 4,"pro_status": "Available", "pro_pix": "/static/pix/cart.jpg"},
    {"pro_id": 5, "pro_name": "crepe", "pro_price": 15000,"pro_design_id": 5,"pro_status": "pending", "pro_pix": "/static/pix/cloth.JPG"},
    {"pro_id": 6, "pro_name": "short", "pro_price": 12000,"pro_design_id": 6,"pro_status": "Available", "pro_pix": "/static/pix/short.jpg"},
    {"pro_id": 7, "pro_name": "cotton gown", "pro_price": 25000,"pro_design_id": 7,"pro_status": "Available", "pro_pix": "/static/pix/cat3.jpg"},
    {"pro_id": 8, "pro_name": "floral gown", "pro_price": 14000,"pro_design_id": 8,"pro_status": "Available", "pro_pix": "/static/pix/cat4.jpg"}
    
    
]


@app.route('/orders/')
def order_page():
    products = Product.query.all()  # Fetch all products from the database
    return render_template('user/order.html', products=products)










@app.route('/orderdetail/', methods=['POST'])  # Use POST for inserting data
def add_order_detail():
    try:
        # Get data from JSON request
        data = request.get_json()
        orderdetails_order_id = data.get('orderdetails_order_id')
        orderdetails_pro_id = data.get('orderdetails_pro_id')
        orderdetails_quantity = data.get('orderdetails_quantity')

        # Validate data
        if not all([orderdetails_order_id, orderdetails_pro_id, orderdetails_quantity]):
            return jsonify({"error": "Missing required fields"}), 400

        # Check if product exists
        product = Product.query.filter_by(pro_id=orderdetails_pro_id).first()
        if not product:
            return jsonify({"error": f"Product ID {orderdetails_pro_id} does not exist."}), 404

        # Calculate total price for this order detail (quantity * unit price)
        total_price = orderdetails_quantity * product.pro_price

        # Create new order detail entry with total price
        new_order_detail = Orderdetails(
            orderdetails_order_id=orderdetails_order_id,
            orderdetails_pro_id=orderdetails_pro_id,
            orderdetails_quantity=orderdetails_quantity,
            orderdetails_amt=total_price  
        )
        db.session.add(new_order_detail)
        db.session.commit()
        
        return jsonify({"message": "Order detail added successfully", "total_price": total_price}), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500



@app.route('/pay/', methods=['GET', 'POST'])
def make_payment():
    loggedin_cust = session.get('loggedin')
    if loggedin_cust:
        order = Order.query.filter_by(order_custid=loggedin_cust, order_status="Pending").order_by(Order.order_date.desc()).first()
        
        if not order:
            flash("Error: Order not found", "error")
            return redirect('/checkout/')
        
        if request.method == 'GET':
            cust_deets = Customer.query.get(loggedin_cust)
            return render_template("user/pay.html", cust_deets=cust_deets, order=order)
        else:
            amt = order.order_totalamt  
            ref = int(random.random() * 1000000000)
            session['refno'] = ref

            pay = Payment(payment_custid=loggedin_cust, payment_amt=amt, payment_ref=ref, payment_order_id=order.order_id)
            db.session.add(pay)
            db.session.commit()
            
            return redirect('/pay/confirm/')
    else:
        flash("Error: Payment not found", "error")
        return redirect('/checkout/')
    

# @app.route('/pay/confirm/', methods=['GET', 'POST'])
# def payment_confirmation():
#     loggedin_cust = session.get('loggedin')
#     if loggedin_cust:
#         refno = session.get('refno')
#         if refno:
#             trxdeets = Payment.query.filter_by(payment_ref=refno).first()
#             if not trxdeets:
#                 flash("Error: No transaction found for this reference.", "error")
#                 return redirect('/pay/')

#             if request.method == 'GET':
#                 return render_template('user/pay_confirm.html', trxdeets=trxdeets)
#             else:
#                 url = "https://api.paystack.co/transaction/initialize"
#                 PAYSTACK_SECRET_KEY = os.getenv('PAYSTACK_SECRET_KEY')

#                 headers = {
#                     "Content-Type": "application/json",
#                     "Authorization": f"Bearer {PAYSTACK_SECRET_KEY}"
#                 }

#                 amt_kobo = int(trxdeets.payment_amt * 100)
#                 data = {
#                     "reference": refno,
#                     "amount": amt_kobo,
#                     "email": trxdeets.cust.cust_email,
#                     "callback_url": "http://127.0.0.1:8082/payment/update/"
#                 }
                
#                 response = requests.post(url, headers=headers, data=json.dumps(data))
#                 json_response = json.loads(response.text)

#                 if json_response.get('status'):
#                     return redirect(json_response['data']['authorization_url'])
#                 else:
#                     flash("Error: Payment initialization failed.", "error")
#                     return redirect('/pay/')
#         else:
#             flash("Error: Please start the transaction from the payment page.", "error")
#             return redirect('/pay/')
#     else:
#         flash("Error: You must be logged in to confirm payment.", "error")
#         return redirect('/login/')

@app.route('/pay/confirm/', methods=['GET', 'POST'])
def payment_confirmation():
    loggedin_cust = session.get('loggedin')
    if not loggedin_cust:
        flash("Error: You must be logged in to confirm payment.", "error")
        return redirect('/login/')
    
    refno = session.get('refno')
    if not refno:
        flash("Error: Transaction reference missing. Please start again.", "error")
        return redirect('/pay/')
    
    trxdeets = Payment.query.filter_by(payment_ref=refno).first()
    if not trxdeets:
        flash("Error: No transaction found for this reference.", "error")
        return redirect('/pay/')
    
    print(f"DEBUG: trxdeets = {trxdeets}")  # Debugging

    if request.method == 'GET':
        return render_template('user/pay_confirm.html', trxdeets=trxdeets)
    
    # Handling POST request
    url = "https://api.paystack.co/transaction/initialize"
    PAYSTACK_SECRET_KEY = os.getenv('PAYSTACK_SECRET_KEY')

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {PAYSTACK_SECRET_KEY}"
    }

    amt_kobo = int(trxdeets.payment_amt * 100)
    data = {
        "reference": refno,
        "amount": amt_kobo,
        "email": trxdeets.cust.cust_email,
        "callback_url": "http://127.0.0.1:8082/payment/update/"
    }
    
    response = requests.post(url, headers=headers, data=json.dumps(data))
    json_response = json.loads(response.text)

    if json_response.get('status'):
        return redirect(json_response['data']['authorization_url'])
    else:
        flash("Error: Payment initialization failed.", "error")
        return redirect('/pay/')


@app.route('/payment/update/')
def paystack_update():
    loggedin_cust = session.get('loggedin')
    refno = session.get('refno')

    if loggedin_cust and refno:
        try:
            PAYSTACK_SECRET_KEY = os.getenv('PAYSTACK_SECRET_KEY')

            url = f"https://api.paystack.co/transaction/verify/{refno}"
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {PAYSTACK_SECRET_KEY}"
            }
            response = requests.get(url, headers=headers)
            rsp = json.loads(response.text)

            print("DEBUG: Paystack Response JSON:", rsp)  # Debugging

            if rsp.get('status') and rsp['data']['status'] == "success":  #  Ensure payment success
                pay = db.session.query(Payment).filter(Payment.payment_ref == refno).first()

                if pay:
                    pay.payment_status = 'paid'
                    pay.payment_date = datetime.utcnow()
                    db.session.commit()

                    #  Update order status to "Processing"
                    order = db.session.query(Order).filter_by(order_id=pay.payment_order_id).first()
                    if order:
                        order.order_status = 'Processing'
                        db.session.commit()

                    flash("successmsg", "Payment successful!")
                else:
                    flash("errormsg", "Payment record not found.")

            else:  #  Payment verification failed
                failure_reason = rsp.get('message', 'Payment failed')
                pay = db.session.query(Payment).filter(Payment.payment_ref == refno).first()

                if pay:
                    pay.payment_status = 'failed'
                    pay.payment_date = datetime.utcnow()  # Store timestamp
                    db.session.commit()

                flash("errormsg", f"Payment verification failed: {failure_reason}")

            return redirect("/dashboard/")

        except Exception as e:
            print("ERROR: Paystack verification failed", e)  # Log error
            flash("errormsg", "Paystack is down, try again.")
            return redirect('/pay/')

    else:
        flash("errormsg", "Invalid session. Please start the payment process again.")
        return redirect('/checkout/')
