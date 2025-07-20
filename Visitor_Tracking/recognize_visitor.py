#
# import cv2
# import numpy as np
# import pandas as pd
# import json
# import os
# from scipy.spatial.distance import cosine
# import mediapipe as mp
# from insightface.app import FaceAnalysis
#
# CSV_PATH = r"C:\Users\affan\OneDrive\Desktop\MultiBioFuse\Backend\uploads\visitor_data\visitor_csv\visitor_embeddings.csv"
#
# # Initialize InsightFace (CPU)
# face_app = FaceAnalysis(providers=['CPUExecutionProvider'])
# face_app.prepare(ctx_id=0, det_size=(224, 224))
#
# # Load stored embeddings and normalize
# def load_embeddings():
#     df = pd.read_csv(CSV_PATH)
#     embeddings = []
#     for _, row in df.iterrows():
#         try:
#             emb = np.array(json.loads(row["embedding"]), dtype=np.float32)
#             emb /= np.linalg.norm(emb)
#             embeddings.append({
#                 "user_id": row["user_id"],
#                 "label": row["label"],
#                 "embedding": emb
#             })
#         except Exception as e:
#             print(f"Skipping invalid embedding: {e}")
#     return embeddings
#
# VISITORS = load_embeddings()
#
# # Crop face helper
# def crop_face(image, bbox, margin=20):
#     x, y, w, h = map(int, bbox[:4])
#     x1 = max(x - margin, 0)
#     y1 = max(y - margin, 0)
#     x2 = min(x + w + margin, image.shape[1])
#     y2 = min(y + h + margin, image.shape[0])
#     return image[y1:y2, x1:x2]
#
# # Recognize using optimized cosine similarity
# def recognize_face_embeddings(face_embedding, visitor_embeddings, threshold=0.70):
#     visitor_matrix = np.array([v['embedding'] for v in visitor_embeddings])
#     similarities = np.dot(visitor_matrix, face_embedding)
#     best_index = np.argmax(similarities)
#     best_score = similarities[best_index]
#
#     if best_score > threshold:
#         best_visitor = visitor_embeddings[best_index]
#         return {
#             "user_id": best_visitor["user_id"],
#             "label": best_visitor["label"],
#             "confidence": round(float(best_score), 2)
#         }
#     return {"user_id": None, "label": "Unknown", "confidence": 0.0}
#
# # Compress and resize video
# def compress_video(input_path, scale=0.5, fps_limit=10):
#     cap = cv2.VideoCapture(input_path)
#     frames = []
#     frame_rate = cap.get(cv2.CAP_PROP_FPS)
#     frame_interval = max(1, int(frame_rate / fps_limit))
#
#     count = 0
#     while cap.isOpened():
#         ret, frame = cap.read()
#         if not ret:
#             break
#
#         if count % frame_interval == 0:
#             resized = cv2.resize(frame, (0, 0), fx=scale, fy=scale)
#             frames.append(resized)
#         count += 1
#
#     cap.release()
#     return frames
#
# # Process only useful frames
# def process_video_from_api(video_path):
#     visitor_embeddings = load_embeddings()
#     if not os.path.exists(video_path):
#         return {"error": "Video not found"}
#
#     # Step 1: Compress
#     frames = compress_video(video_path)
#
#     recognized_faces_all = []
#     for frame in frames:
#         results = face_app.get(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
#         if not results:
#             continue
#
#         for face in results:
#             cropped = crop_face(frame, face.bbox)
#             embedding = np.array(face.embedding, dtype=np.float32)
#             embedding /= np.linalg.norm(embedding)
#
#
#             result = recognize_face_embeddings(embedding, visitor_embeddings)
#
#             recognized_faces_all.append(result)
#
#     # Aggregate results
#     final = {}
#     for face in recognized_faces_all:
#         label = face["label"]
#         if label not in final or final[label]["confidence"] < face["confidence"]:
#             final[label] = face
#
#     return {
#         "recognized_faces": list(final.values())
#     }
import cv2
import numpy as np
import pandas as pd
import json
import os
from scipy.spatial.distance import cosine
from insightface.app import FaceAnalysis
from Backend.Controllers.GuardController import GuardController

CSV_PATH = r"C:\Users\affan\OneDrive\Desktop\MultiBioFuse\Backend\uploads\visitor_data\visitor_csv\visitor_embeddings.csv"

# Load stored embeddings

def load_embeddings():
    df = pd.read_csv(CSV_PATH)
    visitors = []

    for _, row in df.iterrows():
        try:
            embedding = json.loads(row["embedding"])
            embedding = np.array(embedding, dtype=np.float32).flatten()
            embedding /= np.linalg.norm(embedding)
            visitors.append({
                "user_id": row["user_id"],
                "label": row["label"],
                "embedding": embedding
            })
        except Exception as e:
            print(f"Skipping invalid entry {row.get('user_id', 'Unknown')}: {str(e)}")

    return visitors


# VISITORS = load_embeddings()
# print(f"✅ Loaded {len(VISITORS)} visitors' embeddings")

# Initialize InsightFace for better detection
face_app = FaceAnalysis(name='buffalo_l', providers=['CPUExecutionProvider'])
face_app.prepare(ctx_id=0)
print("✅ InsightFace initialized for detection and recognition")


