from flask import Blueprint, request, jsonify
from api.DatabaseConnection.connection import DBConnection

edit_credit_card_api = Blueprint('edit_credit_card_api', __name__)

@edit_credit_card_api.route('/api/edit-credit-card', methods=['PUT'])
def edit_credit_card():
    data = request.json

    card_id = data.get("card_id")
    card_number = data.get("card_number")
    expiry_date = data.get("expiry_date")
    cvv = data.get("cvv")
    billing_address_id = data.get("billing_address_id")

    if not card_id:
        return jsonify(success=False, message="Missing card_id"), 400

    fields = []
    values = []

    if card_number:
        fields.append("card_number = %s")
        values.append(card_number)
    if expiry_date:
        fields.append("expiry_date = %s")
        values.append(expiry_date)
    if cvv:
        fields.append("cvv = %s")
        values.append(cvv)
    if billing_address_id:
        fields.append("billing_address_id = %s")
        values.append(billing_address_id)

    if not fields:
        return jsonify(success=False, message="No fields to update"), 400

    values.append(card_id)

    try:
        db_connection = DBConnection.get_instance().get_connection()
        cursor = db_connection.cursor()

        query = f"""
            UPDATE credit_cards
            SET {', '.join(fields)}
            WHERE card_id = %s;
        """
        cursor.execute(query, values)

        db_connection.commit()
        cursor.close()

        return jsonify(success=True, message="Credit card updated successfully!"), 200
    except Exception as e:
        return jsonify(success=False, message=f"An error occurred: {str(e)}"), 500
