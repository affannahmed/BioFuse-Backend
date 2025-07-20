from collections import defaultdict
from sqlite3 import IntegrityError
from werkzeug.utils import secure_filename
from Backend.Models import User, Role, UserDepartment, Location, Path,  Camera
from Backend.Models.CameraConnections import CameraConnections
import os
import cv2
import json
import csv
import numpy as np
import pandas as pd
import face_recognition
from flask import jsonify, request
from sqlalchemy.exc import IntegrityError
from Backend.Local_Upload import upload_profile_pictures
from Backend.Models import User, Role, UserDepartment
from . import db
from insightface.app import FaceAnalysis
import mediapipe as mp

from ..Models.VisitorDeviations import VisitorDeviations

# Initialize InsightFace (CPU mode)
face_app = FaceAnalysis(providers=['CPUExecutionProvider'])
face_app.prepare(ctx_id=0, det_size=(224, 224))

# Initialize MediaPipe Face Detection
mp_face_detection = mp.solutions.face_detection
face_detector = mp_face_detection.FaceDetection(model_selection=1, min_detection_confidence=0.5)

# Directories
BASE_FOLDER = r"C:\Users\affan\OneDrive\Desktop\MultiBioFuse\Backend\uploads\visitor_data"
CROPPED_FOLDER = os.path.join(BASE_FOLDER, "cropped_faces")
CSV_PATH = os.path.join(BASE_FOLDER, "visitor_csv", "visitor_embeddings.csv")

os.makedirs(CROPPED_FOLDER, exist_ok=True)

