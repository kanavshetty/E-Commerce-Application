import traceback
from flask import Blueprint, request, jsonify
from api.DatabaseConnection.connection import DBConnection

view_credit_card_api = Blueprint('view_credit_card_api', __name__)

@view_credit_card_api.route('/api/view-credit-cards', methods=['GET'])
def view_credit_cards():
    customer_id = request.args.get('customer_id')

    if not customer_id:
        return jsonify(success=False, message="Missing customer_id"), 400

    try:
        db_connection = DBConnection.get_instance().get_connection()
        cursor = db_connection.cursor()

        cursor.execute("""
            SELECT card_id, card_number, expiration_date, payment_address_id
            FROM credit_cards
            WHERE customer_id = %s;

        """, (customer_id,))

        cards = cursor.fetchall()
        cursor.close()

        card_list = []
        for card in cards:
            card_list.append({
                "card_id": card['card_id'],
                "card_number": card['card_number'],
                "last4": card["card_number"][-4:],
                "expiry": card["expiration_date"],
                "billing_address_id": card['payment_address_id']
            })

        return jsonify(success=True, cards=card_list), 200
    except Exception as e:
        traceback.print_exc()
        return jsonify(success=False, message=f"An error occurred: {str(e)}"), 500
