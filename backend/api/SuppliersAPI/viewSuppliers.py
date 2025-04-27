from flask import Blueprint, request, jsonify
from api.DatabaseConnection.connection import DBConnection

supplier_api = Blueprint('view_suppliers_api', __name__)

@supplier_api.route('/api/view-suppliers', methods=['GET'])
def view_suppliers():
    try:
        db_connection = DBConnection.get_instance().get_connection()
        cursor = db_connection.cursor()

        cursor.execute("""
            SELECT s.supplier_id, s.name, s.address, p.product_id, p.name, sp.supplier_price
            FROM suppliers s
            LEFT JOIN supplier_products sp ON s.supplier_id = sp.supplier_id
            LEFT JOIN products p ON sp.product_id = p.product_id
            ORDER BY s.name ASC;
        """)

        rows = cursor.fetchall()
        cursor.close()

        suppliers = {}
        for row in rows:
            supplier_id = row[0]
            if supplier_id not in suppliers:
                suppliers[supplier_id] = {
                    "supplier_id": supplier_id,
                    "name": row[1],
                    "address": row[2],
                    "products": []
                }
            if row[3]:  # if product_id is not NULL
                suppliers[supplier_id]["products"].append({
                    "product_id": row[3],
                    "product_name": row[4],
                    "supplier_price": row[5]
                })

        return jsonify(success=True, suppliers=list(suppliers.values())), 200
    except Exception as e:
        return jsonify(success=False, message=f"An error occurred: {str(e)}"), 500
