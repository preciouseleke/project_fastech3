import requests, json,random,secrets,os
from datetime import datetime
from flask import render_template,request,redirect,flash,session,url_for,jsonify
from werkzeug.security import generate_password_hash,check_password_hash
from werkzeug.utils import secure_filename
from fashapp import app

from fashapp.models import db,Customer,Admin,State,Lga,Payment,Category,Order,Orderdetails,Design,Product,Price

from sqlalchemy import and_, or_  ,desc

from fashapp.forms import AdminLoginForm,AddProductForm

@app.route('/admin/')
def admin_home():
   customer=db.session.query(Customer).all()
   total_records=db.session.query(Customer).count()
   result=customer
   return render_template('admin/dashboard.html',result=result,total_records=total_records)



@app.route('/adminlog/', methods=["GET", "POST"])
def admin_login():
    if "admin_loggedin" in session:  
        return redirect(url_for('admin_dashboard'))  # Redirect if already logged in

    form = AdminLoginForm()

    if form.validate_on_submit():
        email = form.email.data.strip().lower()
        password = form.password.data.strip()  # Get raw password input

        admin = Admin.query.filter_by(admin_email=email).first()

        if not admin:
            flash("Admin account not found!", "danger")
            return redirect(url_for('admin_login'))

        # Compare directly since passwords are not hashed
        if admin.admin_password == password:
            session["admin_loggedin"] = admin.admin_id  # Store admin ID in session
            flash("Login successful!", "success")
            return redirect(url_for('admin_dashboard'))
        else:
            flash("Invalid email or password!", "danger")

    return render_template("admin/login.html", adminloginform=form)


@app.route('/admin-logout/')
def admin_logout():
    session.pop("admin_loggedin", None)  # Remove admin session
    flash("Logged out successfully!", "info")
    return redirect(url_for('admin_login'))  # Redirect to login page

    



@app.route('/admin-dashboard/', methods=["GET"])
def admin_dashboard():
    admin_id = session.get("admin_loggedin")
    if not admin_id:
        flash("You need to log in first!", "error")
        return redirect(url_for("admin_login"))  

    # Fetch all products
    products = Product.query.all()

    # Fetch ordered product IDs (products that appear in Orderdetails)
    ordered_product_ids = {p[0] for p in db.session.query(Orderdetails.orderdetails_pro_id).distinct().all()}

    return render_template("admin/dashboard.html", products=products, ordered_product_ids=ordered_product_ids)


@app.route('/admin/customers/')
def customer_records():
    admin_id = session.get("admin_loggedin")
    if not admin_id:
        flash("You need to log in first!", "error")
        return redirect(url_for("admin_login"))  # Restrict access to admins

    customers = Customer.query.all()  # Fetch all customers
    return render_template('admin/customer_record.html', customers=customers)



@app.route('/customer-orders/')
def customer_orders():
    admin_id = session.get("admin_loggedin")
    if not admin_id:
        flash("You need to log in first!", "error")
        return redirect(url_for('admin_login'))  

    orders = Order.query.join(Customer, Order.order_custid == Customer.cust_id).all()  

    return render_template('admin/customer_orders.html', orders=orders)



@app.route('/delete-product/<int:pro_id>', methods=["POST"])
def delete_product(pro_id):
    admin_id = session.get("admin_loggedin")
    if not admin_id:
        flash("You need to log in first!", "error")
        return redirect(url_for("admin_login"))  

    product = Product.query.get_or_404(pro_id)

    #  Check for existing orders using the correct column name
    product_in_orders = db.session.query(Orderdetails).filter_by(orderdetails_pro_id=pro_id).first()

    if product_in_orders:
        flash("Cannot delete product. It has been ordered by a customer!", "danger")
        return redirect(url_for("view_products"))  

    db.session.delete(product)
    db.session.commit()

    flash("Product deleted successfully!", "success")
    return redirect(url_for("view_products"))  

# @app.route('/add-product/', methods=["GET", "POST"])
# def add_product():
#     admin_id = session.get("admin_loggedin")
#     if not admin_id:
#         flash("You need to log in first!", "error")
#         return redirect(url_for('admin_login'))  

#     form = AddProductForm()
#     products = Product.query.all()  # Fetch all products
#     designs = Design.query.all()  # Fetch all designs

#     if request.method == "POST" and form.validate_on_submit():
#         new_price = Price(price_amt=form.price_amt.data)
#         db.session.add(new_price)
#         db.session.commit()  

