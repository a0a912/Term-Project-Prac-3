from flask import Blueprint, jsonify, request
from db import db
from models import Product

api_products_bp = Blueprint("api_products", __name__)



@api_products_bp.route('/')
def products_json():
	statement = db.select(Product).order_by(Product.name)
	results = db.session.execute(statement).scalars()
	products_json = [product.to_json() for product in results]
	return jsonify(products_json)




@api_products_bp.route('/<int:id>')
def products_detail_json(id):
	statement = db.select(Product).where(Product.id == id)
	results = db.session.execute(statement).scalars()
	products_json = [product.to_json() for product in results]
	return jsonify(products_json)


#Delete Product
@api_products_bp.route("/<int:product_id>", methods=["DELETE"])
def product_delete(product_id):
	product = db.get_or_404(Product, product_id)
	db.session.delete(product)
	db.session.commit()
	return "", 204


@api_products_bp.route("/", methods=["POST"])
def product_create():
	data = request.get_json()
	if 'name' not in data or 'price' not in data:
		return "Invalid request", 400
	if data['price'] <= 0:
		return "Price must be a positive float.", 400
	new_product = Product(**data)
	db.session.add(new_product)
	db.session.commit()
	return jsonify(new_product.to_json()), 201



@api_products_bp.route("/<int:product_id>", methods=["PUT"])
def product_update(product_id):
	data = request.get_json()
	product = db.get_or_404(Product, product_id)

	if 'name' in data:
		product.name = data['name']

	if 'price' in data:
		#Check if price is positive float
		try:
			product.price = float(data['price'])
			if product.price <= 0:
				return "Price must be a positive float.", 400
		except ValueError:
			return "Invalid price", 400
	#Don't know if we get quantity or available as the keyword. Need to account for both
	if 'quantity' in data or 'available' in data:
		#I can lambda this
		quantity_or_available ='quantity' if 'quantity' in data else 'available'
		try:
			product.available = int(data[quantity_or_available])
			if product.available < 0:
				return f"{quantity_or_available} must be a positive integer", 400
		except ValueError:
			return f"Invalid {quantity_or_available}", 400

	db.session.commit()
	return jsonify(product.to_json()), 204
