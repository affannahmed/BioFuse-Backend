# # # import os
# # # import csv
# # # import json
# # # import numpy as np
# # #
# # # # CSV file path
# # # CSV_PATH = r"C:\Users\affan\OneDrive\Desktop\MultiBioFuse\Backend\uploads\visitor_csv\visitor_embeddings.csv"
# # #
# # #
# # # def insert_better_unknown_data():
# # #     """Inserts multiple diverse 'Unknown' embeddings into the CSV for better classification."""
# # #     if not os.path.exists(CSV_PATH):  # Create file if it doesn't exist
# # #         with open(CSV_PATH, mode='w', newline='') as file:
# # #             writer = csv.writer(file)
# # #             writer.writerow(["user_id", "embeddings", "label"])  # Write header
# # #
# # #     try:
# # #         with open(CSV_PATH, mode='r', newline='') as file:
# # #             reader = csv.reader(file)
# # #             rows = list(reader)
# # #
# # #             # If "Unknown" entries already exist, don't add them again
# # #             if any(row[2] == "Unknown" for row in rows[1:]):
# # #                 print("Unknown embeddings already exist. Skipping...")
# # #                 return
# # #     except (FileNotFoundError, IndexError):
# # #         pass  # If file is empty or missing, continue
# # #
# # #     with open(CSV_PATH, mode='a', newline='') as file:
# # #         writer = csv.writer(file)
# # #
# # #         for _ in range(5):  # Add 5 randomized unknown embeddings
# # #             random_embedding = np.random.uniform(-1, 1, 128).tolist()  # Random values between -1 and 1
# # #             writer.writerow([-1, json.dumps([random_embedding]), "Unknown"])
# # #
# # #     print("Added multiple diverse 'Unknown' embeddings.")
# # #
# # #
# # # if __name__ == "__main__":
# # #     insert_better_unknown_data()
# # # import importlib
# # #
# # # packages = [
# # #     "flask", "flask_cors", "sqlalchemy", "pandas", "numpy", "cv2",
# # #     "mysql.connector", "insightface", "mediapipe", "face_recognition", "werkzeug"
# # # ]
# # #
# # # for package in packages:
# # #     try:
# # #         importlib.import_module(package)
# # #         print(f"{package} is installed ✅")
# # #     except ImportError:
# # #         print(f"{package} is NOT installed ❌")
# #
# # import csv
# #
# # def clear_csv_file(file_path):
# #     with open(file_path, 'w', newline='') as file:
# #         writer = csv.writer(file)
# #         writer.writerow(["user_id", "embedding", "label"])  # Writing column names
# #
# # # Specify the path
# # csv_file_path = r"C:\Users\affan\OneDrive\Desktop\MultiBioFuse\Backend\uploads\visitor_data\visitor_csv\visitor_embeddings.csv"
# #
# # # Clear the CSV
# # clear_csv_file(csv_file_path)
# #
# # print("CSV file cleared successfully.")
# # #
# # import csv
# #
# # def clear_csv_file(file_path):
# #     with open(file_path, 'w', newline='') as file:
# #         writer = csv.writer(file)
# #         writer.writerow(["user_id", "angles", "label"])  # Writing column names
# #
# # # Specify the path
# # csv_file_path = r"C:\Users\affan\OneDrive\Desktop\MultiBioFuse\Backend\uploads\visitor_data\visitor_csv\gait_recognition_visitor.csv"
# #
# # # Clear the CSV
# # clear_csv_file(csv_file_path)
# #
# # print("CSV file cleared successfully for gait recognition.")
# # generate_users.py
# from werkzeug.security import generate_password_hash
#
# users = [
#     ("Dr Hassan", "drhassan@biofuse.com", "224488"),
#     ("Shahid Jamil", "shahid@biofuse.com", "224488"),
#     ("Sir Zahid", "zahid@biofuse.com", "224488"),
#     ("Umer Farooq", "umer@biofuse.com", "224488")
# ]
#
# for name, email, pwd in users:
#     hashed = generate_password_hash(pwd)
#     print(f"('{name}', '{email}', '{hashed}')")
#
#
import os
#
# JSON-like list of camera data
camera_data = [
    {"camera_model": "GateCam-1", "id": 1, "location": "Main Gate"},
    {"camera_model": "GroundCam-1", "id": 2, "location": "Play Ground"},
    {"camera_model": "EntranceCam-1", "id": 3, "location": "Main Entrance"},
    {"camera_model": "MosqueCam-1", "id": 4, "location": "Mosque"},
    {"camera_model": "CafeCam-1", "id": 5, "location": "Student Cafeteria"},
    {"camera_model": "RecStairsCam-1", "id": 6, "location": "Reception Stairs"},
    {"camera_model": "DirOfficeCam-1", "id": 7, "location": "Director’s Office"},
    {"camera_model": "DataCam-1", "id": 8, "location": "Data Cell"},
    {"camera_model": "ServerCam-1", "id": 9, "location": "Server Room"},
    {"camera_model": "ResLabCam-1", "id": 10, "location": "Research Lab"},
    {"camera_model": "LibraryCam-1", "id": 11, "location": "Library"},
    {"camera_model": "RoundStairsCam-1", "id": 12, "location": "Round Stairs"},
    {"camera_model": "AdminCam-1", "id": 13, "location": "Admin Office"},
    {"camera_model": "AdmStairsCam-1", "id": 14, "location": "Admin Stairs"},
    {"camera_model": "ShopCam-1", "id": 15, "location": "Stationary Shop"},
    {"camera_model": "FlipRoomCam-1", "id": 16, "location": "Flip Room"},
    {"camera_model": "AdmBasementCam-1", "id": 17, "location": "Admin Basement Stairs"},
    {"camera_model": "AiResearch Cam-1", "id": 18, "location": "AI Research Lab"},
    {"camera_model": "ProjectAi Cam-1", "id": 19, "location": "AI Project Deployment"},
    {"camera_model": "ML-Cam-1", "id": 20, "location": "Machine Learning Wing"},
    {"camera_model": "DL-Cam-1", "id": 21, "location": "Deep Learning Unit"},
    {"camera_model": "CV-Cam-1", "id": 22, "location": "Computer Vision Hub"},
    {"camera_model": "AiEthichs-Cam1", "id": 23, "location": "AI Ethics & Policy Section"},
    {"camera_model": "AI-Model-Cam1", "id": 24, "location": "AI Model Testing & Evaluation"}
]

