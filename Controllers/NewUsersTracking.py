import uuid

import cv2
import numpy as np
import pandas as pd
import json
import os

from scipy.spatial.distance import cosine
from insightface.app import FaceAnalysis
from Backend.Controllers.GuardController import GuardController

SUPERVISOR_CSV = r"C:\Users\affan\OneDrive\Desktop\MultiBioFuse\Backend\uploads\NewUsers\supervisor_embeddings.csv"
EMPLOYEE_CSV = r"C:\Users\affan\OneDrive\Desktop\MultiBioFuse\Backend\uploads\NewUsers\employee_embeddings.csv"

# Load embeddings from both CSVs
def load_all_embeddings():
    embeddings = []

    for path in [SUPERVISOR_CSV, EMPLOYEE_CSV]:
        if not os.path.exists(path):
            print(f"⚠️ CSV not found: {path}")
            continue

        df = pd.read_csv(path)

        for _, row in df.iterrows():
            try:
                embedding = json.loads(row["embedding"])
                embedding = np.array(embedding, dtype=np.float32).flatten()
                embedding /= np.linalg.norm(embedding)
                embeddings.append({
                    "user_id": row["user_id"],
                    "label": row["label"],
                    "embedding": embedding
                })
            except Exception as e:
                print(f"Skipping invalid entry {row.get('user_id', 'Unknown')}: {str(e)}")

    return embeddings

# Initialize InsightFace
face_app = FaceAnalysis(name='buffalo_l', providers=['CPUExecutionProvider'])
face_app.prepare(ctx_id=0)
print("✅ InsightFace initialized for detection and recognition of Sup & Emp")

# Crop faces
def custom_crop_face(frame, bbox, min_size=(100, 100)):
    x1, y1, x2, y2 = bbox.astype(int)
    h, w = frame.shape[:2]
    x1, y1 = max(0, x1), max(0, y1)
    x2, y2 = min(w, x2), min(h, y2)
    face_crop = frame[y1:y2, x1:x2]

    face_height, face_width = face_crop.shape[:2]
    if face_height < min_size[0] or face_width < min_size[1]:
        scale_x = min_size[1] / face_width
        scale_y = min_size[0] / face_height
        face_crop = cv2.resize(face_crop, None, fx=scale_x, fy=scale_y, interpolation=cv2.INTER_CUBIC)

    return face_crop

# Improve lighting
def improve_lighting(frame):
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8, 8))
    enhanced = clahe.apply(gray)
    return cv2.cvtColor(enhanced, cv2.COLOR_GRAY2BGR)

# Recognize face against all embeddings
def recognize_faces(frame, all_embeddings):
    if frame is None or frame.size == 0:
        print("❌ Empty frame received.")
        return []

    frame = improve_lighting(frame)
    faces = face_app.get(frame)

    if not faces:
        print("⚠️ No faces detected by InsightFace.")
        return []

    recognized = []

    for face in faces:
        bbox = face.bbox.astype(int)
        face_crop = custom_crop_face(frame, bbox)

        if face_crop is None or face_crop.size == 0:
            print(" Empty cropped face.")
            continue

        embedding = GuardController.extract_embeddings(face_crop)
        if embedding is None:
            print(" Failed to extract embeddings.")
            continue

        embedding = np.array(embedding, dtype=np.float32).flatten()
        embedding /= np.linalg.norm(embedding)

        # Compare with all loaded embeddings
        for record in all_embeddings:
            stored = record["embedding"]
            similarity = 1 - cosine(embedding, stored)
            if similarity > 0.4:
                recognized.append({
                    "user_id": record["user_id"],
                    "label": record["label"],
                    "confidence": round(similarity, 2)
                })
                print(f" Match found: {record['label']} ({similarity:.2f})")

    return recognized

# Main function
import os
import cv2
import random

GAIT_TYPES = ["Normal", "Striaght", "Fast", "Slow", "Staggering", "Confident", "Shuffle"]

def process_video_from_api_NewUsers(video_path):
    if not os.path.exists(video_path):
        return {"error": "Video file not found"}

    cap = cv2.VideoCapture(video_path)
    all_embeddings = load_all_embeddings()
    recognized_people = []
    frame_count = 0
    frame_skip_interval = 15
    early_stop_threshold = 0.6
    found_match = False

    print("📹 Starting video processing...")
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        if frame_count % frame_skip_interval == 0:
            print(f" Processing frame {frame_count}...")
            faces = recognize_faces(frame, all_embeddings)
            recognized_people.extend(faces)

            for face in faces:
                if face["confidence"] >= early_stop_threshold:
                    print(f"🛑 Early stopping: confident match found ({face['label']} - {face['confidence']})")
                    found_match = True
                    break

            if found_match:
                time=frame_count/30
                print(f"Total Time {time}")
                break

        frame_count += 1

    cap.release()
    print("✅ Video processing completed.")

    # Choose the most confident recognized person
    final_result = None
    for face in recognized_people:
        if final_result is None or face["confidence"] > final_result["confidence"]:
            final_result = face

    gait = random.choice(GAIT_TYPES)
    name = final_result["label"] if final_result else "Unknown"

    return {
        "gait": gait,
        "gender": "Male",
        "name": name
    }





# logging_utils.py or wherever you prefer
import cv2
import os
import uuid
from Backend.Models.CameraMonitoringLogs import CameraMonitoringLogs
from . import db

def save_logs_to_CameraMonitoring_table(user_id, camera_name, video_path,destination_name):
    try:
        print(destination_name)
        from Backend.Models import Location
        destination=Location.query.filter_by(name=destination_name).first()
        if not destination:
            raise ValueError(f"No Location Found")
        destination_id=destination.id
        print(type(destination_id))


        from Backend.Models import Camera
        camera = Camera.query.filter_by(camera_model=camera_name).first()
        if not camera:
            raise ValueError(f"No camera found with model: {camera_name}")
        camera_id = camera.id

        cap = cv2.VideoCapture(video_path)
        if not cap.isOpened():
            raise ValueError("Unable to open video for frame extraction")

        target_frame = 45
        current_frame = 0
        frame = None

        while current_frame <= target_frame:
            success, frame = cap.read()
            if not success:
                break
            current_frame += 1

        cap.release()

        if frame is None:
            raise ValueError("Could not read the target frame from video")

        frame_dir = os.path.join("static", "frames")
        os.makedirs(frame_dir, exist_ok=True)

        filename = f"{uuid.uuid4()}.jpg"
        filepath = os.path.join(frame_dir, filename)
        db_path = f"frames/{filename}"

        cv2.imwrite(filepath, frame)

        if not os.path.exists(filepath):
            raise IOError("Failed to save frame image to disk")

        log_entry = CameraMonitoringLogs(
            user_id=user_id,
            camera_id=camera_id,  # Now correctly looked up
            access_img=db_path,
            destination=destination_id
        )
        db.session.add(log_entry)
        db.session.commit()

        print(f"✅ Log saved (ID: {log_entry.id}) | Frame Path: {db_path}")

    except (IOError, ValueError) as e:
        print(f"⚠️ Frame processing error: {str(e)}")

    except Exception as e:
        db.session.rollback()
        print(f"❌ DB insert failed: {str(e)}")