# Function to crop faces, especially distant ones
def custom_crop_face(frame, bbox, min_size=(100, 100)):
    x1, y1, x2, y2 = bbox.astype(int)

    # Ensure bounding box is within frame boundaries
    h, w = frame.shape[:2]
    x1, y1 = max(0, x1), max(0, y1)
    x2, y2 = min(w, x2), min(h, y2)

    # Crop the face region from the frame
    face_crop = frame[y1:y2, x1:x2]

    # Resize the face if necessary (making sure distant faces are scaled)
    face_height, face_width = face_crop.shape[:2]
    if face_height < min_size[0] or face_width < min_size[1]:
        scale_x = min_size[1] / face_width
        scale_y = min_size[0] / face_height
        face_crop = cv2.resize(face_crop, None, fx=scale_x, fy=scale_y, interpolation=cv2.INTER_CUBIC)

    return face_crop


# Improve lighting conditions using histogram equalization or CLAHE
def improve_lighting(frame):
    # Convert to grayscale
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    # Apply CLAHE (Contrast Limited Adaptive Histogram Equalization)
    clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8, 8))
    enhanced_frame = clahe.apply(gray)

    # Convert back to BGR
    enhanced_frame = cv2.cvtColor(enhanced_frame, cv2.COLOR_GRAY2BGR)
    return enhanced_frame


# Recognize faces using InsightFace
def recognize_faces(frame):
    if frame is None or frame.size == 0:
        print("❌ Empty frame received.")
        return []

    VISITORS = load_embeddings()
    # Enhance lighting and image quality
    frame = improve_lighting(frame)

    faces = face_app.get(frame)
    if not faces:
        print("⚠️ No faces detected by InsightFace.")
        return []

    recognized_faces = []

    for face in faces:
        bbox = face.bbox.astype(int)
        x1, y1, x2, y2 = bbox

        # Crop and resize the face if necessary using the custom function
        face_crop = custom_crop_face(frame, bbox)
        if face_crop is None or face_crop.size == 0:
            print("❌ Empty cropped face.")
            continue

        # Extract embeddings from the cropped face
        embedding = GuardController.extract_embeddings(face_crop)
        if embedding is None:
            print("❌ Failed to extract embeddings.")
            continue

        embedding = np.array(embedding, dtype=np.float32).flatten()
        embedding /= np.linalg.norm(embedding)

        # Compare with stored embeddings
        for visitor in VISITORS:
            stored_embedding = visitor["embedding"]
            similarity = 1 - cosine(embedding, stored_embedding)
            if similarity > 0.4:  # Adjust threshold if needed
                recognized_faces.append({
                    "user_id": visitor["user_id"],
                    "label": visitor["label"],
                    "confidence": round(similarity, 2)
                })
                print(f"✅ Match found: {visitor['label']} ({similarity:.2f})")

    return recognized_faces


# # Function to process video
# def process_video_from_api(video_path):
#     if not os.path.exists(video_path):
#         return {"error": "Video file not found"}
#
#     cap = cv2.VideoCapture(video_path)
#     recognized_people = []
#     frame_count = 0
#
#     print("📹 Starting video processing...")
#     while cap.isOpened():
#         ret, frame = cap.read()
#         if not ret:
#             break
#
#         if frame_count % 10 == 0:
#             print(f"🧠 Processing frame {frame_count}...")
#             faces = recognize_faces(frame)
#             recognized_people.extend(faces)
#
#         frame_count += 1
#
#     cap.release()
#     print("✅ Video processing completed.")
#
#     # Aggregate best match per person
#     final_results = {}
#     for face in recognized_people:
#         label = face["label"]
#         confidence = face["confidence"]
#         user_id = face["user_id"]
#
#         if label not in final_results or final_results[label]["confidence"] < confidence:
#             final_results[label] = {"confidence": confidence, "user_id": user_id}
#
#     return {
#         "recognized_faces": [
#             {"label": label, "confidence": float(data["confidence"]), "user_id": data["user_id"]}
#             for label, data in final_results.items()
#         ]
#     }
# early stopping and skipping frames
def process_video_from_api(video_path):
    if not os.path.exists(video_path):
        return {"error": "Video file not found"}

    cap = cv2.VideoCapture(video_path)
    recognized_people = []
    frame_count = 0
    frame_skip_interval = 15
    early_stop_threshold = 0.6  # Stop if a match exceeds this confidence
    found_match = False

    print("📹 Starting video processing...")
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        if frame_count % frame_skip_interval == 0:
            print(f"🧠 Processing frame {frame_count}...")
            faces = recognize_faces(frame)
            recognized_people.extend(faces)

            # Check for early stopping condition
            for face in faces:
                if face["confidence"] >= early_stop_threshold:
                    print(f"🛑 Early stopping: confident match found ({face['label']} - {face['confidence']})")
                    found_match = True
                    break

            if found_match:
                break

        frame_count += 1

    cap.release()
    print("✅ Video processing completed.")

    # Aggregate best match per person
    final_results = {}
    for face in recognized_people:
        label = face["label"]
        confidence = face["confidence"]
        user_id = face["user_id"]

        if label not in final_results or final_results[label]["confidence"] < confidence:
            final_results[label] = {"confidence": confidence, "user_id": user_id}

    return {
        "recognized_faces": [
            {"label": label, "confidence": float(data["confidence"]), "user_id": data["user_id"]}
            for label, data in final_results.items()
        ]
    }