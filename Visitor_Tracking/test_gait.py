# import cv2
# import mediapipe as mp
# import numpy as np
# import pandas as pd
# from sklearn.neighbors import KNeighborsClassifier
# from sklearn.ensemble import RandomForestClassifier
# from sklearn.svm import SVC
# from scipy.signal import savgol_filter
# from sklearn.model_selection import train_test_split
# from sklearn.metrics import accuracy_score
# import os
#
# # Constants
# csv_file_path = r"C:\Users\affan\OneDrive\Desktop\MultiBioFuse\Backend\uploads\visitor_data\visitor_csv\gait_recognition_visitor.csv"
# test_video_path = r"C:\Users\affan\OneDrive\Desktop\MultiBioFuse\gait_recognition_project\videos\Affan_Male\video16.mp4"  # Replace with test video
#
# # Initialize MediaPipe
# mp_pose = mp.solutions.pose
#
# def calculate_angle(a, b, c):
#     a, b, c = np.array(a), np.array(b), np.array(c)
#     ba = a - b
#     bc = c - b
#     cosine_angle = np.dot(ba, bc) / (np.linalg.norm(ba) * np.linalg.norm(bc))
#     angle = np.arccos(np.clip(cosine_angle, -1.0, 1.0))
#     return np.degrees(angle)
#
# def extract_angles_from_video(video_path):
#     cap = cv2.VideoCapture(video_path)
#     angle_data = []
#
#     with mp_pose.Pose(min_detection_confidence=0.5, min_tracking_confidence=0.5) as pose:
#         while cap.isOpened():
#             ret, frame = cap.read()
#             if not ret:
#                 break
#
#             frame = cv2.resize(frame, (640, 480))
#             frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
#             results = pose.process(frame_rgb)
#
#             if results.pose_landmarks:
#                 lm = results.pose_landmarks.landmark
#
#                 def get_point(p): return [lm[p].x, lm[p].y]
#
#                 try:
#                     right_shoulder = get_point(mp_pose.PoseLandmark.RIGHT_SHOULDER)
#                     left_shoulder = get_point(mp_pose.PoseLandmark.LEFT_SHOULDER)
#                     right_hip = get_point(mp_pose.PoseLandmark.RIGHT_HIP)
#                     left_hip = get_point(mp_pose.PoseLandmark.LEFT_HIP)
#                     right_knee = get_point(mp_pose.PoseLandmark.RIGHT_KNEE)
#                     left_knee = get_point(mp_pose.PoseLandmark.LEFT_KNEE)
#                     right_ankle = get_point(mp_pose.PoseLandmark.RIGHT_ANKLE)
#                     left_ankle = get_point(mp_pose.PoseLandmark.LEFT_ANKLE)
#
#                     angles = [
#                         calculate_angle(right_shoulder, right_hip, right_knee),
#                         calculate_angle(left_shoulder, left_hip, left_knee),
#                         calculate_angle(right_hip, right_knee, right_ankle),
#                         calculate_angle(left_hip, left_knee, left_ankle),
#                         calculate_angle(left_shoulder, right_shoulder, right_hip),
#                         calculate_angle(right_shoulder, left_shoulder, left_hip),
#                     ]
#
#                     angle_data.append(angles)
#                 except:
#                     continue
#
#     cap.release()
#
#     if not angle_data:
#         print("[ERROR] No valid pose landmarks found.")
#         return None
#
#     angle_data = np.array(angle_data)
#     angle_data = savgol_filter(angle_data, window_length=5, polyorder=2, axis=0)
#     angle_data = np.clip(angle_data, 0, 180)
#
#     return angle_data
#
# def load_training_data(csv_path):
#     df = pd.read_csv(csv_path)
#     df['angles'] = df['angles'].apply(eval)  # Convert string to list
#     X = np.array(df['angles'].tolist())
#     y = df['label'].values
#     return X, y
#
# def classify_gait(test_angles, X_train, y_train):
#     if test_angles is None:
#         print("No test angles found.")
#         return "Can't detect"
#
#     # Take average embedding from test video
#     test_avg = np.mean(test_angles, axis=0).reshape(1, -1)
#
#     # Classifiers
#     knn = KNeighborsClassifier(n_neighbors=3)
#     svm = SVC(probability=True)
#     rf = RandomForestClassifier(n_estimators=100)
#
#     # Fit on full training set
#     knn.fit(X_train, y_train)
#     svm.fit(X_train, y_train)
#     rf.fit(X_train, y_train)
#
#     # You can switch the model here
#     model = knn
#     prediction = model.predict(test_avg)[0]
#     confidence = max(model.predict_proba(test_avg)[0])
#
#     if confidence < 0.6:
#         return "Can't recognize (low confidence)"
#     return prediction
#
# if __name__ == "__main__":
#     print("[INFO] Loading training data...")
#     X, y = load_training_data(csv_file_path)
#
#     print("[INFO] Extracting angles from test video...")
#     test_data = extract_angles_from_video(test_video_path)
#
#     print("[INFO] Predicting identity...")
#     result = classify_gait(test_data, X, y)
#     print(f"[RESULT] Recognized as: {result}")


