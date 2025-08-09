from flask import Blueprint, request, jsonify, make_response
from flask_jwt_extended import create_access_token, set_access_cookies
from api.DatabaseConnection.connection import DBConnection
from datetime import timedelta
import bcrypt
import traceback  # <-- ADD THIS

customer_account_api = Blueprint('customer_register_api', __name__)

@customer_account_api.route('/api/register-customer', methods=['POST'])
def register_customer():
    data = request.json
    name = data.get('name')
    email = data.get('email')
    password = data.get('password')
    balance = float(data.get('balance', 0))
    is_staff = bool(data.get('is_staff', False))

    if not all([name, email, password]):
        return jsonify(success=False, message="All fields are required"), 400

    try:
        db_connection = DBConnection.get_instance().get_connection()
        cursor = db_connection.cursor()

        print(f"Registering user: name={name}, email={email}, balance={balance}, is_staff={is_staff}")

        # Check if email already exists
        cursor.execute("SELECT * FROM customers WHERE email = %s;", (email,))
        existing = cursor.fetchone()
        if existing:
            return jsonify(success=False, message="Email already registered"), 400

        # Hash password
        password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        print(f"Password hash generated: {password_hash}")

        # Insert new customer
        print("About to execute INSERT INTO customers...")
        cursor.execute("""
            INSERT INTO customers (name, email, password_hash, balance, is_staff)
            VALUES (%s, %s, %s, %s, %s)
            RETURNING customer_id;
        """, (name, email, password_hash, balance, is_staff))

        customer_id = cursor.fetchone()['customer_id']
        db_connection.commit()
        cursor.close()

        access_token = create_access_token(identity=customer_id, expires_delta=timedelta(days=1))
        response = make_response(jsonify(success=True, message="Registration successful", customer_id=customer_id))
        set_access_cookies(response, access_token)

        return response, 201

    except Exception as e:
        print("🔴 Full error during registration:")
        traceback.print_exc()
        return jsonify(success=False, message="An error occurred during registration"), 500
