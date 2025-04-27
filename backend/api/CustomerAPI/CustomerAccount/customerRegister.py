from flask import Blueprint, request, jsonify
from api.DatabaseConnection.connection import DBConnection
import bcrypt

customer_account_api = Blueprint('customer_register_api', __name__)

@customer_account_api.route('/api/register-customer', methods=['POST'])
def register_customer():
    data = request.json

    name = data.get("name")
    email = data.get("email")
    password = data.get("password")

    if not all([name, email, password]):
        return jsonify(success=False, message="Missing fields"), 400

    try:
        db_connection = DBConnection.get_instance().get_connection()
        cursor = db_connection.cursor()

        # Check if email already exists
        cursor.execute("""
            SELECT customer_id FROM customers WHERE email = %s;
        """, (email,))
        existing = cursor.fetchone()
        if existing:
            return jsonify(success=False, message="Email already registered"), 409

        # Hash the password
        hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

        cursor.execute("""
            INSERT INTO customers (name, email, password_hash)
            VALUES (%s, %s, %s)
            RETURNING customer_id;
        """, (name, email, hashed_password))

        customer_id = cursor.fetchone()[0]

        db_connection.commit()
        cursor.close()

        return jsonify(success=True, message="Customer registered successfully!", customer_id=customer_id), 201
    except Exception as e:
        return jsonify(success=False, message=f"An error occurred: {str(e)}"), 500