#                           with one comparing technique

# import cv2
# import mediapipe as mp
# import numpy as np
# import pandas as pd
# from sklearn.neighbors import KNeighborsClassifier
# from sklearn.ensemble import RandomForestClassifier
# from sklearn.svm import SVC
# from scipy.signal import savgol_filter
#
# # === Constants ===
# csv_file_path = r"C:\Users\affan\OneDrive\Desktop\MultiBioFuse\Backend\uploads\visitor_data\visitor_csv\gait_recognition_visitor.csv"
# test_video_path = r"C:\Users\affan\OneDrive\Desktop\New folder\VID_20250328_122447.mp4"
#
# # === Initialize MediaPipe ===
# mp_pose = mp.solutions.pose
#
# def calculate_angle(a, b, c):
#     a, b, c = np.array(a), np.array(b), np.array(c)
#     ba = a - b
#     bc = c - b
#     cosine_angle = np.dot(ba, bc) / (np.linalg.norm(ba) * np.linalg.norm(bc))
#     angle = np.arccos(np.clip(cosine_angle, -1.0, 1.0))
#     return np.degrees(angle)
#
# def extract_angles_from_video(video_path):
#     cap = cv2.VideoCapture(video_path)
#     angle_data = []
#
#     with mp_pose.Pose(min_detection_confidence=0.5, min_tracking_confidence=0.5) as pose:
#         while cap.isOpened():
#             ret, frame = cap.read()
#             if not ret:
#                 break
#
#             frame = cv2.resize(frame, (640, 480))
#             frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
#             results = pose.process(frame_rgb)
#
#             if results.pose_landmarks:
#                 lm = results.pose_landmarks.landmark
#                 def get_point(p): return [lm[p].x, lm[p].y]
#
#                 try:
#                     # Original 6-angle set
#                     right_shoulder = get_point(mp_pose.PoseLandmark.RIGHT_SHOULDER)
#                     left_shoulder = get_point(mp_pose.PoseLandmark.LEFT_SHOULDER)
#                     right_hip = get_point(mp_pose.PoseLandmark.RIGHT_HIP)
#                     left_hip = get_point(mp_pose.PoseLandmark.LEFT_HIP)
#                     right_knee = get_point(mp_pose.PoseLandmark.RIGHT_KNEE)
#                     left_knee = get_point(mp_pose.PoseLandmark.LEFT_KNEE)
#                     right_ankle = get_point(mp_pose.PoseLandmark.RIGHT_ANKLE)
#                     left_ankle = get_point(mp_pose.PoseLandmark.LEFT_ANKLE)
#
#                     angles = [
#                         calculate_angle(right_shoulder, right_hip, right_knee),
#                         calculate_angle(left_shoulder, left_hip, left_knee),
#                         calculate_angle(right_hip, right_knee, right_ankle),
#                         calculate_angle(left_hip, left_knee, left_ankle),
#                         calculate_angle(left_shoulder, right_shoulder, right_hip),
#                         calculate_angle(right_shoulder, left_shoulder, left_hip),
#                     ]
#
#                     angle_data.append(angles)
#                 except:
#                     continue
#
#     cap.release()
#
#     if not angle_data:
#         print("[ERROR] No valid pose landmarks found.")
#         return None
#
#     angle_data = np.array(angle_data)
#     angle_data = savgol_filter(angle_data, window_length=5, polyorder=2, axis=0)
#     angle_data = np.clip(angle_data, 0, 180)
#
#     return angle_data
#
# def load_training_data(csv_path):
#     df = pd.read_csv(csv_path)
#     df['angles'] = df['angles'].apply(eval)  # Convert string to list
#     X = np.array(df['angles'].tolist())
#     y = df['label'].values
#     return X, y
#
# def classify_gait(test_angles, X_train, y_train):
#     if test_angles is None:
#         print("No test angles found.")
#         return "Can't detect"
#
#     test_avg = np.mean(test_angles, axis=0).reshape(1, -1)
#
#     knn = KNeighborsClassifier(n_neighbors=3)
#     svm = SVC(probability=True)
#     rf = RandomForestClassifier(n_estimators=100)
#
#     knn.fit(X_train, y_train)
#     svm.fit(X_train, y_train)
#     rf.fit(X_train, y_train)
#
#     model = knn
#     prediction = model.predict(test_avg)[0]
#     confidence = max(model.predict_proba(test_avg)[0])
#
#     if confidence < 0.6:
#         return "Can't recognize (low confidence)"
#     return prediction
#
# if __name__ == "__main__":
#     print("[INFO] Loading training data...")
#     X, y = load_training_data(csv_file_path)
#
#     print("[INFO] Extracting angles from test video...")
#     test_data = extract_angles_from_video(test_video_path)
#
#     print("[INFO] Predicting identity...")
#     result = classify_gait(test_data, X, y)
#     print(f"[RESULT] Recognized as: {result}")


