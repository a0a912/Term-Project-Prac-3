import csv


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

categories = read_csv('data/products.csv')

print(categories)


'''
The error you're encountering occurs because you're trying to jsonify a list of objects that include instances of your Product class, which are not directly serializable to JSON. To fix this, you need to ensure that the products are converted to JSON-compatible dictionaries before passing them to jsonify.

You can modify your Product class to include a to_json method similar to what you have in your Category class. Then, you can call this method for each product in the products_in_category list before appending it to your categories list.

Here's how you can modify your code:

python
Copy code
class Product(db.Model):
    id = mapped_column(Integer, primary_key=True)
    name = mapped_column(String(200), nullable=False, unique=True)
    price = mapped_column(DECIMAL(18, 2), nullable=False)
    available = mapped_column(Integer, nullable=False, default=0)
    category = mapped_column(String(200), nullable=False, unique=False)

    def to_json(self):
        return {
            "id": self.id,
            "name": self.name,
            "price": str(self.price),  # Convert DECIMAL to string for JSON compatibility
            "available": self.available,
        }

@html_bp.route("/final/categories")
def categories():
    # Get list of all categories names and only names
    categories_names = db.session.query(Category).all()

    # Create list of dictionaries for each category
    categories = []
    for category in categories_names:
        # Need to get a list of all products in the category
        products_in_category = Product.query.filter_by(category=category.name).all()

        # Convert products to JSON-compatible dictionaries
        products_json = [product.to_json() for product in products_in_category]

        categories.append({
            "name": category.name,
            "description": category.description,
            "products": products_json
        })

    # Return list as JSON
    return jsonify(categories)
Now, each product in the products_in_category list is converted to a JSON-compatible dictionary using the to_json method defined in the Product class before being added to the categories list. This should resolve the TypeError you were encountering.
'''