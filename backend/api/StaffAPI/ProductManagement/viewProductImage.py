from flask import Blueprint, request, jsonify
from api.DatabaseConnection.connection import DBConnection

product_image_api = Blueprint('view_product_image_api', __name__)

@product_image_api.route('/api/view-product-image', methods=['GET'])
def view_product_image():
    product_id = request.args.get('product_id')

    if not product_id:
        return jsonify(success=False, message="Missing product_id"), 400

    try:
        db_connection = DBConnection.get_instance().get_connection()
        cursor = db_connection.cursor()

        cursor.execute("""
            SELECT image_path
            FROM products
            WHERE product_id = %s;
        """, (product_id,))

        result = cursor.fetchone()
        cursor.close()

        if not result or not result[0]:
            return jsonify(success=False, message="No image found for this product"), 404

        return jsonify(success=True, image_path=result[0]), 200
    except Exception as e:
        return jsonify(success=False, message=f"An error occurred: {str(e)}"), 500
