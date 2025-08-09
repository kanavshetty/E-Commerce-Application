from flask import Blueprint, request, jsonify
from api.DatabaseConnection.connection import DBConnection
import psycopg2.extras

cart_api = Blueprint('update_cart_item_api', __name__)

@cart_api.route('/api/update-cart', methods=['PUT'])
def update_cart_item():
    data = request.json

    customer_id = data.get("customer_id")
    product_id = data.get("product_id")
    quantity = data.get("quantity")

    # Validate input
    if not all([customer_id, product_id, quantity]):
        return jsonify(success=False, message="Missing fields"), 400

    if quantity <= 0:
        return jsonify(success=False, message="Quantity must be greater than 0"), 400

    try:
        db = DBConnection.get_instance().get_connection()
        cursor = db.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

        # Get the cart ID for this customer
        cursor.execute("SELECT cart_id FROM shopping_carts WHERE customer_id = %s", (customer_id,))
        cart = cursor.fetchone()

        if not cart:
            return jsonify(success=False, message="Cart not found for this customer"), 404

        cart_id = cart['cart_id']

        # Update quantity in cart_items
        cursor.execute("""
            UPDATE cart_items
            SET quantity = %s
            WHERE cart_id = %s AND product_id = %s;
        """, (quantity, cart_id, product_id))

        if cursor.rowcount == 0:
            return jsonify(success=False, message="Cart item not found"), 404

        db.commit()
        cursor.close()

        return jsonify(success=True, message="Cart item updated"), 200

    except Exception as e:
        db.rollback()
        return jsonify(success=False, message=f"An error occurred: {str(e)}"), 500
