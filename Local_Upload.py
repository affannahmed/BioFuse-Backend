# import os
# import datetime
# from pathlib import Path
# from Backend import db
# from Backend.Models.UserBiometric import UserBiometric
# from Backend.Models.User import User
# from flask import current_app
# from Backend.Models.Department import Department
# from Backend.Models.UserDepartment import UserDepartment
#
# def create_user_biometric_folders(user_id):
#     base_dir = Path("E:/MultiBioFuse")
#     if not base_dir.exists():
#         os.makedirs(base_dir)
#
#     user_folder = base_dir / f"user_{user_id}"
#     biometric_types = ["Gait", "Audio", "Face"]
#
#     os.makedirs(user_folder, exist_ok=True)
#     for b_type in biometric_types:
#         os.makedirs(user_folder / b_type, exist_ok=True)
#
#     return user_folder
#
# def save_biometric_path_to_db(user_id, biometric_type, path):
#     try:
#         new_biometric = UserBiometric(
#             user_id=user_id,
#             biometric_type=biometric_type,
#             biometric_path=str(path),
#             status='pending'
#         )
#         db.session.add(new_biometric)
#         db.session.commit()
#     except Exception as e:
#         db.session.rollback()
#         current_app.logger.error(
#             f"Error saving biometric path to DB for user_id {user_id} and biometric_type {biometric_type}: {str(e)}"
#         )
#         raise
#
# def upload_biometric(user_id, biometric_type, file):
#     user_folder = create_user_biometric_folders(user_id)
#     folder_path = user_folder / biometric_type
#
#     timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
#     file_extension = file.filename.split('.')[-1]
#     file_path = folder_path / f"{biometric_type}_{timestamp}.{file_extension}"
#
#     print(f"Saving file to: {file_path}")
#
#     file.save(file_path)
#
#     save_biometric_path_to_db(user_id, biometric_type, file_path)
#     print("File uploaded and database entry created successfully!")
#
#
# def get_user_biometric(user_id):
#     try:
#         biometric_data = UserBiometric.query.filter_by(user_id=user_id).all()
#         if biometric_data:
#             return biometric_data
#         else:
#             current_app.logger.warning(f"No biometric data found for user_id {user_id}.")
#             return None
#     except Exception as e:
#         current_app.logger.error(f"Error retrieving biometric data for user_id {user_id}: {str(e)}")
#         return None
#
#
# def create_profile_image_folder():
#     profile_images_folder = Path("E:/MultiBioFuse/Profile_Images")
#     if not profile_images_folder.exists():
#         profile_images_folder.mkdir(parents=True, exist_ok=True)
#         current_app.logger.info("Profile Images folder created successfully.")
#     return profile_images_folder
#
# def upload_profile_picture(user_id, file):
#     profile_images_folder = create_profile_image_folder()
#     timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
#     file_extension = file.filename.split('.')[-1]
#     file_name = f"profile_{user_id}_{timestamp}.{file_extension}"
#     file_path = profile_images_folder / file_name
#
#     print(f"Saving profile picture to: {file_path}")
#     file.save(file_path)
#
#
#     try:
#         user = User.query.get(user_id)
#         if user:
#             user.profile_img = str(file_path)
#             db.session.commit()
#             print("Profile picture uploaded and database entry updated successfully!")
#         else:
#             current_app.logger.warning(f"No user found with ID {user_id}.")
#     except Exception as e:
#         db.session.rollback()
#         current_app.logger.error(
#             f"Error saving profile picture path to DB for user_id {user_id}: {str(e)}"
#         )
#         raise
#
#     return str(file_path)
#
# # def upload_profile_picture(user_id, file):
# #     profile_images_folder = create_profile_image_folder()
# #     timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
# #     file_extension = file.filename.split('.')[-1]
# #     file_name = f"profile_{user_id}_{timestamp}.{file_extension}"
# #     file_path = profile_images_folder / file_name
# #
# #     print(f"Saving profile picture to: {file_path}")
# #
# #     file.save(file_path)
# #
# #     # Save the path to the user's profile in the database
# #     try:
# #         user = User.query.get(user_id)
# #         if user:
# #             user.profile_img = str(file_path)
# #             db.session.commit()
# #             print("Profile picture uploaded and database entry updated successfully!")
# #         else:
# #             current_app.logger.warning(f"No user found with ID {user_id}.")
# #     except Exception as e:
# #         db.session.rollback()
# #         current_app.logger.error(
# #             f"Error saving profile picture path to DB for user_id {user_id}: {str(e)}"
# #         )
# #         raise
#
#
# def get_user_profile_picture(user_id):
#     try:
#         user = User.query.get(user_id)
#         if user and user.profile_img:
#             return user.profile_img
#         else:
#             current_app.logger.warning(f"No profile image found for user_id {user_id}.")
#             return None
#     except Exception as e:
#         current_app.logger.error(f"Error retrieving profile image for user_id {user_id}: {str(e)}")
#         return None

