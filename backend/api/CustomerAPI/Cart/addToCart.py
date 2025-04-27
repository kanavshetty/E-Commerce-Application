from flask import Blueprint, request, jsonify
from api.DatabaseConnection.connection import DBConnection

cart_api = Blueprint('add_to_cart_api', __name__)

@cart_api.route('/api/add-to-cart', methods=['POST'])
def add_to_cart():
    data = request.json

    customer_id = data.get("customer_id")
    product_id = data.get("product_id")
    quantity = data.get("quantity", 1)

    if not all([customer_id, product_id]):
        return jsonify(success=False, message="Missing fields"), 400

    try:
        db_connection = DBConnection.get_instance().get_connection()
        cursor = db_connection.cursor()

        # Check if item already in cart
        cursor.execute("""
            SELECT quantity FROM shopping_cart
            WHERE customer_id = %s AND product_id = %s;
        """, (customer_id, product_id))

        existing = cursor.fetchone()

        if existing:
            # Update quantity
            new_quantity = existing[0] + quantity
            cursor.execute("""
                UPDATE shopping_cart
                SET quantity = %s
                WHERE customer_id = %s AND product_id = %s;
            """, (new_quantity, customer_id, product_id))
        else:
            # Insert new cart item
            cursor.execute("""
                INSERT INTO shopping_cart (customer_id, product_id, quantity)
                VALUES (%s, %s, %s);
            """, (customer_id, product_id, quantity))

        db_connection.commit()
        cursor.close()

        return jsonify(success=True, message="Item added to cart"), 201
    except Exception as e:
        return jsonify(success=False, message=f"An error occurred: {str(e)}"), 500
