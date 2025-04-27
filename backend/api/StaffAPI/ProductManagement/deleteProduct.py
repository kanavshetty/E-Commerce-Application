from flask import Blueprint, request, jsonify
from api.DatabaseConnection.connection import DBConnection

product_api = Blueprint('delete_product_api', __name__)

@product_api.route('/api/delete-product', methods=['DELETE'])
def delete_product():
    data = request.json

    product_id = data.get("product_id")

    if not product_id:
        return jsonify(success=False, message="Missing product_id"), 400

    try:
        db_connection = DBConnection.get_instance().get_connection()
        cursor = db_connection.cursor()

        cursor.execute("""
            DELETE FROM products
            WHERE product_id = %s;
        """, (product_id,))

        db_connection.commit()
        cursor.close()

        return jsonify(success=True, message="Product deleted successfully!"), 200
    except Exception as e:
        return jsonify(success=False, message=f"An error occurred: {str(e)}"), 500
