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
            SELECT cc.card_id, cc.card_number, cc.expiry_date, cc.billing_address_id
            FROM credit_cards cc
            INNER JOIN customer_credit_cards ccc ON cc.card_id = ccc.card_id
            WHERE ccc.customer_id = %s;
        """, (customer_id,))

        cards = cursor.fetchall()
        cursor.close()

        card_list = []
        for card in cards:
            card_list.append({
                "card_id": card[0],
                "card_number": card[1],
                "expiry_date": card[2],
                "billing_address_id": card[3]
            })

        return jsonify(success=True, cards=card_list), 200
    except Exception as e:
        return jsonify(success=False, message=f"An error occurred: {str(e)}"), 500
