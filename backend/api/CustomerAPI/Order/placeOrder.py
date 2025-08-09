from flask import Blueprint, request, jsonify
from api.DatabaseConnection.connection import DBConnection
from datetime import datetime

order_api = Blueprint('place_order_api', __name__)

@order_api.route('/api/place-order', methods=['POST'])
def place_order():
    data = request.json

    customer_id = data.get("customer_id")
    credit_card_id = data.get("credit_card_id") or data.get("card_id")
    products = data.get("products")  # List of dicts: [{ "product_id": x, "quantity": y }]
    delivery_type = data.get("delivery_type", "standard")  # Default is "standard"
    delivery_price = data.get("delivery_price", 5.0)  # Default fee if none specified

    if not all([customer_id, credit_card_id, products]):
        return jsonify(success=False, message="Missing fields"), 400

    if not isinstance(products, list) or not products:
        return jsonify(success=False, message="Products must be a non-empty list"), 400

    try:
        db_connection = DBConnection.get_instance().get_connection()
        cursor = db_connection.cursor()

        # Insert the order first
        cursor.execute("""
            INSERT INTO orders (customer_id, card_id, status, order_date)
            VALUES (%s, %s, %s, %s)
            RETURNING order_id;
        """, (customer_id, credit_card_id, 'issued', datetime.utcnow()))



        order_id = cursor.fetchone()['order_id']

        # Insert each product into order_items
        for item in products:
            product_id = item["product_id"]
            quantity = item["quantity"]

            cursor.execute("""
                INSERT INTO order_items (order_id, product_id, quantity)
                VALUES (%s, %s, %s);
            """, (order_id, product_id, quantity))

        # Insert into delivery_plans
        cursor.execute("""
            INSERT INTO delivery_plans (order_id, delivery_type, delivery_price, delivery_date, ship_date)
            VALUES (%s, %s, %s, NULL, NULL);
        """, (order_id, delivery_type, delivery_price))

        # Update customer balance (assuming each product has a price you can multiply)
        total_amount = 0
        for item in products:
            product_id = item["product_id"]
            quantity = item["quantity"]

            cursor.execute("SELECT price FROM product_prices WHERE product_id = %s;", (product_id,))
            price = cursor.fetchone()['price']
            total_amount += price * quantity

        cursor.execute("""
            UPDATE customers
            SET balance = balance + %s
            WHERE customer_id = %s;
        """, (total_amount, customer_id))

        db_connection.commit()
        cursor.close()

        return jsonify(success=True, message="Order placed successfully!", order_id=order_id, total=float(total_amount)), 201
    except Exception as e:
        return jsonify(success=False, message=f"An error occurred: {str(e)}"), 500
