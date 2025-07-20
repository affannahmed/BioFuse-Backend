import os

from flask import request, jsonify, url_for
from werkzeug.security import check_password_hash
from Backend.Models.Role import Role
from . import db
from Backend.Models.User import User
from .. import UserDepartment
import hashlib
from base64 import b64decode


class UserController :
    # for visitor
    @staticmethod
    def get_user_by_id(user_id):
        user = User.query.get(user_id)
        if user:
            profile_image = None
            if user.profile_img:
                # Get first image from comma-separated list
                first_img = user.profile_img.split(',')[0]
                # Extract the path after 'uploads\' and make it web-compatible
                relative_path = first_img.split("uploads\\")[-1].replace("\\", "/")
                # Create full URL
                profile_image = f"{request.host_url}uploads/{relative_path}"

            return {
                "name": user.name,
                "cnic": user.cnic,
                "contact": user.contact,
                "profile_img": profile_image
            }
        else:
            return None



    @staticmethod
    def login():
        data = request.get_json()
        email = data.get('email')
        password = data.get('password')

        if not email or not password:
            return jsonify({"error": "Email and password are required."}), 400

        user = User.query.filter_by(email=email).first()
        if not user:
            return jsonify({"error": "Invalid email or password."}), 401

        try:
            stored_password = user.password
            scrypt_params = stored_password.split('$')
            if len(scrypt_params) != 3:
                return jsonify({"error": "Stored password format is incorrect."}), 500

            n, r, p = map(int, scrypt_params[0].split(':')[1:])  # Retrieve N, R, P values
            salt = b64decode(scrypt_params[1])  # Decode salt from base64
            stored_hash = bytes.fromhex(scrypt_params[2])  # Convert hex hash to bytes

            # Generate the hash using the provided password
            derived_key = hashlib.scrypt(
                password.encode(),
                salt=salt,
                n=n,
                r=r,
                p=p
            )

            # Compare the derived key with the stored hash
            if derived_key != stored_hash:
                return jsonify({"error": "Invalid email or password."}), 401

        except Exception as e:
            return jsonify({"error": f"Password verification failed: {str(e)}"}), 500

        # Determine role and fetch additional details
        user_department = UserDepartment.query.filter_by(user_id=user.id).first()

        if user_department:
            role = Role.query.get(user_department.role_id)  # Fetch Role object
            if role:
                role_name = role.name
                department_name = user_department.department.name  # Assuming there's a department relation
            else:
                return jsonify({"error": "Role not found."}), 403
        else:
            return jsonify({"error": "User department not found."}), 404

        # ✅ Fix profile image URL
        if user.profile_img:
            filename = os.path.basename(user.profile_img)  # Extract just the filename
            profile_img_url = f"{request.host_url}uploads/profile_images/{filename}"
        else:
            profile_img_url = None

        # Prepare the response based on the user's role
        if role_name == 'Admin':
            message = f"Welcome {user.name}"
        elif role_name == 'Supervisor':
            message = f"Hello {user.name}, you are assigned to {department_name}."
        elif role_name == 'Employee':
            message = f"Hello {user.name}, you belong to {department_name}."
        elif role_name=='Director':
            message =f"Welcome {user.name}"
        else:
            return jsonify({"error": "Role not found."}), 403

        # Return response including profile image URL
        return jsonify({
            "message": message,
            "role": role_name,
            "profile_img": profile_img_url  # Now correctly formatted
        }), 200


