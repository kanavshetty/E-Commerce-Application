from flask import Blueprint, request, jsonify
from api.DatabaseConnection.connection import DBConnection

edit_address_api = Blueprint('edit_address_api', __name__)

@edit_address_api.route('/api/edit-address', methods=['PUT'])
def edit_address():
    data = request.json

    address_id = data.get("address_id")
    street = data.get("street")
    city = data.get("city")
    state = data.get("state")
    zip_code = data.get("zip_code")
    country = data.get("country")

    if not address_id:
        return jsonify(success=False, message="Missing address_id"), 400

    fields = []
    values = []

    if street:
        fields.append("street = %s")
        values.append(street)
    if city:
        fields.append("city = %s")
        values.append(city)
    if state:
        fields.append("state = %s")
        values.append(state)
    if zip_code:
        fields.append("zip_code = %s")
        values.append(zip_code)
    if country:
        fields.append("country = %s")
        values.append(country)

    if not fields:
        return jsonify(success=False, message="No fields to update"), 400

    values.append(address_id)

    try:
        db_connection = DBConnection.get_instance().get_connection()
        cursor = db_connection.cursor()

        query = f"""
            UPDATE addresses
            SET {', '.join(fields)}
            WHERE address_id = %s;
        """
        cursor.execute(query, values)

        db_connection.commit()
        cursor.close()

        return jsonify(success=True, message="Address updated successfully!"), 200
    except Exception as e:
        return jsonify(success=False, message=f"An error occurred: {str(e)}"), 500
