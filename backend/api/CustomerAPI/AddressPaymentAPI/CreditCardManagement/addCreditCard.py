from flask import Blueprint, request, jsonify
from api.DatabaseConnection.connection import DBConnection

credit_card_api = Blueprint('credit_card_api', __name__)

@credit_card_api.route('/api/add-credit-card', methods=['POST'])
def add_credit_card():
    data = request.json

    customer_id = data.get("customer_id")
    card_number = data.get("card_number")
    expiry_date = data.get("expiry_date")
    cvv = data.get("cvv")
    billing_address_id = data.get("billing_address_id")  # Assume user picks from their addresses

    if not all([customer_id, card_number, expiry_date, cvv, billing_address_id]):
        return jsonify(success=False, message="Missing credit card fields"), 400

    try:
        db_connection = DBConnection.get_instance().get_connection()
        cursor = db_connection.cursor()

        cursor.execute("""
            INSERT INTO credit_cards (card_number, expiry_date, cvv, billing_address_id)
            VALUES (%s, %s, %s, %s)
            RETURNING card_id;
        """, (card_number, expiry_date, cvv, billing_address_id))

        card_id = cursor.fetchone()[0]

        cursor.execute("""
            INSERT INTO customer_credit_cards (customer_id, card_id)
            VALUES (%s, %s);
        """, (customer_id, card_id))

        db_connection.commit()
        cursor.close()

        return jsonify(
            success=True,
            message="Credit card added successfully!",
            card_id=card_id,
        ), 201
    except Exception as e:
        return jsonify(success=False, message=f"An error occurred: {str(e)}"), 500