import cv2
import mediapipe as mp
import numpy as np
import pandas as pd
from sklearn.neighbors import KNeighborsClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.svm import SVC
from scipy.signal import savgol_filter
import time
import shutil
from datetime import datetime
import os

mp_pose = mp.solutions.pose

# ---------- Utility to Calculate Angle Between Joints ----------
def calculate_angle(a, b, c):
    a, b, c = np.array(a), np.array(b), np.array(c)
    ba = a - b
    bc = c - b
    cosine_angle = np.dot(ba, bc) / (np.linalg.norm(ba) * np.linalg.norm(bc))
    angle = np.arccos(np.clip(cosine_angle, -1.0, 1.0))
    return np.degrees(angle)

# ---------- Extract Angles from Pose in Video ----------
def extract_angles_from_video(video_path):
    cap = cv2.VideoCapture(video_path)
    angle_data = []

    with mp_pose.Pose(min_detection_confidence=0.5, min_tracking_confidence=0.5) as pose:
        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break

            frame = cv2.resize(frame, (640, 480))
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            results = pose.process(frame_rgb)

            if results.pose_landmarks:
                lm = results.pose_landmarks.landmark
                def get_point(p): return [lm[p].x, lm[p].y]

                try:
                    right_shoulder = get_point(mp_pose.PoseLandmark.RIGHT_SHOULDER)
                    left_shoulder = get_point(mp_pose.PoseLandmark.LEFT_SHOULDER)
                    right_hip = get_point(mp_pose.PoseLandmark.RIGHT_HIP)
                    left_hip = get_point(mp_pose.PoseLandmark.LEFT_HIP)
                    right_knee = get_point(mp_pose.PoseLandmark.RIGHT_KNEE)
                    left_knee = get_point(mp_pose.PoseLandmark.LEFT_KNEE)
                    right_ankle = get_point(mp_pose.PoseLandmark.RIGHT_ANKLE)
                    left_ankle = get_point(mp_pose.PoseLandmark.LEFT_ANKLE)

                    angles = [
                        calculate_angle(right_shoulder, right_hip, right_knee),
                        calculate_angle(left_shoulder, left_hip, left_knee),
                        calculate_angle(right_hip, right_knee, right_ankle),
                        calculate_angle(left_hip, left_knee, left_ankle),
                        calculate_angle(left_shoulder, right_shoulder, right_hip),
                        calculate_angle(right_shoulder, left_shoulder, left_hip),
                    ]
                    angle_data.append(angles)
                except:
                    continue

    cap.release()

    if not angle_data:
        return None

    angle_data = np.array(angle_data)
    angle_data = savgol_filter(angle_data, window_length=5, polyorder=2, axis=0)
    angle_data = np.clip(angle_data, 0, 180)

    return angle_data


VISUALIZATION_FRAMES_PATH = os.path.join("uploads", "visitor_data", "gait_frame_previews")
os.makedirs(VISUALIZATION_FRAMES_PATH, exist_ok=True)

