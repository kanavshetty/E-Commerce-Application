from flask import Blueprint, request, jsonify
from api.DatabaseConnection.connection import DBConnection

stock_api = Blueprint('add_stock_api', __name__)

@stock_api.route('/api/add-stock', methods=['POST'])
def add_stock():
    data = request.json

    product_id = data.get("product_id")
    warehouse_id = data.get("warehouse_id")
    quantity = data.get("quantity")

    if not all([product_id, warehouse_id, quantity]):
        return jsonify(success=False, message="Missing fields"), 400

    try:
        db_connection = DBConnection.get_instance().get_connection()
        cursor = db_connection.cursor()

        # Check if stock record already exists
        cursor.execute("""
            SELECT quantity FROM stock
            WHERE product_id = %s AND warehouse_id = %s;
        """, (product_id, warehouse_id))
        
        existing = cursor.fetchone()

        if existing:
            # Update quantity
            new_quantity = existing[0] + quantity
            cursor.execute("""
                UPDATE stock
                SET quantity = %s
                WHERE product_id = %s AND warehouse_id = %s;
            """, (new_quantity, product_id, warehouse_id))
        else:
            # Insert new stock record
            cursor.execute("""
                INSERT INTO stock (product_id, warehouse_id, quantity)
                VALUES (%s, %s, %s);
            """, (product_id, warehouse_id, quantity))

        db_connection.commit()
        cursor.close()

        return jsonify(success=True, message="Stock updated successfully!"), 200
    except Exception as e:
        return jsonify(success=False, message=f"An error occurred: {str(e)}"), 500
