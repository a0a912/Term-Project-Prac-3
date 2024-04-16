from flask import Flask
from db import db
from app import app
from models import Customer, Product, Order, ProductOrder, Category
from pathlib import Path
import csv
import random
from sqlalchemy.sql import func

app.instance_path = Path("data").resolve()
app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{app.instance_path}/store.db'


# Need to read the CSV and feed the data into the database

# CSV Reader function
"""
Reads a CSV file and stores its contents in a list. 

:param filename: The name of the CSV file to read.
:return: A list containing the data read from the CSV file.
"""
def read_csv(filename):
	temp = []
	with open(filename, 'r') as file:
		reader = csv.DictReader(file)
		for row in reader:
			temp.append(row)
		return temp

# Function to create random orders

def create_random_orders(num_orders=5):
	"""
	Function to create random orders in the database.

	Parameters:
		num_orders (int): Number of random orders to create. Defaults to 5.

	Returns:
		None
	"""
	for ii in range(num_orders):
		# Randomly select one customer
		customer = db.session.query(Customer).order_by(func.random()).first()

		# Make an order for the selected customer
		order = Order(customer=customer)
		db.session.add(order)

		# Find a random product
		product = db.session.query(Product).order_by(func.random()).first()

		# Generate a random quantity for the product in the order
		rand_qty = random.randint(10, 20)

		# Add the product to the order
		product_order = ProductOrder(order=order, product=product, quantity=rand_qty)

		db.session.add(product_order)

	# Commit the changes to the database
	db.session.commit()
	# After adding all products to orders, update the total for each order
	orders = Order.query.all()
	for order in orders:
		order.calculate_total()
	db.session.commit()


def set_product_availability(min_quantity=0, max_quantity=100):
	"""
	Set the availability of products within a given quantity range.

	:param min_quantity: the minimum quantity for availability (default is 0)
	:param max_quantity: the maximum quantity for availability (default is 100)
	:return: None
	"""
	products = Product.query.all()
	for product in products:
		product.available = random.randint(min_quantity, max_quantity)
	db.session.commit()


if __name__ == '__main__':
	with app.app_context():
		db.drop_all()
		db.create_all()
		customers = read_csv('data/customers.csv')
		products = read_csv('data/products.csv')
		categories = read_csv('data/products.csv')
		#There are duplicate categories. Gotta find a way to remove them before I add them to the database :(
		#Try this approach: res = list(set(val for dic in test_list for val in dic.values()))
		unique_categories = list({category['category'] for category in categories})

		# Wait. I can cheese this with kwargs!!!!!!!!!!!
		for customer in customers:
			db.session.add(Customer(**customer))
		for product in products:
			db.session.add(Product(**product))

		for category in unique_categories:
			db.session.add(Category(name=category))
			#db.session.add(Category(name=category['category']))

		set_product_availability()
		create_random_orders(10)
		db.session.commit()
