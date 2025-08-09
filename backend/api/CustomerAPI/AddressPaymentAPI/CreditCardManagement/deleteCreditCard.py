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

        cursor.execute("SELECT 1 FROM orders WHERE card_id = %s LIMIT 1;", (card_id,))
        if cursor.fetchone():
            return jsonify(success=False, message="Cannot delete card: it is used in existing orders."), 400


        # Only need to delete from credit_cards
        cursor.execute("""
            DELETE FROM credit_cards
            WHERE card_id = %s;
        """, (card_id,))

        db_connection.commit()
        cursor.close()

        return jsonify(success=True, message="Credit card deleted successfully!"), 200

    except Exception as e:
        db_connection.rollback()
        return jsonify(success=False, message=f"An error occurred: {str(e)}"), 500
