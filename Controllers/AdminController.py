import hashlib
import os
from base64 import b64encode
from datetime import datetime
import werkzeug
from insightface.app import FaceAnalysis
from sqlalchemy import func
from werkzeug.utils import secure_filename
from Backend.Models.CameraMonitoringLogs import CameraMonitoringLogs
from flask import jsonify, request, current_app
from werkzeug.security import generate_password_hash
from . import db
from Backend.Models.Department import Department
from Backend.Models.DepartmentSection import DepartmentSection
from Backend.Models.User import User
from Backend.Models.UserDepartment import UserDepartment
from Backend.Models.Role import Role
from Backend.Models.AssignSupervisor import AssignSupervisor
from Backend.Models.UserBiometric import UserBiometric
from ..Models import Camera, Location
from Backend.Local_Upload import  upload_profile_pictures_for_other
from Backend.Models.VisitorDeviations import VisitorDeviations



class AdminController:

    # FUnction to make admin run this for only one time:
    @staticmethod
    def add_admin():
        name = request.form.get("name")
        email = request.form.get("email")
        password = request.form.get("password")
        cnic = request.form.get("cnic")
        contact = request.form.get("contact")
        profile_img_file = request.files.get("profile_img")

        if not name or not email or not password or not cnic or not contact or not profile_img_file:
            return jsonify({"error": "Name, Email, Password, CNIC, Contact, and Profile Image are required"}), 400

        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            return jsonify({"error": "Email already exists"}), 400

        n = 16384
        r = 8
        p = 1
        salt = os.urandom(16)
        hashed_password = hashlib.scrypt(password.encode(), salt=salt, n=n, r=r, p=p)

        encoded_salt = b64encode(salt).decode('utf-8')
        formatted_password = f"scrypt:{n}:{r}:{p}${encoded_salt}${hashed_password.hex()}"

        new_user = User(
            name=name,
            email=email,
            password=formatted_password,
            cnic=cnic,
            contact=contact,
            profile_img=None
        )

        db.session.add(new_user)
        db.session.commit()
        try:
            profile_img_path = upload_profile_pictures_for_other(new_user.id, profile_img_file)
            new_user.profile_img = profile_img_path
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Error uploading profile picture for admin_id {new_user.id}: {str(e)}")
            return jsonify({"error": "Failed to upload profile picture"}), 500

        return jsonify({"message": "Admin added successfully"}), 201



        # --- Update profile of admin -----

    @staticmethod
    def update_admin():
        email = request.form.get("email")
        if not email:
            return jsonify({"error": "Email is required to identify the admin"}), 400

        admin = User.query.filter_by(email=email).first()
        if not admin:
            return jsonify({"error": "Admin with this email not found"}), 404

        name = request.form.get("name")
        password = request.form.get("password")
        cnic = request.form.get("cnic")
        contact = request.form.get("contact")
        profile_img = request.files.get("profile_img")

        if name:
            admin.name = name
        if cnic:
            admin.cnic = cnic
        if contact:
            admin.contact = contact

        if password:
            n, r, p = 16384, 8, 1
            salt = os.urandom(16)
            hashed_password = hashlib.scrypt(password.encode(), salt=salt, n=n, r=r, p=p)
            encoded_salt = b64encode(salt).decode('utf-8')
            formatted_password = f"scrypt:{n}:{r}:{p}${encoded_salt}${hashed_password.hex()}"
            admin.password = formatted_password

        if profile_img and hasattr(profile_img, 'filename'):
            try:
                upload_profile_pictures_for_other(admin.id, profile_img)
            except Exception as e:
                db.session.rollback()
                current_app.logger.error(f"Error uploading profile picture for admin_id {admin.id}: {str(e)}")
                return jsonify({"error": "Failed to upload profile picture"}), 500

        try:
            db.session.commit()
            return jsonify({"message": "Admin profile updated successfully"}), 200
        except Exception as e:
            print(f"Failed to update admin {admin.id if admin else 'unknown'}: {e}")
            return jsonify({"error": "Server error occurred"}), 500

        # --- ADD DEPARTMENT & SUBSECTIONS MODULE ---

    @staticmethod
    def add_department():
        data = request.get_json()
        if 'name' not in data or not data['name']:
            return jsonify({'error': 'Department name is required'}), 400

        department_name = data['name']

        try:
            new_department = Department(name=department_name)
            db.session.add(new_department)
            db.session.commit()

            return jsonify({
                'message': 'Department added successfully',
                'department_id': new_department.id
            }), 201

        except Exception as e:
            db.session.rollback()
            return jsonify({'error': str(e)}), 500

    # ADD NEW DEPARTMENT Sections
    @staticmethod
    def add_department_section():
        data = request.get_json()

        if 'name' not in data or not data['name']:
            return jsonify({'error': 'Subsection name is required'}), 400
        if 'department_id' not in data or not data['department_id']:
            return jsonify({'error': 'Department ID is required'}), 400

        section_name = data['name']
        department_id = data['department_id']
        camera_id = data.get('camera_id')

        try:
            department = Department.query.get(department_id)
            if not department:
                return jsonify({'error': 'Department not found'}), 404

            if camera_id:
                camera = Camera.query.get(camera_id)
                if not camera:
                    return jsonify({'error': 'Camera not found'}), 404

            new_section = DepartmentSection(
                name=section_name,
                department_id=department_id,
                camera_id=camera_id
            )

            db.session.add(new_section)
            db.session.commit()

            return jsonify({'message': 'Subsection added successfully'}), 201

        except Exception as e:
            db.session.rollback()
            return jsonify({'error': str(e)}), 500

    # ALL SUBSECTIONS
    @staticmethod
    def get_sections_by_department(department_id):
        sections = DepartmentSection.query.filter_by(department_id=department_id).all()
        section_list = [
            {
                "id": section.id,
                "name": section.name
            }
            for section in sections
        ]
        return jsonify({'sections': section_list}), 200

                     # --- MANAGE SUPERVISORS  MODULE ---

    # VIEW ALL SUPERVISORS
    @staticmethod
    def get_all_supervisors():
        supervisors = (
            db.session.query(User.name, User.profile_img, Department.name.label("department_name"))
            .join(UserDepartment, User.id == UserDepartment.user_id)
            .join(Role, UserDepartment.role_id == Role.id)
            .join(AssignSupervisor, UserDepartment.id == AssignSupervisor.supervisor_id)
            .join(Department, AssignSupervisor.department_id == Department.id)
            .filter(Role.name == 'Supervisor', UserDepartment.is_valid == True)
            .all()
        )

        supervisor_list = []

        for supervisor in supervisors:
            if supervisor.profile_img:
                filename = os.path.basename(supervisor.profile_img)
                profile_img_url = f"{request.host_url}uploads/profile_images/{filename}"
            else:
                profile_img_url = None

            supervisor_list.append({
                "name": supervisor.name,
                "profile_img": profile_img_url,
                "department_name": supervisor.department_name
            })

        return jsonify({"supervisors": supervisor_list}), 200

    # Get supervisors with id and name for dropdown :)
    @staticmethod
    def get_supervisors():
        supervisors = (
            db.session.query(User.id, User.name)
            .join(UserDepartment, User.id == UserDepartment.user_id)
            .join(Role, UserDepartment.role_id == Role.id)
            .filter(Role.name == 'Supervisor', UserDepartment.is_valid == True)
            .all()
        )

        supervisor_list = [{"id": supervisor.id, "name": supervisor.name} for supervisor in supervisors]
        return jsonify(supervisor_list), 200

    # Show all departments name
    @staticmethod
    def get_departments():
        departments = Department.query.with_entities(Department.id, Department.name).all()
        department_list = [{"id": department.id, "name": department.name} for department in departments]
        return jsonify({"departments": department_list}), 200

    # # Assign supervisor now
    # @staticmethod
    # def assign_supervisor():
    #     data = request.get_json()
    #     supervisor_id = data.get("supervisor_id")
    #     department_id = data.get("department_id")
    #
    #     if not supervisor_id or not department_id:
    #         return jsonify({"error": "Supervisor ID and Department ID are required"}), 400
    #
    #     assignment = AssignSupervisor(supervisor_id=supervisor_id, department_id=department_id)
    #     db.session.add(assignment)
    #     db.session.commit()
    #
    #     return jsonify({"message": "Supervisor assigned to department successfully"}), 201
    #

            # --- ADD NEW SUPERVISOR

    @staticmethod
    def add_supervisor():

        import os, cv2, csv, json, hashlib
        import numpy as np
        from base64 import b64encode
        from werkzeug.utils import secure_filename
        import pandas as pd
        from datetime import datetime
        import mediapipe as mp
        face_app = FaceAnalysis(providers=['CPUExecutionProvider'])
        face_app.prepare(ctx_id=0, det_size=(224, 224))

        mp_face_detection = mp.solutions.face_detection
        face_detector = mp_face_detection.FaceDetection(model_selection=1, min_detection_confidence=0.5)

        name = request.form.get("name")
        email = request.form.get("email")
        password = request.form.get("password")
        department_id = request.form.get("department_id")
        images = request.files.getlist("images")

        if not email or not password or not department_id:
            return jsonify({"error": "Email, Password, and Department ID are required"}), 400
        if len(images) < 6:
            return jsonify({"error": "At least 6 face images are required"}), 400

        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            return jsonify({"error": "Email already exists"}), 400

        n, r, p = 16384, 8, 1
        salt = os.urandom(16)
        hashed_password = hashlib.scrypt(password.encode(), salt=salt, n=n, r=r, p=p)
        encoded_salt = b64encode(salt).decode('utf-8')
        formatted_password = f"scrypt:{n}:{r}:{p}${encoded_salt}${hashed_password.hex()}"

        new_user = User(
            name=name,
            email=email,
            password=formatted_password,
            cnic=None,
            contact="PENDING",
            profile_img="DEFAULT_PROFILE_IMAGE_PATH"
        )

        db.session.add(new_user)
        db.session.commit()

        user_id = new_user.id

        supervisor_role = Role.query.filter_by(name="Supervisor").first()
        if not supervisor_role:
            return jsonify({"error": "Supervisor role not found"}), 404

        user_department = UserDepartment(
            user_id=user_id,
            department_id=department_id,
            role_id=supervisor_role.id
        )

        db.session.add(user_department)
        db.session.commit()

        assignment = AssignSupervisor(supervisor_id=user_department.id, department_id=department_id)
        db.session.add(assignment)
        db.session.commit()

        BASE_PATH = r"C:\Users\affan\OneDrive\Desktop\MultiBioFuse\Backend\uploads\NewUsers"
        CROPPED_PATH = os.path.join(BASE_PATH, "cropped_faces")
        CSV_PATH = os.path.join(BASE_PATH, "supervisor_embeddings.csv")
        os.makedirs(CROPPED_PATH, exist_ok=True)

        def crop_face(image):
            try:
                img_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
                results = face_detector.process(img_rgb)
                if not results.detections:
                    return None
                h, w, _ = image.shape
                bbox = results.detections[0].location_data.relative_bounding_box
                x, y, w_box, h_box = int(bbox.xmin * w), int(bbox.ymin * h), int(bbox.width * w), int(bbox.height * h)
                padding = 0.2
                x = max(0, int(x - w_box * padding))
                y = max(0, int(y - h_box * padding))
                w_box = min(w - x, int(w_box * (1 + 2 * padding)))
                h_box = min(h - y, int(h_box * (1 + 2 * padding)))
                cropped = image[y:y + h_box, x:x + w_box]
                return cv2.resize(cropped, (224, 224)) if cropped.size else None
            except Exception as e:
                print(f" Error cropping face: {e}")
                return None

        def extract_embeddings(image):
            try:
                img_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
                faces = face_app.get(img_rgb)
                return faces[0].embedding.tolist() if faces else None
            except Exception as e:
                print(f"Error extracting embedding: {e}")
                return None

        embeddings = []
        image_paths = []

        for img_file in images:
            filename = secure_filename(img_file.filename)
            temp_path = os.path.join(CROPPED_PATH, f"{user_id}_{filename}")
            image = cv2.imdecode(np.frombuffer(img_file.read(), np.uint8), cv2.IMREAD_COLOR)

            cropped = crop_face(image)
            if cropped is None:
                return jsonify({"error": f"Face not detected in {filename}"}), 400

            cv2.imwrite(temp_path, cropped)
            image_paths.append(temp_path)

            embedding = extract_embeddings(cropped)
            if embedding:
                embeddings.append(embedding)

        if not embeddings:
            return jsonify({"error": "No valid face embeddings extracted"}), 500

        final_embedding = np.mean(embeddings, axis=0)
        final_embedding /= np.linalg.norm(final_embedding)

        try:
            df = pd.read_csv(CSV_PATH)
            df = df[df["user_id"] != user_id]
            df.to_csv(CSV_PATH, index=False)
        except FileNotFoundError:
            pass

        file_exists = os.path.exists(CSV_PATH)
        with open(CSV_PATH, mode='a', newline='') as file:
            writer = csv.writer(file)
            if not file_exists:
                writer.writerow(["user_id", "embedding", "label"])
            writer.writerow([user_id, json.dumps(final_embedding.tolist()), name])


        return jsonify({"message": "Supervisor added successfully with face embeddings."}), 201



        # ---   USER MANAGEMENT  MODULE ---
    # Set User Credentials
    @staticmethod
    def add_employee(name, email, password, department_id, images):
        import os, cv2, csv, json, hashlib
        import numpy as np
        from base64 import b64encode
        from werkzeug.utils import secure_filename
        import pandas as pd
        from datetime import datetime
        import mediapipe as mp
        from insightface.app import FaceAnalysis

        face_app = FaceAnalysis(providers=['CPUExecutionProvider'])
        face_app.prepare(ctx_id=0, det_size=(224, 224))

        mp_face_detection = mp.solutions.face_detection
        face_detector = mp_face_detection.FaceDetection(model_selection=1, min_detection_confidence=0.5)

        # name = request.form.get("name")
        # email = request.form.get("email")
        # password = request.form.get("password")
        # department_id = request.form.get("department_id")
        # images = request.files.getlist("images")

        if not all([email, password, department_id]):
            return jsonify({"error": "Email, Password, and Department ID are required"}), 400
        if len(images) < 6:
            return jsonify({"error": "At least 6 face images are required"}), 400

        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            return jsonify({"error": "Email already exists"}), 400

        n, r, p = 16384, 8, 1
        salt = os.urandom(16)
        hashed_password = hashlib.scrypt(password.encode(), salt=salt, n=n, r=r, p=p)
        encoded_salt = b64encode(salt).decode('utf-8')
        formatted_password = f"scrypt:{n}:{r}:{p}${encoded_salt}${hashed_password.hex()}"

        new_user = User(
            name=name,
            email=email,
            password=formatted_password,
            cnic=None,
            contact="PENDING",
            profile_img="DEFAULT_PROFILE_IMAGE_PATH"
        )

        try:
            db.session.add(new_user)
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            return jsonify({"error": "Error adding employee: " + str(e)}), 500

        user_id = new_user.id

        employee_role = Role.query.filter_by(name="Employee").first()
        if not employee_role:
            return jsonify({"error": "Employee role not found"}), 404

        user_department = UserDepartment(
            user_id=user_id,
            department_id=department_id,
            role_id=employee_role.id
        )

        try:
            db.session.add(user_department)
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            return jsonify({"error": "Error assigning user to department: " + str(e)}), 500

        BASE_FACE_PATH = r"C:\Users\affan\OneDrive\Desktop\MultiBioFuse\Backend\uploads\NewUsers"
        CROPPED_PATH = os.path.join(BASE_FACE_PATH, "cropped_faces")
        CSV_PATH = r"C:\Users\affan\OneDrive\Desktop\MultiBioFuse\Backend\uploads\NewUsers\employee_embeddings.csv"
        os.makedirs(CROPPED_PATH, exist_ok=True)
        os.makedirs(os.path.dirname(CSV_PATH), exist_ok=True)

        def crop_face(image):
            try:
                img_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
                results = face_detector.process(img_rgb)
                if not results.detections:
                    return None
                h, w, _ = image.shape
                bbox = results.detections[0].location_data.relative_bounding_box
                x, y, w_box, h_box = int(bbox.xmin * w), int(bbox.ymin * h), int(bbox.width * w), int(bbox.height * h)
                padding = 0.2
                x = max(0, int(x - w_box * padding))
                y = max(0, int(y - h_box * padding))
                w_box = min(w - x, int(w_box * (1 + 2 * padding)))
                h_box = min(h - y, int(h_box * (1 + 2 * padding)))
                cropped = image[y:y + h_box, x:x + w_box]
                return cv2.resize(cropped, (224, 224)) if cropped.size else None
            except Exception as e:
                print(f"Error cropping face: {e}")
                return None

        def extract_embeddings(image):
            try:
                img_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
                faces = face_app.get(img_rgb)
                return faces[0].embedding.tolist() if faces else None
            except Exception as e:
                print(f"Error extracting embedding: {e}")
                return None

        embeddings = []
        image_paths = []

        for img_file in images:
            filename = secure_filename(img_file.filename)
            temp_path = os.path.join(CROPPED_PATH, f"{user_id}_{filename}")
            image = cv2.imdecode(np.frombuffer(img_file.read(), np.uint8), cv2.IMREAD_COLOR)

            cropped = crop_face(image)
            if cropped is None:
                return jsonify({"error": f"Face not detected in {filename}"}), 400

            cv2.imwrite(temp_path, cropped)
            image_paths.append(temp_path)

            embedding = extract_embeddings(cropped)
            if embedding:
                embeddings.append(embedding)

        if not embeddings:
            return jsonify({"error": "No valid face embeddings extracted"}), 500

        final_embedding = np.mean(embeddings, axis=0)
        final_embedding /= np.linalg.norm(final_embedding)

        try:
            df = pd.read_csv(CSV_PATH)
            df = df[df["user_id"] != user_id]
            df.to_csv(CSV_PATH, index=False)
        except FileNotFoundError:
            pass

        file_exists = os.path.exists(CSV_PATH)
        with open(CSV_PATH, mode='a', newline='') as file:
            writer = csv.writer(file)
            if not file_exists:
                writer.writerow(["user_id", "embedding", "label"])
            writer.writerow([user_id, json.dumps(final_embedding.tolist()), name])

        return jsonify({"message": "Employee added successfully with face embeddings."}), 201

        # Incomplete Profiles :)

    @staticmethod
    def incomplete_user_attributes():
        incomplete_users = (
            db.session.query(User.email)
            .join(UserDepartment, User.id == UserDepartment.user_id)
            .filter(
                UserDepartment.role_id.in_([2, 3]),
                (User.name == "") |
                (User.name == "pending") |
                (User.profile_img == "DEFAULT_PROFILE_IMAGE_PATH") |
                (User.cnic == "") |
                (User.contact == "")
            )
        )

        incomplete_biometrics = (
            db.session.query(User.email)
            .join(UserDepartment, User.id == UserDepartment.user_id)
            .outerjoin(UserBiometric, User.id == UserBiometric.user_id)
            .filter(UserDepartment.role_id.in_([2, 3]))
            .group_by(User.id)
            .having(db.func.count(UserBiometric.biometric_type) < 3)
        )

        incomplete_users = incomplete_users.union(incomplete_biometrics).all()

        user_list = [user.email for user in incomplete_users]

        return jsonify({"incomplete_users": user_list}), 200

    # Noti jee to incomplete users
    # @staticmethod
    # def send_notifications():
    #     incomplete_users = (
    #         db.session.query(User.id, User.email)
    #         .join(UserDepartment, User.id == UserDepartment.user_id)
    #         .filter(
    #             UserDepartment.role_id.in_([2, 3]),
    #             (User.name == "") |
    #             (User.name == "pending") |
    #             (User.profile_img == "DEFAULT_PROFILE_IMAGE_PATH") |
    #             (User.cnic == "") |
    #             (User.contact == "")
    #         )
    #     )
    #
    #     # Fetch users missing biometric data
    #     incomplete_biometrics = (
    #         db.session.query(User.id, User.email)
    #         .join(UserDepartment, User.id == UserDepartment.user_id)
    #         .outerjoin(UserBiometric, User.id == UserBiometric.user_id)
    #         .filter(UserDepartment.role_id.in_([2, 3]))
    #         .group_by(User.id)
    #         .having(db.func.count(UserBiometric.biometric_type) < 3)  # Must have all 3 biometrics
    #     )
    #
    #     # Combine both queries
    #     incomplete_users = incomplete_users.union(incomplete_biometrics).all()
    #
    #     # Prepare notifications (without storing in DB)
    #     message = "Please complete your profile information to register yourself."
    #     notifications = [{"user_id": user.id, "email": user.email, "message": message} for user in incomplete_users]
    #
    #     for notification in notifications:
    #         print(f"Notification for {notification['email']}: {notification['message']}")
    #     return jsonify({"message": "Notifications sent successfully"}), 200


        # ------ ACCESS LOGS HISTORY ------

    # ---------  Show all the employees who are in logs  --------------
    @staticmethod
    def fetch_employees():
        data = request.json
        department_id = data.get('department_id')
        start_date = data.get('start_date')
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

        users = (
            db.session.query(User)
            .join(UserDepartment)
            .join(CameraMonitoringLogs)
            .filter(UserDepartment.department_id == department_id)
            .filter(UserDepartment.is_valid.is_(True))
            .filter(func.date(CameraMonitoringLogs.date_time) >= start_date)
            .filter(func.date(CameraMonitoringLogs.date_time) <= end_date)
            .all()
        )

        if not users:
            return jsonify({"message": "No users found for the selected department and date range."}), 404

        results = [{"id": user.id, "name": user.name} for user in users]
        return jsonify(results), 200

    # ------- Call this when clicks on details button --------
    @staticmethod
    def fetch_employee_details():
        data = request.json
        user_dept_id = data.get('id')
        start_date = data.get('start_date')
        end_date = data.get('end_date')

        if not user_dept_id or not start_date or not end_date:
            return jsonify({"message": "Missing required fields (id, start_date, end_date)"}), 400

        try:
            start_date = datetime.fromisoformat(start_date)
            end_date = datetime.fromisoformat(end_date)
        except ValueError:
            return jsonify({"message": "Invalid date format. Use ISO format (YYYY-MM-DDTHH:MM:SS)"}), 400

        user_dept = db.session.query(UserDepartment).filter_by(id=user_dept_id).first()
        if not user_dept:
            return jsonify({"message": "User not found in department"}), 404

        user = user_dept.user
        role = user_dept.role.name

        logs = (
            db.session.query(CameraMonitoringLogs)
            .filter_by(user_id=user_dept_id)
            .filter(CameraMonitoringLogs.date_time.between(start_date, end_date))
            .join(Camera)
            .join(Location)
            .all()
        )

        if not logs:
            return jsonify({"message": "No logs found for the specified user and date range."}), 404

        logs_list = []
        for log in logs:
            logs_list.append({
                "log_id": log.id,
                "date_time": log.date_time.isoformat(),
                "access_img": log.access_img,
                "location": log.camera.location.name if log.camera and log.camera.location else "Unknown"
            })

        result = {
            "user_id": user.id,
            "name": user.name,
            "role": role,
        }

        if role.lower() == "employee":
            result["designation"] = getattr(user, "designation", "N/A")

        result["access_logs"] = logs_list

        return jsonify(result)

    @staticmethod
    def fetch_access_image_by_id():
        data = request.json
        log_id = data.get('id')


        if not log_id:
            return jsonify({"error": "Missing log ID."}), 400

        log = CameraMonitoringLogs.query.get(log_id)
        if not log:
            return jsonify({"error": "No access log found for this ID."}), 404

        host_url = request.host_url.rstrip('/')
        image_url = f"{host_url}/static/{log.access_img}"

        result = {
            "date_time": log.date_time.strftime('%Y-%m-%d %H:%M:%S'),
            "access_img": image_url
        }

        return jsonify(result)

        # ------ Visitors Logs history Module ------
    @staticmethod
    def get_visitors():
        visitors = db.session.query(User.id, User.name). \
            join(UserDepartment, User.id == UserDepartment.user_id). \
            join(Role, UserDepartment.role_id == Role.id). \
            filter(Role.id == 4, UserDepartment.is_valid.is_(True)). \
            all()

        visitor_list = [{'id': visitor.id, 'name': visitor.name} for visitor in visitors]

        return jsonify(visitor_list)


    @staticmethod
    def get_visitor_details(user_id):
        visitor = User.query.get(user_id)

        if visitor:
            user_dept = UserDepartment.query.filter_by(user_id=user_id, is_valid=True).order_by(
                UserDepartment.date_assigned.desc()).first()

            first_img = None
            if visitor.profile_img:
                first_img_path = visitor.profile_img.split(',')[0]
                filename = first_img_path.replace('\\', '/').split('uploads/')[-1]  # Extract path after 'uploads/'
                first_img = f"{request.host_url}uploads/{filename}".replace('///', '//')  # Avoid double slashes

            visitor_details = {
                'name': visitor.name,
                'cnic': visitor.cnic,
                'contact': visitor.contact,
                'profile_img': first_img,
                'date_assigned': user_dept.date_assigned if user_dept else None
            }

            return jsonify(visitor_details)
        else:
            return jsonify({'message': 'Visitor not found'}), 404

    # @staticmethod
    # def camera_Violations():
    #     try:
    #         data = request.get_json()
    #         camera_id = data.get('camera_id')
    #         start_date = data.get('start_date')
    #         end_date = data.get('end_date')
    #
    #         if not camera_id or not start_date or not end_date:
    #             return jsonify({"error": "camera_id, start_date, and end_date are required"}), 400
    #
    #         from datetime import datetime, timedelta
    #
    #         start = datetime.strptime(start_date, "%Y-%m-%d")
    #         end = datetime.strptime(end_date, "%Y-%m-%d") + timedelta(days=1) - timedelta(seconds=1)
    #
    #         # 🧠 Query all violations on this camera within the date range
    #         violations = db.session.query(VisitorDeviations, User).join(
    #             User, VisitorDeviations.visitor_id == User.id
    #         ).filter(
    #             VisitorDeviations.deviated_camera_id == camera_id,
    #             VisitorDeviations.date_time >= start,
    #             VisitorDeviations.date_time <= end
    #         ).all()
    #
    #         result = []
    #         for violation, user in violations:
    #             result.append({
    #                 "visitor_id": user.id,
    #                 "visitor_name": user.name,
    #                 "date_time": violation.date_time.strftime("%Y-%m-%d %H:%M:%S"),
    #                 "last_location": violation.last_location,
    #                 "destination": violation.destination
    #             })
    #
    #         return jsonify(result), 200
    #
    #
    #     except Exception as e:
    #         return jsonify({"error": str(e)}), 500
    #
    @staticmethod
    def camera_Violations():
        try:
            data = request.get_json()
            camera_id = data.get('camera_id')
            start_date = data.get('start_date')
            end_date = data.get('end_date')

            if not start_date or not end_date:
                return jsonify({"error": "camera_id, start_date, and end_date are required"}), 400

            from datetime import datetime, timedelta

            start = datetime.strptime(start_date, "%Y-%m-%d")
            end = datetime.strptime(end_date, "%Y-%m-%d") + timedelta(days=1) - timedelta(seconds=1)

            violations = db.session.query(CameraMonitoringLogs, User).join(
                User, CameraMonitoringLogs.user_id == User.id
            ).filter(
                CameraMonitoringLogs.camera_id == camera_id,
                CameraMonitoringLogs.date_time >= start,
                CameraMonitoringLogs.date_time <= end,
                CameraMonitoringLogs.destination
            ).all()

            result = []

            for violation, user in violations:
                # print(f"{violations}")
                # print(f"{user}")

                result.append({
                    "visitor_id": user.id,
                    "visitor_name": user.name,
                    "date_time": violation.date_time.strftime("%Y-%m-%d %H:%M:%S"),
                    "destination":violation.destination
                })

            return jsonify(result), 200


        except Exception as e:
            return jsonify({"error": str(e)}), 500



    @staticmethod
    def fetch_logs_task():
        try:
            data = request.get_json()
            # violated_person= db.session.query(VisitorDeviations, User).join(
            #     User, VisitorDeviations.visitor_id == User.id
            # ).filter(
            #     VisitorDeviations.deviated_camera_id ==
            #     VisitorDeviations.date_time >= start_time,
            #     VisitorDeviations.date_time <= end_time
            # ).all()
            # violated_person = db.session.query()

            start_date = data.get('start_date')
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

            users = (
                db.session.query(User)
                .join(UserDepartment)
                .join(CameraMonitoringLogs)
                .filter(UserDepartment.is_valid.is_(True))
                .filter(func.date(CameraMonitoringLogs.date_time) >= start_date)
                .filter(func.date(CameraMonitoringLogs.date_time) <= end_date)
                .all()
            )

            if not users:
                return jsonify({"message": "No users found for the selected department and date range."}), 404

            results = [{"id": user.id, "name": user.name} for user in users]
            return jsonify(results), 200





        except Exception as e:
            return jsonify({"error": str(e)}), 500


