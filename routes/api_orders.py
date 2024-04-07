from flask import Blueprint, jsonify, request
from db import db
from models import Customer, Product, Order, ProductOrder
from sqlalchemy.sql import func

api_orders_bp = Blueprint("api_orders", __name__)


#display orders api
@api_orders_bp.route("/")
def orders_json():
	statement = db.select(Order).order_by(Order.created)
	results = db.session.execute(statement).scalars()
	orders_json = [order.to_json() for order in results]
	return jsonify(orders_json)

#Display Specific Order by ID
@api_orders_bp.route("/<int:order_id>")
def order_detail_json(order_id):
	statement = db.select(Order).where(Order.id == order_id)
	results = db.session.execute(statement).scalars()
	orders_json = [order.to_json() for order in results]
	return jsonify(orders_json)

#Create Order
@api_orders_bp.route("/", methods=["POST"])
def order_create():
	data = request.get_json()
	if 'customer_id' not in data or 'items' not in data:
		return "Invalid request", 400

	#Check if customer exists
	customer = db.get_or_404(Customer, data['customer_id'])

	# Extract items from the data and create ProductOrder instances
	items = data['items']
	product_orders = []
	for item in items:
		if 'name' not in item or 'quantity' not in item:
			return "Each item must have a name and quantity", 400

		product_name = item['name']
		quantity = item['quantity']
		# Find the product
		product = Product.query.filter_by(name=product_name).first()
		if not product:
			continue  # Ignore the product if it doesn't exist

		# Create ProductOrder instance
		product_order = ProductOrder(product=product, quantity=quantity)
		product_orders.append(product_order)

		#product_orders.api_orders_bpend(product_order)

	# Create the order and associate it with the customer
	new_order = Order(customer=customer, items=product_orders)
	db.session.add(new_order)
	#new_order = Order(**data)
	# Calculate and update the total for the order
	new_order.calculate_total()
	db.session.commit()
	return jsonify(new_order.to_json()), 201

#Order Api delete
@api_orders_bp.route("/<int:order_id>", methods=["DELETE"])
def order_delete(order_id):
	order = db.get_or_404(Order, order_id)
	if order.processed:
		return jsonify({"error": "Cannot delete a processed order"}), 400
	db.session.delete(order)
	db.session.commit()
	return "", 204

#Process Order thing
@api_orders_bp.route("/<int:order_id>", methods=["PUT"])
def process_order(order_id):
	order = db.get_or_404(Order, order_id)
	data = request.get_json()

	if not data or "process" not in data:
		return "Invalid request", 400

	process = data["process"]
	if "strategy" in data:
		strategy = data["strategy"]
	else:
		strategy = "adjust"

	success, message = order.process(strategy)
	if success:
		return jsonify({"message": "Order processed successfully"}), 200
	else:
		return jsonify({"message": message}), 400

	db.session.commit()
	return jsonify(order.to_json()), 200
