from flask import Blueprint, request, jsonify
from api.DatabaseConnection.connection import DBConnection

delete_address_api = Blueprint('delete_address_api', __name__)

@delete_address_api.route('/api/delete-address', methods=['DELETE'])
def delete_address():
    data = request.json

    address_id = data.get("address_id")

    if not address_id:
        return jsonify(success=False, message="Missing address_id"), 400

    try:
        db_connection = DBConnection.get_instance().get_connection()
        cursor = db_connection.cursor()

        # First remove from customer_addresses
        cursor.execute("""
            DELETE FROM customer_addresses
            WHERE address_id = %s;
        """, (address_id,))

        # Then remove the address itself
        cursor.execute("""
            DELETE FROM addresses
            WHERE address_id = %s;
        """, (address_id,))

        db_connection.commit()
        cursor.close()

        return jsonify(success=True, message="Address deleted successfully!"), 200
    except Exception as e:
        return jsonify(success=False, message=f"An error occurred: {str(e)}"), 500
