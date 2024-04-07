from flask import Blueprint, jsonify, request
from db import db
from models import Customer

api_customers_bp = Blueprint("api_customers", __name__)


#Customers api

@api_customers_bp.route('/')
def customers_json():
	statement = db.select(Customer).order_by(Customer.name)
	results = db.session.execute(statement).scalars()
	customers_json = [customer.to_json() for customer in results]
	return jsonify(customers_json)



@api_customers_bp.route('/<int:id>')
def customers_detail_json(id):
	statement = db.select(Customer).where(Customer.id == id)
	results = db.session.execute(statement).scalars()
	customers_json = [customer.to_json() for customer in results]
	return jsonify(customers_json)



@api_customers_bp.route("/<int:customer_id>", methods=["DELETE"])
def customer_delete(customer_id):
	customer = db.get_or_404(Customer, customer_id)
	db.session.delete(customer)
	db.session.commit()
	return "", 204


#Create Customer with POST
@api_customers_bp.route("/", methods=["POST"])
def customer_create():
	data = request.get_json()
	if 'name' not in data or 'phone' not in data:
		return "Invalid request", 400
	#Hey. I can use **kwargs here to flex.
	#new_customer = Customer(name=data['name'], phone=data['phone'])
	new_customer = Customer(**data)
	db.session.add(new_customer)
	db.session.commit()
	#Check if it even worked
	return jsonify(new_customer.to_json()), 201


#PUT request to update customer
@api_customers_bp.route("/<int:customer_id>", methods=["PUT"])
def customer_update(customer_id):
	data = request.get_json()
	customer = db.get_or_404(Customer, customer_id)
	if 'balance' in data:
		customer.balance = data['balance']
	else:
		return "Invalid request", 400
	db.session.commit()
	#Why doesn't this return the updated customer and only the status code?
	return jsonify(customer.to_json()), 204

