from sqlalchemy import Boolean, Float, Numeric, ForeignKey, Integer, String, DECIMAL, DateTime
from sqlalchemy.orm import mapped_column, relationship
from sqlalchemy.sql import func
from db import db
from datetime import datetime

# Customer Class

class Customer(db.Model):
	id = mapped_column(Integer, primary_key=True)
	name = mapped_column(String(200), nullable=False, unique=True)
	phone = mapped_column(String(20), nullable=False)
	balance = mapped_column(DECIMAL(18, 2), nullable=False, default=0)
	orders = relationship("Order")

	def to_json(self):
		return {
			"id": self.id,
			"name": self.name,
			"phone": self.phone,
			"balance": self.balance
		}


# Product Class
class Product(db.Model):
	id = mapped_column(Integer, primary_key=True)
	name = mapped_column(String(200), nullable=False, unique=True)
	price = mapped_column(DECIMAL(18, 2), nullable=False)
	available = mapped_column(Integer, nullable=False, default=0)

	def to_json(self):
		return {
			"id": self.id,
			"name": self.name,
			"price": self.price,
			"available": self.available,
		}


# Order Class
class Order(db.Model):
	id = mapped_column(Integer, primary_key=True)
	customer_id = mapped_column(Integer, ForeignKey('customer.id'), nullable=False)
	total = mapped_column(DECIMAL(18, 2), nullable=False, default=0)
	created = mapped_column(DateTime, nullable=False, default=func.now())
	processed = mapped_column(DateTime, nullable=True, default=None)
	customer = relationship("Customer", back_populates="orders")
	items = relationship("ProductOrder", cascade="all, delete-orphan")

	def to_json(self):
		items_json = []
		for thing in self.items:
			product = thing.product
			item = {"name": product.to_json()['name'], "quantity": thing.quantity}
			items_json.append(item)

		return {
			"id": self.id,
			"customer_id": self.customer_id,
			"total": self.total,
			"items": items_json,
			"created": self.created,
			"processed": self.processed
		}

#Proccessed Stuff
	def process(self, strategy="adjust"):
		#Check if already processed
		if self.processed:
			return False, "Order already processed"
		#Check if customer has enough balance
		if self.customer.balance < self.total:
			return False, "Insufficient balance"

		# Iterate through each product in the order
		for item in self.items:
			product = item.product
			quantity_ordered = item.quantity

			# Check if the quantity ordered exceeds the available quantity in the store
			if quantity_ordered > product.available:
				if strategy == 'reject':
					return False, "Order cannot be processed due to insufficient stock"
				elif strategy == 'ignore':
					item.quantity = 0
				else:  # adjust (default strategy)
					item.quantity = product.available

			# Compute the price for the product
			item_price = item.quantity * product.price

			# Subtract the quantity ordered from the quantity available in the store
			product.available -= item.quantity

			# Update the total price of the order
			self.total += item_price

		# Subtract the order price from the customer balance
		self.customer.balance -= self.total

		# Set the processed field to the current date/time
		self.processed = datetime.now()

		# Commit changes to the database
		db.session.commit()

		return True, "Order processed successfully"



	def calculate_total(self):
		total = 0
		for item in self.items:
			total += item.product.price * item.quantity
		self.total = total
		return round(self.total, 2)


class ProductOrder(db.Model):
	id = mapped_column(Integer, primary_key=True)
	order_id = mapped_column(Integer, ForeignKey(Order.id), nullable=False)
	product_id = mapped_column(Integer, ForeignKey(Product.id), nullable=False)
	quantity = mapped_column(Integer, nullable=False)
	product = relationship("Product")
	order = relationship("Order", back_populates="items")

	def to_json(self):
		return {
			"id": self.id,
			"order_id": self.order_id,
			"product_id": self.product_id,
			"quantity": self.quantity,
		}
