import os
import os
import shutil
import tempfile
import random

import cv2
from flask import send_from_directory, url_for
from werkzeug.utils import secure_filename
from Backend import app, db, User
from pathlib import Path
from flask import Flask, request, jsonify, send_file, Blueprint, current_app
from Backend.Controllers.AdminController import AdminController
from Backend.Controllers.EmployeeController import EmployeeController
from Backend.Controllers.GuardController import GuardController
from Backend.Controllers.NewUsersTracking import process_video_from_api_NewUsers
from Backend.Local_Upload import upload_biometric, upload_profile_pictures, get_user_biometric, get_user_profile_picture
from Backend.Controllers.UserController import UserController
from Backend.Controllers.CameraController import CameraController
from Backend.Controllers.SupervisorController import SupervisorController
from Backend.Models import UserBiometric, UserDepartment
from Backend.Models.EmployeeDesignation import EmployeeDesignation
from Backend.Visitor_Tracking.recognize_visitor import process_video_from_api
from Backend.Visitor_Tracking.test_gait import classify_gait , save_annotated_frames

router = Blueprint('router', __name__)

# ---------------- LOG IN SCREEN  -------------------
@router.route('/login', methods=['POST'])
def login():
    return UserController.login()

# --------------- Update Admin Profile --------------
@router.route('/get_admin', methods=['GET'])
def get_admin_info():
    email = request.args.get('email')

    if not email:
        return jsonify({"error": "Email parameter is missing"}), 400

    user = User.query.filter_by(email=email).first()

    if not user:
        return jsonify({"error": "Admin not found"}), 404

    profile_image = None
    if user.profile_img:
        first_img = user.profile_img.split(',')[0]
        relative_path = first_img.split("uploads\\")[-1].replace("\\", "/")
        profile_image = f"{request.host_url}uploads/{relative_path}"

    return jsonify({
        "name": user.name,
        "email": user.email,
        "profile_img": profile_image,
        "cnic": user.cnic,
        "contact": user.contact
    }), 200

# Update info
@router.route('/update_admin', methods=['PUT'])
def update_admin():
    return AdminController.update_admin()

