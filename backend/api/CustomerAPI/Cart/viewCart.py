from flask import Blueprint, request, jsonify
from api.DatabaseConnection.connection import DBConnection

cart_api = Blueprint('view_cart_api', __name__)

@cart_api.route('/api/view-cart', methods=['GET'])
def view_cart():
    customer_id = request.args.get('customer_id')

    if not customer_id:
        return jsonify(success=False, message="Missing customer_id"), 400

    try:
        db_connection = DBConnection.get_instance().get_connection()
        cursor = db_connection.cursor()

        cursor.execute("""
            SELECT sc.product_id, p.name, p.price, sc.quantity
            FROM shopping_cart sc
            JOIN products p ON sc.product_id = p.product_id
            WHERE sc.customer_id = %s;
        """, (customer_id,))

        items = cursor.fetchall()
        cursor.close()

        cart_items = []
        for item in items:
            cart_items.append({
                "product_id": item[0],
                "product_name": item[1],
                "price": item[2],
                "quantity": item[3],
            })

        return jsonify(success=True, cart=cart_items), 200
    except Exception as e:
        return jsonify(success=False, message=f"An error occurred: {str(e)}"), 500
