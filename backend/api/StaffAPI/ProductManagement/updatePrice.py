import traceback
from flask import Blueprint, request, jsonify
from api.DatabaseConnection.connection import DBConnection

price_api = Blueprint('update_price_api', __name__)

@price_api.route('/api/update-price', methods=['PUT'])
def update_price():
    print("test")
    data = request.json

    

    product_id = data.get("product_id")
    price = data.get("price")

    if not all([product_id, price]):
        return jsonify(success=False, message="Missing fields"), 400

    try:
        db_connection = DBConnection.get_instance().get_connection()
        cursor = db_connection.cursor()

        cursor.execute("""
            UPDATE product_prices
            SET price = %s
            WHERE product_id = %s;
        """, (price, product_id))

        db_connection.commit()
        cursor.close()

        return jsonify(success=True, message="Price updated successfully!"), 200
    except Exception as e:
        traceback.print_exc()
        return jsonify(success=False, message=f"An error occurred: {str(e)}"), 500
