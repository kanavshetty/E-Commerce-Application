from flask import Blueprint, request, jsonify
from api.DatabaseConnection.connection import DBConnection

product_search_api = Blueprint('search_product_api', __name__)

@product_search_api.route('/api/search-products', methods=['GET'])
def search_products():
    keyword = request.args.get('keyword')

    if not keyword:
        return jsonify(success=False, message="Missing search keyword"), 400

    try:
        db_connection = DBConnection.get_instance().get_connection()
        cursor = db_connection.cursor()

        search_query = f"""
            SELECT product_id, name, description, category, brand, size, price
            FROM products
            WHERE LOWER(name) LIKE %s
               OR LOWER(description) LIKE %s
               OR LOWER(category) LIKE %s
               OR LOWER(brand) LIKE %s
            ORDER BY name ASC;
        """

        keyword_like = f"%{keyword.lower()}%"

        cursor.execute(search_query, (keyword_like, keyword_like, keyword_like, keyword_like))

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
