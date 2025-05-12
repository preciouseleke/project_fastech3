from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import text
db = SQLAlchemy()

class Admin(db.Model):
    admin_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    admin_email = db.Column(db.String(100), nullable=False)
    admin_password = db.Column(db.String(255), nullable=False)
    
class Category(db.Model):
    cat_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    cat_name = db.Column(db.String(100), nullable=False)
    # Many-to-Many Relationship with Customer
    mycust = db.relationship("Customer", secondary='design', back_populates="mycat")
    
    


class Customer(db.Model):
    cust_id =db.Column(db.Integer, primary_key=True, autoincrement=True)
    cust_firstname = db.Column(db.String(100), nullable=False)
    cust_lname =db.Column(db.String(100), nullable=False)
    cust_email =db.Column(db.String(200), nullable=False)
    cust_password =db.Column(db.String(255), nullable=False)
    cust_stateid =db.Column(db.Integer(), db.ForeignKey('state.state_id'), nullable=True)
    cust_datereg =db.Column(db.DateTime(),default=datetime.utcnow)
    cust_status= db.Column(db.Enum('pending','active','inactive'), nullable=False, server_default=('active'))
    cust_coverimage = db.Column(db.String(255),nullable=True) 
    cust_lga = db.Column(db.Integer(),  db.ForeignKey('lga.lga_id'), nullable=True )
    #relationship
    
    orders= db.relationship('Order',backref='miniorder')
    #relationship for many to many
    mycat = db.relationship("Category", secondary='design', back_populates="mycust")
    cart = db.relationship('Cart', backref='mycustomer')


    
    
class Design(db.Model):
    design_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    design_name = db.Column(db.String(100), nullable=False)
    design_catid = db.Column(db.Integer, db.ForeignKey('category.cat_id'), nullable=False)
    design_custid = db.Column(db.Integer, db.ForeignKey('customer.cust_id'), nullable=False)

    category = db.relationship('Category', backref='minidesign')
    customer = db.relationship('Customer', backref='maxdesign')
    
    



class State(db.Model):
    state_id= db.Column(db.Integer(),primary_key=True,autoincrement=True)
    state_name= db.Column(db.String(100), nullable=False)
    lgas =db.relationship('Lga', backref='state')
    starcus= db.relationship('Customer',backref='mystate')

    # Relationship to Customers
    customers = db.relationship('Customer', backref='state', lazy=True)
    def __repr__(self):
        return f'{self.state_id}:{self.state_name}'
   

class Lga(db.Model):
    lga_id= db.Column(db.Integer,primary_key=True,autoincrement=True)
    lga_name= db.Column(db.String(100), nullable=False)
    lga_state=  db.Column(db.Integer(), db.ForeignKey('state.state_id'), nullable=True)

    # Relationship to Customers
    customers = db.relationship('Customer', backref='lga', lazy=True)

    def __repr__(self):
        return f'{self.lga_id}:{self.lga_name}'
    

class Payment(db.Model):
    payment_id= db. Column(db.Integer(),primary_key=True,autoincrement=True)
    payment_custid= db. Column(db.Integer(), db.ForeignKey('customer.cust_id'), nullable=False)
    payment_order_id = db.Column(db.Integer(), db.ForeignKey('order.order_id'), nullable=True)
    payment_amt= db.Column(db.Float(), nullable=True)
    payment_ref = db.Column(db.String(100), nullable=True)
    payment_status = db.Column(db.Enum('pending', 'paid', 'failed'), nullable=False, server_default='pending')

    payment_date= db. Column(db.DateTime(),default=datetime.utcnow)

    cust= db.relationship('Customer',backref='mypayments')
    order = db.relationship('Order', back_populates='pay')

class Price(db.Model):
    price_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    price_amt = db.Column(db.Float(), nullable=False)
    



class Product(db.Model):
    pro_id = db.Column(db.Integer(), primary_key=True, autoincrement=True)
    pro_name = db.Column(db.String(100), nullable=False)
    pro_price = db.Column(db.Float(), nullable=False)  # Change from String to Float
    pro_added_on = db.Column(db.DateTime, default=datetime.utcnow)
    pro_design_id = db.Column(db.Integer(), db.ForeignKey('design.design_id'), nullable=True)
    pro_status = db.Column(db.Enum('Available', 'Out of stock', 'Pending', 'Discontinued'), nullable=False, server_default='Pending')
    pro_pix = db.Column(db.String(255), nullable=True)

    des = db.relationship('Design', backref='mydesigns')
    cart = db.relationship('Cart', backref='myproduct')



class Cart(db.Model):
    cart_id= db.Column(db.Integer(),primary_key=True)
    cart_quantity= db.Column(db.Integer(), nullable=False)

    cust_id= db.Column(db.Integer(), db.ForeignKey('customer.cust_id'), nullable=True)
    pro_id= db.Column(db.Integer(), db.ForeignKey('product.pro_id'), nullable=True)
    
    def __repr__(self):
        return f'{self.cart_id}:{self.cart_quantity}'
   


class Order(db.Model):
    order_id= db.Column(db.Integer(),primary_key=True,autoincrement=True)
    order_date= db.Column(db.DateTime, default=datetime.utcnow)
    order_totalamt= db.Column(db.Float(), nullable=True)
    order_status = db.Column(db.Enum('Pending', 'Delivered', 'Processing', 'Cancelled'), nullable=False, server_default='Pending')
    order_custid= db.Column(db.Integer(), db.ForeignKey('customer.cust_id'),nullable=True)

    
    pay = db.relationship('Payment', back_populates='order', cascade="all, delete-orphan", lazy=True)


class Orderdetails(db.Model):
    orderdetails_id= db.Column(db.Integer(),primary_key=True,autoincrement=True)
    orderdetails_order_id= db.Column(db.Integer(), db.ForeignKey('order.order_id'),nullable=False)
    orderdetails_pro_id= db.Column(db.Integer(), db.ForeignKey('product.pro_id'), nullable=True)
    orderdetails_quantity= db.Column(db.Integer(),nullable=False)
    orderdetails_amt = db.Column(db.Float(), nullable=False)



    


