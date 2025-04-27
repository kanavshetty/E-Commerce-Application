from flask import Blueprint, request, jsonify
from api.DatabaseConnection.connection import DBConnection

customer_change_api = Blueprint('customer_change_api', __name__)

@customer_change_api.route('/api/change-customer-details', methods=['PUT'])
def change_customer_details():
    data = request.json

    customer_id = data.get("customer_id")
    new_name = data.get("new_name")
    new_email = data.get("new_email")

    if not customer_id:
        return jsonify(success=False, message="Missing customer_id"), 400

    fields = []
    values = []

    if new_name:
        fields.append("name = %s")
        values.append(new_name)
    if new_email:
        fields.append("email = %s")
        values.append(new_email)

    if not fields:
        return jsonify(success=False, message="No fields to update"), 400

    values.append(customer_id)

    try:
        db_connection = DBConnection.get_instance().get_connection()
        cursor = db_connection.cursor()

        query = f"""
            UPDATE customers
            SET {', '.join(fields)}
            WHERE customer_id = %s;
        """
        cursor.execute(query, values)

        db_connection.commit()
        cursor.close()

        return jsonify(success=True, message="Customer details updated successfully!"), 200
    except Exception as e:
        return jsonify(success=False, message=f"An error occurred: {str(e)}"), 500
