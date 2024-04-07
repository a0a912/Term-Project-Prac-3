from flask import Flask, render_template, jsonify, request, redirect, url_for
import csv
from pathlib import Path
from db import db
from routes.html import html_bp
from routes.api_customers import api_customers_bp
from routes.api_products import api_products_bp
from routes.api_orders import api_orders_bp
from models import Customer, Product, ProductOrder, Order



app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///store.db"
app.instance_path = Path("data").resolve()

#BluePrints
app.register_blueprint(html_bp, url_prefix="/")
app.register_blueprint(api_customers_bp, url_prefix="/api/customers")
app.register_blueprint(api_products_bp, url_prefix="/api/products")
app.register_blueprint(api_orders_bp, url_prefix="/api/orders")


db.init_app(app)



'''
# Render the customer.html file
# This route reads from the data/customers.csv file and displays a list of all customers in customers.html
@app.route("/customers")
def customers():
	#Initialize Empty List
	customer_data = []
	#Open and Read file
	with open('data/customers.csv') as file:
		#Use CSV reader
		reader = csv.DictReader(file)
		for row in reader:
			customer_data.append(row)
	return render_template("customers.html", customers=customer_data)

#Render the products.html file
#This route reads from the data/products.csv file and displays a list of all products in products.html
@app.route("/products")
def products():
    product_data = []
    with open('data/products.csv') as file:
        reader = csv.DictReader(file)
        for row in reader:
            product_data.append(row)
    return render_template("products.html", products=product_data)
'''

if __name__ == "__main__":
	app.run(debug=True, port=8888)
