from flask import Blueprint, request, jsonify, make_response
from api.DatabaseConnection.connection import DBConnection
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity, set_access_cookies, unset_jwt_cookies
from datetime import timedelta
import bcrypt

auth_api = Blueprint('auth_api', __name__)

@auth_api.route('/api/login', methods=['POST'])
def login():
    data = request.json
    email = data.get('email')
    password = data.get('password')

    if not email or not password:
        return jsonify(success=False, message="Missing fields"), 400

    try:
        db_connection = DBConnection.get_instance().get_connection()
        cursor = db_connection.cursor()

        cursor.execute("SELECT customer_id, email, password_hash FROM customers WHERE email = %s;", (email,))
        user = cursor.fetchone()
        cursor.close()

        if not user:
            return jsonify(success=False, message="Invalid email or password"), 401

        customer_id, email, password_hash = user[0], user[1], user[2]

        if not bcrypt.checkpw(password.encode('utf-8'), password_hash.encode('utf-8')):
            return jsonify(success=False, message="Invalid email or password"), 401

        # Create JWT Token
        access_token = create_access_token(identity=customer_id, expires_delta=timedelta(days=1))

        # Set token inside a cookie
        response = make_response(jsonify(success=True, message="Login successful"))
        set_access_cookies(response, access_token)

        return response, 200

    except Exception as e:
        return jsonify(success=False, message=f"An error occurred: {str(e)}"), 500

@auth_api.route('/api/logout', methods=['POST'])
@jwt_required()
def logout():
    response = make_response(jsonify(success=True, message="Logout successful"))
    unset_jwt_cookies(response)
    return response, 200

@auth_api.route('/api/check-auth', methods=['GET'])
@jwt_required()
def check_auth():
    customer_id = get_jwt_identity()
    return jsonify(success=True, customer_id=customer_id), 200
