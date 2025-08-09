from flask import Blueprint, request, jsonify, make_response
from api.DatabaseConnection.connection import DBConnection
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity, set_access_cookies, unset_jwt_cookies
from datetime import timedelta
import bcrypt

auth_api = Blueprint('auth_api', __name__)

@auth_api.route('/api/login', methods=['POST'])
def login_customer():
    data = request.json
    email = data.get('email')
    password = data.get('password')

    if not all([email, password]):
        return jsonify(success=False, message="Both Email and Password are required"), 400

    try:
        db_connection = DBConnection.get_instance().get_connection()
        cursor = db_connection.cursor()


        cursor.execute("SELECT customer_id, password_hash, is_staff FROM customers WHERE email = %s;", (email,))
        user = cursor.fetchone()
        cursor.close()

        if not user:
            return jsonify(success=False, message="Invalid email or password"), 401

        customer_id = user['customer_id']
        password_hash = user['password_hash']
        is_staff = user['is_staff']

        if not bcrypt.checkpw(password.encode('utf-8'), password_hash.encode('utf-8')):
            return jsonify(success=False, message="Invalid email or password"), 401

        # Generate JWT token and set cookie
        access_token = create_access_token(identity=customer_id, expires_delta=timedelta(days=1))
        response = make_response(jsonify(success=True, message="Login successful", customer_id=customer_id, is_staff=is_staff))
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

    try:
        db_connection = DBConnection.get_instance().get_connection()
        cursor = db_connection.cursor(dictionary=True)

        cursor.execute("SELECT name, email FROM customers WHERE customer_id = %s;", (customer_id,))
        user = cursor.fetchone()
        cursor.close()

        if not user:
            return jsonify(success=False, message="User not found"), 404

        return jsonify(success=True, user=user), 200

    except Exception as e:
        return jsonify(success=False, message=f"An error occurred: {str(e)}"), 500

