from flask import jsonify
from . import db
from Backend.Models.CameraPath import CameraPath
from Backend.Models.Location import Location
from Backend.Models.Camera import Camera
from Backend.Models.CameraConnections import CameraConnections
from Backend.Models.Path import Path
from sqlalchemy.orm import aliased
import os
import shutil

class CameraController:
    # Show All Locations
    @staticmethod
    def all_location():
        locs = Location.query.all()
        loc_list = [
            {
                "id": loc.id,
                "name": loc.name
            }
            for loc in locs

        ]
        return loc_list

    # Add New Location
    @staticmethod
    def add_location(name):
        if not name:
            return "Location name cannot be empty"

        try:
            loc = Location(name=name)
            db.session.add(loc)
            db.session.commit()
            return "Location Added"
        except Exception as e:
            db.session.rollback()
            return str(e)

    # Add New Camera Jee and assign it a location to be installed
    # @staticmethod
    # def add_camera(camera_model, location_id):
    #     if not camera_model:
    #         return "Camera model cannot be empty"
    #     if not location_id:
    #         return "Location ID cannot be empty"
    #
    #     try:
    #         location = Location.query.get(location_id)
    #         if not location:
    #             return "Location not found"
    #
    #         new_camera = Camera(camera_model=camera_model, location_id=location_id)
    #         db.session.add(new_camera)
    #         db.session.commit()
    #         return "Camera Added"
    #     except Exception as e:
    #         db.session.rollback()
    #         return str(e)
    @staticmethod
    def add_camera(camera_model, location_id):
        if not camera_model:
            return "Camera model cannot be empty"
        if not location_id:
            return "Location ID cannot be empty"

        try:
            # Validate location
            location = Location.query.get(location_id)
            if not location:
                return "Location not found"

            # Add to DB
            new_camera = Camera(camera_model=camera_model, location_id=location_id)
            db.session.add(new_camera)
            db.session.commit()

            # --- Accurate path setup from project root ---
            # Get absolute path to project root
            project_root = os.path.abspath(
                os.path.join(os.path.dirname(__file__), "..", "..")  # Up from Controllers/ to Backend/ to MultiBioFuse/
            )

            video_root = os.path.join(project_root, "Video_AutoBrowsing")
            all_videos_path = os.path.join(video_root, "all_person_videos")
            cameras_path = os.path.join(video_root, "Cameras")
            new_camera_folder = os.path.join(cameras_path, camera_model)

            # Debug prints (you can remove later)
            print("[+] Project Root:", project_root)
            print("[+] Camera Folder To Create:", new_camera_folder)

            # Create camera folder
            os.makedirs(new_camera_folder, exist_ok=True)

            # Copy videos into camera folder
            if os.path.exists(all_videos_path):
                for video in os.listdir(all_videos_path):
                    if video.endswith((".mp4", ".avi", ".mov")):
                        src = os.path.join(all_videos_path, video)
                        dst = os.path.join(new_camera_folder, video)
                        if not os.path.exists(dst):
                            shutil.copy(src, dst)
            else:
                print(f"[ERROR] all_person_videos folder not found: {all_videos_path}")

            return "Camera Added"

        except Exception as e:
            db.session.rollback()
            return str(e)

    # Show All Cameras
    @staticmethod
    def get_all_cameras():
        try:
            cameras = Camera.query.all()
            if not cameras:
                return "No cameras found"

            camera_list = [
                {
                    'id': camera.id,
                    'camera_model': camera.camera_model,
                    'location': camera.location.name if camera.location else "Unknown"  # Fetch location name
                }
                for camera in cameras
            ]
            return camera_list
        except Exception as e:
            return str(e)

    # Setting Camera Connections :)
    @staticmethod
    def add_connection(camera_name_1, camera_name_2, delay):
        if not camera_name_1:
            return "Source camera name cannot be empty"
        if not camera_name_2:
            return "Destination camera name cannot be empty"
        if delay is None:
            return "Delay cannot be empty"

        try:
            # Find cameras by name
            camera_1 = Camera.query.filter_by(camera_model=camera_name_1).first()
            camera_2 = Camera.query.filter_by(camera_model=camera_name_2).first()

            if not camera_1:
                return f"Source camera '{camera_name_1}' not found"
            if not camera_2:
                return f"Destination camera '{camera_name_2}' not found"

            # Insert new connection
            new_connection = CameraConnections(
                camera_id_1=camera_1.id,
                camera_id_2=camera_2.id,
                delay=delay
            )
            db.session.add(new_connection)
            db.session.commit()
            return "Camera connection added successfully"
        except Exception as e:
            db.session.rollback()
            return str(e)

    @staticmethod
    def update_connection(camera_name_1, camera_name_2, delay):
        if not camera_name_1 or not camera_name_2 or delay is None:
            return "Invalid input"

        try:
            # Get camera IDs from names
            camera_1 = Camera.query.filter_by(camera_model=camera_name_1).first()
            camera_2 = Camera.query.filter_by(camera_model=camera_name_2).first()

            if not camera_1 or not camera_2:
                return "One or both cameras not found"

            # Check both directions for bidirectional connection
            connection = CameraConnections.query.filter(
                ((CameraConnections.camera_id_1 == camera_1.id) & (CameraConnections.camera_id_2 == camera_2.id)) |
                ((CameraConnections.camera_id_1 == camera_2.id) & (CameraConnections.camera_id_2 == camera_1.id))
            ).first()

            if not connection:
                return "Connection not found"

            # Update delay
            connection.delay = delay
            db.session.commit()

            return "Connection updated successfully"

        except Exception as e:
            db.session.rollback()
            return str(e)

    # ---- Delete the camera ----
    @staticmethod
    def delete_camera(camera_id):
        try:
            # Get camera record
            camera = Camera.query.get(camera_id)
            if not camera:
                return "Camera not found", 404

            # Store camera folder name before deletion
            camera_model = camera.camera_model  # e.g., "Camera_1"

            # Delete camera from DB
            db.session.delete(camera)
            db.session.commit()

            # --- Dynamic path setup ---
            # Go two levels up to reach project root
            project_root = os.path.abspath(
                os.path.join(os.path.dirname(__file__), "..", "..")
            )

            video_root = os.path.join(project_root, "Video_AutoBrowsing")
            cameras_path = os.path.join(video_root, "Cameras")
            camera_folder = os.path.join(cameras_path, camera_model)

            # Delete the folder if it exists
            if os.path.exists(camera_folder) and os.path.isdir(camera_folder):
                shutil.rmtree(camera_folder)
                print(f"[INFO] Deleted folder: {camera_folder}")
            else:
                print(f"[WARNING] Camera folder not found: {camera_folder}")

            return "Camera and related records deleted successfully", 200

        except Exception as e:
            db.session.rollback()
            return str(e), 500

    # ----- Delete Connection
    @staticmethod
    def delete_connection_by_names(camera_name_1, camera_name_2):
        if not camera_name_1 or not camera_name_2:
            return "Both camera names are required"

        try:
            # Find the camera IDs based on camera names
            camera1 = Camera.query.filter_by(camera_model=camera_name_1).first()
            camera2 = Camera.query.filter_by(camera_model=camera_name_2).first()

            if not camera1 or not camera2:
                return "One or both cameras not found"

            # Find the connection between these two cameras in the CameraConnections table
            connection = CameraConnections.query.filter(
                ((CameraConnections.camera_id_1 == camera1.id) & (CameraConnections.camera_id_2== camera2.id)) |
                ((CameraConnections.camera_id_2 == camera2.id) & (CameraConnections.camera_id_1 == camera1.id))
            ).first()

            if not connection:
                return "No connection found between these cameras"

            # Delete the connection
            db.session.delete(connection)
            db.session.commit()
            return "Camera connection deleted successfully"

        except Exception as e:
            db.session.rollback()
            return str(e)

   # Getting camera connections :)
    @staticmethod
    def get_camera_adjacency_matrix():
        try:
            # Create an alias for the second Camera join
            CameraAlias = aliased(Camera)

            # Query to join CameraConnections with Camera table twice
            connections = (
                db.session.query(
                    CameraConnections.camera_id_1,
                    CameraConnections.camera_id_2,
                    Camera.camera_model.label("camera_name_1"),
                    CameraAlias.camera_model.label("camera_name_2"),
                    CameraConnections.delay
                )
                .join(Camera, CameraConnections.camera_id_1 == Camera.id)
                .join(CameraAlias, CameraConnections.camera_id_2 == CameraAlias.id)  # Alias used here
                .all()
            )

            # Create adjacency matrix
            adjacency_matrix = {}

            for connection in connections:
                # Add camera_1 to the adjacency matrix
                if connection.camera_name_1 not in adjacency_matrix:
                    adjacency_matrix[connection.camera_name_1] = {}

                # Add camera_2 to the adjacency matrix
                if connection.camera_name_2 not in adjacency_matrix:
                    adjacency_matrix[connection.camera_name_2] = {}

                # Store delays (bidirectional connection)
                adjacency_matrix[connection.camera_name_1][connection.camera_name_2] = connection.delay
                adjacency_matrix[connection.camera_name_2][
                    connection.camera_name_1] = connection.delay  # Since it's bidirectional

            return jsonify({'adjacency_matrix': adjacency_matrix}), 200

        except Exception as e:
            return jsonify({'error': str(e)}), 500

    # @staticmethod
    # def get_camera_adjacency_matrix():
    #     try:
    #         # Create alias for second join
    #         CameraAlias = aliased(Camera)
    #
    #         # Query with both camera names and connection ID
    #         connections = (
    #             db.session.query(
    #                 CameraConnections.id.label("connection_id"),
    #                 Camera.camera_model.label("camera_name_1"),
    #                 CameraAlias.camera_model.label("camera_name_2"),
    #                 CameraConnections.delay
    #             )
    #             .join(Camera, CameraConnections.camera_id_1 == Camera.id)
    #             .join(CameraAlias, CameraConnections.camera_id_2 == CameraAlias.id)
    #             .all()
    #         )
    #
    #         # Build list of connection dictionaries
    #         connection_list = []
    #         for conn in connections:
    #             connection_list.append({
    #                 "camera_name_1": conn.camera_name_1,
    #                 "camera_name_2": conn.camera_name_2,
    #                 "delay": conn.delay,
    #                 "connection_id": conn.connection_id
    #             })
    #
    #         return jsonify({"connections": connection_list}), 200
    #
    #     except Exception as e:
    #         return jsonify({'error': str(e)}), 500

    # Naye nayeee Pathh daloooo
    @staticmethod
    def add_path(source, destination):
        if not source or not destination:
            return jsonify({"error": "Source and destination cannot be empty"}), 400

        try:
            source_location = Location.query.get(source)
            destination_location = Location.query.get(destination)

            if not source_location:
                return jsonify({"error": "Source location not found"}), 404

            if not destination_location:
                return jsonify({"error": "Destination location not found"}), 404


            new_path = Path(source=source, destination=destination)
            db.session.add(new_path)
            db.session.commit()
            return jsonify({"message": "Path added successfully"}), 201
        except Exception as e:
            db.session.rollback()
            return jsonify({"error": str(e)}), 500

    # Show all paths
    @staticmethod
    def all_paths():
        paths = Path.query.all()
        path_list = []

        for path in paths:
            source_location = Location.query.get(path.source)
            destination_location = Location.query.get(path.destination)

            if source_location and destination_location:
                path_name = f"{source_location.name} to {destination_location.name}"
            else:
                path_name = "Unknown Path"  # Fallback if a location is missing

            path_list.append({
                "id": path.id,
                "path": path_name
            })

        return jsonify({"paths": path_list}), 200

    # Add Camera Path jee :)
    @staticmethod
    def add_camera_path(camera_path, camera_id, sequence):
        if not camera_path or not camera_id or sequence is None:
            return jsonify({"error": "All fields are required"}), 400

        try:
            path = Path.query.get(camera_path)
            camera = Camera.query.get(camera_id)

            if not path:
                return jsonify({"error": "Path not found"}), 404

            if not camera:
                return jsonify({"error": "Camera not found"}), 404

            new_camera_path = CameraPath(camera_path=camera_path, camera_id=camera_id, sequence=sequence)
            db.session.add(new_camera_path)
            db.session.commit()
            return jsonify({"message": "Camera path added successfully", "camera_path": str(new_camera_path)}), 201
        except Exception as e:
            db.session.rollback()
            return jsonify({"error": str(e)}), 500