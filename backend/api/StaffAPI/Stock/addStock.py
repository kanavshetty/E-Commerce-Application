from flask import Blueprint, request, jsonify
from api.DatabaseConnection.connection import DBConnection

stock_api = Blueprint('add_stock_api', __name__)

@stock_api.route('/api/add-stock', methods=['POST'])
def add_stock():
    data = request.json

    product_id = data.get("product_id")
    warehouse_id = data.get("warehouse_id")
    quantity = data.get("quantity")

    # Validate input
    if product_id is None or warehouse_id is None or quantity is None:
        return jsonify(success=False, message="Missing product_id, warehouse_id or quantity"), 400

    if not isinstance(quantity, int) or quantity <= 0:
        return jsonify(success=False, message="Quantity must be a positive integer"), 400

    try:
        db = DBConnection.get_instance().get_connection()
        cursor = db.cursor()

        # Check if record exists
        cursor.execute("""
            SELECT quantity FROM stock
            WHERE product_id = %s AND warehouse_id = %s;
        """, (product_id, warehouse_id))
        existing = cursor.fetchone()

        if existing:
            new_quantity = existing['quantity'] + quantity
            cursor.execute("""
                UPDATE stock
                SET quantity = %s
                WHERE product_id = %s AND warehouse_id = %s;
            """, (new_quantity, product_id, warehouse_id))
        else:
            cursor.execute("""
                INSERT INTO stock (product_id, warehouse_id, quantity)
                VALUES (%s, %s, %s);
            """, (product_id, warehouse_id, quantity))

        db.commit()
        cursor.close()

        return jsonify(success=True, message="Stock updated successfully"), 200

    except Exception as e:
        return jsonify(success=False, message=f"An error occurred: {str(e)}"), 500
