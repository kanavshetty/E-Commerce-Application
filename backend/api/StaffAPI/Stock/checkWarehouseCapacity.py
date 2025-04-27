from flask import Blueprint, request, jsonify
from api.DatabaseConnection.connection import DBConnection

warehouse_api = Blueprint('check_warehouse_capacity_api', __name__)

@warehouse_api.route('/api/check-warehouse-capacity', methods=['GET'])
def check_warehouse_capacity():
    warehouse_id = request.args.get('warehouse_id')

    if not warehouse_id:
        return jsonify(success=False, message="Missing warehouse_id"), 400

    try:
        db_connection = DBConnection.get_instance().get_connection()
        cursor = db_connection.cursor()

        # Get warehouse max size
        cursor.execute("""
            SELECT size
            FROM warehouses
            WHERE warehouse_id = %s;
        """, (warehouse_id,))
        
        warehouse = cursor.fetchone()

        if not warehouse:
            return jsonify(success=False, message="Warehouse not found"), 404

        max_size = warehouse[0]

        # Sum of all stock in this warehouse
        cursor.execute("""
            SELECT COALESCE(SUM(quantity), 0)
            FROM stock
            WHERE warehouse_id = %s;
        """, (warehouse_id,))

        used_size = cursor.fetchone()[0]

        available_space = max_size - used_size

        cursor.close()

        return jsonify(
            success=True,
            max_size=max_size,
            used_size=used_size,
            available_space=available_space
        ), 200
    except Exception as e:
        return jsonify(success=False, message=f"An error occurred: {str(e)}"), 500
