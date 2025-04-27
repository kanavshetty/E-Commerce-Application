from flask import Blueprint, request, jsonify
from api.DatabaseConnection.connection import DBConnection

supplier_api = Blueprint('add_supplier_api', __name__)

@supplier_api.route('/api/add-supplier', methods=['POST'])
def add_supplier():
    data = request.json

    name = data.get("name")
    address = data.get("address")

    if not all([name, address]):
        return jsonify(success=False, message="Missing supplier fields"), 400

    try:
        db_connection = DBConnection.get_instance().get_connection()
        cursor = db_connection.cursor()

        cursor.execute("""
            INSERT INTO suppliers (name, address)
            VALUES (%s, %s)
            RETURNING supplier_id;
        """, (name, address))

        supplier_id = cursor.fetchone()[0]

        db_connection.commit()
        cursor.close()

        return jsonify(success=True, message="Supplier added successfully!", supplier_id=supplier_id), 201
    except Exception as e:
        return jsonify(success=False, message=f"An error occurred: {str(e)}"), 500
