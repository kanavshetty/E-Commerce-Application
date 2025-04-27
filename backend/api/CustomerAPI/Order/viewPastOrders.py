from flask import Blueprint, request, jsonify
from api.DatabaseConnection.connection import DBConnection

order_api = Blueprint('view_past_orders_api', __name__)

@order_api.route('/api/view-past-orders', methods=['GET'])
def view_past_orders():
    customer_id = request.args.get('customer_id')

    if not customer_id:
        return jsonify(success=False, message="Missing customer_id"), 400

    try:
        db_connection = DBConnection.get_instance().get_connection()
        cursor = db_connection.cursor()

        cursor.execute("""
            SELECT o.order_id, o.status, o.order_date, dp.delivery_type
            FROM orders o
            JOIN delivery_plans dp ON o.order_id = dp.order_id
            WHERE o.customer_id = %s AND o.status = 'received'
            ORDER BY o.order_date DESC;
        """, (customer_id,))

        orders = cursor.fetchall()
        cursor.close()

        order_list = []
        for order in orders:
            order_list.append({
                "order_id": order[0],
                "status": order[1],
                "order_date": order[2],
                "delivery_type": order[3],
            })

        return jsonify(success=True, orders=order_list), 200
    except Exception as e:
        return jsonify(success=False, message=f"An error occurred: {str(e)}"), 500
