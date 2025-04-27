from flask import Blueprint, request, jsonify
from api.DatabaseConnection.connection import DBConnection

supplier_api = Blueprint('connect_supplier_product_api', __name__)

@supplier_api.route('/api/connect-supplier-product', methods=['POST'])
def connect_supplier_product():
    data = request.json

    supplier_id = data.get("supplier_id")
    product_id = data.get("product_id")
    supplier_price = data.get("supplier_price")

    if not all([supplier_id, product_id, supplier_price]):
        return jsonify(success=False, message="Missing fields"), 400

    try:
        db_connection = DBConnection.get_instance().get_connection()
        cursor = db_connection.cursor()

        cursor.execute("""
            INSERT INTO supplier_products (supplier_id, product_id, supplier_price)
            VALUES (%s, %s, %s);
        """, (supplier_id, product_id, supplier_price))

        db_connection.commit()
        cursor.close()

        return jsonify(success=True, message="Supplier connected to product successfully!"), 201
    except Exception as e:
        return jsonify(success=False, message=f"An error occurred: {str(e)}"), 500
