from flask import Blueprint, render_template, redirect, url_for, jsonify
from db import db
from models import Customer, Product, Order

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
