# In LoginAPI.py or admin-specific API file
from flask import Blueprint, jsonify
from api.DatabaseConnection.connection import DBConnection

admin_api = Blueprint("admin_api", __name__)

@admin_api.route('/api/users', methods=['GET'])
def get_users():
    try:
        db_connection = DBConnection.get_instance().get_connection()
        cursor = db_connection.cursor()
        # Fetch all required fields
        cursor.execute("""
            SELECT * FROM addresses
        """)
        users = cursor.fetchall()
        return jsonify(success=True, users=users), 200
    except Exception as e:
        return jsonify(success=False, message=f"An error occurred: {str(e)}"), 500
