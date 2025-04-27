from flask import Blueprint, request, jsonify
from api.DatabaseConnection.connection import DBConnection

product_api = Blueprint('view_product_api', __name__)

@product_api.route('/api/view-products', methods=['GET'])
def view_products():
    try:
        db_connection = DBConnection.get_instance().get_connection()
        cursor = db_connection.cursor()

        cursor.execute("""
            SELECT product_id, name, description, category, brand, size, price
            FROM products;
        """)

        products = cursor.fetchall()
        cursor.close()

        product_list = []
        for p in products:
            product_list.append({
                "product_id": p[0],
                "name": p[1],
                "description": p[2],
                "category": p[3],
                "brand": p[4],
                "size": p[5],
                "price": p[6],
            })

        return jsonify(success=True, products=product_list), 200
    except Exception as e:
        return jsonify(success=False, message=f"An error occurred: {str(e)}"), 500
