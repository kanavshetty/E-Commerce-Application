from flask import Blueprint, request, jsonify
from api.DatabaseConnection.connection import DBConnection
import traceback
import psycopg2.extras

cart_api = Blueprint('view_cart_api', __name__)

@cart_api.route('/api/view-cart', methods=['GET'])
def view_cart():
    customer_id = request.args.get('customer_id')

    try:
        customer_id = int(customer_id)
    except (TypeError, ValueError):
        return jsonify(success=False, message="Invalid or missing customer_id"), 400

    try:
        db_connection = DBConnection.get_instance().get_connection()
        cursor = db_connection.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

        # Step 1: Get cart_id using customer_id
        cursor.execute("""
            SELECT cart_id FROM shopping_carts WHERE customer_id = %s;
        """, (customer_id,))
        result = cursor.fetchone()

        if not result:
            return jsonify(success=True, cart=[]), 200  # No cart yet

        cart_id = result['cart_id']

        # Step 2: Get cart items with product info
        cursor.execute("""
            SELECT
                ci.product_id,
                p.name,
                pp.price,
                ci.quantity
            FROM cart_items ci
            JOIN products p ON ci.product_id = p.product_id
            LEFT JOIN product_prices pp ON p.product_id = pp.product_id
            WHERE ci.cart_id = %s;
        """, (cart_id,))

        items = cursor.fetchall()
        cursor.close()

        cart_items = [
            {
                "product_id": item['product_id'],
                "product_name": item['name'],
                "price": float(item['price']) if item['price'] is not None else None,
                "quantity": item['quantity'],
            }
            for item in items
        ]

        return jsonify(success=True, cart=cart_items), 200

    except Exception as e:
        db_connection.rollback()
        traceback.print_exc()
        return jsonify(success=False, message=f"An error occurred: {str(e)}"), 500
