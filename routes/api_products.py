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

#Final Exam stuff
'''
Find products that are almost out of stock
Create the following route: /api/products/final/warning . This route responds to POST requests, and returns JSON data containing a list of all products that are below the threshold provided in the request. The list contains dictionaries. Each dictionary contains the name of the product, and how many are still available in the store.
The JSON format for the request is:
{
	"threshold": 12
}
The request above must display all products with strictly less than 12 items in stock. The format for the response is:
{
	"threshold": 12,
	"products": [
		{
			"name": "Lemon",
			"available": 3
		},
		{
			"name": "banana",
			"available": 0
		}
	]
'''

#Find products that are almost out of stock
@api_products_bp.route('/final/warning', methods=['POST'])
def products_warning():
	#Get JSON data
	data = request.get_json()
	threshold = data['threshold']

	#Get list of products below threshold
	products = Product.query.filter(Product.available < threshold).all()

	#Create list of dictionaries of name and available
	products_list = []
	for product in products:
		#Need to json it first
		product_json = product.to_json()
		products_list.append({
			'name': product_json['name'],
			'available': product_json['available']
		})
	return jsonify({
		'threshold': threshold,
		'products': products_list
	})

'''
Add products to a category (JSON)
Make up a URL of your choice to add products to a given category, and create a new route that accepts JSON data. The URL for this route must contain the name of the category. For example, to add products to the fruits category, the URL must contain fruits .
The route must answer HTTP PUT requests. You can assume the requests will always contain JSON data. The JSON data has the following format:
{
"products": [ "lemon",
"orange", "tomato" }]

You can assume the JSON data will always be a dictionary, with a key products containing a list. The list contains the names of the products that must be added to the given category. In the example above, if the request was made to /do/not/use/this/url/fruits , this will make the products lemon , orange and tomato belong to the category fruits .
The route must return the list of names of all products that now belong to the category. For example: {
"products": [ "apple", "lemon", "orange",
"strawberries", "tomato",
] }
'''
#DO I even have time to do this? Nah. It's only marks with 10 minutes. Gotta take the L here.