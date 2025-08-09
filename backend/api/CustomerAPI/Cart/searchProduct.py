from flask import Blueprint, request, jsonify
from api.DatabaseConnection.connection import DBConnection
import psycopg2.extras  # or import the one your DB API uses

product_search_api = Blueprint('search_product_api', __name__)

@product_search_api.route('/api/search-products', methods=['GET'])
def search_products():
    keyword = request.args.get('keyword')

    if not keyword:
        return jsonify(success=False, message="Missing search keyword"), 400

    try:
        db_connection = DBConnection.get_instance().get_connection()
        cursor = db_connection.cursor(cursor_factory=psycopg2.extras.RealDictCursor)  # ✅ dict output

        search_query = """
            SELECT 
                p.product_id,
                p.name,
                p.description,
                p.category,
                p.brand,
                p.size,
                pp.price
            FROM 
                products p
            LEFT JOIN 
                product_prices pp ON p.product_id = pp.product_id
            WHERE 
                LOWER(p.name) LIKE %s OR
                LOWER(p.description) LIKE %s OR
                LOWER(p.category) LIKE %s OR
                LOWER(p.brand) LIKE %s
            ORDER BY 
                p.name ASC;
        """

        keyword_like = f"%{keyword.strip().lower()}%"
        cursor.execute(search_query, (keyword_like,) * 4)

        products = cursor.fetchall()
        cursor.close()

        return jsonify(success=True, products=products), 200  # Already a list of dicts
    except Exception as e:
        return jsonify(success=False, message=f"An error occurred: {str(e)}"), 500
