from flask import Blueprint, render_template, redirect, url_for, jsonify
from db import db
from models import Customer, Product, Order, Category

html_bp = Blueprint("html", __name__)

@html_bp.route("/")
def home():
    return render_template("base.html")



@html_bp.route('/customers')
def customers():
    #Cheese with .query.all() instead of db.select(Customer).order_by(Customer.name)
    customer_list = Customer.query.all()
    return render_template('customers.html', customers=customer_list)


@html_bp.route('/products')
def products():
    # Cheese with .query.all() instead of db.select(Product).order_by(Product.name)
    product_list = Product.query.all()
    return render_template('products.html', products=product_list)

#Orders html

@html_bp.route('/orders')
def orders():
    # Cheese with .query.all() instead of db.select(Product).order_by(Product.name)
    order_list = Order.query.all()
    return render_template('orders.html', orders=order_list)


@html_bp.route("/order/<int:order_id>")
def order_detail(order_id):
    # Retrieve the order from the database using the order_id
    order = Order.query.get(order_id)
    if not order:
        return "Order not found", 404
    # Calculate the estimated total for the order
    estimated_total = order.calculate_total()
    #estimated_total = order.total
    # Render the template with order details
    return render_template("order_detail.html", order=order, estimated_total=estimated_total)
@html_bp.route("/orders/<int:order_id>/delete", methods=["POST"])
def order_delete_web(order_id):
    # Need this to avoid a bug from having 2 similar routes for some reason

    order = db.get_or_404(Order, order_id)

    if order.processed:
        return jsonify({"error": "Cannot delete a processed order"}), 400

    # Delete the order
    db.session.delete(order)
    db.session.commit()

    # Redirect the user to the list of orders
    return redirect(url_for("html.orders"))


@html_bp.route("/orders/<int:order_id>/process", methods=["POST"])
def order_process_web(order_id):
    #Need this to avoid a bug from having 2 similar routes for some reason
    # Retrieve the order from the database
    order = Order.query.get_or_404(order_id)

    # Check if the order has already been processed
    if order.processed:
        # Redirect to the order detail page with a message indicating the order has already been processed
        return redirect(url_for('html.order_detail', order_id=order_id))

    # Process the order
    success, message = order.process("adjust")
    if success:
        db.session.commit()
        return redirect(url_for('html.order_detail', order_id=order_id))

    # Redirect to the order detail page with an error message
    return redirect(url_for('html.order_detail', order_id=order_id, error=message))



    # Redirect back to the order detail page after processing
    return redirect(url_for('order_detail', order_id=order_id))

#Final exam additions

'''
Find customers with 0 or negative balance
Create the following route: /final/customers-warning . This route responds to GET requests, and returns JSON data with a list of all customers that have 0 or a negative balance. The list contains dictionaries, and each dictionary includes the customer name, balance, and the link to the API route for the customer JSON detail view (see term project, part 2, top of page 2) - use url_for .
'''
@html_bp.route("/final/customers-warning")
def customers_warning():
    #Get list of all customers with 0 or negative balance
    customers_with_low_balance = Customer.query.filter(Customer.balance <= 0).all()

    #Create list of dictionaries for each customer
    customers = []
    for customer in customers_with_low_balance:
        customers.append({
            "name": customer.name,
            "balance": customer.balance,
            "url": url_for("api_customers.customers_detail_json", id=customer.id)
        })
    #Return list as JSON
    return jsonify(customers)

'''
Find products that are out of stock
Create the following route: /final/out-of-stock. This route responds to GET requests, and returns a JSON list of all product names that are out of stock (= items with available quantity equal to 0). For example, if lemon and chicken are out of stock, the endpoint will return:
[
    "Lemon",
    "Chicken"
]
'''

@html_bp.route("/final/out-of-stock")
def out_of_stock():
    #Get list of all products with 0 availability
    products_out_of_stock = Product.query.filter(Product.available == 0).all()
    #Create list of each product so I can use it in the JSON
    products = []
    for product in products_out_of_stock:
        products.append({
            "name": product.name
        })
    #Return list as JSON
    return jsonify(products)

'''
List of categories (JSON)
Make up a URL of your choice that will be used to display the list of categories. This route must return a JSON list of dictionaries. Each dictionary contains:
name: the name of the category description: the description of the category products: a list of dictionaries with information for each product that belong to the category: name: the name of the product url: the link to the product page (term project). The link may just be the URL path, without the hostname (use url_for ).

'''
@html_bp.route("/final/categories")
def categories():
    # Get list of all categories names
    categories_names = db.session.query(Category).all()

    # Create list of dictionaries for each category
    categories = []
    for category in categories_names:
        # Need to get a list of all products in the category
        products_in_category = Product.query.filter_by(category=category.name).all()
        # Create list of dictionaries for each product
        json_products = []
        for product in products_in_category:
            json_products.append({
                "name": product.name,
                "url": url_for("html.products")
            })

        categories.append({
            "name": category.name,
            "description": category.description,
            "products": json_products
        })

    # Return list as JSON
    return jsonify(categories)