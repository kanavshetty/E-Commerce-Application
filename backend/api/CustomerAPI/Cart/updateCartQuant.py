from flask import Blueprint, request, jsonify
from api.DatabaseConnection.connection import DBConnection

cart_api = Blueprint('update_cart_item_api', __name__)

@cart_api.route('/api/update-cart-item', methods=['PUT'])
def update_cart_item():
    data = request.json

    customer_id = data.get("customer_id")
    product_id = data.get("product_id")
    quantity = data.get("quantity")

    if not all([customer_id, product_id, quantity]):
        return jsonify(success=False, message="Missing fields"), 400

    if quantity <= 0:
        return jsonify(success=False, message="Quantity must be greater than 0"), 400

    try:
        db_connection = DBConnection.get_instance().get_connection()
        cursor = db_connection.cursor()

        cursor.execute("""
            UPDATE shopping_cart
            SET quantity = %s
            WHERE customer_id = %s AND product_id = %s;
        """, (quantity, customer_id, product_id))

        db_connection.commit()
        cursor.close()

        return jsonify(success=True, message="Cart item updated"), 200
    except Exception as e:
        return jsonify(success=False, message=f"An error occurred: {str(e)}"), 500
