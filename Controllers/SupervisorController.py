import os
from datetime import datetime

from flask import jsonify, request, current_app
from sqlalchemy import func

from Backend.Models.AccessControl import AccessControl
from . import db
from Backend.Models.User import User
from Backend.Models.UserDepartment import UserDepartment
from Backend.Models.Role import Role
from Backend.Models.UserBiometric import UserBiometric
from Backend.Local_Upload import upload_profile_pictures, upload_biometric, upload_profile_pictures_for_other
from Backend.Models.EmployeeDesignation import EmployeeDesignation
from Backend.Models.DepartmentSection import DepartmentSection
from ..Models import Camera, CameraMonitoringLogs
from Backend.Models.EmployeeViolations import EmployeeViolations

class SupervisorController:

    @staticmethod
    def checkCompleteOrNot(email):
        user = User.query.filter_by(email=email).first()

        if not user:
            return {"error": "User not found"}, 404


        required_fields = [
            user.name,
            user.cnic,
            user.contact,
            user.email,
            user.profile_img
        ]


        for field in required_fields:
            if not field or field.strip() == "":
                return {"isComplete": False}

        return {"isComplete": True}

    @staticmethod
    def save_supervisor_profile(email, profile_img_file, name, phone_number, cnic):
        try:
            # Find user by email
            user = User.query.filter_by(email=email).first()
            if not user:
                current_app.logger.warning(f"No user found with email {email}.")
                return {"error": "User not found"}, 404

            # Upload profile picture
            upload_profile_pictures_for_other(user.id, profile_img_file)
        except Exception as e:
            current_app.logger.error(f"Error uploading profile picture for email {email}: {str(e)}")
            return {"error": "Failed to upload profile picture"}, 500

        try:
            # Update user basic information
            user.name = name
            user.contact = phone_number
            user.cnic = cnic
            db.session.commit()
            current_app.logger.info("User information updated successfully!")
            return {"message": "Supervisor profile saved successfully"}, 200
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Error updating user information for email {email}: {str(e)}")
            return {"error": "Failed to update user information"}, 500

    # Employees Overview Screen
    @staticmethod
    def get_employees_overview():
        email = request.args.get('email')

        if not email:
            return jsonify({"error": "Email is required."}), 400

        try:
            user = User.query.filter_by(email=email).first()
            if not user:
                return jsonify({"error": "User not found."}), 404

            user_department = UserDepartment.query.filter_by(user_id=user.id).first()
            if not user_department:
                return jsonify({"error": "Supervisor does not belong to any department."}), 404

            department_id = user_department.department_id
            role_id = user_department.role_id

            supervisor_role = Role.query.filter_by(id=role_id).first()
            if not supervisor_role or supervisor_role.name != 'Supervisor':
                return jsonify({"error": "User is not a Supervisor."}), 403

            employees = (
                UserDepartment.query
                .join(User)
                .join(Role)
                .filter(UserDepartment.department_id == department_id)
                .filter(Role.name == 'Employee')
                .all()
            )

            base_url = request.host_url.rstrip('/')
            employee_overview = []

            for emp in employees:
                profile_path = emp.user.profile_img
                if profile_path:
                    filename = os.path.basename(profile_path)
                    profile_url = f"{request.host_url}uploads/profile_images/{filename}"
                else:
                    profile_url = None

                employee_data = {
                    "id": emp.user.id,
                    "name": emp.user.name,
                    "profile_img": profile_url
                }
                employee_overview.append(employee_data)

            return jsonify(employee_overview), 200

        except Exception as e:
            return jsonify({"error": f"Error retrieving employees: {str(e)}"}), 500

    # Per Employee details
    @staticmethod
    def employee_details_route():
        employee_id = request.args.get('id')

        if not employee_id:
            return jsonify({"error": "Employee ID is required."}), 400

        try:
            # Fetch the user
            user = User.query.filter_by(id=employee_id).first()
            if not user:
                return jsonify({"error": "Employee not found."}), 404

            # Fetch the user's department
            user_department = UserDepartment.query.filter_by(user_id=user.id).first()
            if not user_department:
                return jsonify({"error": "User does not belong to any department."}), 404

            # Fetch the employee's designation
            designation = EmployeeDesignation.query.filter_by(user_id=user_department.id).first()
            designation_name = designation.designation.name if designation else "N/A"

            # ✅ Construct correct profile image URL
            if user.profile_img:
                filename = os.path.basename(user.profile_img)
                profile_url = f"{request.host_url}uploads/profile_images/{filename}"
            else:
                profile_url = None

            # Prepare the response
            employee_details = {
                "name": user.name,
                "profile_img": profile_url,
                "email": user.email,
                "contact": user.contact,
                "cnic": user.cnic,
                "designation": designation_name,
            }

            return jsonify(employee_details), 200

        except Exception as e:
            return jsonify({"error": f"Error retrieving employee details: {str(e)}"}), 500

        # --------- ACCESS CONTROL SYSTEM -----------

    # --------  to show relevant subsections :( -----------
    @staticmethod
    def relevantSubsections(user_id):
        # Step 1: Find the UserDepartment record for this user
        user_dept = UserDepartment.query.filter_by(user_id=user_id, is_valid=True).first()

        if not user_dept:
            return {"error": "No valid department found for this user"}, 404

        department_id = user_dept.department_id

        # Step 2: Find all DepartmentSection entries linked to this department
        sections = DepartmentSection.query.filter_by(department_id=department_id).all()

        if not sections:
            return [], 200  # Return empty list if no sections

        # Step 3: Prepare and return simple list of maps
        section_data = [{"id": section.id, "name": section.name} for section in sections]
        return section_data, 200

    # -------- function to Access Control table. -----------
    @staticmethod
    def grant_access_to_employee(employee_id, subsection_ids):
        if not employee_id or not subsection_ids:
            return jsonify({"error": "Employee ID and subsection IDs are required."}), 400

        try:
            access_entries = []
            for subsection_id in subsection_ids:
                access_entry = AccessControl(
                    employee_id=employee_id,
                    subsection_id=subsection_id
                )
                db.session.add(access_entry)
                access_entries.append(access_entry)

            db.session.commit()
            return jsonify({
                "message": "Access granted successfully"
            }), 201

        except Exception as e:
            db.session.rollback()
            return jsonify({"error": f"Failed to grant access: {str(e)}"}), 500


    # -------------  Track Employee ------

    # ---- show subsections -------
    @staticmethod
    def relevant_subsections_by_email(email):
        # Step 1: Find the user by email
        user = User.query.filter_by(email=email).first()

        if not user:
            return {"error": "User not found"}, 404

        # Step 2: Get UserDepartment
        user_dept = UserDepartment.query.filter_by(user_id=user.id, is_valid=True).first()

        if not user_dept:
            return {"error": "No valid department found for this user"}, 404

        department_id = user_dept.department_id

        # Step 3: Get DepartmentSections
        sections = DepartmentSection.query.filter_by(department_id=department_id).all()

        if not sections:
            return [], 200

        # Step 4: Prepare response
        section_data = [{"id": section.id, "name": section.name} for section in sections]

        return section_data, 200

    # -------   accesssible places for the employee -----
    @staticmethod
    def get_employee_access():
        employee_user_id = request.args.get('employee_id')

        if not employee_user_id:
            return jsonify({"error": "Employee ID is required."}), 400

        try:
            # Step 1: Get userdepartment.id using user_id
            user_department = UserDepartment.query.filter_by(user_id=employee_user_id).first()
            if not user_department:
                return jsonify({"error": "No department record found for this employee."}), 404

            # Step 2: Get all allowed subsection_ids from AccessControl table
            access_entries = AccessControl.query.filter_by(employee_id=user_department.id).all()
            allowed_subsection_ids = [entry.subsection_id for entry in access_entries]

            if not allowed_subsection_ids:
                return jsonify({"message": "No access granted to this employee yet.", "sections": []}), 200

            # Step 3: Fetch subsection names and camera IDs (cid) from departmentsection
            sections = DepartmentSection.query.filter(DepartmentSection.id.in_(allowed_subsection_ids)).all()

            section_list = []
            for section in sections:
                camera = Camera.query.get(section.camera_id)  # Get camera info by camera_id
                section_list.append({
                    "section_id": section.id,
                    "section_name": section.name,
                    "camera_id": section.camera_id,
                    "camera_model": camera.camera_model if camera else None  # Safely handle missing camera
                })

            return jsonify({
                "employee_id": employee_user_id,
                "allowed_sections": section_list
            }), 200

        except Exception as e:
            return jsonify({"error": f"Error retrieving access: {str(e)}"}), 500

    @staticmethod
    def access_logs_for_employees():
        data = request.json
        email = data.get("email")
        start_date = data.get("start_date")  # Expected format: "YYYY-MM-DD"
        end_date = data.get("end_date")  # Expected format: "YYYY-MM-DD"

        try:
            # 1. Find user by email
            user = User.query.filter_by(email=email).first()
            if not user:
                return jsonify({"error": "User with provided email not found"}), 404

            # 2. Find UserDepartment entry where this user is Supervisor (role_id = 2)
            supervisor_ud = UserDepartment.query.filter_by(user_id=user.id, role_id=2).first()
            if not supervisor_ud:
                return jsonify({"error": "Supervisor role not found for this user"}), 404

            department_id = supervisor_ud.department_id

            # 3. Find all employees (role_id = 3) in the same department
            employee_ud_list = UserDepartment.query.filter_by(department_id=department_id, role_id=3).all()
            employee_ud_ids = [emp_ud.id for emp_ud in employee_ud_list]

            if not employee_ud_ids:
                return jsonify({"message": "No employees found under this supervisor"}), 200

            # 4. Convert date-only input to full datetime range
            from datetime import datetime

            start_dt = datetime.strptime(start_date + " 00:00:00", "%Y-%m-%d %H:%M:%S")
            end_dt = datetime.strptime(end_date + " 23:59:59", "%Y-%m-%d %H:%M:%S")

            # 5. Filter logs for these employee user_department_ids between dates
            logs = CameraMonitoringLogs.query.filter(
                CameraMonitoringLogs.user_id.in_(employee_ud_ids),
                CameraMonitoringLogs.date_time >= start_dt,
                CameraMonitoringLogs.date_time <= end_dt
            ).all()

            # 6. Get unique employee ids from logs
            logged_user_dept_ids = list(set(log.user_id for log in logs))

            # 7. Map back to User
            employee_info = []
            for ud_id in logged_user_dept_ids:
                user_dept = UserDepartment.query.get(ud_id)
                if user_dept and user_dept.user:
                    employee_info.append({
                        "id": user_dept.user.id,
                        "name": user_dept.user.name
                    })

            return jsonify( employee_info
            ), 200

        except Exception as e:
            return jsonify({"error": str(e)}), 500

    # ---- Store violations of Employee ------
    @staticmethod
    def store_employee_violations():
        try:
            data = request.get_json()
            user_id = data.get("user_id")
            camera_id = data.get("camera_id")

            # Validation
            if not user_id or not camera_id:
                return jsonify({"error": "Missing user_id or camera_id"}), 400

            # Create a new violation record
            new_violation = EmployeeViolations(user_id=user_id, camera_id=camera_id)
            db.session.add(new_violation)
            db.session.commit()

            return jsonify({
                "message": "Employee violation logged successfully.",
            }), 201

        except Exception as e:
            db.session.rollback()
            return jsonify({"error": str(e)}), 500
