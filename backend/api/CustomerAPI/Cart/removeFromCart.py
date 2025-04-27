from flask import Blueprint, request, jsonify
from api.DatabaseConnection.connection import DBConnection

cart_api = Blueprint('remove_from_cart_api', __name__)

@cart_api.route('/api/remove-from-cart', methods=['DELETE'])
def remove_from_cart():
    data = request.json

    customer_id = data.get("customer_id")
    product_id = data.get("product_id")

    if not all([customer_id, product_id]):
        return jsonify(success=False, message="Missing fields"), 400

    try:
        db_connection = DBConnection.get_instance().get_connection()
        cursor = db_connection.cursor()

        cursor.execute("""
            DELETE FROM shopping_cart
            WHERE customer_id = %s AND product_id = %s;
        """, (customer_id, product_id))

        db_connection.commit()
        cursor.close()

        return jsonify(success=True, message="Item removed from cart"), 200
    except Exception as e:
        return jsonify(success=False, message=f"An error occurred: {str(e)}"), 500
