import os
from flask import Blueprint, request, jsonify
from werkzeug.utils import secure_filename
from api.DatabaseConnection.connection import DBConnection

product_image_api = Blueprint('upload_product_image_api', __name__)

UPLOAD_FOLDER = 'static/uploads/products/'  # Example upload path (make sure it exists)

@product_image_api.route('/api/upload-product-image', methods=['POST'])
def upload_product_image():
    if 'image' not in request.files:
        return jsonify(success=False, message="No image file provided"), 400

    file = request.files['image']
    product_id = request.form.get('product_id')

    if not product_id:
        return jsonify(success=False, message="Missing product_id"), 400

    if file.filename == '':
        return jsonify(success=False, message="Empty filename"), 400

    try:
        filename = secure_filename(file.filename)
        save_path = os.path.join(UPLOAD_FOLDER, filename)
        file.save(save_path)

        # Save image path in database
        db_connection = DBConnection.get_instance().get_connection()
        cursor = db_connection.cursor()

        cursor.execute("""
            UPDATE products
            SET image_path = %s
            WHERE product_id = %s;
        """, (save_path, product_id))

        db_connection.commit()
        cursor.close()

        return jsonify(success=True, message="Image uploaded successfully!", image_path=save_path), 201
    except Exception as e:
        return jsonify(success=False, message=f"An error occurred: {str(e)}"), 500
