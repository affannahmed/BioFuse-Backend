# import cv2
# import mediapipe as mp
# import numpy as np
# import pandas as pd
# import os
# from scipy.signal import savgol_filter
#
# # Output CSV path
# csv_file_path = r"C:\Users\affan\OneDrive\Desktop\MultiBioFuse\Backend\uploads\visitor_data\visitor_csv\gait_recognition_visitor.csv"
# label = "Sir Hassan"
# user_id = 3
#
# # Initialize MediaPipe
# mp_drawing = mp.solutions.drawing_utils
# mp_pose = mp.solutions.pose
#
# def calculate_angle(a, b, c):
#     """Calculate angle between 3 points."""
#     a, b, c = np.array(a), np.array(b), np.array(c)
#     ba = a - b
#     bc = c - b
#     cosine_angle = np.dot(ba, bc) / (np.linalg.norm(ba) * np.linalg.norm(bc))
#     angle = np.arccos(np.clip(cosine_angle, -1.0, 1.0))
#     return np.degrees(angle)
#
# def process_video(video_path):
#     cap = cv2.VideoCapture(video_path)
#     angle_data = []
#
#     with mp_pose.Pose(min_detection_confidence=0.5, min_tracking_confidence=0.5) as pose:
#         while cap.isOpened():
#             ret, frame = cap.read()
#             if not ret:
#                 break
#
#             # Resize & convert color
#             frame = cv2.resize(frame, (640, 480))
#             frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
#
#             # Pose estimation
#             results = pose.process(frame_rgb)
#
#             if results.pose_landmarks:
#                 lm = results.pose_landmarks.landmark
#
#                 # Get coordinates
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
#                     # Calculate angles
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
#
#                 except:
#                     continue
#
#     cap.release()
#
#     if not angle_data:
#         print("No valid body landmarks detected.")
#         return
#
#     # Smoothing & Normalization
#     angle_data = np.array(angle_data)
#     angle_data = savgol_filter(angle_data, window_length=5, polyorder=2, axis=0)  # smoothing
#     angle_data = np.clip(angle_data, 0, 180).tolist()  # normalization to 0–180 degrees
#
#     # Save to CSV
#     df = pd.DataFrame({
#         "user_id": [user_id] * len(angle_data),
#         "angles": [angle_list for angle_list in angle_data],
#         "label": [label] * len(angle_data)
#     })
#
#     os.makedirs(os.path.dirname(csv_file_path), exist_ok=True)
#
#     if os.path.exists(csv_file_path):
#         df.to_csv(csv_file_path, mode='a', header=False, index=False)
#     else:
#         df.to_csv(csv_file_path, index=False)
#
#     print(f"[INFO] Successfully processed and saved angles to CSV.")
#
#
# video=r"C:\Users\affan\OneDrive\Desktop\New folder\VID_20250328_122619.mp4"
#
# # Example usage
# if __name__ == "__main__":
#     process_video(video)  # Replace with your input video path
import cv2
import mediapipe as mp
import numpy as np
import pandas as pd
import os
from scipy.signal import savgol_filter

BASE_CSV_PATH = r"C:\Users\affan\OneDrive\Desktop\MultiBioFuse\Backend\uploads\visitor_data\visitor_csv"

# Initialize MediaPipe
mp_drawing = mp.solutions.drawing_utils
mp_pose = mp.solutions.pose

def calculate_angle(a, b, c):
    a, b, c = np.array(a), np.array(b), np.array(c)
    ba = a - b
    bc = c - b
    cosine_angle = np.dot(ba, bc) / (np.linalg.norm(ba) * np.linalg.norm(bc))
    angle = np.arccos(np.clip(cosine_angle, -1.0, 1.0))
    return np.degrees(angle)

def process_video_for_visitor(video_path, user_id, label):
    csv_file_path = os.path.join(BASE_CSV_PATH, "gait_recognition_visitor.csv")
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
        print("No valid body landmarks detected.")
        return

    angle_data = np.array(angle_data)
    angle_data = savgol_filter(angle_data, window_length=5, polyorder=2, axis=0)
    angle_data = np.clip(angle_data, 0, 180).tolist()

    df = pd.DataFrame({
        "user_id": [user_id] * len(angle_data),
        "angles": [angle_list for angle_list in angle_data],
        "label": [label] * len(angle_data)
    })

    os.makedirs(os.path.dirname(csv_file_path), exist_ok=True)

    if os.path.exists(csv_file_path):
        df.to_csv(csv_file_path, mode='a', header=False, index=False)
    else:
        df.to_csv(csv_file_path, index=False)

    print(f"[INFO] Successfully processed and saved gait angles to CSV.")
