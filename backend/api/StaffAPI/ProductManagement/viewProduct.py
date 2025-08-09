from flask import Blueprint, request, jsonify
from api.DatabaseConnection.connection import DBConnection

product_api = Blueprint('view_product_api', __name__)

@product_api.route('/api/view-products', methods=['GET'])
def view_products():
    try:
        db_connection = DBConnection.get_instance().get_connection()
        cursor = db_connection.cursor()

        cursor.execute("""
            SELECT 
                p.*, 
                pp.price
            FROM 
                products p
            LEFT JOIN 
                product_prices pp
            ON 
                p.product_id = pp.product_id;
        """)

        products = cursor.fetchall()
        cursor.close()

        return jsonify(success=True, products=products), 200
    except Exception as e:
        return jsonify(success=False, message=f"An error occurred: {str(e)}"), 500
