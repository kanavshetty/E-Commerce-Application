from flask import Blueprint, request, jsonify
from api.DatabaseConnection.connection import DBConnection

delete_credit_card_api = Blueprint('delete_credit_card_api', __name__)

@delete_credit_card_api.route('/api/delete-credit-card', methods=['DELETE'])
def delete_credit_card():
    data = request.json

    card_id = data.get("card_id")

    if not card_id:
        return jsonify(success=False, message="Missing card_id"), 400

    try:
        db_connection = DBConnection.get_instance().get_connection()
        cursor = db_connection.cursor()

        # First remove the association from customer_credit_cards
        cursor.execute("""
            DELETE FROM customer_credit_cards
            WHERE card_id = %s;
        """, (card_id,))

        # Then remove the credit card itself
        cursor.execute("""
            DELETE FROM credit_cards
            WHERE card_id = %s;
        """, (card_id,))

        db_connection.commit()
        cursor.close()

        return jsonify(success=True, message="Credit card deleted successfully!"), 200
    except Exception as e:
        return jsonify(success=False, message=f"An error occurred: {str(e)}"), 500
