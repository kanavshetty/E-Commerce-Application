from flask import Blueprint, request, jsonify
from api.DatabaseConnection.connection import DBConnection

address_api = Blueprint('address_api', __name__)

@address_api.route('/api/add-address', methods=['POST'])
def addAddress():
    data = request.json

    customer_id = data.get("customer_id")
    street = data.get("street")
    city = data.get("city")
    state = data.get("state")
    zip_code = data.get("zip_code")
    country = data.get("country")
    address_type = data.get("address_type")

    address_type= address_type.strip().lower(),


    if not all([customer_id, street, city, state, zip_code, country, address_type]):
        return jsonify(success=False, message="Missing address fields"), 400

    try:
        db_connection = DBConnection.get_instance().get_connection()
        cursor = db_connection.cursor()

        cursor.execute("""
            INSERT INTO addresses (street, city, state, zip_code, country)
            VALUES (%s, %s, %s, %s, %s)
            RETURNING address_id;
        """, (street, city, state, zip_code, country))

        address_id = cursor.fetchone()['address_id']

        cursor.execute("""
            INSERT INTO customer_addresses (customer_id, address_id, address_type)
            VALUES (%s, %s, %s);
        """, (customer_id, address_id, address_type))

        db_connection.commit()
        cursor.close()

        return jsonify(
            success=True,
            message="Address added successfully!",
            address_id=address_id,
        ), 201
   
    except Exception as e:
        db_connection.rollback()  # ← REQUIRED
        return jsonify(success=False, message=f"An error occurred: {str(e)}"), 500

