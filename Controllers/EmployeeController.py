import os
from datetime import datetime
from flask import jsonify, request, current_app
from sqlalchemy import func
from sqlalchemy.orm import joinedload
from werkzeug.security import generate_password_hash
from . import db
from Backend.Models.User import User
from Backend.Models.UserDepartment import UserDepartment
from Backend.Models.Designation import Designation
from Backend.Local_Upload import upload_profile_pictures
from Backend.Models.EmployeeDesignation import EmployeeDesignation
from ..Models import CameraMonitoringLogs, Location, Camera
from Backend.Local_Upload import upload_profile_pictures_for_other


class EmployeeController:
    @staticmethod
    def save_employee_profile(email, cnic, contact, designation_id, profile_img_file):
        try:
            user = User.query.filter_by(email=email).first()
            if not user:
                current_app.logger.warning(f"No user found with email: {email}")
                return {"error": "User not found"}, 404

            current_app.logger.info(f"User found: {user.id}")

            user_id = user.id

            profile_img_path = upload_profile_pictures_for_other(user_id, profile_img_file)
            user.profile_img = profile_img_path
            current_app.logger.info(f"Image uploaded at: {profile_img_path}")

            user.cnic = cnic
            user.contact = contact

            user_department = UserDepartment.query.filter_by(user_id=user_id).first()
            if not user_department:
                current_app.logger.warning(f"No UserDepartment found for user_id: {user_id}")
                return {"error": f"No user department entry found for user_id {user_id}"}, 404

            current_app.logger.info(f"UserDepartment found: {user_department.id}")

            designation = Designation.query.get(designation_id)
            if not designation:
                return {"error": f"Designation with ID {designation_id} not found"}, 404

            current_app.logger.info(f"Designation found: {designation.name}")

            emp_designation = EmployeeDesignation.query.filter_by(user_id=user_department.id).first()

            if emp_designation:
                emp_designation.designation_id = designation_id
                current_app.logger.info("Updated existing EmployeeDesignation")
            else:
                emp_designation = EmployeeDesignation(
                    user_id=user_department.id,
                    designation_id=designation_id
                )
                db.session.add(emp_designation)
                current_app.logger.info("Added new EmployeeDesignation")

            db.session.commit()

            current_app.logger.info(f"Employee profile saved successfully for user_id: {user_id}")
            return {"message": "Employee profile saved successfully"}, 200

        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Error in save_employee_profile for email {email}: {str(e)}")
            return {"error": "Failed to save employee profile"}, 500

    # --- get the designations ---
    @staticmethod
    def all_designation_forEmp():
        try:
            designations = Designation.query.all()
            result = [{"id": d.id, "name": d.name} for d in designations]

            current_app.logger.info("Fetched all designations successfully.")
            return result, 200

        except Exception as e:
            current_app.logger.error(f"Error fetching designations: {str(e)}")
            return {"error": "Failed to fetch designations"}, 500

        # ----------    ACCESS LOGS HISTORY OF EMPLOYEE

    @staticmethod
    def fetch_my_emp_logs():
        try:
            # Get query parameters from request
            email = request.args.get('email')
            start_date = request.args.get('start_date')
            end_date = request.args.get('end_date')

            # Validate inputs
            if not all([email, start_date, end_date]):
                return jsonify({"error": "Email, start_date and end_date are required."}), 400

            def validate_date(date_str):
                try:
                    date_str = date_str.strip()  # Strip leading/trailing whitespace
                    date_obj = datetime.strptime(date_str, "%Y-%m-%d")
                    return date_obj
                except ValueError:
                    return None

            start_date_obj = validate_date(start_date)
            end_date_obj = validate_date(end_date)

            if not start_date_obj or not end_date_obj:
                return jsonify({"error": "Invalid date format. Please use YYYY-MM-DD."}), 400

            # Find the user by email
            user = User.query.filter_by(email=email).first()
            if not user:
                return jsonify({"error": "User not found."}), 404

            # Find user_department entry for this user
            user_dept = UserDepartment.query.filter_by(user_id=user.id).first()
            if not user_dept:
                return jsonify({"error": "User department not found."}), 404

            # Fetch logs for this user_id from CameraMonitoringLogs within the date range
            logs = CameraMonitoringLogs.query.options(
                joinedload(CameraMonitoringLogs.camera).joinedload(Camera.location)
            ).filter(
                CameraMonitoringLogs.user_id == user_dept.id,
                CameraMonitoringLogs.date_time.between(start_date_obj, end_date_obj)
            ).all()

            log_list = []
            for log in logs:
                camera = log.camera
                location_name = camera.location.name if camera.location else None
                camera_model = camera.camera_model

                # Build full image URL
                access_img_url = f"{request.host_url}static/{log.access_img}"

                log_list.append({
                    "camera_model": camera_model,
                    "location_name": location_name,
                    "date_time": log.date_time.strftime("%Y-%m-%d %H:%M:%S"),
                    "access_img_url": access_img_url
                })

            return jsonify(log_list), 200

        except Exception as e:
            return jsonify({"error": str(e)}), 500

    @staticmethod
    def fetch_my_logs(employee_id):
        data = request.json
        start_date = data.get('start_date')  # Expected format: YYYY-MM-DD
        end_date = data.get('end_date')

        def validate_date(date_str):
            try:
                date_obj = datetime.strptime(date_str, "%Y-%m-%d")
                return date_obj.strftime("%Y-%m-%d")
            except ValueError:
                return None

        start_date = validate_date(start_date)
        end_date = validate_date(end_date)

        if not start_date or not end_date:
            return jsonify({"error": "Invalid date format. Please use YYYY-MM-DD."}), 400

        logs = (
            db.session.query(CameraMonitoringLogs)
            .filter(CameraMonitoringLogs.user_id == employee_id)
            .filter(func.date(CameraMonitoringLogs.date_time) >= start_date)
            .filter(func.date(CameraMonitoringLogs.date_time) <= end_date)
            .all()
        )

        if not logs:
            return jsonify({"message": "No access logs found for the selected date range."}), 404

        access_logs = [{"date_time": log.date_time.strftime('%Y-%m-%d %H:%M:%S'), "camera_id": log.camera_id} for log in
                       logs]
        return jsonify(access_logs), 200


    @staticmethod
    def fetch_my_details(employee_id):
        employee = (
            db.session.query(User)
            .filter(User.id == employee_id)
            .one_or_none()
        )

        if not employee:
            return jsonify({"message": "Employee not found."}), 404

        result = {
            "id": employee.id,
            "name": employee.name,
            "profile_img": employee.profile_img,
        }

        return jsonify(result), 200


