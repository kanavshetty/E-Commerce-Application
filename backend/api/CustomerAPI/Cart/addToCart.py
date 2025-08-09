from flask import Blueprint, request, jsonify
from api.DatabaseConnection.connection import DBConnection
import traceback
import psycopg2.extras  # assuming PostgreSQL

cart_api = Blueprint('add_to_cart_api', __name__)

@cart_api.route('/api/add-to-cart', methods=['POST'])
def add_to_cart():
    data = request.get_json()

    customer_id = data.get("customer_id")
    product_id = data.get("product_id")
    quantity = data.get("quantity", 1)

    try:
        # Validate and convert types
        customer_id = int(customer_id)
        product_id = int(product_id)
        quantity = int(quantity)

        db = DBConnection.get_instance().get_connection()
        cursor = db.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

        # Check if cart exists for this customer
        cursor.execute("SELECT cart_id FROM shopping_carts WHERE customer_id = %s LIMIT 1;", (customer_id,))
        cart = cursor.fetchone()

        if cart:
            cart_id = cart["cart_id"]
        else:
            # Create new cart
            cursor.execute(
                "INSERT INTO shopping_carts (customer_id) VALUES (%s) RETURNING cart_id;",
                (customer_id,)
            )
            cart_id = cursor.fetchone()["cart_id"]

        # Check if item already exists
        cursor.execute(
            "SELECT quantity FROM cart_items WHERE cart_id = %s AND product_id = %s;",
            (cart_id, product_id)
        )
        item = cursor.fetchone()

        if item:
            new_qty = item["quantity"] + quantity
            cursor.execute(
                "UPDATE cart_items SET quantity = %s WHERE cart_id = %s AND product_id = %s;",
                (new_qty, cart_id, product_id)
            )
        else:
            cursor.execute(
                "INSERT INTO cart_items (cart_id, product_id, quantity) VALUES (%s, %s, %s);",
                (cart_id, product_id, quantity)
            )

        db.commit()
        cursor.close()
        return jsonify(success=True, message="Item added to cart"), 201

    except Exception as e:
        traceback.print_exc()
        return jsonify(success=False, message=f"An error occurred: {e}"), 500
