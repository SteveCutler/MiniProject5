



from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from marshmallow import fields, validate
from marshmallow import ValidationError

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+mysqlconnector://root:Lazerbeak12@localhost/e_commerce_db'
db = SQLAlchemy(app)
ma = Marshmallow(app)


#Customer Schema Creation
class CustomerSchema(ma.Schema):
    name = fields.String(required=True)
    email = fields.String(required=True)
    phone = fields.String(required=True)
    id = fields.Integer()

customer_schema = CustomerSchema()
customers_schema = CustomerSchema(many=True)

#Customer Account Schema Creation

class CustomerAccountSchema(ma.Schema):
    id = fields.Integer()
    username = fields.String(required=True, validate=validate.Length(min=4))
    password = fields.String(required=True, validate=validate.Length(min=4))


customerAccount_schema = CustomerAccountSchema()
customerAccounts_schema = CustomerAccountSchema(many=True)


#Product Schema

class ProductSchema(ma.Schema):
    id = fields.Integer()
    name = fields.String(required=True, validate = validate.Length(min=1))
    price = fields.Float(required = True)

productSchema = ProductSchema()
productsSchema = ProductSchema(many=True)

#Order Schema

class OrderSchema(ma.Schema):
    id = fields.Integer()
    date = fields.Date(required=True)
    customer_id = fields.Integer(required = True)
    product_id = fields.Integer(required=True)

orderSchema = OrderSchema()
ordersSchema = OrderSchema(many=True)



##Tables

class Customer(db.Model):
    __tablename__ = 'Customers'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255),nullable=False)
    email = db.Column(db.String(255))
    phone = db.Column(db.String(15))
    orders = db.relationship('Order', backref='customer') #one-to-many

class Order(db.Model):
    __tablename__ = 'Orders'
    id = db.Column(db.Integer, primary_key = True)
    date = db.Column(db.Date, nullable = False)
    customer_id = db.Column(db.Integer, db.ForeignKey('Customers.id'))
    product_id = db.Column(db.Integer, db.ForeignKey('Products.id'))
    



class CustomerAccount(db.Model):
    __tablename__ = "Customer_Accounts"
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(255), unique = True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    customer_id = db.Column(db.Integer, db.ForeignKey("Customers.id"))
    customer = db.relationship("Customer", backref = "customer_accounts", uselist = False) #one-to-one

order_product = db.Table("Order_Product",
        db.Column("order_id", db.Integer, db.ForeignKey("Orders.id"), primary_key = True),
        db.Column("product_id", db.Integer, db.ForeignKey("Products.id"), primary_key = True)
    )

class Product(db.Model):
    __tablename__ = "Products"
    id = db.Column(db.Integer, primary_key = True)
    name = db.Column(db.String(255), nullable = False)
    price = db.Column(db.Float(10), nullable = False)
    orders = db.relationship('Order', secondary = order_product, backref="product")

#Customers CRUD

@app.route("/customers", methods = ['GET'])
def get_all_customers():
   
    customers = Customer.query.all()
    return customers_schema.jsonify(customers)

@app.route("/customers/<int:id>", methods = ['GET'])
def get_customers(id):

    customer = Customer.query.get_or_404(id)
    return customer_schema.jsonify(customer)

@app.route('/customers', methods=['POST'])
def add_customer():

    try:
        customer_data = customer_schema.load(request.json)
    except ValidationError as err:
        return jsonify(err.messages), 400

    new_customer = Customer(name=customer_data['name'], email=customer_data['email'], phone=customer_data['phone'])
    db.session.add(new_customer)
    db.session.commit()
    return jsonify({"message": "New Customer added succesfully!"}), 201

@app.route('/customers/<int:id>', methods = ['PUT'])
def update_customer(id):
    customer = Customer.query.get_or_404(id)

    try:
        customer_data = customer_schema.load(request.json)
    except ValidationError as err:
        return jsonify(err.messages), 400

    customer.name = customer_data['name']
    customer.email = customer_data['email']
    customer.phone = customer_data['phone']

    db.session.commit()
    return jsonify({"message":"Customer details updated succesfully!"}), 200

@app.route('/customers/<int:id>', methods = ['DELETE'])
def delete_customer(id):
    customer = Customer.query.get_or_404(id)
    db.session.delete(customer)
    db.session.commit()
    return jsonify({"message":"Customer Deleted succesfully!"}), 200

## Account CRUD

