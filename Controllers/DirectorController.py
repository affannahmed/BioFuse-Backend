from flask import jsonify, request
from datetime import date, timedelta
from sqlalchemy import cast, Date
from sqlalchemy.sql import func
from flask import request, jsonify
from datetime import datetime
from sqlalchemy import extract
from Backend.Models import User, Role, UserDepartment, Location, Path,  Camera
from . import db
from Backend.Models.CameraMonitoringLogs import CameraMonitoringLogs
from Backend.Models.Department import Department
from Backend.Models.EmployeeViolations import EmployeeViolations
from Backend.Models.EmployeeDesignation import EmployeeDesignation
from Backend.Models import Designation, AccessControl


class DirectorController:
    @staticmethod
    def fetch_all_available_paths_fordr(current_location_id, desired_location_id):
        results = []

        if not current_location_id or not desired_location_id:
            return {"error": "Missing current_location_id or desired_location_id"}

        current_location = Location.query.get(current_location_id)
        desired_location = Location.query.get(desired_location_id)

        if not current_location or not desired_location:
            return {"error": "Invalid location IDs"}

        # DFS helper – get all paths regardless of status
        def find_paths(current_id, destination_id, visited, path=[]):
            if current_id in visited:
                return []
            if current_id == destination_id:
                return [path + [destination_id]]
            visited.add(current_id)
            paths = []
            direct_paths = Path.query.filter_by(source=current_id).all()
            for path_obj in direct_paths:
                sub_paths = find_paths(path_obj.destination, destination_id, visited, path + [current_id])
                for sub_path in sub_paths:
                    if sub_path not in paths:
                        paths.append(sub_path)
            visited.remove(current_id)
            return paths

        path_sequences = find_paths(current_location_id, desired_location_id, set())
        all_cleaned_paths = []
        unique_paths = set()

        for location_sequence in path_sequences:
            cleaned_path = []
            valid = True
            min_status = 1  # assume all segments are active unless one is discarded

            for loc_id in location_sequence:
                location = Location.query.get(loc_id)
                if not location:
                    valid = False
                    break

                cameras = Camera.query.filter_by(location_id=loc_id).all()
                if not cameras:
                    valid = False
                    break

                cleaned_path.append(location.name)

            # Check status of each (src, dst) segment
            for i in range(len(location_sequence) - 1):
                src = location_sequence[i]
                dst = location_sequence[i + 1]
                path_record = Path.query.filter_by(source=src, destination=dst).first()
                if path_record and path_record.status == 0:
                    min_status = 0
                    break

            if valid:
                path_tuple = tuple(cleaned_path)
                if path_tuple not in unique_paths:
                    unique_paths.add(path_tuple)
                    all_cleaned_paths.append({
                        "path": cleaned_path,
                        "status": min_status
                    })

        results.append({
            "current_location": current_location.name,
            "desired_location": desired_location.name,
            "paths": all_cleaned_paths
        })

        return results

    @staticmethod
    def discard_selected_paths():
        data = request.json
        path_location_names = data.get("path")
        new_status = data.get("status")

        if not path_location_names or len(path_location_names) < 2:
            return jsonify({"error": "Path must include at least two locations"}), 400

        if new_status not in [0, 1]:
            return jsonify({"error": "Invalid status. Must be 0 or 1"}), 400

        # Convert location names to IDs
        location_ids = []
        for name in path_location_names:
            location = Location.query.filter_by(name=name).first()
            if not location:
                return jsonify({"error": f"Location not found: {name}"}), 404
            location_ids.append(location.id)

        updated_path_ids = []

        # Update each (source, destination) segment
        for i in range(len(location_ids) - 1):
            src = location_ids[i]
            dst = location_ids[i + 1]

            path_record = Path.query.filter_by(source=src, destination=dst).first()
            if path_record:
                path_record.status = new_status
                updated_path_ids.append(path_record.id)

        db.session.commit()

        return jsonify({
            "message": f"Path status updated to {new_status}.",
            "updated_path_ids": updated_path_ids
        }), 200

    @staticmethod
    def dailyVisitors():
        try:
            today = db.session.query(func.current_date()).scalar()
            print(f"DB Today: {today}")  # debug

            # Fetch ALL user departments with role_id 4 (visitor)
            all_visitors = (
                db.session.query(User.id, User.name, UserDepartment.date_assigned)
                .join(UserDepartment, User.id == UserDepartment.user_id)
                .filter(UserDepartment.role_id == 4)
                .all()
            )

            print("All visitor entries (with role_id=4):")
            for v in all_visitors:
                print(f"Visitor: {v.name} | Date Assigned: {v.date_assigned}")

            # Now filter only for today
            visitors_today = [
                {"id": v.id, "name": v.name}
                for v in all_visitors
                if v.date_assigned.date() == today
            ]

            return jsonify({
                "date": str(today),
                "total_visitors": len(visitors_today),
                "visitors": visitors_today
            }), 200

        except Exception as e:
            return jsonify({"error": str(e)}), 500



    @staticmethod
    def monthly_Visitors():
        try:
            data = request.args  # expects query params: ?month=7&year=2025
            month = int(data.get("month"))
            year = int(data.get("year"))

            if not month or not year:
                return jsonify({"error": "Please provide both 'month' and 'year'"}), 400

            visitors = (
                db.session.query(User.id, User.name)
                .join(UserDepartment, User.id == UserDepartment.user_id)
                .filter(
                    UserDepartment.role_id == 4,
                    extract('month', UserDepartment.date_assigned) == month,
                    extract('year', UserDepartment.date_assigned) == year
                )
                .all()
            )

            result = [{"id": v.id, "name": v.name} for v in visitors]

            return jsonify({
                "month": month,
                "year": year,
                "total_visitors_monthly": len(result),
                "visitors": result
            }), 200

        except Exception as e:
            return jsonify({"error": str(e)}), 500

    @staticmethod
    def Yearly_Visitors():
        try:
            data = request.args  # expects query param: ?year=2025
            year = int(data.get("year"))

            if not year:
                return jsonify({"error": "Please provide 'year'"}), 400

            visitors = (
                db.session.query(User.id, User.name)
                .join(UserDepartment, User.id == UserDepartment.user_id)
                .filter(
                    UserDepartment.role_id == 4,
                    extract('year', UserDepartment.date_assigned) == year
                )
                .all()
            )

            result = [{"id": v.id, "name": v.name} for v in visitors]

            return jsonify({
                "year": year,
                "total_visitors_yearly": len(result),
                "visitors": result
            }), 200

        except Exception as e:
            return jsonify({"error": str(e)}), 500



            # CHECK ATTENDANCE MODULE
    # ----------- Daily Employees & Supervisor  --------------
    @staticmethod
    def check_daily_attendance():
        try:
            today = db.session.query(func.current_date()).scalar()

            db.session.expire_all()  # Clear session cache to ensure fresh data

            # Step 1: Get all valid employees & supervisors
            all_users = (
                db.session.query(
                    User.id.label("user_id"),
                    User.name,
                    Role.name.label("role"),
                    Department.name.label("department")
                )
                .join(UserDepartment, User.id == UserDepartment.user_id)
                .join(Role, UserDepartment.role_id == Role.id)
                .join(Department, UserDepartment.department_id == Department.id)
                .filter(Role.name.in_(["Employee", "Supervisor"]))
                .filter(UserDepartment.is_valid == True)
                .all()
            )

            # Step 2: Get first appearance of each user for today
            attendance_logs = (
                db.session.query(
                    UserDepartment.user_id.label("user_id"),
                    CameraMonitoringLogs.date_time,
                    CameraMonitoringLogs.access_img,
                    Camera.camera_model,
                    Location.name.label("location")
                )
                .join(UserDepartment, CameraMonitoringLogs.user_id == UserDepartment.id)
                .join(Camera, CameraMonitoringLogs.camera_id == Camera.id)
                .join(Location, Camera.location_id == Location.id)
                .filter(func.date(CameraMonitoringLogs.date_time) == today)
                .all()
            )

            # Step 3: Build a map from user_id to first log entry
            first_log_map = {}
            for log in attendance_logs:
                if log.user_id not in first_log_map:
                    first_log_map[log.user_id] = log  # Only take the first appearance

            # Step 4: Build result response
            def build_image_url(filename):
                return f"{request.host_url}static/frames/{filename.split('/')[-1]}"

            result = []
            for user in all_users:
                log = first_log_map.get(user.user_id)
                is_present = log is not None
                result.append({
                    "PresentToday": "Yes" if is_present else "No",
                    "Name": user.name,
                    "Department": user.department,
                    "Role": user.role,
                    "AccessTime": log.date_time.strftime("%Y-%m-%d %H:%M:%S") if log else None,
                    "AccessImage": build_image_url(log.access_img) if log else None,
                    "Location": log.location if log else None
                })

            # Step 5: Count present/absent
            total_present = sum(1 for r in result if r["PresentToday"] == "Yes")
            total_absent = len(result) - total_present

            return jsonify({
                "date": str(today),
                "TotalPresentToday": total_present,
                "TotalAbsentToday": total_absent,
                "records": result
            }), 200

        except Exception as e:
            return jsonify({"error": str(e)}), 500

    # --------- Monthly plus Most Regular / Least Regular ( Employees and SUpervisor ) -----

    @staticmethod
    def monthly_Employees():
        try:
            year = request.args.get("year", type=int)
            month = request.args.get("month", type=int)

            if not year or not month:
                return jsonify({"error": "Missing 'year' or 'month' parameter"}), 400

            # 🔁 Force refresh session to avoid stale data
            db.session.expire_all()

            # Step 1: Get all valid Employees and Supervisors
            valid_users = (
                db.session.query(
                    User.id.label("user_id"),
                    User.name,
                    Role.name.label("role"),
                    Department.name.label("department")
                )
                .join(UserDepartment, User.id == UserDepartment.user_id)
                .join(Role, UserDepartment.role_id == Role.id)
                .join(Department, UserDepartment.department_id == Department.id)
                .filter(Role.name.in_(["Employee", "Supervisor"]))
                .filter(UserDepartment.is_valid == True)
                .all()
            )

            # Step 2: Build attendance map for selected month using cast(Date)
            attendance_data = (
                db.session.query(
                    UserDepartment.user_id,
                    func.count(func.distinct(cast(CameraMonitoringLogs.date_time, Date))).label("attendance_days")
                )
                .join(CameraMonitoringLogs, CameraMonitoringLogs.user_id == UserDepartment.id)
                .filter(cast(CameraMonitoringLogs.date_time, Date).between(f"{year}-{month:02d}-01",
                                                                           f"{year}-{month:02d}-31"))
                .group_by(UserDepartment.user_id)
                .all()
            )

            # Step 3: Create map from user_id to attendance count
            attendance_map = {r.user_id: r.attendance_days for r in attendance_data}

            # Step 4: Build result list with attendance info
            result = []
            for u in valid_users:
                result.append({
                    "Name": u.name,
                    "Role": u.role,
                    "Department": u.department,
                    "TotalAttendanceMonthly": attendance_map.get(u.user_id, 0)
                })

            # Step 5: Sort by attendance
            result.sort(key=lambda x: x["TotalAttendanceMonthly"], reverse=True)

            if result:
                max_attendance = result[0]["TotalAttendanceMonthly"]
                min_attendance = result[-1]["TotalAttendanceMonthly"]

                most_regular = [r["Name"] for r in result if r["TotalAttendanceMonthly"] == max_attendance]
                least_regular = [r["Name"] for r in result if r["TotalAttendanceMonthly"] == min_attendance]
            else:
                most_regular = []
                least_regular = []

            return jsonify({
                "year": year,
                "month": month,
                "MostRegular": most_regular,
                "LeastRegular": least_regular,
                "records": result
            }), 200

        except Exception as e:
            return jsonify({"error": str(e)}), 500
    # -------- WHole Yearly Employees and Supervisors  ---------
    @staticmethod
    def yearly_Employees():
        try:
            year = request.args.get("year", type=int)
            if not year:
                return jsonify({"error": "Missing 'year' parameter"}), 400

            # Step 1: Get all valid Employees and Supervisors
            valid_users = (
                db.session.query(
                    User.id.label("user_id"),
                    User.name,
                    Role.name.label("role"),
                    Department.name.label("department")
                )
                .join(UserDepartment, User.id == UserDepartment.user_id)
                .join(Role, UserDepartment.role_id == Role.id)
                .join(Department, UserDepartment.department_id == Department.id)
                .filter(Role.name.in_(["Employee", "Supervisor"]))
                .filter(UserDepartment.is_valid == True)
                .all()
            )

            # Step 2: Count distinct attendance days from CameraMonitoringLogs in the YEAR
            attendance_data = (
                db.session.query(
                    UserDepartment.user_id,
                    func.count(func.distinct(func.date(CameraMonitoringLogs.date_time))).label("attendance_days")
                )
                .join(CameraMonitoringLogs, CameraMonitoringLogs.user_id == UserDepartment.id)
                .filter(extract('year', CameraMonitoringLogs.date_time) == year)
                .group_by(UserDepartment.user_id)
                .all()
            )

            # Step 3: Build user_id -> attendance count map
            attendance_map = {r.user_id: r.attendance_days for r in attendance_data}

            # Step 4: Merge attendance data with all users
            result = []
            for u in valid_users:
                result.append({
                    "Name": u.name,
                    "Role": u.role,
                    "Department": u.department,
                    "TotalAttendanceYearly": attendance_map.get(u.user_id, 0)
                })

            # Step 5: Sort and find most/least regular
            result.sort(key=lambda x: x["TotalAttendanceYearly"], reverse=True)

            if result:
                max_att = result[0]["TotalAttendanceYearly"]
                min_att = result[-1]["TotalAttendanceYearly"]

                most_regular = [r["Name"] for r in result if r["TotalAttendanceYearly"] == max_att]
                least_regular = [r["Name"] for r in result if r["TotalAttendanceYearly"] == min_att]
            else:
                most_regular = []
                least_regular = []

            return jsonify({
                "year": year,
                "MostRegular": most_regular,
                "LeastRegular": least_regular,
                "records": result
            }), 200

        except Exception as e:
            return jsonify({"error": str(e)}), 500


    #   check employees who violatee
    @staticmethod
    def get_emp_violations():
        try:
            violations = EmployeeViolations.query.all()

            result = []
            for v in violations:
                user_department = v.user  # This is UserDepartment object
                user = User.query.filter_by(id=user_department.user_id).first()

                result.append({
                    "user_id": user.id,
                    "name": user.name,
                    "camera_id": v.camera_id,
                    "violation_time": v.violation_time.strftime('%Y-%m-%d %H:%M:%S')
                })

            return jsonify({
                "total_violations": len(result),
                "violations": result
            }), 200

        except Exception as e:
            print(f"❌ Error fetching violations: {e}")
            return jsonify({"error": "Failed to fetch employee violations"}), 500



    #  -------- fetch all the etails of the violation person.
    @staticmethod
    def get_violation_details():
        try:
            user_id = request.args.get("user_id", type=int)
            camera_id = request.args.get("camera_id", type=int)
            violation_time_str = request.args.get("violation_time")

            if not user_id or not camera_id or not violation_time_str:
                return jsonify({"error": "Missing required parameters"}), 400

            violation_time = datetime.strptime(violation_time_str, "%Y-%m-%d %H:%M:%S")

            # 🔍 Find the user department record
            user_dept = UserDepartment.query.filter_by(id=user_id).first()
            if not user_dept:
                return jsonify({"error": "UserDepartment not found"}), 404

            user = User.query.get(user_dept.user_id)
            if not user:
                return jsonify({"error": "User not found"}), 404

            # 🔍 Match camera monitoring log within ±30 seconds
            time_threshold = timedelta(seconds=30)
            logs = CameraMonitoringLogs.query.filter_by(
                user_id=user_id,
                camera_id=camera_id
            ).all()

            matching_log = None
            for log in logs:
                if abs((log.date_time - violation_time).total_seconds()) <= time_threshold.total_seconds():
                    matching_log = log
                    break

            if not matching_log:
                return jsonify({"error": "No matching access log found"}), 404

            # 📷 Access image URL
            host_url = request.host_url.rstrip('/')
            access_img_url = f"{host_url}/static/{matching_log.access_img}"

            # 🖼️ Profile image URL
            import os

            filename = os.path.basename(user.profile_img or "")
            profile_img_url = f"{request.host_url}uploads/profile_images/{filename}"

            # 📛 Designation
            designation_name = None
            emp_designation = EmployeeDesignation.query.filter_by(user_id=user_dept.id).first()
            if emp_designation:
                designation = Designation.query.get(emp_designation.designation_id)
                if designation:
                    designation_name = designation.name

            # 🏢 Department
            department_name = user_dept.department.name if user_dept.department else None

            # 📌 Allowed Sections
            access_controls = AccessControl.query.filter_by(employee_id=user_dept.id).all()
            allowed_areas = []
            for ctrl in access_controls:
                section = ctrl.subsection
                if section:
                    allowed_areas.append(section.name)

            # 📍 Violation Location
            camera = Camera.query.get(camera_id)
            violation_location = camera.location.name if camera and camera.location else None

            return jsonify({
                "user_id": user_id,
                "name": user.name,
                "contact": user.contact,
                "designation": designation_name,
                "department": department_name,
                "profile_img_url": profile_img_url,
                "allowed_areas": allowed_areas,
                "violation_location": violation_location,
                "access_time_image": access_img_url
            })

        except Exception as e:
            print("Error:", str(e))
            return jsonify({"error": "Something went wrong", "details": str(e)}), 500