def save_annotated_frames(video_path, visitor_id, max_gait_frames=4, max_face_frames=4):
    VISUALIZATION_FRAMES_PATH = os.path.join("uploads", "visitor_data", "gait_frame_previews")
    os.makedirs(VISUALIZATION_FRAMES_PATH, exist_ok=True)

    # Clear previous frames for this visitor
    for f in os.listdir(VISUALIZATION_FRAMES_PATH):
        if f.startswith(f"visitor_{visitor_id}_"):
            os.remove(os.path.join(VISUALIZATION_FRAMES_PATH, f))

    cap = cv2.VideoCapture(video_path)
    frame_count = 0
    gait_saved = 0
    face_saved = 0

    mp_drawing = mp.solutions.drawing_utils
    pose = mp_pose.Pose(
        static_image_mode=False,
        min_detection_confidence=0.5,
        min_tracking_confidence=0.5
    )

    while cap.isOpened() and (gait_saved < max_gait_frames or face_saved < max_face_frames):
        ret, frame = cap.read()
        if not ret:
            break
        frame_count += 1

        # Process every 3rd frame
        if frame_count % 3 != 0:
            continue

        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = pose.process(frame_rgb)

        if not results.pose_landmarks:
            continue

        height, width, _ = frame.shape
        lm = results.pose_landmarks.landmark

        xs = [int(l.x * width) for l in lm]
        ys = [int(l.y * height) for l in lm]
        min_x, max_x = min(xs), max(xs)
        min_y, max_y = min(ys), max(ys)
        bbox_width = max_x - min_x
        bbox_height = max_y - min_y

        # 🟦 Gait Frame with Annotations
        if gait_saved < max_gait_frames and bbox_width > 100 and bbox_height > 100:
            annotated_frame = frame.copy()

            mp_drawing.draw_landmarks(
                annotated_frame,
                results.pose_landmarks,
                mp_pose.POSE_CONNECTIONS,
                landmark_drawing_spec=mp_drawing.DrawingSpec(color=(245, 117, 66), thickness=2, circle_radius=3),
                connection_drawing_spec=mp_drawing.DrawingSpec(color=(245, 66, 230), thickness=1, circle_radius=2)
            )

            # Bounding box padding
            pad = 30
            x1 = max(min_x - pad, 0)
            y1 = max(min_y - pad, 0)
            x2 = min(max_x + pad, width)
            y2 = min(max_y + pad, height)

            # Draw yellow bounding box
            cv2.rectangle(annotated_frame, (x1, y1), (x2, y2), (0, 255, 255), 3)

            crop = annotated_frame[y1:y2, x1:x2]
            filename = f"visitor_{visitor_id}_{gait_saved + 1}.jpg"
            save_path = os.path.join(VISUALIZATION_FRAMES_PATH, filename)
            cv2.imwrite(save_path, crop)
            gait_saved += 1

        # 🟥 Face Frame with Clean Crop
        elif face_saved < max_face_frames:
            try:
                nose = lm[mp_pose.PoseLandmark.NOSE]
                left_ear = lm[mp_pose.PoseLandmark.LEFT_EAR]
                right_ear = lm[mp_pose.PoseLandmark.RIGHT_EAR]

                fx = [int(nose.x * width), int(left_ear.x * width), int(right_ear.x * width)]
                fy = [int(nose.y * height), int(left_ear.y * height), int(right_ear.y * height)]

                min_fx, max_fx = max(0, min(fx) - 40), min(width, max(fx) + 40)
                min_fy, max_fy = max(0, min(fy) - 40), min(height, max(fy) + 40)

                face_crop = frame[min_fy:max_fy, min_fx:max_fx]

                if face_crop.shape[0] < 80 or face_crop.shape[1] < 80:
                    continue

                filename = f"visitor_{visitor_id}_{max_gait_frames + face_saved + 1}.jpg"
                save_path = os.path.join(VISUALIZATION_FRAMES_PATH, filename)
                cv2.imwrite(save_path, face_crop)
                face_saved += 1

            except Exception as e:
                print(f"⚠️ Face frame skipped: {str(e)}")
                continue

    cap.release()
# ---------- Load Training Data ----------
def load_training_data(csv_path):
    df = pd.read_csv(csv_path)
    df['angles'] = df['angles'].apply(eval)  # Convert string to list
    X = np.array(df['angles'].tolist())
    y = df['label'].values
    ids = df['user_id'].values
    return X, y, ids, df  # Keep df for mapping label to user_id

# ---------- Classify Test Video Gait ----------
def classify_gait(test_video_path, training_csv_path, confidence_threshold=0.6):
    try:
        X_train, y_train, user_ids, df = load_training_data(training_csv_path)
        test_angles = extract_angles_from_video(test_video_path)

        if test_angles is None:
            return {"recognized_faces": []}

        test_avg = np.mean(test_angles, axis=0).reshape(1, -1)

        # Initialize classifier
        model = KNeighborsClassifier(n_neighbors=3)
        model.fit(X_train, y_train)

        prediction = model.predict(test_avg)[0]
        confidence = max(model.predict_proba(test_avg)[0])

        if confidence < confidence_threshold:
            return {
                "recognized_faces": [
                    {
                        "label": "Unknown",
                        "confidence": float(confidence),
                        "user_id": None
                    }
                ]
            }

        # Get the corresponding user_id
        user_row = df[df['label'] == prediction].iloc[0]
        user_id = user_row['user_id']

        return {
            "recognized_faces": [
                {
                    "label": prediction,
                    "confidence": float(confidence),
                    "user_id": int(user_id)
                }
            ]
        }

    except Exception as e:
        return {"recognized_faces": [], "error": str(e)}


