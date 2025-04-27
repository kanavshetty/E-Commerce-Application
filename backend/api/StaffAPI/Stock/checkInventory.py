from flask import Blueprint, request, jsonify
from api.DatabaseConnection.connection import DBConnection

stock_api = Blueprint('check_inventory_api', __name__)

@stock_api.route('/api/check-inventory', methods=['GET'])
def check_inventory():
    product_id = request.args.get('product_id')

    if not product_id:
        return jsonify(success=False, message="Missing product_id"), 400

    try:
        db_connection = DBConnection.get_instance().get_connection()
        cursor = db_connection.cursor()

        cursor.execute("""
            SELECT w.address, s.quantity
            FROM stock s
            JOIN warehouses w ON s.warehouse_id = w.warehouse_id
            WHERE s.product_id = %s;
        """, (product_id,))

        stock_info = cursor.fetchall()
        cursor.close()

        stock_list = []
        for stock in stock_info:
            stock_list.append({
                "warehouse_address": stock[0],
                "quantity": stock[1]
            })

        return jsonify(success=True, stock=stock_list), 200
    except Exception as e:
        return jsonify(success=False, message=f"An error occurred: {str(e)}"), 500
