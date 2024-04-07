from flask import Flask
from db import db
from app import app
from models import Customer, Product, Order, ProductOrder
from pathlib import Path
import csv
import random
from sqlalchemy.sql import func

app.instance_path = Path("data").resolve()
app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{app.instance_path}/store.db'


# Need to read the CSV and feed the data into the database

# CSV Reader function
def read_csv(filename):
	temp = []
	with open(filename, 'r') as file:
		reader = csv.DictReader(file)
		for row in reader:
			temp.append(row)
		return temp


def create_random_orders(num_orders=5):
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
		# Wait. I can cheese this with kwargs!!!!!!!!!!!
		for customer in customers:
			db.session.add(Customer(**customer))
		for product in products:
			db.session.add(Product(**product))
		set_product_availability()
		create_random_orders(10)
		db.session.commit()
