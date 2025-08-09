import traceback
import psycopg2.extras
from flask import Blueprint, request, jsonify
from api.DatabaseConnection.connection import DBConnection

view_orders_api = Blueprint('view_past_orders_api', __name__)

@view_orders_api.route('/api/view-past-orders', methods=['GET'])
def view_past_orders():
    customer_id = request.args.get('customer_id')

    if not customer_id:
        return jsonify(success=False, message="Missing customer_id"), 400

    try:
        db_connection = DBConnection.get_instance().get_connection()
        cursor = db_connection.cursor(cursor_factory=psycopg2.extras.RealDictCursor)  # ✅ Fix here

        cursor.execute("""
            SELECT 
                o.order_id, 
                o.status, 
                o.order_date, 
                dp.delivery_type,
                COALESCE(SUM(oi.quantity * pp.price), 0) AS total
            FROM orders o
            LEFT JOIN delivery_plans dp ON o.order_id = dp.order_id
            LEFT JOIN order_items oi ON o.order_id = oi.order_id
            LEFT JOIN product_prices pp ON oi.product_id = pp.product_id
            WHERE o.customer_id = %s
            GROUP BY o.order_id, dp.delivery_type
            ORDER BY o.order_date DESC;

        """, (customer_id,))

        orders = cursor.fetchall()
        cursor.close()

        order_list = []
        for order in orders:
            order_list.append({
                "order_id": order['order_id'],
                "status": order['status'],
                "order_date": str(order['order_date']),
                "delivery_type": order['delivery_type'],
                "total": float(order['total'])
            })

        return jsonify(success=True, orders=order_list), 200

    except Exception as e:
        traceback.print_exc()
        return jsonify(success=False, message=f"An error occurred: {str(e)}"), 500