#         new_product = Product(
#             pro_name=form.pro_name.data,
#             pro_price=new_price.price_amt,
#             pro_design_id=form.pro_design_id.data,
#             pro_status=form.pro_status.data,
#             pro_added_on=datetime.utcnow()
#         )

#         #  IMAGE UPLOAD HANDLING
#         allowed_ext = ['.jpg', '.jpeg', '.png', '.gif']
#         file = request.files.get('pro_pix')

#         if file:
#             _, ext = os.path.splitext(file.filename)
#             if ext.lower() in allowed_ext:
#                 rand_str = secrets.token_hex(10)  # Generate a random filename
#                 filename = f'{rand_str}{ext}'
#                 upload_folder = os.path.join(app.root_path, 'static', 'pix')
#                 os.makedirs(upload_folder, exist_ok=True)  # Ensure directory exists
#                 file.save(os.path.join(upload_folder, filename))  # Save file
                
#                 new_product.pro_pix = f'static/pix/{filename}' # Store correct relative path
                                                                 

#         db.session.add(new_product)
#         db.session.commit()

#         flash('Product added successfully!', 'success')
#         return redirect(url_for('add_product'))  

#     return render_template('admin/add_product.html', form=form, products=products, designs=designs)

# @app.route('/add-product/', methods=["GET", "POST"])
# def add_product():
#     admin_id = session.get("admin_loggedin")
#     if not admin_id:
#         flash("You need to log in first!", "error")
#         return redirect(url_for('admin_login'))  

#     form = AddProductForm()
#     products = Product.query.all()  # Fetch all products
#     designs = Design.query.all()  # Fetch all designs

#     # Populate design choices in the form before validation
#     form.pro_design_id.choices = [(design.design_id, design.design_name) for design in designs]
    
#     # Ensure choices are not empty
#     if not form.pro_design_id.choices:
#         form.pro_design_id.choices = [(0, "No Designs Available")]

#     if request.method == "POST" and form.validate_on_submit():
#         new_price = Price(price_amt=form.price_amt.data)
#         db.session.add(new_price)
#         db.session.commit()  

#         new_product = Product(
#             pro_name=form.pro_name.data,
#             pro_price=new_price.price_amt,
#             pro_design_id=form.pro_design_id.data,
#             pro_status=form.pro_status.data,
#             pro_added_on=datetime.utcnow()
#         )

#         #  IMAGE UPLOAD HANDLING
#         allowed_ext = ['.jpg', '.jpeg', '.png', '.gif']
#         file = request.files.get('pro_pix')

#         if file:
#             _, ext = os.path.splitext(file.filename)
#             if ext.lower() in allowed_ext:
#                 rand_str = secrets.token_hex(10)  # Generate a random filename
#                 filename = f'{rand_str}{ext}'
#                 upload_folder = os.path.join(app.root_path, 'static', 'pix')
#                 os.makedirs(upload_folder, exist_ok=True)  # Ensure directory exists
#                 file.save(os.path.join(upload_folder, filename))  # Save file
                
#                 new_product.pro_pix = f'static/pix/{filename}' # Store correct relative path
                                                                 

#         db.session.add(new_product)
#         db.session.commit()

#         flash('Product added successfully!', 'success')
#         return redirect(url_for('add_product'))  

#     return render_template('admin/add_product.html', form=form, products=products, designs=designs)


# @app.route('/add-product/', methods=["GET", "POST"])
# def add_product():
#     admin_id = session.get("admin_loggedin")
#     if not admin_id:
#         flash("You need to log in first!", "error")
#         return redirect(url_for('admin_login'))  

#     form = AddProductForm()
#     products = Product.query.all()  # Fetch all products
#     designs = Design.query.all()  # Fetch all designs

#     # Populate design choices in the form before validation
#     form.pro_design_id.choices = [(d.design_id, d.design_name) for d in designs] or [(0, "No Designs Available")]

#     if request.method == "POST":
#         if form.validate_on_submit():
#             try:
#                 # Create and store price
#                 new_price = Price(price_amt=form.price_amt.data)
#                 db.session.add(new_price)
#                 db.session.commit()  

#                 # Create product
#                 new_product = Product(
#                     pro_name=form.pro_name.data,
#                     pro_price=new_price.price_amt,
#                     pro_design_id=form.pro_design_id.data,
#                     pro_status=form.pro_status.data,
#                     pro_added_on=datetime.utcnow()
#                 )

