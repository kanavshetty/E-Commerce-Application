from flask import Blueprint, request, jsonify
from api.DatabaseConnection.connection import DBConnection

product_api = Blueprint('modify_product_api', __name__)

@product_api.route('/api/modify-product', methods=['PUT'])
def modify_product():
    data = request.json

    product_id = data.get("product_id")
    name = data.get("name")
    description = data.get("description")
    category = data.get("category")
    brand = data.get("brand")
    size = data.get("size")

    if not product_id:
        return jsonify(success=False, message="Missing product_id"), 400

    fields = []
    values = []

    if name:
        fields.append("name = %s")
        values.append(name)
    if description:
        fields.append("description = %s")
        values.append(description)
    if category:
        fields.append("category = %s")
        values.append(category)
    if brand:
        fields.append("brand = %s")
        values.append(brand)
    if size:
        fields.append("size = %s")
        values.append(size)

    if not fields:
        return jsonify(success=False, message="No fields to update"), 400

    values.append(product_id)

    try:
        db_connection = DBConnection.get_instance().get_connection()
        cursor = db_connection.cursor()

        query = f"""
            UPDATE products
            SET {', '.join(fields)}
            WHERE product_id = %s;
        """
        cursor.execute(query, values)

        db_connection.commit()
        cursor.close()

        return jsonify(success=True, message="Product modified successfully!"), 200
    except Exception as e:
        return jsonify(success=False, message=f"An error occurred: {str(e)}"), 500
