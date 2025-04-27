from flask import Blueprint, request, jsonify
from api.DatabaseConnection.connection import DBConnection

product_api = Blueprint('add_product_api', __name__)

@product_api.route('/api/add-product', methods=['POST'])
def add_product():
    data = request.json

    name = data.get("name")
    description = data.get("description")
    category = data.get("category")
    brand = data.get("brand")
    size = data.get("size")
    price = data.get("price")

    if not all([name, description, category, brand, size, price]):
        return jsonify(success=False, message="Missing product fields"), 400

    try:
        db_connection = DBConnection.get_instance().get_connection()
        cursor = db_connection.cursor()

        cursor.execute("""
            INSERT INTO products (name, description, category, brand, size, price)
            VALUES (%s, %s, %s, %s, %s, %s)
            RETURNING product_id;
        """, (name, description, category, brand, size, price))

        product_id = cursor.fetchone()[0]

        db_connection.commit()
        cursor.close()

        return jsonify(success=True, message="Product added successfully!", product_id=product_id), 201
    except Exception as e:
        return jsonify(success=False, message=f"An error occurred: {str(e)}"), 500