############################################  LOCAL DEVELOPMENT ROUTES ########################################################
@router.route('/upload', methods=['POST'])
def upload():
    user_id = request.form.get('user_id')
    biometric_type = request.form.get('biometric_type')
    file = request.files.get('file')

    if not user_id or not biometric_type or not file:
        return jsonify({"error": "Missing user_id, biometric_type or file"}), 400

    try:
        upload_biometric(user_id, biometric_type, file)
        return jsonify({"message": "File uploaded successfully"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@router.route('/upload/profile_picture', methods=['POST'])
def upload_profile_picture_route():
    user_id = request.form.get('user_id')
    file = request.files.get('file')

    if not user_id or not file:
        return jsonify({"error": "Missing user_id or file"}), 400

    try:
        upload_profile_pictures(user_id, file)
        return jsonify({"message": "Profile picture uploaded successfully"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
@router.route('/uploads/<path:subpath>')
def serve_upload(subpath):
    upload_dir = os.path.join(current_app.root_path, 'uploads')
    try:
        return send_from_directory(upload_dir, subpath)
    except FileNotFoundError:
        return jsonify({"error": "File not found"}), 404

@router.route('/user/<int:user_id>/biometrics', methods=['GET'])
def get_user_biometric_route(user_id):
    """Get biometric URLs"""
    try:
        biometrics = get_user_biometric(user_id)
        if biometrics:
            return jsonify({"biometrics": biometrics}), 200
        return jsonify({"message": "No biometrics found"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@router.route('/user/<int:user_id>/profile_picture', methods=['GET'])
def get_user_profile_picture_route(user_id):
    """Get profile picture URL"""
    try:
        profile_url = get_user_profile_picture(user_id)
        return jsonify({"profile_url": profile_url}) if profile_url else \
               jsonify({"message": "No profile picture"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500


###########################################  ADMIN ROUTES ###############################################################

# ---------- Add Admin to a System  --------------
@router.route('/add_admin', methods=['POST'])
def add_admin():
    return AdminController.add_admin()

                            # --- CAMERA & Location MODULE ---

# ------ Add New Location --------
@router.route('/add_location', methods=['POST'])
def adding_location():
    data = request.get_json()
    name = data.get('name')
    message = CameraController.add_location(name)
    return jsonify({"message": message})

# -------- Show All Locations ----------
@router.route('/all_locations',methods=['GET'])
def get_all_location():
    loc_list=CameraController.all_location()
    sorted_list = sorted(loc_list, key=lambda x: x['id'])
    return jsonify(sorted_list)

# ------- Add New Camera  --------
@router.route('/add_camera', methods=['POST'])
def add_camera():
    data = request.get_json()
    camera_model = data.get('camera_model')
    location_id = data.get('location_id')

    result = CameraController.add_camera(camera_model, location_id)
    if "Added" in result:
        return jsonify({"message": result})
    else:
        return jsonify({"error": result})

# -------- Get All Cameras  ------------
@router.route('/get_cameras', methods=['GET'])
def get_cameras():
    result = CameraController.get_all_cameras()
    if isinstance(result, list):
        return jsonify(result)
    else:
        return jsonify({"error": result})


# ---------  Set CameraConnections ---------
@router.route('/add_connection', methods=['POST'])
def add_connection():
    data = request.get_json()
    camera_name_1 = data.get('camera_name_1')
    camera_name_2 = data.get('camera_name_2')
    delay = data.get('delay')

    result = CameraController.add_connection(camera_name_1, camera_name_2, delay)
    if "successfully" in result:
        return jsonify({"message": result})
    else:
        return jsonify({"error": result})


# -------- Update Connection  -----
@router.route('/update_connection', methods=['PUT'])
def update_connection():
    data = request.get_json()
    camera_name_1 = data.get('camera_name_1')
    camera_name_2 = data.get('camera_name_2')
    delay = data.get('delay')

    result = CameraController.update_connection(camera_name_1, camera_name_2, delay)

    if "successfully" in result:
        return jsonify({"message": result}), 200
    else:
        return jsonify({"error": result}), 400


# --------- Get CameraConnections  -----------
@router.route('/get_connections',methods=['GET'])
def camera_connection():
    return CameraController.get_camera_adjacency_matrix()

# ---- Delete the Camera ---
@router.route('/delete_camera/<int:camera_id>', methods=['DELETE'])
def delete_camera(camera_id):
    result, status_code = CameraController.delete_camera(camera_id)
    return jsonify({"message": result}), status_code

# ---------- Delete connection  ---------
@router.route('/delete_connection', methods=['DELETE'])
def delete_connection():
    camera_name_1 = request.args.get('camera_name_1')
    camera_name_2 = request.args.get('camera_name_2')

    result = CameraController.delete_connection_by_names(camera_name_1, camera_name_2)

    if "successfully" in result:
        return jsonify({"message": result})
    else:
        return jsonify({"error": result}), 400

# ----------- Add Path --------------
@router.route('/add_path', methods=['POST'])
def add_path():
    data = request.get_json()
    source = data.get('source')
    destination = data.get('destination')
    return CameraController.add_path(source, destination)


# ------------ All Paths show ---------------
@router.route('/all_paths', methods=['GET'])
def get_all_paths():
    return CameraController.all_paths()


# --------- Add a new camera path  -----------
@router.route('/add_camera_path', methods=['POST'])
def add_camera_path():
    data = request.get_json()
    camera_path = data.get('camera_path')
    camera_id = data.get('camera_id')
    sequence = data.get('sequence')
    return CameraController.add_camera_path(camera_path, camera_id, sequence)


             # --------- ADD DEPARTMENT & SUBSECTIONS MODULE --------

# --------- Add new department --------------
@router.route('/add_department', methods=['POST'])
def add_department():
    return AdminController.add_department()


# --------------- Add a new department subsection  ---------------
@router.route('/add_department_section', methods=['POST'])
def add_department_section():
    return AdminController.add_department_section()


# ------------ See all the subsections ------------------
@router.route('/get_sections/<int:department_id>', methods=['GET'])
def get_sections(department_id):
    return AdminController.get_sections_by_department(department_id)



                 # ---------- MANAGE SUPERVISORS  MODULE -------------

# ------------- View All Supervisors and there Name, Profile, Department :| --------------
@router.route('/supervisors', methods=['GET'])
def get_supervisors():
    return AdminController.get_all_supervisors()

# Supervisor Dropdown
@router.route('/supervisor_dropdown', methods=['GET'])
def get_supervisors_dropdown():
    return AdminController.get_supervisors()

# All Departments names
@router.route('/get_departments', methods=['GET'])
def get_departments_route():
    return AdminController.get_departments()

# ----- New Supervisor -----------
# @router.route('/add_supervisor', methods=['POST'])
# def add_supervisor_route():
#     return AdminController.add_supervisor()

@router.route('/add_supervisor', methods=['POST'])
def add_supervisor_route():
    if 'images' not in request.files:
        return jsonify({"error": "At least 6 face images are required."}), 400

    if 'gait_video' not in request.files:
        return jsonify({"error": "Gait video is required."}), 400

    data = request.form
    name = data.get("name")
    gait_video = request.files["gait_video"]

    if not name:
        return jsonify({"error": "Name is required for video saving."}), 400

    try:
        project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
        video_base = os.path.join(project_root, "Video_AutoBrowsing")
        all_person_videos = os.path.join(video_base, "all_person_videos")
        cameras_path = os.path.join(video_base, "Cameras")

        os.makedirs(all_person_videos, exist_ok=True)
        os.makedirs(cameras_path, exist_ok=True)

        # Clean filename (convert to snake_case style)
        clean_name = name.strip().replace(" ", "_")
        filename = f"{clean_name}.mp4"
        saved_path = os.path.join(all_person_videos, filename)

        # ✅ Save the gait video to all_person_videos
        gait_video.save(saved_path)

        # ✅ Copy to each camera folder
        for cam_folder in os.listdir(cameras_path):
            cam_folder_path = os.path.join(cameras_path, cam_folder)
            if os.path.isdir(cam_folder_path):
                dst_path = os.path.join(cam_folder_path, filename)
                shutil.copyfile(saved_path, dst_path)

        print(f"[INFO] Supervisor gait video saved and copied to all cameras.")

    except Exception as e:
        print(f"[ERROR] Failed to save supervisor video: {e}")
        return jsonify({"error": "Error saving gait video."}), 500

    # ✅ Now pass to controller for database + face handling
    return AdminController.add_supervisor()

                # ------------ USER MANAGEMENT ---------------


# ------------ Add New Employee ------------
# @router.route('/add_employee', methods=['POST'])
# def add_employee_route():
#     return AdminController.add_employee()

# FOR AUTOMATION
@router.route('/add_employee', methods=['POST'])
def add_employee_route():
    if 'images' not in request.files:
        return jsonify({"error": "At least 6 face images are required."}), 400

    if 'gait_video' not in request.files:
        return jsonify({"error": "Gait video is required."}), 400

    data = request.form
    name = data.get("name")
    email = data.get("email")
    password = data.get("password")
    department_id = data.get("department_id")
    face_images = request.files.getlist("images")
    gait_video = request.files["gait_video"]

    if not all([email, password, department_id]):
        return jsonify({"error": "Email, Password, and Department ID are required"}), 400
    if len(face_images) < 6:
        return jsonify({"error": "At least 6 face images are required"}), 400

    try:
        project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
        video_base = os.path.join(project_root, "Video_AutoBrowsing")
        all_person_videos = os.path.join(video_base, "all_person_videos")
        cameras_path = os.path.join(video_base, "Cameras")

        os.makedirs(all_person_videos, exist_ok=True)
        os.makedirs(cameras_path, exist_ok=True)

        # Clean filename
        clean_name = name.strip().replace(" ", "_")
        filename = f"{clean_name}.mp4"
        saved_path = os.path.join(all_person_videos, filename)

        # Save the gait video
        gait_video.save(saved_path)

        # Copy to each camera folder
        for cam_folder in os.listdir(cameras_path):
            cam_folder_path = os.path.join(cameras_path, cam_folder)
            if os.path.isdir(cam_folder_path):
                dst_path = os.path.join(cam_folder_path, filename)
                shutil.copyfile(saved_path, dst_path)

        print(f"[INFO] Employee gait video saved and copied to all cameras.")

    except Exception as e:
        print(f"[ERROR] Failed to save video: {e}")
        return jsonify({"error": "Error saving gait video."}), 500

    # Pass everything to controller
    return AdminController.add_employee(name, email, password, department_id, face_images)

# # ------------ Incomplete profiles ------------
# @router.route('/incomplete_profiles', methods=['GET'])
# def get_incomplete_user_attributes():
#     return AdminController.incomplete_user_attributes()


                # ------ ACCESS LOGS HISTORY ------
# All Employees
@router.route('/fetch_employees_logs', methods=['POST'])
def logs():
    return AdminController.fetch_employees()

# Details button of every employee
@router.route('/fetch_employee_details', methods=['POST'])
def fetch_employee_details():
    return AdminController.fetch_employee_details()

# View Access image on between dates
@router.route('/fetch_access_images', methods=['POST'])
def fetch_access_images():
    return AdminController.fetch_access_image_by_id()




                                            # --- Visitors logs history module -----

@router.route('/visitors', methods=['GET'])
def visits():
    return AdminController.get_visitors()

@router.route('/visitors_details/<int:user_id>',methods=['GET'])
def visitors_details(user_id):
    return AdminController.get_visitor_details(user_id)

        # ----  Fetch Per Camera Violations Admin Module ----
@router.route('/camera/violations',methods=['POST'])
def get_camera_violations():
    return AdminController.camera_Violations()



#########################################     SUPERVISOR JEE        ########################################################

                        # ------ SUPERVISOR DASHBOARD -----

# ----- Check Profile Completion Status ----
@router.route('/CompletionSupervisor', methods=['POST'])
def isCompleteSupervisor():
    data = request.get_json()
    email = data.get('email')

    if not email:
        return jsonify({"error": "Email is required"}), 400

    return SupervisorController.checkCompleteOrNot(email)

# -------- Completing the supervisor profile screen 1  ---------
@router.route('/supervisor/profile', methods=['POST'])
def update_supervisor_profile():
    email = request.form.get('email')
    if not email:
        return jsonify({"error": "Email is required"}), 400

    profile_img_file = request.files.get('profile_img')
    name = request.form.get('name')
    phone_number = request.form.get('phone_number')
    cnic = request.form.get('cnic')

    response, status_code = SupervisorController.save_supervisor_profile(
        email,
        profile_img_file,
        name,
        phone_number,
        cnic
    )

    return jsonify(response), status_code

# ----------- Employee Overview -----------
@router.route('/employees/overview', methods=['GET'])
def employees_overview_route():
    result, status_code = SupervisorController.get_employees_overview()
    return result, status_code

# -------------- Per Emp Details ----------
@router.route('/employee/details', methods=['GET'])
def get_employee_details():
    return SupervisorController.employee_details_route()

#  ----------- To Show Relevant subsections of deartment  -------
@router.route('/show/subsections', methods=['GET'])
def show_subsections_department():
    user_id = request.args.get('user_id', type=int)

    if not user_id:
        return jsonify({"error": "Missing or invalid user_id parameter"}), 400

    result, status_code = SupervisorController.relevantSubsections(user_id)
    return jsonify(result), status_code

# ------- Access Control System -----------
@router.route('/grantaccess', methods=['POST'])
def grant_access():
    data = request.get_json()

    employee_id = data.get('employee_id')
    subsection_ids = data.get('subsection_ids')
    return SupervisorController.grant_access_to_employee(employee_id, subsection_ids)

# ---------- Track Employee Module ( Supervisor ) -----------
# --- Show dropdown of Subsections ---
@router.route('/subsections/overview', methods=['GET'])
def subsections_overview():
    email = request.args.get('email')
    if not email:
        return jsonify({"error": "Email is required"}), 400

    result, status_code = SupervisorController.relevant_subsections_by_email(email)
    return jsonify(result), status_code

# --- check if employye is allowed on which subsections
@router.route('/employee/access', methods=['GET'])
def employee_access():
    return SupervisorController.get_employee_access()

# ----   Access Logs History   ----
@router.route('/employee/logs',methods=['POST'])
def accesslogs_for_employee():
    return SupervisorController.access_logs_for_employees()








############################################ EMPLOYEE JEE ########################################################

# ----- Complete Profile : show drop down of designations
@router.route('/desginations',methods=['GET'])
def all_designations():
    return EmployeeController.all_designation_forEmp()

# ------ Complete profile full of employee -------
@router.route('/save_employee', methods=['POST'])
def save_employee_profile_route():
    email = request.form.get('email')
    cnic = request.form.get('cnic')
    contact = request.form.get('contact')
    designation_id = request.form.get('designation_id')
    profile_img_file = request.files.get('profile_img')

    if not all([email, cnic, contact, designation_id, profile_img_file]):
        return jsonify({"error": "All fields are required"}), 400

    # Ensure designation_id is an integer
    try:
        designation_id = int(designation_id)
    except ValueError:
        return jsonify({"error": "designation_id must be an integer"}), 400

    # Call controller function
    response, status_code = EmployeeController.save_employee_profile(
        email=email,
        cnic=cnic,
        contact=contact,
        designation_id=designation_id,
        profile_img_file=profile_img_file,
    )

    return jsonify(response), status_code



                # ACCESS LOGS HISTORY
# -------Route for fetching employee own logs----------
@router.route('/emp_logs',methods=['GET'])
def fetch_logs_employee():
    return EmployeeController.fetch_my_emp_logs()



# Route for fetching employee details
@router.route('/my_details/<int:employee_id>', methods=['GET'])
def fetch_details(employee_id):
    return EmployeeController.fetch_my_details(employee_id)




            ######## ------------ ( Module ) GUARD JEE  ------------########

# ------------ ADDING visitor to a system ------------
# @router.route('/add_visitor', methods=['POST'])
# def add_visitor():
#     if 'profile_img' not in request.files:
#         return jsonify({"message": "At least 6 profile images are required."}), 400
#
#     data = request.form
#     profile_img = request.files.getlist('profile_img')
#     gait_video = request.files.get('gait_video')
#
#     if len(profile_img) < 6:
#         return jsonify({"message": "At least 6 images are required."}), 400
#
#     if not gait_video:
#         return jsonify({"message": "Gait Video is Required."}), 400
#
#     name = data.get('name')
#     cnic = data.get('cnic')
#     contact = data.get('contact')
#
#     return GuardController.add_visitor(name, cnic, contact, profile_img, gait_video)

#  ------- FOR AUTOMATION  ----------
@router.route('/add_visitor', methods=['POST'])
def add_visitor():
    if 'profile_img' not in request.files:
        return jsonify({"message": "At least 6 profile images are required."}), 400

    data = request.form
    profile_img = request.files.getlist('profile_img')
    gait_video = request.files.get('gait_video')

    if len(profile_img) < 6:
        return jsonify({"message": "At least 6 images are required."}), 400

    if not gait_video:
        return jsonify({"message": "Gait Video is Required."}), 400

    name = data.get('name')
    cnic = data.get('cnic')
    contact = data.get('contact')

    try:
        # 💡 From: Backend/Router.py → go up one level to MultiBioFuse
        project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

        video_base = os.path.join(project_root, "Video_AutoBrowsing")
        all_person_videos = os.path.join(video_base, "all_person_videos")
        cameras_path = os.path.join(video_base, "Cameras")

        os.makedirs(all_person_videos, exist_ok=True)
        os.makedirs(cameras_path, exist_ok=True)

        # Format file name safely
        filename = f"{name.strip()}.mp4"

        saved_path = os.path.join(all_person_videos, filename)

        # ✅ Save gait video to all_person_videos permanently
        gait_video.save(saved_path)

        # ✅ Copy it into each camera folder
        for cam_folder in os.listdir(cameras_path):
            cam_folder_path = os.path.join(cameras_path, cam_folder)
            if os.path.isdir(cam_folder_path):
                dst_path = os.path.join(cam_folder_path, filename)
                shutil.copyfile(saved_path, dst_path)

        print(f"[INFO] Visitor video saved as '{filename}' and copied to all camera folders.")

    except Exception as e:
        print(f"[ERROR] Video handling failed: {e}")
        return jsonify({"error": "Error saving visitor gait video."}), 500

    return GuardController.add_visitor(name, cnic, contact, profile_img, gait_video)





# ------------- To Get All the Possible Paths  --------------
@router.route('/find_all_paths', methods=['POST'])
def track_multiple_visitors():
    data = request.get_json()

    if not isinstance(data, list) or len(data) == 0:
        return jsonify({"error": "At least one visitor record must be provided"}), 400

    result = GuardController.find_all_paths_for_multiple_visitors(data)

    return jsonify(result), 200

 #   task router to fetch the path
@router.route('/path_for_visitor', methods=['POST'])
def path_for_visitor():
    data = request.get_json()

    if not isinstance(data, list) or len(data) == 0:
        return jsonify({"error": "At least one visitor record must be provided"}), 400

    result = GuardController.find_path_visitors(data)

    return jsonify(result), 200


# --------  Visitor Face Recognition ------------
import os
UPLOAD_FOLDER = os.path.join(os.getcwd(), "backend", "uploads")
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
@router.route('/process_video', methods=['POST'])
def process_video_api():
    if 'video' not in request.files:
        return jsonify({"error": "No video file provided"}), 400

    video = request.files['video']
    video_path = os.path.join(UPLOAD_FOLDER, video.filename)
    video.save(video_path)
    results = process_video_from_api(video_path)
    return jsonify(results)

# --------- Visitor Gait Recognition -------------------
UPLOAD_FOLDER = os.path.join("uploads", "visitor_data", "gait_videos")
TRAINING_CSV = os.path.join("uploads", "visitor_data", "visitor_csv", "gait_recognition_visitor.csv")
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
@router.route("/recognize-gait", methods=["POST"])
def recognize_gait():
    if 'video' not in request.files:
        return jsonify({"status": "fail", "message": "No video file part in the request."}), 400

    file = request.files['video']
    if file.filename == '':
        return jsonify({"status": "fail", "message": "No selected file."}), 400

    filename = secure_filename(file.filename)
    file_path = os.path.join(UPLOAD_FOLDER, filename)
    file.save(file_path)

    result = classify_gait(file_path, TRAINING_CSV)

    return jsonify(result)


# ----------------- Unified Gait and Face Recognition ( Fusion ) -------------------------
   # FOR ONE VISITOR AT A TIME
# from concurrent.futures import ThreadPoolExecutor
# FACE_UPLOAD_FOLDER = os.path.join(os.getcwd(), "backend", "uploads")
# GAIT_UPLOAD_FOLDER = os.path.join("uploads", "visitor_data", "gait_video_cool_show")
# TRAINING_CSV = os.path.join("uploads", "visitor_data", "visitor_csv", "gait_recognition_visitor.csv")
# os.makedirs(FACE_UPLOAD_FOLDER, exist_ok=True)
# os.makedirs(GAIT_UPLOAD_FOLDER, exist_ok=True)
#
# @router.route('/unified-recognition', methods=['POST'])
# def unified_recognition():
#     print("Request received")
#     print("Content-Type:", request.content_type)
#     print("Request.files keys:", request.files.keys())
#     if 'video' not in request.files:
#         return jsonify({"error": "No video file provided"}), 400
#
#     video = request.files['video']
#     filename = secure_filename(video.filename)
#     face_video_path = os.path.join(FACE_UPLOAD_FOLDER, filename)
#     video.save(face_video_path)
#     video.stream.seek(0)
#     gait_video_path = os.path.join(GAIT_UPLOAD_FOLDER, filename)
#     video.save(gait_video_path)
#     save_annotated_frames(gait_video_path)
#
#     def run_face():
#         return process_video_from_api(face_video_path)
#
#     def run_gait():
#         return classify_gait(gait_video_path, TRAINING_CSV)
#
#     with ThreadPoolExecutor(max_workers=2) as executor:
#         face_future = executor.submit(run_face)
#         gait_future = executor.submit(run_gait)
#
#         face_result = face_future.result()
#         gait_result = gait_future.result()
#
#
#     if (
#         isinstance(face_result, dict)
#         and face_result.get("recognized_faces")
#         and isinstance(face_result["recognized_faces"], list)
#         and len(face_result["recognized_faces"]) > 0
#     ):
#         return jsonify(face_result)
#     return jsonify(gait_result)



         # ---------- Guard side of Multiple Visitor Threading --------- :)
# import os
# import uuid
# import threading
# from flask import request, jsonify
# from werkzeug.utils import secure_filename
# from datetime import datetime
# from concurrent.futures import ThreadPoolExecutor
#
# FACE_UPLOAD_FOLDER = os.path.join(os.getcwd(), "backend", "uploads")
# GAIT_UPLOAD_FOLDER = os.path.join("uploads", "visitor_data", "gait_video_cool_show")
# TRAINING_CSV = os.path.join("uploads", "visitor_data", "visitor_csv", "gait_recognition_visitor.csv")
#
# os.makedirs(FACE_UPLOAD_FOLDER, exist_ok=True)
# os.makedirs(GAIT_UPLOAD_FOLDER, exist_ok=True)
#
# tasks = {}
# executor = ThreadPoolExecutor(max_workers=4)
#
# def process_recognition_task(task_id, face_path, gait_path, visitor_id):
#     start_time = datetime.now()
#     print(f"[{start_time}] Task {task_id} started")
#
#     try:
#         tasks[task_id] = {"status": 0}
#
#         try:
#             save_annotated_frames(gait_path, visitor_id=visitor_id)
#             print(f"Annotated frames saved for {gait_path}")
#         except Exception as e:
#             print(f"Warning: Failed to save annotated frames: {e}")
#
#         face_result = process_video_from_api(face_path)
#         gait_result = classify_gait(gait_path, TRAINING_CSV)
#
#         result = face_result if (
#             isinstance(face_result, dict)
#             and face_result.get("recognized_faces")
#             and len(face_result["recognized_faces"]) > 0
#         ) else gait_result
#
#         tasks[task_id] = {"status": 1, "result": result}
#
#     except Exception as e:
#         tasks[task_id] = {"status": -1, "result": str(e)}
#         print(f"Error in task {task_id}: {e}")
#
#     end_time = datetime.now()
#     print(f"[{end_time}] Task {task_id} completed in {(end_time - start_time).total_seconds()}s")
#
#
# @router.route('/unified-recognition/start', methods=['POST'])
# def start_unified_recognition():
#     if 'video' not in request.files:
#         return jsonify({"error": "No video file provided"}), 400
#
#     if 'visitor_id' not in request.form:
#         return jsonify({"error": "No visitor_id provided"}), 400
#
#     visitor_id = request.form['visitor_id']
#     video = request.files['video']
#     filename = secure_filename(video.filename)
#     unique_id = uuid.uuid4().hex
#     new_filename = f"{unique_id}_{filename}"
#
#     face_video_path = os.path.join(FACE_UPLOAD_FOLDER, new_filename)
#     gait_video_path = os.path.join(GAIT_UPLOAD_FOLDER, new_filename)
#
#     video.save(face_video_path)
#     from shutil import copyfile
#     copyfile(face_video_path, gait_video_path)
#
#     task_id = uuid.uuid4().hex
#     executor.submit(process_recognition_task, task_id, face_video_path, gait_video_path, visitor_id)
#
#     return jsonify({"task_id": task_id}), 202
#
#
# @router.route('/unified-recognition/status/<task_id>', methods=['GET'])
# def get_task_status(task_id):
#     task = tasks.get(task_id)
#     if not task:
#         return jsonify({"status": -2, "message": "Task ID not found"}), 404
#     return jsonify(task)


                 # Changes before task
#             # -------- MULTIPLE VISITOR TRACKING VIA AUTOMATION PROCESS
# import os
# import uuid
# import threading
# from flask import request, jsonify
# from werkzeug.utils import secure_filename
# from datetime import datetime
# from concurrent.futures import ThreadPoolExecutor
#
# FACE_UPLOAD_FOLDER = os.path.join(os.getcwd(), "backend", "uploads")
# GAIT_UPLOAD_FOLDER = os.path.join("uploads", "visitor_data", "gait_video_cool_show")
# TRAINING_CSV = os.path.join("uploads", "visitor_data", "visitor_csv", "gait_recognition_visitor.csv")
#
# os.makedirs(FACE_UPLOAD_FOLDER, exist_ok=True)
# os.makedirs(GAIT_UPLOAD_FOLDER, exist_ok=True)
#
# tasks = {}
# executor = ThreadPoolExecutor(max_workers=4)
#
# def process_recognition_task(task_id, face_path, gait_path, visitor_id):
#     start_time = datetime.now()
#     print(f"[{start_time}] Task {task_id} started")
#
#     try:
#         tasks[task_id] = {"status": 0}
#
#         try:
#             save_annotated_frames(gait_path, visitor_id=visitor_id)
#             print(f"Annotated frames saved for {gait_path}")
#         except Exception as e:
#             print(f"Warning: Failed to save annotated frames: {e}")
#
#         face_result = process_video_from_api(face_path)
#         gait_result = classify_gait(gait_path, TRAINING_CSV)
#
#         result = face_result if (
#             isinstance(face_result, dict)
#             and face_result.get("recognized_faces")
#             and len(face_result["recognized_faces"]) > 0
#         ) else gait_result
#
#         tasks[task_id] = {"status": 1, "result": result}
#
#     except Exception as e:
#         tasks[task_id] = {"status": -1, "result": str(e)}
#         print(f"Error in task {task_id}: {e}")
#
#     end_time = datetime.now()
#     print(f"[{end_time}] Task {task_id} completed in {(end_time - start_time).total_seconds()}s")
#
#
# @router.route('/unified-recognition/start', methods=['POST'])
# def start_unified_recognition():
#     print("[DEBUG] Received request to /unified-recognition/start")
#
#     try:
#         data = request.get_json(force=True)
#         print(f"[DEBUG] Data received: {data}")
#
#         visitor_id = data.get('visitor_id')
#         visitor_name = data.get('visitor_name', '').strip()
#         camera_name = data.get('camera_name', '').strip()
#
#
#         if not visitor_id or visitor_id == 'null' or not visitor_name or not camera_name:
#             print("[ERROR] Missing or invalid visitor_id, visitor_name, or camera_name")
#             return jsonify({"error": "Missing or invalid visitor_id, visitor_name, or camera_name"}), 400
#
#         # Clean names
#         visitor_name_clean = visitor_name.strip()
#         name_with_underscores = visitor_name_clean.replace(' ', '_')
#         name_with_spaces = visitor_name_clean  # already stripped
#
#         # Build base path
#         project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
#         camera_folder = os.path.join(project_root, "Video_AutoBrowsing", "Cameras", camera_name)
#
#         # Possible file paths
#         file1 = os.path.join(camera_folder, f"{name_with_spaces}.mp4")
#         file2 = os.path.join(camera_folder, f"{name_with_underscores}.mp4")
#
#         # Decide which file exists
#         video_path = None
#         if os.path.exists(file1):
#             video_path = file1
#         elif os.path.exists(file2):
#             video_path = file2
#
#         print(f"[DEBUG] Checked paths:\n - {file1}\n - {file2}")
#
#         if not video_path:
#             print("[ERROR] Video file not found.")
#             return jsonify({"error": "Video not found for visitor"}), 404
#
#         # Create and submit task
#         task_id = uuid.uuid4().hex
#         print(f"[DEBUG] Starting recognition task with ID: {task_id}")
#
#         executor.submit(
#             process_recognition_task,
#             task_id,
#             video_path,  # Face path
#             video_path,  # Gait path
#             visitor_id
#         )
#
#         return jsonify({"task_id": task_id}), 202
#
#     except Exception as e:
#         print(f"[ERROR] Exception during recognition start: {e}")
#         return jsonify({"error": str(e)}), 500
#
#
#
# @router.route('/unified-recognition/status/<task_id>', methods=['GET'])
# def get_task_status(task_id):
#     task = tasks.get(task_id)
#     if not task:
#         return jsonify({"status": -2, "message": "Task ID not found"}), 404
#     return jsonify(task)
#
#
#         # -------- Store the violations of visitor , when alerts  --------
# @router.route('/store-violations-visitor',methods=['POST'])
# def store_violations():
#     return GuardController.store_violations_of_visitors()


            # ----- Changes after the task
import os
import uuid
import threading
from flask import request, jsonify
from werkzeug.utils import secure_filename
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor

FACE_UPLOAD_FOLDER = os.path.join(os.getcwd(), "backend", "uploads")
GAIT_UPLOAD_FOLDER = os.path.join("uploads", "visitor_data", "gait_video_cool_show")
TRAINING_CSV = os.path.join("uploads", "visitor_data", "visitor_csv", "gait_recognition_visitor.csv")

os.makedirs(FACE_UPLOAD_FOLDER, exist_ok=True)
os.makedirs(GAIT_UPLOAD_FOLDER, exist_ok=True)

tasks = {}
executor = ThreadPoolExecutor(max_workers=4)

def process_recognition_task(task_id, face_path, gait_path, visitor_id):
    start_time = datetime.now()
    print(f"[{start_time}] Task {task_id} started")

    try:
        tasks[task_id] = {"status": 0}

        try:
            save_annotated_frames(gait_path, visitor_id=visitor_id)
            print(f"Annotated frames saved for {gait_path}")
        except Exception as e:
            print(f"Warning: Failed to save annotated frames: {e}")

        face_result = process_video_from_api(face_path)
        gait_result = classify_gait(gait_path, TRAINING_CSV)

        result = face_result if (
            isinstance(face_result, dict)
            and face_result.get("recognized_faces")
            and len(face_result["recognized_faces"]) > 0
        ) else gait_result

        tasks[task_id] = {"status": 1, "result": result}

    except Exception as e:
        tasks[task_id] = {"status": -1, "result": str(e)}
        print(f"Error in task {task_id}: {e}")

    end_time = datetime.now()
    print(f"[{end_time}] Task {task_id} completed in {(end_time - start_time).total_seconds()}s")


@router.route('/unified-recognition/start', methods=['POST'])
def start_unified_recognition():
    print("[DEBUG] Received request to /unified-recognition/start")

    try:
        data = request.get_json(force=True)
        print(f"[DEBUG] Data received: {data}")

        visitor_id = data.get('visitor_id')
        visitor_name = data.get('visitor_name', '').strip()
        camera_name = data.get('camera_name', '').strip()
        destination = data.get('destination','').strip()

        if not visitor_id or visitor_id == 'null' or not visitor_name or not camera_name:
            print("[ERROR] Missing or invalid visitor_id, visitor_name, or camera_name")
            return jsonify({"error": "Missing or invalid visitor_id, visitor_name, or camera_name"}), 400

        # Clean names
        visitor_name_clean = visitor_name.strip()
        name_with_underscores = visitor_name_clean.replace(' ', '_')
        name_with_spaces = visitor_name_clean  # already stripped

        # Build base path
        project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
        camera_folder = os.path.join(project_root, "Video_AutoBrowsing", "Cameras", camera_name)

        # Possible file paths
        file1 = os.path.join(camera_folder, f"{name_with_spaces}.mp4")
        file2 = os.path.join(camera_folder, f"{name_with_underscores}.mp4")

        # Decide which file exists
        video_path = None
        if os.path.exists(file1):
            video_path = file1
        elif os.path.exists(file2):
            video_path = file2

        print(f"[DEBUG] Checked paths:\n - {file1}\n - {file2}")

        if not video_path:
            print("[ERROR] Video file not found.")
            return jsonify({"error": "Video not found for visitor"}), 404


        # Storing the info of every visitor in the db :)) Task
        save_logs_to_CameraMonitoring_table(visitor_id, camera_name, video_path,destination)

        # Create and submit task
        task_id = uuid.uuid4().hex
        print(f"[DEBUG] Starting recognition task with ID: {task_id}")

        executor.submit(
            process_recognition_task,
            task_id,
            video_path,  # Face path
            video_path,  # Gait path
            visitor_id
        )

        return jsonify({"task_id": task_id}), 202

    except Exception as e:
        print(f"[ERROR] Exception during recognition start: {e}")
        return jsonify({"error": str(e)}), 500



@router.route('/unified-recognition/status/<task_id>', methods=['GET'])
def get_task_status(task_id):
    task = tasks.get(task_id)
    if not task:
        return jsonify({"status": -2, "message": "Task ID not found"}), 404
    return jsonify(task)




        # -------- Store the violations of visitor , when alerts  --------
@router.route('/store-violations-visitor',methods=['POST'])
def store_violations():
    return GuardController.store_violations_of_visitors()

        # Get all logs form camera ML and VisitorDeviation table
@router.route('/fetch_task_logs',methods=['POST'])
def fetch_tasklogs():
    return AdminController.fetch_logs_task()

        # -------- This will serve the actual Images of Visitor ----------
@router.route('/visitor/image/<filename>')
def serve_visitor_image(filename):
    response = send_from_directory(IMAGE_FOLDER, filename)
    response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '0'
    return response

            #------------- Visitor's ACCESS IMAGES -------------
IMAGE_FOLDER = os.path.join(os.getcwd(), 'uploads', 'visitor_data', 'gait_frame_previews')
@router.route('/visitor/images', methods=['GET'])
def get_visitor_images():
    try:
        visitor_id = request.args.get('visitor_id')
        if not visitor_id:
            return jsonify({"error": "visitor_id is required as a query parameter"}), 400
        image_files = [
            f for f in os.listdir(IMAGE_FOLDER)
            if f.startswith(f"visitor_{visitor_id}_") and f.endswith(('.jpg', '.png'))
        ]

        image_urls = [
            url_for('router.serve_visitor_image', filename=filename, _external=True)
            for filename in image_files
        ]

        return jsonify({"images": image_urls})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# --------------------- Alert Screen of Visitor  --------------------------
@router.route('/user/<int:user_id>', methods=['GET'])
def get_user(user_id):
    user_data = UserController.get_user_by_id(user_id)
    if user_data:
        return jsonify(user_data)
    else:
        return jsonify({"message": "User not found"}), 404
@router.route('/uploads/<path:filename>')
def serve_uploads(filename):
    return send_from_directory('uploads', filename)

# -----------------  Check Previous Violations of the Visitor  -------------------
@router.route('/get_past_violations_visior',methods=['POST'])
def past_violations():
    return GuardController.past_violations_visitor()


####################################################################################

            # ------ IN USE This sectionis resposible for Track Supervisor Screen ( ADMIN MODULE )----
# UPLOAD_FOLDER = "static/uploads"
# CUTOFF_DATE = datetime.strptime("2025-06-21 13:28:13", "%Y-%m-%d %H:%M:%S")
# @router.route('/route_user_video', methods=['POST'])
# def route_user_video():
#     try:
#         user_id = request.form.get('user_id')
#         camera_id = request.form.get('camera_id')
#
#         if not user_id:
#             return jsonify({"error": "user_id is required"}), 400
#         if 'video' not in request.files:
#             return jsonify({"error": "No video part in request"}), 400
#
#         file = request.files['video']
#         if file.filename == '':
#             return jsonify({"error": "No selected video"}), 400
#
#         user_dept = UserDepartment.query.filter_by(user_id=user_id, is_valid=True).first()
#         if not user_dept:
#             return jsonify({"error": "User department assignment not found"}), 404
#
#         # Save uploaded video
#         filename = secure_filename(file.filename)
#         unique_filename = f"{uuid.uuid4().hex}_{filename}"
#         video_path = os.path.join(UPLOAD_FOLDER, unique_filename)
#         file.save(video_path)
#         from Backend.Controllers.NewUsersTracking import save_logs_to_CameraMonitoring_table
#         save_logs_to_CameraMonitoring_table(user_dept.id, camera_id, video_path)
#
#         # For Adding the records in the database
#         save_annotated_frames(video_path, visitor_id=user_id)
#         # Case 1: New User → Use Face + Random Gait style
#         if user_dept.date_assigned > CUTOFF_DATE:
#             result = process_video_from_api_NewUsers(video_path)
#
#         # Case 2: Old User → Use Gait Model (which now also returns same format)
#         else:
#             try:
#                 result = analyze_video(video_path)
#             except Exception as e:
#                 result = {
#                     "gait": "Unknown",
#                     "gender": "Male",
#                     "name": "Unknown",
#                     "error": str(e)
#                 }
#
#         # Remove video after processing
#         if os.path.exists(video_path):
#             os.remove(video_path)
#
#         return jsonify(result)
#
#     except Exception as e:
#         return jsonify({"error": str(e)}), 500

#     # ------ IN USE This sectionis resposible for Track Supervisor and Employee Screen ( ADMIN MODULE )----
# from flask import current_app, request, jsonify
# from concurrent.futures import ThreadPoolExecutor
# import uuid
# import os
# from werkzeug.utils import secure_filename
# from datetime import datetime
# from Backend.Controllers.NewUsersTracking import save_logs_to_CameraMonitoring_table
#
# tasks_employee = {}
# executor_employee = ThreadPoolExecutor(max_workers=4)
#
# UPLOAD_FOLDER = "static/uploads"
# CUTOFF_DATE = datetime.strptime("2025-06-21 13:28:13", "%Y-%m-%d %H:%M:%S")
#
#
# def process_user_video_task(app, task_id, user_id, camera_id, video_path):
#     print(f"[THREAD STARTED] Task {task_id}")
#     with app.app_context():
#         try:
#             from Backend.Models import UserDepartment  # ✅ Place inside context
#             print(f"[TASK {task_id}] Fetching user department")
#             user_dept = UserDepartment.query.filter_by(user_id=user_id, is_valid=True).first()
#             if not user_dept:
#                 tasks_employee[task_id] = {"status": -1, "error": "User department assignment not found"}
#                 return
#
#             print(f"[TASK {task_id}] Saving logs to camera monitoring")
#             save_logs_to_CameraMonitoring_table(user_dept.id, camera_id, video_path)
#
#             print(f"[TASK {task_id}] Saving annotated frames")
#             save_annotated_frames(video_path, visitor_id=user_id)
#
#             if user_dept.date_assigned > CUTOFF_DATE:
#                 print(f"[TASK {task_id}] Processing video from NewUser API")
#                 result = process_video_from_api_NewUsers(video_path)
#             else:
#                 try:
#                     print(f"[TASK {task_id}] Processing with gait model")
#                     result = analyze_video(video_path)
#                 except Exception as e:
#                     print(f"[TASK {task_id}] Error during gait analysis: {e}")
#                     result = {
#                         "gait": "Unknown",
#                         "gender": "Male",
#                         "name": "Unknown",
#                         "error": str(e)
#                     }
#
#             if os.path.exists(video_path):
#                 os.remove(video_path)
#
#             print(f"[TASK {task_id}] Completed")
#             tasks_employee[task_id] = {"status": 1, "result": result}
#
#         except Exception as e:
#             print(f"[TASK {task_id}] FAILED: {e}")
#             tasks_employee[task_id] = {"status": -1, "error": str(e)}
#
#
# @router.route('/route_user_video', methods=['POST'])
# def route_user_video():
#     try:
#         user_id = request.form.get('user_id')
#         camera_id = request.form.get('camera_id')
#
#         if not user_id:
#             return jsonify({"error": "user_id is required"}), 400
#         if 'video' not in request.files:
#             return jsonify({"error": "No video part in request"}), 400
#
#         file = request.files['video']
#         if file.filename == '':
#             return jsonify({"error": "No selected video"}), 400
#
#         task_id = uuid.uuid4().hex
#         filename = secure_filename(file.filename)
#         unique_filename = f"{uuid.uuid4().hex}_{filename}"
#         video_path = os.path.join(UPLOAD_FOLDER, unique_filename)
#
#         os.makedirs(UPLOAD_FOLDER, exist_ok=True)
#         file.save(video_path)
#
#         tasks_employee[task_id] = {"status": 0}
#
#         app = current_app._get_current_object()  # ✅ Get actual app
#         executor_employee.submit(process_user_video_task, app, task_id, user_id, camera_id, video_path)
#
#         return jsonify({"task_id": task_id}), 202
#
#     except Exception as e:
#         return jsonify({"error": str(e)}), 500
#
#
# @router.route('/route_user_video/status/<task_id>', methods=['GET'])
# def get_user_task_status(task_id):
#     task = tasks_employee.get(task_id)
#     if not task:
#         return jsonify({"status": -2, "message": "Task ID not found"}), 404
#     return jsonify(task)

        # -------- AFTER AUTOMATION FOR SUPERVISOR AND EMPLOYEE

import os
import uuid
from flask import request, jsonify, current_app
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor
from Backend.Controllers.NewUsersTracking import save_logs_to_CameraMonitoring_table

tasks_employee_auto = {}
executor_employee_auto = ThreadPoolExecutor(max_workers=4)
CUTOFF_DATE = datetime.strptime("2025-06-21 13:28:13", "%Y-%m-%d %H:%M:%S")

@router.route('/auto_track_user', methods=['POST'])
def auto_track_user():
    try:
        data = request.get_json(force=True)
        user_id = data.get("user_id")
        user_name = data.get("user_name", "").strip()
        camera_name = data.get("camera_name", "").strip()

        if not user_id or not user_name or not camera_name:
            return jsonify({"error": "user_id, user_name and camera_name are required"}), 400

        name_with_spaces = user_name
        name_with_underscores = user_name.replace(" ", "_")

        # Video path logic
        project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
        camera_folder = os.path.join(project_root, "Video_AutoBrowsing", "Cameras", camera_name)

        file1 = os.path.join(camera_folder, f"{name_with_spaces}.mp4")
        file2 = os.path.join(camera_folder, f"{name_with_underscores}.mp4")

        video_path = file1 if os.path.exists(file1) else file2 if os.path.exists(file2) else None

        if not video_path:
            return jsonify({"error": "Video not found for this user"}), 404

        task_id = uuid.uuid4().hex
        tasks_employee_auto[task_id] = {"status": 0}

        app = current_app._get_current_object()
        executor_employee_auto.submit(
            process_user_video_auto_task,
            app,
            task_id,
            user_id,
            camera_name,
            video_path
        )

        return jsonify({"task_id": task_id}), 202

    except Exception as e:
        return jsonify({"error": str(e)}), 500


def process_user_video_auto_task(app, task_id, user_id, camera_name, video_path):
    print(f"[AUTO-TASK STARTED] ID: {task_id}")
    with app.app_context():
        try:
            from Backend.Models import UserDepartment
            user_dept = UserDepartment.query.filter_by(user_id=user_id, is_valid=True).first()

            if not user_dept:
                tasks_employee_auto[task_id] = {"status": -1, "error": "No department assigned to this user"}
                return
            destination_name="Main Gate"
            # Save logs
            save_logs_to_CameraMonitoring_table(user_dept.id, camera_name, video_path,destination_name)

            # Annotate frames
            save_annotated_frames(video_path, visitor_id=user_id)

            # Decide which model to use
            if user_dept.date_assigned > CUTOFF_DATE:
                print(f"[{task_id}] New user flow")
                result = process_video_from_api_NewUsers(video_path)
            else:
                print(f"[{task_id}] Old user gait flow")
                try:
                    result = analyze_video(video_path)
                except Exception as e:
                    result = {
                        "gait": "Unknown",
                        "gender": "Unknown",
                        "name": "Unknown",
                        "error": str(e)
                    }

            # Do not delete video anymore (important for future runs)
            print(f"🔁 Video retained for reprocessing: {video_path}")

            tasks_employee_auto[task_id] = {"status": 1, "result": result}

        except Exception as e:
            tasks_employee_auto[task_id] = {"status": -1, "error": str(e)}
            print(f"[AUTO-TASK ERROR] {e}")


@router.route('/auto_track_user/status/<task_id>', methods=['GET'])
def get_auto_user_task_status(task_id):
    task = tasks_employee_auto.get(task_id)
    if not task:
        return jsonify({"status": -2, "message": "Task ID not found"}), 404
    return jsonify(task)



        # --------  To show Access Images of Supervisor during tracking  --------------
# Use this endpoint /visitor/images

##########################################################################
 # --- to track new users Testing purpose ------
@router.route('/track_new_users', methods=['POST'])
def track_new_users():
    if 'video' not in request.files:
        return jsonify({"error": "No video part in request"}), 400

    file = request.files['video']
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400

    with tempfile.NamedTemporaryFile(delete=False, suffix=".mp4") as temp_video:
        file.save(temp_video.name)
        video_path = temp_video.name

    try:
        result = process_video_from_api_NewUsers(video_path)
        return jsonify(result)
    finally:
        # Cleanup: remove temp video file
        if os.path.exists(video_path):
            os.remove(video_path)

        # --------- API OF GAIT MODEL ( For Testing Purpose SOLO GAIT)  -------------
from GaitRecognition.Testing import analyze_video
@router.route('/analyze_gait', methods=['POST'])
def analyze_gait():
    if 'video' not in request.files:
        print("No video file part in request.")
        return jsonify({'error': 'No video part in request'}), 400

    file = request.files['video']
    if file.filename == '':
        print("Empty filename received.")
        return jsonify({'error': 'No selected file'}), 400

    filename = secure_filename(file.filename)
    unique_filename = f"{uuid.uuid4().hex}_{filename}"
    video_path = os.path.join(UPLOAD_FOLDER, unique_filename)
    file.save(video_path)
    print("Video Received for Recognition of Users")
    try:
        result = analyze_video(video_path)
        os.remove(video_path)
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

       # --------  FOR FACE MODEL API ( FOR TESTING PURPOSE SOLO FACE ) -------
from FaceRecognition.TestingFaceModel import analyze_face_video
@router.route('/analyze_face', methods=['POST'])
def analyze_face():
    if 'video' not in request.files:
        return jsonify({'error': 'No video file part in request'}), 400

    file = request.files['video']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400

    filename = secure_filename(file.filename)
    unique_filename = f"{uuid.uuid4().hex}_{filename}"
    video_path = os.path.join(UPLOAD_FOLDER, unique_filename)
    file.save(video_path)

    try:
        result = analyze_face_video(video_path)
        os.remove(video_path)
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

#         # --------- MERGE FACE + GAIT MODEL  ---------------
# @router.route('/analyze_combined', methods=['POST'])
# def analyze_combined():
#     if 'video' not in request.files:
#         return jsonify({'error': 'No video file part in request'}), 400
#
#     file = request.files['video']
#     if file.filename == '':
#         return jsonify({'error': 'No selected file'}), 400
#
#     filename = secure_filename(file.filename)
#     unique_filename = f"{uuid.uuid4().hex}_{filename}"
#     video_path = os.path.join(UPLOAD_FOLDER, unique_filename)
#     file.save(video_path)
#
#     try:
#
#         face_result = analyze_face_video(video_path)
#         gait_result = analyze_video(video_path)
#         os.remove(video_path)
#         response = {
#             'name': face_result.get('name') or gait_result.get('name'),
#             'gender': face_result.get('gender') or gait_result.get('gender'),
#             'confidence': face_result.get('confidence', None),
#             'gait_style': gait_result.get('gait', 'Unknown')
#         }
#
#         return jsonify(response)
#
#     except Exception as e:
#         return jsonify({'error': str(e)}), 500


        # ----------  Store Employee Violations  -----
@router.route('/emp/violations',methods=['POST'])
def store_emp_violations():
    return SupervisorController.store_employee_violations()

##################################################   DIRECTOR  MODULE  ####################################################

from Backend.Controllers.DirectorController import DirectorController
                        # ------ BLOCK PATHS ( DR MODULE ) ---------
# ------ Show All Available Paths -----
@router.route('/paths_for_dr', methods=['POST'])
def paths_for_dr():
    data = request.json
    current_location_id = data.get('current_location_id')
    desired_location_id = data.get('desired_location_id')

    result = DirectorController.fetch_all_available_paths_fordr(current_location_id, desired_location_id)
    return jsonify(result)

# ------- Discard the paths ------
@router.route('/discard_path',methods=['POST'])
def discard_paths():
    return DirectorController.discard_selected_paths()


        # -------  CHECK VISITOR MODULE  ----------

# ---- daily Visitors -----
@router.route('/check_daily_visitors', methods=['GET'])
def check_daily_visitors():
    return DirectorController.dailyVisitors()

# -------  Monthly Visitors  ---------
@router.route('/check_monthly_visitors', methods=['GET'])
def check_monthly_visitors():
    return DirectorController.monthly_Visitors()

# -------- Yearly Visitors  -----------
@router.route('/check_yearly_visitors', methods=['GET'])
def check_yearly_visitors():
    return DirectorController.Yearly_Visitors()


            # --------- Check Attendance MODULE ( Attendance & Regularity ) ---------

    # ------ Daily Attendance per user -------
@router.route('/check_daily_attendance', methods=['GET'])
def check_daily_attendance():
    return DirectorController.check_daily_attendance()


    # -------- Monthly Attendance -------
@router.route('/monthy/least/most/employees',methods=['GET'])
def check_all_employees():
    return  DirectorController.monthly_Employees()

    # ------------ Yearly Attendance  --------
@router.route('/yearly/least/most/employees', methods=['GET'])
def check_all_employees_yearly():
    return DirectorController.yearly_Employees()


        # ---- Check Violations of Employees WHO VIOLATES ---
@router.route('/get_emp_violations',methods=['GET'])
def get_violations():
    return DirectorController.get_emp_violations()

        # ---- See all the details of the employee -----
@router.route('/see_details_violation',methods=['GET'])
def get_detail_violation():
    return DirectorController.get_violation_details()




if __name__ == '__main__':
    app.run(debug=True)