#                 # IMAGE UPLOAD HANDLING
#                 file = request.files.get('pro_pix')
#                 allowed_ext = ['.jpg', '.jpeg', '.png', '.gif']

#                 if file and file.filename:
#                     _, ext = os.path.splitext(file.filename)
#                     if ext.lower() in allowed_ext:
#                         rand_str = secrets.token_hex(10)  # Generate a random filename
#                         filename = f'{rand_str}{ext}'
#                         upload_folder = os.path.join(app.root_path, 'static', 'pix')
#                         os.makedirs(upload_folder, exist_ok=True)  # Ensure directory exists
#                         file.save(os.path.join(upload_folder, filename))  # Save file
                        
#                         new_product.pro_pix = f'static/pix/{filename}'  # Store correct relative path

#                 db.session.add(new_product)
#                 db.session.commit()

#                 flash('Product added successfully!', 'success')
#                 return redirect(url_for('add_product'))  # Redirect to product list

#             except Exception as e:
#                 db.session.rollback()  # Rollback in case of an error
#                 flash(f"Error adding product: {str(e)}", "error")
#                 print("Error adding product:", str(e))  # Debugging output

#         else:
#             print("Form validation failed:", form.errors)  # Debugging output
#             flash("Failed to add product. Please check the form fields.", "error")

#     return render_template('admin/add_product.html', form=form, products=products, designs=designs)


@app.route('/add-product/', methods=["GET", "POST"])
def add_product():
    admin_id = session.get("admin_loggedin")
    if not admin_id:
        flash("You need to log in first!", "error")
        return redirect(url_for('admin_login'))  

    form = AddProductForm()
    products = Product.query.all()  # Fetch all products
    designs = Design.query.all()  # Fetch all designs

    form.pro_design_id.choices = [(d.design_id, d.design_name) for d in designs] or [(0, "No Designs Available")]

    if request.method == "POST":
        if form.validate_on_submit():
            try:
                new_price = Price(price_amt=form.price_amt.data)
                db.session.add(new_price)
                db.session.commit()  

                new_product = Product(
                    pro_name=form.pro_name.data,
                    pro_price=new_price.price_amt,
                    pro_design_id=form.pro_design_id.data,
                    pro_status=form.pro_status.data,
                    pro_added_on=datetime.utcnow()
                )

                file = request.files.get('pro_pix')
                allowed_ext = ['.jpg', '.jpeg', '.png', '.gif']

                if file and file.filename:
                    _, ext = os.path.splitext(file.filename)
                    if ext.lower() in allowed_ext:
                        rand_str = secrets.token_hex(10)
                        filename = f'{rand_str}{ext}'
                        upload_folder = os.path.join(app.root_path, 'static', 'pix')
                        os.makedirs(upload_folder, exist_ok=True)
                        file.save(os.path.join(upload_folder, filename))
                        
                        new_product.pro_pix = f'static/pix/{filename}'

                db.session.add(new_product)
                db.session.commit()

                flash('Product added successfully!', 'success')
                return redirect(url_for('view_products'))  #  Redirect to product listing page

            except Exception as e:
                db.session.rollback()
                flash(f"Error adding product: {str(e)}", "error")
                print("Error adding product:", str(e))

        else:
            print("Form validation failed:", form.errors)
            flash("Failed to add product. Please check the form fields.", "error")

    return render_template('admin/add_product.html', form=form, products=products, designs=designs)

@app.route('/designs/')
def view_designs():
    designs = Design.query.all()
    return render_template('view_designs.html', designs=designs)

@app.route('/designs/add', methods=['GET', 'POST'])
def add_design():
    if request.method == 'POST':
        design_name = request.form.get('design_name')
        design_catid = request.form.get('design_catid')
        design_custid = request.form.get('design_custid')
        
        if not design_name or not design_catid or not design_custid:
            flash("All fields are required!", "danger")
            return redirect(url_for('add_design'))
        
        new_design = Design(
            design_name=design_name,
            design_catid=design_catid,
            design_custid=design_custid
        )
        db.session.add(new_design)
        db.session.commit()
        flash("Design added successfully!", "success")
        return redirect(url_for('view_designs'))
    
    categories = Category.query.all()
    customers = Customer.query.all()
    return render_template('add_design.html', categories=categories, customers=customers)

@app.route('/products/')
def view_products():
    products = Product.query.all()
    return render_template('admin/product_list.html', products=products)