import os
import datetime
from pathlib import Path
from Backend import db
from Backend.Models.UserDepartment import UserDepartment
from Backend.Models.UserBiometric import UserBiometric
from Backend.Models.User import User
from flask import current_app, url_for
from Backend.Models.Department import Department

# Helper function to get base upload directory
def get_upload_dir():
    return Path(__file__).parent / "uploads"


# User biometric folders management
def create_user_biometric_folders(user_id):
    base_dir = get_upload_dir() / "user_biometrics"
    user_folder = base_dir / f"user_{user_id}"
    biometric_types = ["Gait", "Audio", "Face"]

    user_folder.mkdir(parents=True, exist_ok=True)
    for b_type in biometric_types:
        (user_folder / b_type).mkdir(exist_ok=True)

    return user_folder


def save_biometric_path_to_db(user_id, biometric_type, relative_path):
    try:
        new_biometric = UserBiometric(
            user_id=user_id,
            biometric_type=biometric_type,
            biometric_path=str(relative_path),
            status='pending'
        )
        db.session.add(new_biometric)
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(
            f"Error saving biometric path to DB for user_id {user_id}: {str(e)}"
        )
        raise


def upload_biometric(user_id, biometric_type, file):
    user_folder = create_user_biometric_folders(user_id)
    folder_path = user_folder / biometric_type

    timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
    file_extension = file.filename.split('.')[-1]
    file_name = f"{biometric_type}_{timestamp}.{file_extension}"
    file_path = folder_path / file_name

    file.save(file_path)

    # Save relative path from uploads directory
    relative_path = file_path.relative_to(get_upload_dir())
    save_biometric_path_to_db(user_id, biometric_type, relative_path)

    return str(file_path)


# Profile images management
def create_profile_image_folder():
    profile_dir = get_upload_dir() / "profile_images"
    profile_dir.mkdir(parents=True, exist_ok=True)
    return profile_dir

# for supervisor update , admin , employee
def upload_profile_pictures_for_other(user_id, file):
    profile_dir = create_profile_image_folder()
    timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
    file_extension = file.filename.split('.')[-1]
    file_name = f"profile_{user_id}_{timestamp}.{file_extension}"
    file_path = profile_dir / file_name

    file.save(file_path)

    try:
        user = User.query.get(user_id)
        if user:
            # Store relative path from uploads directory
            relative_path = file_path.relative_to(get_upload_dir())
            user.profile_img = str(relative_path)
            db.session.commit()
        else:
            current_app.logger.warning(f"No user found with ID {user_id}.")
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error saving profile path: {str(e)}")
        raise

    return str(file_path)

# for visitor
def upload_profile_pictures(user_id, files):
    profile_dir = create_profile_image_folder()
    image_paths = []

    for idx, file in enumerate(files):
        timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
        file_extension = file.filename.split('.')[-1]
        file_name = f"Visitor_{user_id}_img{idx + 1}_{timestamp}.{file_extension}"
        file_path = profile_dir / file_name

        file.save(file_path)
        image_paths.append(str(file_path))

    try:
        user = User.query.get(user_id)
        if user:
            user.profile_img = ",".join(image_paths)  # Store multiple image paths as a comma-separated string
            db.session.commit()
        else:
            current_app.logger.warning(f"No user found with ID {user_id}.")
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error saving profile paths: {str(e)}")
        raise

    return image_paths

def get_user_profile_picture(user_id):
    try:
        user = User.query.get(user_id)
        if user and user.profile_img:
            # Return full URL using Flask's url_for
            return url_for('serve_upload', subpath=user.profile_img, _external=True)
        return None
    except Exception as e:
        current_app.logger.error(f"Error getting profile: {str(e)}")
        return None


# Similar get method for biometrics
def get_user_biometric(user_id):
    try:
        biometrics = UserBiometric.query.filter_by(user_id=user_id).all()
        return [{
            'id': bio.id,
            'type': bio.biometric_type,
            'url': url_for('serve_upload', subpath=bio.biometric_path, _external=True)
        } for bio in biometrics]
    except Exception as e:
        current_app.logger.error(f"Error getting biometrics: {str(e)}")
        return []