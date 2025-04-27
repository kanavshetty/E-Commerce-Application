from flask import Blueprint, request, jsonify
from api.DatabaseConnection.connection import DBConnection

order_api = Blueprint('update_order_status_api', __name__)

@order_api.route('/api/update-order-status', methods=['PUT'])
def update_order_status():
    data = request.json

    order_id = data.get("order_id")
    new_status = data.get("new_status")  # Should be: 'issued', 'sent', or 'received'

    if not all([order_id, new_status]):
        return jsonify(success=False, message="Missing fields"), 400

    if new_status not in ["issued", "sent", "received"]:
        return jsonify(success=False, message="Invalid status value"), 400

    try:
        db_connection = DBConnection.get_instance().get_connection()
        cursor = db_connection.cursor()

        cursor.execute("""
            UPDATE orders
            SET status = %s
            WHERE order_id = %s;
        """, (new_status, order_id))

        db_connection.commit()
        cursor.close()

        return jsonify(success=True, message="Order status updated successfully!"), 200
    except Exception as e:
        return jsonify(success=False, message=f"An error occurred: {str(e)}"), 500