@app.route("/accounts", methods = ['GET'])
def get_all_accounts():

    accounts = CustomerAccount.query.all()
    return customerAccounts_schema.jsonify(accounts)


@app.route("/accounts/<int:id>", methods = ['GET'])
def get_accounts(id):
    account = CustomerAccount.query.get_or_404(id)

    return customerAccount_schema.jsonify(account)

@app.route('/accounts', methods=['POST'])
def add_accounts():

    try:
        newAccountData = customerAccount_schema.load(request.json)
    except ValidationError as err:
        return jsonify(err.messages), 400

    newCustomerAccount = CustomerAccount(username=newAccountData['username'], password=newAccountData['password'])
    db.session.add(newCustomerAccount)
    db.session.commit()
    return jsonify({"message": "New Customer Account added succesfully!"}), 201

@app.route('/accounts/<int:id>', methods = ['PUT'])
def update_customerAccount(id):
    account = CustomerAccount.query.get_or_404(id)

    try:
        account_data = customerAccount_schema.load(request.json)
    except ValidationError as err:
        return jsonify(err.messages), 400

    account.username = account_data['username']
    account.password = account_data['password']

    db.session.commit()
    return jsonify({"message":"Customer details updated succesfully!"}), 200

@app.route('/accounts/<int:id>', methods = ['DELETE'])
def delete_accoun(id):
    account = CustomerAccount.query.get_or_404(id)
    db.session.delete(account)
    db.session.commit()
    return jsonify({"message":"Customer Deleted succesfully!"}), 200


### Product CRUD

@app.route("/products", methods = ['GET'])
def get_all_products():
    products = Product.query.all()
    return productsSchema.jsonify(products)

@app.route("/products/<int:id>", methods = ['GET'])
def get_products(id):

    product = Product.query.get_or_404(id)
    return productSchema.jsonify(product)

@app.route('/products', methods=['POST'])
def add_products():

    try:
        newProductData = productSchema.load(request.json)
    except ValidationError as err:
        return jsonify(err.messages), 400

    newProduct = Product(name=newProductData['name'], price=newProductData['price'])
    db.session.add(newProduct)
    db.session.commit()
    return jsonify({"message": "New Product added succesfully!"}), 201

@app.route('/products/<int:id>', methods = ['PUT'])
def update_Product(id):
    product = Product.query.get_or_404(id)

    try:
        product_data = productSchema.load(request.json)
    except ValidationError as err:
        return jsonify(err.messages), 400

    product.name = product_data['name']
    product.price = product_data['price']

    db.session.commit()
    return jsonify({"message":"Product details updated succesfully!"}), 200

@app.route('/products/<int:id>', methods = ['DELETE'])
def delete_product(id):
    product = Product.query.get_or_404(id)
    db.session.delete(product)
    db.session.commit()
    return jsonify({"message":"Product Deleted succesfully!"}), 200



#ORDER CRUD

@app.route("/orders", methods = ['GET'])
def get_all_orders():
    orders = Order.query.all()
    return ordersSchema.jsonify(orders)

@app.route("/orders/<int:id>/", methods = ['GET'])
def get_order(id):

    order = Order.query.get_or_404(id)
    return orderSchema.jsonify(order)

@app.route('/orders', methods=['POST'])
def add_orders():

    try:
        newOrderData = orderSchema.load(request.json)
    except ValidationError as err:
        return jsonify(err.messages), 400

#newProduct = Product(name=newProductData['name'], price=newProductData['price'])

    newOrder = Order(date=newOrderData['date'],customer_id=newOrderData["customer_id"], product_id=newOrderData["product_id"])
    db.session.add(newOrder)

    db.session.commit()
    return jsonify({"message": "New Order added succesfully!"}), 201

@app.route('/orders/<int:id>', methods = ['PUT'])
def update_Order(id):
    order = Order.query.get_or_404(id)

    try:
        order_data = orderSchema.load(request.json)
    except ValidationError as err:
        return jsonify(err.messages), 400

    order.date = order_data['date']
    order.customer_id = order_data['customer_id']
    order.product_id = order_data['product_id']

    db.session.commit()
    return jsonify({"message":"Order details updated succesfully!"}), 200

@app.route('/orders/<int:id>', methods = ['DELETE'])
def delete_order(id):
    order = Order.query.get_or_404(id)
    db.session.delete(order)
    db.session.commit()
    return jsonify({"message":"Order Deleted succesfully!"}), 200



with app.app_context():
    db.create_all()

if __name__ == '__main__':
    app.run(debug=True)