# Base path where folders should be created
base_path = r"C:\Users\affan\OneDrive\Desktop\MultiBioFuse\Video_AutoBrowsing\Cameras"

# Create folders
for cam in camera_data:
    folder_name = cam["camera_model"]
    folder_path = os.path.join(base_path, folder_name)
    os.makedirs(folder_path, exist_ok=True)

print("All camera folders created successfully.")
#
# #
import os
import shutil

# Set your base path
base_path = r"C:\Users\affan\OneDrive\Desktop\MultiBioFuse\Video_AutoBrowsing"

# Paths
people_videos_path = os.path.join(base_path, "all_person_videos")
cameras_path = os.path.join(base_path, "cameras")

# List all videos
videos = [file for file in os.listdir(people_videos_path) if file.endswith((".mp4", ".avi", ".mov"))]

# List all camera folders
camera_folders = [os.path.join(cameras_path, cam) for cam in os.listdir(cameras_path) if os.path.isdir(os.path.join(cameras_path, cam))]

# Copy each video to each camera folder
for cam_folder in camera_folders:
    for video in videos:
        src = os.path.join(people_videos_path, video)
        dst = os.path.join(cam_folder, video)

        # Only copy if not already there
        if not os.path.exists(dst):
            shutil.copy(src, dst)
            print(f"Copied {video} to {cam_folder}")
        else:
            print(f"Skipped (already exists): {video} in {cam_folder}")

print("✅ Done copying all videos to all camera folders.")
