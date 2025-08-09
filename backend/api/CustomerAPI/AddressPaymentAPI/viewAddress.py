import traceback
from flask import Blueprint, request, jsonify
from api.DatabaseConnection.connection import DBConnection

view_address_api = Blueprint('view_address_api', __name__)

@view_address_api.route('/api/view-addresses', methods=['GET'])
def view_addresses():
    customer_id = request.args.get('customer_id')

    if not customer_id:
        return jsonify(success=False, message="Missing customer_id"), 400

    try:
        db_connection = DBConnection.get_instance().get_connection()
        cursor = db_connection.cursor()

        cursor.execute("""
            SELECT a.address_id, a.street, a.city, a.state, a.zip_code, a.country, ca.address_type
            FROM addresses a
            INNER JOIN customer_addresses ca ON a.address_id = ca.address_id
            WHERE ca.customer_id = %s;
        """, (customer_id,))

        addresses = cursor.fetchall()
        cursor.close()

        address_list = []
        for addr in addresses:
            address_list.append({
                "address_id": addr['address_id'],
                "street": addr['street'],
                "city": addr['city'],
                "state": addr['state'],
                "zip_code": addr['zip_code'],
                "country": addr['country'],
                "address_type": addr['address_type'],
            })

        return jsonify(success=True, addresses=address_list), 200
    except Exception as e:
        traceback.print_exc()  # ← Add this
        return jsonify(success=False, message=f"An error occurred: {str(e)}"), 500