class GuardController:
    @staticmethod
    def add_visitor(name, cnic, contact, profile_img,gait_video):
        if len(profile_img) < 6:
            return jsonify({"message": "At least 6 images are required."}), 400

        # Step 1: Add visitor to database
        new_user = User(name=name, cnic=cnic, contact=contact)
        db.session.add(new_user)
        try:
            db.session.commit()
        except IntegrityError:
            db.session.rollback()
            return jsonify({"message": "User with this CNIC or contact already exists."}), 400

        visitor_role = db.session.query(Role).filter(Role.name == "Visitor").one_or_none()
        if not visitor_role:
            return jsonify({"message": "Role 'Visitor' not found."}), 404

        user_department_entry = UserDepartment(user_id=new_user.id, department_id=None, role_id=visitor_role.id)
        db.session.add(user_department_entry)

        try:
            image_paths = upload_profile_pictures(new_user.id, profile_img)
        except Exception as e:
            db.session.rollback()
            return jsonify({"error": str(e)}), 500

        db.session.commit()

        # Step 3: Generate and store face embeddings
        success, message = GuardController.save_face_embeddings(new_user.id, name, image_paths)
        if not success:
            return jsonify({"error": message}), 500

        # Step 4: Save gait video and process
        if gait_video:
            videos_dir = os.path.join(BASE_FOLDER, "gait_register_video")
            os.makedirs(videos_dir, exist_ok=True)

            video_path = os.path.join(videos_dir, f"{new_user.id}_{secure_filename(gait_video.filename)}")
            gait_video.save(video_path)

            # Import and call your gait processing function here
            from Backend.Visitor_Tracking.process_gait import process_video_for_visitor
            try:
                process_video_for_visitor(video_path, new_user.id, name)
            except Exception as e:
                print(f"[ERROR] Gait processing failed: {e}")
                return jsonify({"error": "Gait processing failed."}), 500

        return jsonify(
            {"message": "Visitor added successfully with images and gait video processed.", "id": new_user.id}), 201

    @staticmethod
    def crop_face(image):
        try:
            img_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            results = face_detector.process(img_rgb)
            if not results.detections:
                return None

            h, w, _ = image.shape
            bboxC = results.detections[0].location_data.relative_bounding_box
            x, y, w_box, h_box = (
                int(bboxC.xmin * w),
                int(bboxC.ymin * h),
                int(bboxC.width * w),
                int(bboxC.height * h),
            )

            padding = 0.2
            x = max(0, int(x - w_box * padding))
            y = max(0, int(y - h_box * padding))
            w_box = min(w - x, int(w_box * (1 + 2 * padding)))
            h_box = min(h - y, int(h_box * (1 + 2 * padding)))

            cropped_face = image[y:y + h_box, x:x + w_box]
            if cropped_face.size == 0:
                return None

            return cv2.resize(cropped_face, (224, 224))
        except Exception as e:
            print(f"❌ Error cropping face: {e}")
            return None

    @staticmethod
    def extract_embeddings(cropped_face):
        try:
            img_rgb = cv2.cvtColor(cropped_face, cv2.COLOR_BGR2RGB)
            faces = face_app.get(img_rgb)
            if not faces:
                return None
            return faces[0].embedding.tolist()
        except Exception as e:
            print(f"❌ Error extracting embeddings: {e}")
            return None

    @staticmethod
    def save_face_embeddings(user_id, name, image_paths):
        embeddings_list = []

        for img_path in image_paths:
            image = cv2.imread(img_path)
            cropped_face = GuardController.crop_face(image)
            if cropped_face is None:
                return False, f"Could not detect face in {img_path}"

            # Save cropped face
            cropped_path = os.path.join(CROPPED_FOLDER, f"{user_id}_{os.path.basename(img_path)}")
            cv2.imwrite(cropped_path, cropped_face)

            face_embedding = GuardController.extract_embeddings(cropped_face)
            if face_embedding:
                embeddings_list.append(face_embedding)

        if not embeddings_list:
            return False, "No embeddings generated."

        final_embedding = np.mean(embeddings_list, axis=0)
        final_embedding /= np.linalg.norm(final_embedding)

        try:
            df = pd.read_csv(CSV_PATH)
            df = df[df["user_id"] != user_id]
            df.to_csv(CSV_PATH, index=False)
        except FileNotFoundError:
            pass

        # Save new embeddings
        file_exists = os.path.exists(CSV_PATH)
        with open(CSV_PATH, mode='a', newline='') as file:
            writer = csv.writer(file)
            if not file_exists:
                writer.writerow(["user_id", "embedding", "label"])
            writer.writerow([user_id, json.dumps(final_embedding.tolist()), name])

        return True, "Embeddings saved successfully."


                #     TO GET PATHS WITH DELAYS AS WELL

    # @staticmethod
    # def find_all_paths(current_location_id, desired_location_id):
    #     all_paths_with_cameras = []  # Store all paths with camera sequences and delays
    #
    #     # Fetch the current and desired locations
    #     current_location = Location.query.get(current_location_id)
    #     if not current_location:
    #         return {"error": "Current location not found"}, 404
    #
    #     desired_location = Location.query.get(desired_location_id)
    #     if not desired_location:
    #         return {"error": "Desired location not found"}, 404
    #
    #     # Recursive function to find unique paths with location IDs
    #     def find_paths(current_id, destination_id, visited, path=[]):
    #         if current_id in visited:
    #             return []
    #         if current_id == destination_id:
    #             return [path + [current_id]]  # Append final location
    #
    #         visited.add(current_id)
    #         paths = []
    #
    #         direct_paths = Path.query.filter_by(source=current_id).all()
    #         for path_obj in direct_paths:
    #             sub_paths = find_paths(path_obj.destination, destination_id, visited, path + [current_id])
    #             for sub_path in sub_paths:
    #                 if sub_path not in paths:  # Avoid duplicate sequences
    #                     paths.append(sub_path)
    #
    #         visited.remove(current_id)
    #         return paths
    #
    #     # Find all unique paths (in terms of location IDs)
    #     path_sequences = find_paths(current_location_id, desired_location_id, set())
    #
    #     if not path_sequences:
    #         return {"error": "No paths found from current to desired location"}, 404
    #
    #     # Process each path to include cameras and delays
    #     for location_sequence in path_sequences:
    #         # Get location names and cameras for each location in the path
    #         path_with_names = []
    #         cameras_per_location = []
    #
    #         for loc_id in location_sequence:
    #             location = Location.query.get(loc_id)
    #             if not location:
    #                 break  # Skip invalid paths
    #             path_with_names.append(location.name)
    #
    #             # Fetch cameras at this location
    #             cameras = Camera.query.filter_by(location_id=loc_id).all()
    #             if not cameras:
    #                 break  # Skip paths with locations without cameras
    #             cameras_per_location.append(cameras)
    #         else:  # Only proceed if all locations are valid and have cameras
    #             # Generate all possible camera combinations (one per location)
    #             from itertools import product
    #             camera_combinations = product(*cameras_per_location)
    #
    #             for camera_sequence in camera_combinations:
    #                 valid_sequence = True
    #                 cameras_with_delay = []
    #                 total_delay = 0
    #
    #                 for idx, camera in enumerate(camera_sequence):
    #                     if idx == 0:
    #                         # First camera has 0 delay
    #                         cameras_with_delay.append({
    #                             "camera": camera.camera_model,
    #                             "delay": 0
    #                         })
    #                     else:
    #                         # Get delay from previous camera to current
    #                         prev_camera = camera_sequence[idx - 1]
    #                         connection = CameraConnections.query.filter_by(
    #                             camera_id_1=prev_camera.id,
    #                             camera_id_2=camera.id
    #                         ).first()
    #
    #                         if not connection:
    #                             valid_sequence = False
    #                             break
    #
    #                         cameras_with_delay.append({
    #                             "camera": camera.camera_model,
    #                             "delay": connection.delay
    #                         })
    #                         total_delay += connection.delay
    #
    #                 if valid_sequence:
    #                     # Check for duplicate camera sequences (optional)
    #                     unique_cameras = [c['camera'] for c in cameras_with_delay]
    #                     path_entry = {
    #                         "path": path_with_names.copy(),
    #                         "cameras": cameras_with_delay,
    #                         "total_delay": total_delay  # Optional, include if needed
    #                     }
    #                     # Avoid duplicate entries
    #                     if path_entry not in all_paths_with_cameras:
    #                         all_paths_with_cameras.append(path_entry)
    #
    #     if not all_paths_with_cameras:
    #         return {"error": "No valid camera paths found"}, 404
    #
    #     # Return the structured response
    #     return {
    #         "current_location": current_location.name,
    #         "desired_location": desired_location.name,
    #         "paths": all_paths_with_cameras
    #     }


    # # @staticmethod
    # # def find_all_paths(current_location_id, desired_location_id):
    # #     all_paths_with_cameras = []  # Store all unique paths and their cameras
    # #
    # #     # Fetch the current and desired locations
    # #     current_location = Location.query.get(current_location_id)
    # #     if not current_location:
    # #         return {"error": "Current location not found"}, 404
    # #
    # #     desired_location = Location.query.get(desired_location_id)
    # #     if not desired_location:
    # #         return {"error": "Desired location not found"}, 404
    # #
    # #     # Recursive function to find unique paths with location names
    # #     def find_paths(current_id, destination_id, visited, path=[]):
    # #         if current_id in visited:
    # #             return []
    # #         if current_id == destination_id:
    # #             return [path + [destination_id]]  # Append final location
    # #
    # #         visited.add(current_id)
    # #         paths = []
    # #
    # #         direct_paths = Path.query.filter_by(source=current_id).all()
    # #         for path_obj in direct_paths:
    # #             sub_paths = find_paths(path_obj.destination, destination_id, visited, path + [current_id])
    # #             for sub_path in sub_paths:
    # #                 if sub_path not in paths:  # Avoid duplicate sequences
    # #                     paths.append(sub_path)
    # #
    # #         visited.remove(current_id)
    # #         return paths
    # #
    # #     # Find all unique paths (in terms of location IDs)
    # #     path_sequences = find_paths(current_location_id, desired_location_id, set())
    # #
    # #     if not path_sequences:
    # #         return {"error": "No paths found from current to desired location"}, 404
    # #
    # #     # Convert location IDs to names and fetch cameras
    # #     unique_paths = set()  # To ensure unique paths
    # #     for location_sequence in path_sequences:
    # #         path_with_names = []
    # #         cameras_on_path = []
    # #
    # #         for loc_id in location_sequence:
    # #             location = Location.query.get(loc_id)
    # #             if location:
    # #                 path_with_names.append(location.name)
    # #
    # #                 # Fetch cameras installed at this location
    # #                 cameras = Camera.query.filter_by(location_id=loc_id).all()
    # #                 for camera in cameras:
    # #                     cameras_on_path.append(camera.camera_model)
    # #
    # #         path_tuple = tuple(path_with_names)  # Convert list to tuple for uniqueness
    # #         if path_tuple not in unique_paths:
    # #             unique_paths.add(path_tuple)  # Track unique paths
    # #
    # #             # Add the structured path data
    # #             all_paths_with_cameras.append({
    # #                 "path": path_with_names,
    # #                 "cameras": cameras_on_path
    # #             })
    # #
    # #     # Return the structured response
    # #     return {
    # #         "current_location": current_location.name,
    # #         "desired_location": desired_location.name,
    # #         "paths": all_paths_with_cameras
    #     }
    @staticmethod
    def find_all_paths_for_multiple_visitors(visitor_requests):
        results = []

        for request_data in visitor_requests:
            visitor_id = request_data.get('visitor_id')
            current_location_id = request_data.get('current_location_id')
            desired_location_id = request_data.get('desired_location_id')

            if not visitor_id or not current_location_id or not desired_location_id:
                results.append({
                    "error": f"Missing visitor_id, current_location_id or desired_location_id in record: {request_data}"
                })
                continue

            user = User.query.get(visitor_id)
            if not user:
                results.append({
                    "visitor_id": visitor_id,
                    "error": "Visitor not found in User table"
                })
                continue

            current_location = Location.query.get(current_location_id)
            desired_location = Location.query.get(desired_location_id)

            if not current_location or not desired_location:
                results.append({
                    "visitor_name": user.name,
                    "error": "Invalid location IDs"
                })
                continue

            # ✅ Helper function: Now filters only paths with status == 1
            def find_paths(current_id, destination_id, visited, path=[]):
                if current_id in visited:
                    return []
                if current_id == destination_id:
                    return [path + [destination_id]]
                visited.add(current_id)
                paths = []
                # ✅ Only include active paths
                direct_paths = Path.query.filter_by(source=current_id, status=1).all()
                for path_obj in direct_paths:
                    sub_paths = find_paths(path_obj.destination, destination_id, visited, path + [current_id])
                    for sub_path in sub_paths:
                        if sub_path not in paths:
                            paths.append(sub_path)
                visited.remove(current_id)
                return paths

            path_sequences = find_paths(current_location_id, desired_location_id, set())
            all_paths_with_cameras = []
            unique_paths = set()

            for location_sequence in path_sequences:
                cleaned_path = []
                cameras_on_path = []

                for loc_id in location_sequence:
                    location = Location.query.get(loc_id)
                    if not location:
                        continue  # skip if location doesn't exist

                    cameras = Camera.query.filter_by(location_id=loc_id).all()
                    if not cameras:
                        continue  # skip this checkpoint only

                    cleaned_path.append(location.name)
                    for camera in cameras:
                        cameras_on_path.append(camera.camera_model)

                if cleaned_path:
                    path_tuple = tuple(cleaned_path)
                    if path_tuple not in unique_paths:
                        unique_paths.add(path_tuple)
                        all_paths_with_cameras.append({
                            "path": cleaned_path,
                            "cameras": cameras_on_path
                        })

            results.append({
                "visitor_name": user.name,
                "current_location": current_location.name,
                "desired_location": desired_location.name,
                "paths": all_paths_with_cameras
            })

        return results


    #  fetch for task for showing his followed path.
    @staticmethod
    def find_path_visitors(visitor_requests):
        results = []

        for request_data in visitor_requests:
            visitor_id = request_data.get('visitor_id')
            current_location_id = request_data.get('current_location_id')
            desired_location_id = request_data.get('desired_location_id')

            if not visitor_id or not current_location_id or not desired_location_id:
                results.append({
                    "error": f"Missing visitor_id, current_location_id or desired_location_id in record: {request_data}"
                })
                continue

            user = User.query.get(visitor_id)
            if not user:
                results.append({
                    "visitor_id": visitor_id,
                    "error": "Visitor not found in User table"
                })
                continue

            current_location = Location.query.get(current_location_id)
            desired_location = Location.query.get(desired_location_id)

            if not current_location or not desired_location:
                results.append({
                    "visitor_name": user.name,
                    "error": "Invalid location IDs"
                })
                continue

            def find_paths(current_id, destination_id, visited, path=[]):
                if current_id in visited:
                    return []
                if current_id == destination_id:
                    return [path + [destination_id]]
                visited.add(current_id)
                paths = []
                # ✅ Only include active paths
                direct_paths = Path.query.filter_by(source=current_id, status=1).all()
                for path_obj in direct_paths:
                    sub_paths = find_paths(path_obj.destination, destination_id, visited, path + [current_id])
                    for sub_path in sub_paths:
                        if sub_path not in paths:
                            paths.append(sub_path)
                visited.remove(current_id)
                return paths

            path_sequences = find_paths(current_location_id, desired_location_id, set())
            all_paths_with_cameras = []
            unique_paths = set()

            for location_sequence in path_sequences:
                cleaned_path = []
                cameras_on_path = []

                for loc_id in location_sequence:
                    location = Location.query.get(loc_id)
                    if not location:
                        continue  # skip if location doesn't exist

                    cameras = Camera.query.filter_by(location_id=loc_id).all()
                    if not cameras:
                        continue  # skip this checkpoint only

                    cleaned_path.append(location.name)
                    for camera in cameras:
                        cameras_on_path.append(camera.camera_model)

                if cleaned_path:
                    path_tuple = tuple(cleaned_path)
                    if path_tuple not in unique_paths:
                        unique_paths.add(path_tuple)
                        all_paths_with_cameras.append({
                            "path": cleaned_path,
                            "cameras": cameras_on_path
                        })

            results.append({
                "visitor_name": user.name,
                "desired_location": desired_location.name,
                # "paths": all_paths_with_cameras
                "path":cleaned_path
            })

        return results


    @staticmethod
    def store_violations_of_visitors():
        try:
            data = request.get_json()

            # Extract fields from request
            visitor_id = data.get('visitor_id')
            deviated_camera_id = data.get('deviated_camera_id')
            last_location = data.get('last_location')
            destination = data.get('destination')

            # Basic validation
            if not visitor_id or not deviated_camera_id:
                return jsonify({"error": "visitor_id and deviated_camera_id are required"}), 400

            # Create a new deviation record
            violation = VisitorDeviations(
                visitor_id=visitor_id,
                deviated_camera_id=deviated_camera_id,
                last_location=last_location,
                destination=destination
            )

            # Save to DB
            db.session.add(violation)
            db.session.commit()

            return jsonify({"message": "Violation recorded successfully"}), 201

        except Exception as e:
            db.session.rollback()
            return jsonify({"error": str(e)}), 500



    # --- past violations of visitor ----
    @staticmethod
    def past_violations_visitor():
        try:
            data = request.get_json()
            visitor_id = data.get('visitor_id')

            if not visitor_id:
                return jsonify({"error": "visitor_id is required"}), 400

            # Query all violations for this visitor
            violations = VisitorDeviations.query.filter_by(visitor_id=visitor_id).order_by(
                VisitorDeviations.date_time.desc()).all()

            # Build response list
            violations_list = []
            for v in violations:
                camera = v.deviated_camera  # this uses the relationship
                violations_list.append({
                    "violation_id": v.id,
                    "deviated_camera_id": v.deviated_camera_id,
                    "camera_model": camera.camera_model if camera else None,
                    "last_location": v.last_location,
                    "destination": v.destination,
                    "date_time": v.date_time.strftime("%Y-%m-%d %H:%M:%S")
                })

            return jsonify({
                "visitor_id": visitor_id,
                "total_violations": len(violations_list),
                "violations": violations_list
            }), 200

        except Exception as e:
            return jsonify({"error": str(e)}), 500