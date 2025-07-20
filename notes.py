#
# Purpose	Code	Description
# Add record	db.session.add(obj)	Adds new row
# Save changes	db.session.commit()	Finalize DB change
# Query all	Model.query.all()	Fetch all rows
# Query filter	Model.query.filter_by(...)	Filter records
# Delete record	db.session.delete(obj)	Remove row
# Create DB	db.create_all()	Creates tables
# Rollback on error	db.session.rollback()	Undo changes on error
#
# 🔹 db.session.delete(obj)
# Deletes an object (row) from the database:
# teacher = Teacher.query.get(1)
# db.session.delete(teacher)
# db.session.commit()
#
# 🔹 db.session.commit()
# Saves (commits) the changes made in session to the database:
# db.session.commit()
#
# 🔹 db.session.add(obj)
# Adds a new object (record) to the session:
# new_teacher = Teacher(name="Ali")
# db.session.add(new_teacher)
#
#
#
#
#
# SQL ALCHEMY QUERIES IN FLASK :
#
# 		Aggregate function (min, max, avg, count, sum)
# 1. Write a query to display Maximum CGPA value from student table.
# 2. Write a query to display the Minimum Age value from student table.
# 3. Write a query to display Minimum CGPA value from student table.
# 4. Write a query to display Average CGPA value from student table.
# 5. Write a query to display Average Age value from student table.
# 6. Write a query to display Total CGPA value from student table.
# 7. Write a query to display the Highest, Lowest, and Average Age value from student table.
# 8. Write a query to display Total Number of Students.
# 9. Write a query to display Distinct City Count from student table.
# 10. Write a query to display Total Number of Students whose Last_Name is different.
#
# Assumed Student Model:
# class Student(db.Model):
#     __tablename__ = 'students'
#     id = db.Column(db.Integer, primary_key=True)
#     fname = db.Column(db.String(100))
#     lname = db.Column(db.String(100))
#     age = db.Column(db.Integer)
#     cgpa = db.Column(db.Float)
#     city = db.Column(db.String(100))
#
#
#
# @app.route('/students/max_cgpa')
# def max_cgpa():
#     max_val = db.session.query(func.max(Student.cgpa)).scalar()
#     return jsonify({"max_cgpa": max_val})
#
# @app.route('/students/min_age')
# def min_age():
#     min_val = db.session.query(func.min(Student.age)).scalar()
#     return jsonify({"min_age": min_val})
#
# @app.route('/students/min_cgpa')
# def min_cgpa():
#     min_val = db.session.query(func.min(Student.cgpa)).scalar()
#     return jsonify({"min_cgpa": min_val})
#
# @app.route('/students/avg_cgpa')
# def avg_cgpa():
#     avg_val = db.session.query(func.avg(Student.cgpa)).scalar()
#     return jsonify({"average_cgpa": round(avg_val, 2)})
#
# @app.route('/students/avg_age')
# def avg_age():
#     avg_val = db.session.query(func.avg(Student.age)).scalar()
#     return jsonify({"average_age": round(avg_val, 2)})
#
# @app.route('/students/total_cgpa')
# def total_cgpa():
#     total = db.session.query(func.sum(Student.cgpa)).scalar()
#     return jsonify({"total_cgpa": total})
#
#
#
#
#
#
# @app.route('/students/age_stats')
# def age_stats():
#     max_age = db.session.query(func.max(Student.age)).scalar()
#     min_age = db.session.query(func.min(Student.age)).scalar()
#     avg_age = db.session.query(func.avg(Student.age)).scalar()
#
#     return jsonify({
#         "max_age": max_age,
#         "min_age": min_age,
#         "average_age": round(avg_age, 2)
#     })
#
# @app.route('/students/total_count')
# def student_count():
#     count = db.session.query(func.count(Student.id)).scalar()
#     return jsonify({"total_students": count})
#
#
# @app.route('/students/distinct_city_count')
# def distinct_city_count():
#     count = db.session.query(func.count(func.distinct(Student.city))).scalar()
#     return jsonify({"distinct_cities": count})
#
#
# @app.route('/students/distinct_lname_count')
# def distinct_lname_count():
#     count = db.session.query(func.count(func.distinct(Student.lname))).scalar()
#     return jsonify({"distinct_last_names": count})
#
#
#
#
#
#
# ################################################################
# Aggregate Functions (GROUP Clause and HAVING Clause)
#
# Query 1: Retrieve total number of teachers in each city.
# Query 2: Retrieve city and minimum salary of teacher in each city.
# Query 3: Retrieve qualification and maximum bonus of teacher in each qualification.
# Query 4: Retrieve city and total salary of teacher in each city.
# Query 5: Retrieve qualification and average house allowance of teacher, grouped by qualification.
# (Using: SELECT + FROM + GROUP BY + HAVING)
# Query 1: Retrieve total number of teachers in each city having total number of teachers greater than 3.
# Query 2: Retrieve qualification and minimum salary of teacher for each qualification having minimum salary greater than 120500.
# Query 3: Retrieve city and maximum salary of teacher in each city where maximum salary is less than 120000.
# Query 4: Retrieve city and total salary of teacher in each city having total salary less than 1900000.
# Query 5: Retrieve city and total number of teachers in each city having total number of teachers greater than 4.
#
#
# @app.route('/teachers/count_by_city')
# def count_teachers_by_city():
#     result = db.session.query(Teacher.city, func.count(Teacher.id)).group_by(Teacher.city).all()
#     return jsonify([{"city": r[0], "teacher_count": r[1]} for r in result])
#
# @app.route('/teachers/min_salary_by_city')
# def min_salary_by_city():
#     result = db.session.query(Teacher.city, func.min(Teacher.salary)).group_by(Teacher.city).all()
#     return jsonify([{"city": r[0], "min_salary": r[1]} for r in result])
#
# @app.route('/teachers/max_bonus_by_qualification')
# def max_bonus_by_qualification():
#     result = db.session.query(Teacher.qualification, func.max(Teacher.bonus)).group_by(Teacher.qualification).all()
#     return jsonify([{"qualification": r[0], "max_bonus": r[1]} for r in result])
#
# @app.route('/teachers/total_salary_by_city')
# def total_salary_by_city():
#     result = db.session.query(Teacher.city, func.sum(Teacher.salary)).group_by(Teacher.city).all()
#     return jsonify([{"city": r[0], "total_salary": r[1]} for r in result])
#
#
# @app.route('/teachers/avg_house_allowance_by_qualification')
# def avg_house_by_qualification():
#     result = db.session.query(Teacher.qualification, func.avg(Teacher.house_allowance)).group_by(Teacher.qualification).all()
#     return jsonify([{"qualification": r[0], "avg_house_allowance": round(r[1], 2)} for r in result])
#
#
# @app.route('/teachers/city_count_gt_3')
# def city_count_gt_3():
#     result = db.session.query(Teacher.city, func.count(Teacher.id).label("count")).group_by(Teacher.city).having(func.count(Teacher.id) > 3).all()
#     return jsonify([{"city": r[0], "teacher_count": r[1]} for r in result])
#
#
# @app.route('/teachers/min_salary_qual_gt_120500')
# def min_salary_qual_gt_120500():
#     result = db.session.query(Teacher.qualification, func.min(Teacher.salary).label("min_salary")).group_by(Teacher.qualification).having(func.min(Teacher.salary) > 120500).all()
#     return jsonify([{"qualification": r[0], "min_salary": r[1]} for r in result])
#
#
# @app.route('/teachers/max_salary_city_lt_120000')
# def max_salary_city_lt_120000():
#     result = db.session.query(Teacher.city, func.max(Teacher.salary).label("max_salary")).group_by(Teacher.city).having(func.max(Teacher.salary) < 120000).all()
#     return jsonify([{"city": r[0], "max_salary": r[1]} for r in result])
#
#
# @app.route('/teachers/total_salary_city_lt_19lac')
# def total_salary_city_lt_19lac():
#     result = db.session.query(Teacher.city, func.sum(Teacher.salary).label("total_salary")).group_by(Teacher.city).having(func.sum(Teacher.salary) < 1900000).all()
#     return jsonify([{"city": r[0], "total_salary": r[1]} for r in result])
#
#
# @app.route('/teachers/city_teacher_count_gt_4')
# def city_teacher_count_gt_4():
#     result = db.session.query(Teacher.city, func.count(Teacher.id).label("teacher_count")).group_by(Teacher.city).having(func.count(Teacher.id) > 4).all()
#     return jsonify([{"city": r[0], "teacher_count": r[1]} for r in result])
#
# ################################################################
#
# SQL Joins
# 1. Write a query that will display all those students who have registered a course which is taught by a teacher having name Aslam.
# 2. Write a query that will display tname and course title where category is CS.
# 3. Write a query that will display name of teacher who are teaching a course which is registered by a student having CGPA greater than 3.0.
# 4. Write a query that will display all those Courses which are assigned to students having name Nabeel.
# 5. Write a query that will display all those Courses which are registered by student having name Ali.
# ________________________________________
# 📘 Exercise 14 – Query Statements
# 1. Write a query to show records of those students who are being taught by the eldest teacher.
# 2. Write a query to show City and ages of those students who are taught by a teacher whose age is between 30 to 40 years old.
# 3. Write a query to show cid and title of those courses that are enrolled by the eldest student.
# 4. Write a query to retrieve all records of courses which are allocated to teachers whose salary is between 80000 and 120000.
# 5. Write a query to show data of those courses that are assigned to teachers whose age is maximum.
# 6. Write a query to show sid and name of the student who has registered the course allocated to the teacher whose salary is lowest.
# 7. Write a query to show name and cr_hours of those courses that are allocated to teachers whose age lies between 35 to 45.
# 8. Write a query to show name of those students who are being taught by the eldest teacher.
# 9. Write a query to show name of those students who are being taught by the youngest teacher.
# 10. Write a query to show name of those teachers who are teaching students whose CGPA is between 3.0 and 3.5.
# @app.route('/students/course_by_aslam')
# def students_by_aslam_teacher():
#     students = db.session.query(Student).join(Enrollment).join(Course).join(Teacher).filter(Teacher.t_name == "Aslam").all()
#     return jsonify([s.__dict__ for s in students])
#
# @app.route('/teacher_course_cs')
# def teacher_course_cs():
#     result = db.session.query(Teacher.t_name, Course.title).join(Course).filter(Course.category == "CS").all()
#     return jsonify([{"teacher": r[0], "course": r[1]} for r in result])
#
# @app.route('/teachers_by_cgpa_gt_3')
# def teachers_by_cgpa_students():
#     teachers = db.session.query(Teacher).join(Course).join(Enrollment).join(Student).filter(Student.cgpa > 3.0).distinct().all()
#     return jsonify([t.__dict__ for t in teachers])
#
# @app.route('/courses_by_nabeel')
# def courses_by_nabeel():
#     courses = db.session.query(Course).join(Enrollment).join(Student).filter(Student.fname == "Nabeel").all()
#     return jsonify([c.__dict__ for c in courses])
#
# @app.route('/courses_by_ali')
# def courses_by_ali():
#     courses = db.session.query(Course).join(Enrollment).join(Student).filter(Student.fname == "Ali").all()
#     return jsonify([c.__dict__ for c in courses])
#
# @app.route('/students_by_eldest_teacher')
# def students_by_eldest_teacher():
#     max_age = db.session.query(func.max(Teacher.age)).scalar()
#     students = db.session.query(Student).join(Enrollment).join(Course).join(Teacher).filter(Teacher.age == max_age).all()
#     return jsonify([s.__dict__ for s in students])
#
#
# @app.route('/student_city_age_teacher_30_40')
# def students_by_teacher_30_40():
#     students = db.session.query(Student.city, Student.age).join(Enrollment).join(Course).join(Teacher).filter(Teacher.age.between(30, 40)).distinct().all()
#     return jsonify([{"city": s[0], "age": s[1]} for s in students])
#
# @app.route('/courses_by_eldest_student')
# def course_by_eldest_student():
#     max_age = db.session.query(func.max(Student.age)).scalar()
#     courses = db.session.query(Course.id, Course.title).join(Enrollment).join(Student).filter(Student.age == max_age).all()
#     return jsonify([{"cid": c[0], "title": c[1]} for c in courses])
#
#
# @app.route('/courses_by_salary_range')
# def courses_by_teacher_salary():
#     courses = db.session.query(Course).join(Teacher).filter(Teacher.salary.between(80000, 120000)).all()
#     return jsonify([c.__dict__ for c in courses])
#
#
# @app.route('/courses_by_oldest_teacher')
# def courses_by_oldest_teacher():
#     max_age = db.session.query(func.max(Teacher.age)).scalar()
#     courses = db.session.query(Course).join(Teacher).filter(Teacher.age == max_age).all()
#     return jsonify([c.__dict__ for c in courses])
#
#
# @app.route('/students_lowest_salary_teacher_course')
# def student_by_lowest_salary_teacher():
#     min_salary = db.session.query(func.min(Teacher.salary)).scalar()
#     students = db.session.query(Student.id, Student.fname).join(Enrollment).join(Course).join(Teacher).filter(Teacher.salary == min_salary).all()
#     return jsonify([{"sid": s[0], "name": s[1]} for s in students])
#
#
# @app.route('/courses_by_teacher_35_45')
# def course_by_teacher_age_range():
#     courses = db.session.query(Course.title, Course.cr_hours).join(Teacher).filter(Teacher.age.between(35, 45)).all()
#     return jsonify([{"title": c[0], "cr_hours": c[1]} for c in courses])
#
#
# @app.route('/students_by_youngest_teacher')
# def students_by_youngest_teacher():
#     min_age = db.session.query(func.min(Teacher.age)).scalar()
#     students = db.session.query(Student).join(Enrollment).join(Course).join(Teacher).filter(Teacher.age == min_age).all()
#     return jsonify([s.__dict__ for s in students])
#
#
# @app.route('/teachers_by_cgpa_range')
# def teachers_by_cgpa_students():
#     teachers = db.session.query(Teacher).join(Course).join(Enrollment).join(Student).filter(Student.cgpa.between(3.0, 3.5)).distinct().all()
#     return jsonify([t.__dict__ for t in teachers])
#
#
#
#
# ################################################################
#
# Concatenation Operator, Distinct & Duplicate Record Retrieval
# 1. Write a Sql Statement to merged fname and lname as Full Name of Student.
#  2. Write a Sql Statement to retrieve non repeated lname of student.
# 3. Write a Sql Statement to retrieve different age and section of student
#  4. Write a Sql Statement to retrieve sid as student_id of student.
#  5. Write a Sql Statement to retrieve unique semester number of student.
#
# @app.route('/students/full_name', methods=['GET'])
# def get_full_names():
#     students = db.session.query(
#         (Student.fname + ' ' + Student.lname).label("full_name")
#     ).all()
#
#     result = [{"full_name": row.full_name} for row in students]
#     return jsonify(result)
#
# @app.route('/students/unique_lastnames', methods=['GET'])
# def get_unique_last_names():
#     last_names = db.session.query(
#         distinct(Student.lname)
#     ).all()
#
#     result = [{"lname": lname[0]} for lname in last_names]
#     return jsonify(result)
#
# @app.route('/students/unique_age_section', methods=['GET'])
# def get_unique_age_section():
#     data = db.session.query(
#         distinct(Student.age), Student.section
#     ).all()
#
#     result = [{"age": row[0], "section": row[1]} for row in data]
#     return jsonify(result)
#
# @app.route('/students/student_ids', methods=['GET'])
# def get_student_ids():
#     ids = db.session.query(
#         Student.id.label("student_id")
#     ).all()
#
#     result = [{"student_id": row.student_id} for row in ids]
#     return jsonify(result)
#
# @app.route('/students/unique_semesters', methods=['GET'])
# def get_unique_semesters():
#     semesters = db.session.query(
#         distinct(Student.semester)
#     ).all()
#
#     result = [{"semester": row[0]} for row in semesters]
#     return jsonify(result)
#
# 				Sorting of Data, Selection and Projection
#
# •	Write a query that will display age of teachers in such a way that elder should be shown on top and younger should be shown at bottom.
# •	 Write a query that will retrieve data of teachers whose bonus is 11000.
# •	Write a query that will display yearsofexp of those teachers whose houseallowence is 22700
# •	Write a query that will display all teachers whose tid greater than 5009.
# •	 Write a query that will retrieve name of teachers whose qualification is Ph D
# •	Write a query that will retrieve data of all teachers in such a way that younger teacher should be shown at bottom and elder teacher should be on top.
# •	Write a query that will display all teacher who live in ‘Rwp’.
#
# @app.route('/teachers/by_age_desc', methods=['GET'])
# def get_teachers_by_age_desc():
#     teachers = Teacher.query.order_by(Teacher.age.desc()).all()
#     result = [{"id": t.id, "name": t.name, "age": t.age} for t in teachers]
#     return jsonify(result)
#
# @app.route('/teachers/bonus_11000', methods=['GET'])
# def get_teachers_with_bonus():
#     teachers = Teacher.query.filter_by(bonus=11000).all()
#     result = [{"id": t.id, "name": t.name, "bonus": t.bonus} for t in teachers]
#     return jsonify(result)
#
# @app.route('/teachers/exp_by_allowance', methods=['GET'])
# def get_exp_by_house_allowance():
#     teachers = db.session.query(Teacher.yearsofexp).filter_by(house_allowance=22700).all()
#     result = [{"yearsofexp": exp[0]} for exp in teachers]
#     return jsonify(result)
#
# @app.route('/teachers/id_above_5009', methods=['GET'])
# def get_teachers_id_above_5009():
#     teachers = Teacher.query.filter(Teacher.id > 5009).all()
#     result = [{"id": t.id, "name": t.name} for t in teachers]
#     return jsonify(result)
#
# @app.route('/teachers/phd', methods=['GET'])
# def get_phd_teachers():
#     teachers = Teacher.query.filter_by(qualification='Ph D').all()
#     result = [{"name": t.name} for t in teachers]
#     return jsonify(result)
#
# @app.route('/teachers/by_age_desc_again', methods=['GET'])
# def get_teachers_ordered_by_age_again():
#     teachers = Teacher.query.order_by(Teacher.age.desc()).all()
#     result = [{"id": t.id, "name": t.name, "age": t.age} for t in teachers]
#     return jsonify(result)
#
# @app.route('/teachers/from_rwp', methods=['GET'])
# def get_teachers_from_rwp():
#     teachers = Teacher.query.filter_by(city='Rwp').all()
#     result = [{"id": t.id, "name": t.name, "city": t.city} for t in teachers]
#     return jsonify(result)
#
#
# 		Logical Operators and WHERE Clause
# Query 1: Write a query that will retrieve all data of course whose category is cs.
# Query 2: Write a query that will retrieve title of course whose cr_hours is 4.
# Query 3: Write a query that will retrieve cr_hours of course whose category is either cs or maths.
# Query 4: Write a query that will retrieve all data of course whose cid greater than 1010 and category other than cs.
# Query 5: Retrieve data of all those courses whose title is other than networks.
# 1. Write a query that will display all students whose cgpa is equal to 1.4 and Section is equal to A.
# 2. Write a query that will display name as a Student Name of students whose age is either 22 or 18 or 17 or 23 and display result by name in descending order.
# 3. Write a query that will retrieve sid, age and name as Student Name of students who live in ISB or Rwp, ordered by city ascending.
# 4. Write a query that will retrieve sid, Name, age, city, and degree of students whose degree is other than MCS. Students must be shown from younger to elder.
# 5. Write a query that will retrieve data of all students whose degree is equal to BSCS and city must be Rwp or Multan.
# 6. Write a query that will retrieve all students whose age is equal to 10.
# 7. Write a query that will retrieve age and cgpa of students whose age is either 18 or 20 or 21 or 22.
# 8. Write a SQL statement to retrieve fname and lname of students whose age is neither 18 nor 22 nor 25.
# 9. Write a SQL statement to retrieve all students whose cgpa is neither 2.4 nor 3.4.
# 10. Retrieve all those students whose lname is ali.
#
# @app.route('/courses/category/cs')
# def get_cs_courses():
#     courses = Course.query.filter_by(category='cs').all()
#     result = [c.__dict__ for c in courses]
#     return jsonify([{k: v for k, v in r.items() if not k.startswith('_')} for r in result])
#
# @app.route('/courses/title_by_hours')
# def get_titles_by_cr_hours():
#     titles = db.session.query(Course.title).filter_by(cr_hours=4).all()
#     return jsonify([{"title": t[0]} for t in titles])
#
# @app.route('/courses/credits_cs_maths')
# def get_cr_hours_cs_maths():
#     crs = db.session.query(Course.cr_hours).filter(Course.category.in_(['cs', 'maths'])).all()
#     return jsonify([{"cr_hours": c[0]} for c in crs])
#
# @app.route('/courses/id_gt_1010_not_cs')
# def get_filtered_courses():
#     courses = Course.query.filter(Course.id > 1010, Course.category != 'cs').all()
#     return jsonify([c.__dict__ for c in courses])
#
# @app.route('/courses/title_not_networks')
# def get_courses_not_networks():
#     courses = Course.query.filter(Course.title != 'networks').all()
#     return jsonify([c.__dict__ for c in courses])
#
# @app.route('/students/cgpa_1_4_section_a')
# def get_students_specific_cgpa_section():
#     students = Student.query.filter_by(cgpa=1.4, section='A').all()
#     return jsonify([s.__dict__ for s in students])
#
# @app.route('/students/selected_ages')
# def get_students_selected_ages():
#     students = db.session.query(
#         (Student.fname + " " + Student.lname).label("Student Name")
#     ).filter(Student.age.in_([22, 18, 17, 23])).order_by(Student.fname.desc()).all()
#
#     return jsonify([{"Student Name": s[0]} for s in students])
#
# @app.route('/students/city_filter')
# def get_students_by_city():
#     students = db.session.query(
#         Student.id, Student.age, (Student.fname + " " + Student.lname).label("Student Name"), Student.city
#     ).filter(Student.city.in_(['ISB', 'Rwp'])).order_by(Student.city.asc()).all()
#
#     return jsonify([
#         {
#             "sid": s[0],
#             "age": s[1],
#             "Student Name": s[2],
#             "city": s[3]
#         } for s in students
#     ])
#
# @app.route('/students/not_mcs')
# def get_not_mcs_students():
#     students = Student.query.filter(Student.degree != 'MCS').order_by(Student.age.asc()).all()
#     result = [{"sid": s.id, "name": s.fname + " " + s.lname, "age": s.age, "city": s.city, "degree": s.degree} for s in students]
#     return jsonify(result)
#
# @app.route('/students/bscs_from_rwp_or_multan')
# def get_bscs_students_rwp_multan():
#     students = Student.query.filter(
#         Student.degree == 'BSCS',
#         Student.city.in_(['Rwp', 'Multan'])
#     ).all()
#     return jsonify([s.__dict__ for s in students])
#
# @app.route('/students/age_10')
# def get_students_age_10():
#     students = Student.query.filter_by(age=10).all()
#     return jsonify([s.__dict__ for s in students])
#
#
# @app.route('/students/age_cgpa_range')
# def get_age_cgpa():
#     students = db.session.query(Student.age, Student.cgpa).filter(Student.age.in_([18, 20, 21, 22])).all()
#     return jsonify([{"age": s[0], "cgpa": s[1]} for s in students])
#
#
# @app.route('/students/age_not_18_22_25')
# def get_students_age_not_in():
#     students = db.session.query(Student.fname, Student.lname).filter(~Student.age.in_([18, 22, 25])).all()
#     return jsonify([{"fname": s[0], "lname": s[1]} for s in students])
#
#
# @app.route('/students/cgpa_not_in')
# def get_students_cgpa_not():
#     students = Student.query.filter(~Student.cgpa.in_([2.4, 3.4])).all()
#     return jsonify([s.__dict__ for s in students])
#
#
# @app.route('/students/lname_ali')
# def get_students_lname_ali():
#     students = Student.query.filter_by(lname='ali').all()
#     return jsonify([s.__dict__ for s in students])
#
#
#
# 			SOME IMP
#
# 1 Write a query to display the name (fName, lName) and age of students
# whose age is not in the range of 19 and 21
# 58
# DBS LAB MANUALS
# 2 Write a query to display all data of students whose cgpa is in the range
# of 3.5 to 4.0 and age is not equal to 19.
# 3 Write a query to display all data of student whose city is neither rwp nor
# isb and age is greater than or equal to 20.
# 4 Write a query to display the full name (fname and lname), and city of
# students whose section is other than A.
# 5 Write a query to select all records of students whose lname is either 'ali'
# or 'ahmed'
# 6 Write a query to display the full name (t_fname and t_lname), and
# salary of teachers whose salary is out of the range 100000 and 125000
# and make the result set in descending order by the full name.
# 7 Write a query to display the full name (t_fname and t_lname), house
# allowance and yearofexp for those teachers who was doing “Ph D” and
# make the result set in ascending order by age.
# 8 Write a query that will retrieve top two record of Teachers order by
# Salary Ascending.
# 9 Write a query that will retrieve half records of teachers and make result
# set by age in descending order.
# 10 Write a query that will retrieve top 70 percent records of Teachers
# whose salary is greater than or equal to 120000.
#
#
# @app.route('/students/age_not_19_to_21')
# def students_age_not_in_range():
#     students = db.session.query(Student.fname, Student.lname, Student.age).filter(~Student.age.between(19, 21)).all()
#     return jsonify([{"fname": s[0], "lname": s[1], "age": s[2]} for s in students])
#
# @app.route('/students/cgpa_range_and_age_not_19')
# def get_students_cgpa_age():
#     students = Student.query.filter(Student.cgpa.between(3.5, 4.0), Student.age != 19).all()
#     return jsonify([s.__dict__ for s in students])
#
# @app.route('/students/city_not_rwp_isb_age_20_plus')
# def get_students_by_city_age():
#     students = Student.query.filter(~Student.city.in_(['rwp', 'isb']), Student.age >= 20).all()
#     return jsonify([s.__dict__ for s in students])
#
# @app.route('/students/not_in_section_a')
# def get_students_not_in_section_a():
#     students = db.session.query(
#         (Student.fname + ' ' + Student.lname).label("full_name"),
#         Student.city
#     ).filter(Student.section != 'A').all()
#     return jsonify([{"full_name": s[0], "city": s[1]} for s in students])
#
# @app.route('/students/lname_ali_or_ahmed')
# def get_students_by_lname():
#     students = Student.query.filter(Student.lname.in_(['ali', 'ahmed'])).all()
#     return jsonify([s.__dict__ for s in students])
#
# @app.route('/teachers/salary_out_of_range')
# def teachers_salary_out_of_range():
#     teachers = db.session.query(
#         (Teacher.t_fname + ' ' + Teacher.t_lname).label("full_name"),
#         Teacher.salary
#     ).filter(~Teacher.salary.between(100000, 125000)).order_by((Teacher.t_fname + ' ' + Teacher.t_lname).desc()).all()
#
#     return jsonify([{"full_name": t[0], "salary": t[1]} for t in teachers])
#
# @app.route('/teachers/phd_sorted_by_age')
# def teachers_phd_by_age():
#     teachers = db.session.query(
#         (Teacher.t_fname + ' ' + Teacher.t_lname).label("full_name"),
#         Teacher.house_allowance,
#         Teacher.yearsofexp
#     ).filter(Teacher.qualification == 'Ph D').order_by(Teacher.age.asc()).all()
#
#     return jsonify([{"full_name": t[0], "house_allowance": t[1], "yearsofexp": t[2]} for t in teachers])
#
# @app.route('/teachers/top_2_by_salary')
# def top_2_teachers_salary():
#     teachers = Teacher.query.order_by(Teacher.salary.asc()).limit(2).all()
#     return jsonify([t.__dict__ for t in teachers])
#
# @app.route('/teachers/half_by_age')
# def half_teachers_by_age():
#     total = Teacher.query.count()
#     half = total // 2
#     teachers = Teacher.query.order_by(Teacher.age.desc()).limit(half).all()
#     return jsonify([t.__dict__ for t in teachers])
#
# @app.route('/teachers/top_70_percent_salary')
# def top_70_salary_teachers():
#     total = Teacher.query.filter(Teacher.salary >= 120000).count()
#     limit = int(total * 0.7)
#     teachers = Teacher.query.filter(Teacher.salary >= 120000).limit(limit).all()
#     return jsonify([t.__dict__ for t in teachers])
#
#
# Comparison Operators (LIKE, NOT LIKE)
#
# Query 1: Retrieve all those teachers whose first name 2nd letter is “I”.
# Query 2: Retrieve all those teachers whose first name starts with T.
# Query 3: Retrieve full name of teacher whose last name ends on “a”.
# Query 4: Retrieve salary from teachers whose last name 3rd letter is either “a” or “e” or “I”.
# Query 5: Retrieve all those teachers whose last name contains “ee”.
# 1. Write a query to display the First Name of teacher whose first name has both "a" and "m" at any position in any sequence.
# 2. Write a query to display data of all Teachers whose Last Name starts with “j” and ends on “d”.
# 3. Write a query to display the First Name, Last Name as Full Name of teachers whose First Name starts with either “a” or “b” or “c” and make result set by last name in descending order.
# 4. Write a query to display the last name of teachers whose last name 3rd letter is either 'e' or “I” or “o” or “u”.
# 5. Write a query to display the last name of teachers whose last names contain exactly 6 characters.
# 6. Write a query to display the full name (First Name, Last Name) and salary of teachers whose experience is greater than 8.
# 7. Write a SQL Statement that will retrieve all those teachers whose city contains “a” at any position.
#
#
# @app.route('/teachers/fname_second_letter_i')
# def fname_second_letter_i():
#     teachers = Teacher.query.filter(Teacher.t_fname.ilike('_i%')).all()
#     return jsonify([t.__dict__ for t in teachers])
#
# @app.route('/teachers/fname_start_t')
# def fname_start_t():
#     teachers = Teacher.query.filter(Teacher.t_fname.ilike('t%')).all()
#     return jsonify([t.__dict__ for t in teachers])
#
# @app.route('/teachers/lname_end_a')
# def lname_end_a():
#     teachers = db.session.query(
#         (Teacher.t_fname + ' ' + Teacher.t_lname).label("full_name")
#     ).filter(Teacher.t_lname.ilike('%a')).all()
#
#     return jsonify([{"full_name": t[0]} for t in teachers])
#
# @app.route('/teachers/lname_3rd_letter')
# def lname_3rd_letter_match():
#     teachers = db.session.query(Teacher.salary).filter(
#         db.or_(
#             Teacher.t_lname.ilike('__a%'),
#             Teacher.t_lname.ilike('__e%'),
#             Teacher.t_lname.ilike('__i%')
#         )
#     ).all()
#     return jsonify([{"salary": s[0]} for s in teachers])
#
#
# @app.route('/teachers/lname_contains_ee')
# def lname_contains_ee():
#     teachers = Teacher.query.filter(Teacher.t_lname.ilike('%ee%')).all()
#     return jsonify([t.__dict__ for t in teachers])
#
# @app.route('/teachers/fname_contains_a_m')
# def fname_contains_a_m():
#     teachers = Teacher.query.filter(
#         Teacher.t_fname.ilike('%a%'),
#         Teacher.t_fname.ilike('%m%')
#     ).all()
#     return jsonify([t.__dict__ for t in teachers])
#
# @app.route('/teachers/lname_start_j_end_d')
# def lname_start_j_end_d():
#     teachers = Teacher.query.filter(Teacher.t_lname.ilike('j%d')).all()
#     return jsonify([t.__dict__ for t in teachers])
#
#
# @app.route('/teachers/fname_abc_lname_desc')
# def fname_starts_abc():
#     teachers = db.session.query(
#         (Teacher.t_fname + " " + Teacher.t_lname).label("full_name")
#     ).filter(
#         db.or_(
#             Teacher.t_fname.ilike('a%'),
#             Teacher.t_fname.ilike('b%'),
#             Teacher.t_fname.ilike('c%')
#         )
#     ).order_by(Teacher.t_lname.desc()).all()
#
#     return jsonify([{"full_name": t[0]} for t in teachers])
#
#
# @app.route('/teachers/lname_3rd_letter_vowels')
# def lname_3rd_letter_vowel():
#     teachers = db.session.query(Teacher.t_lname).filter(
#         db.or_(
#             Teacher.t_lname.ilike('__e%'),
#             Teacher.t_lname.ilike('__i%'),
#             Teacher.t_lname.ilike('__o%'),
#             Teacher.t_lname.ilike('__u%')
#         )
#     ).all()
#
#     return jsonify([{"t_lname": t[0]} for t in teachers])
#
#
# @app.route('/teachers/lname_length_6')
# def lname_length_6():
#     teachers = Teacher.query.filter(func.length(Teacher.t_lname) == 6).all()
#     return jsonify([t.__dict__ for t in teachers])
#
#
# @app.route('/teachers/exp_gt_8')
# def exp_gt_8():
#     teachers = db.session.query(
#         (Teacher.t_fname + ' ' + Teacher.t_lname).label("full_name"),
#         Teacher.salary
#     ).filter(Teacher.yearsofexp > 8).all()
#
#     return jsonify([{"full_name": t[0], "salary": t[1]} for t in teachers])
#
# @app.route('/teachers/city_contains_a')
# def city_contains_a():
#     teachers = Teacher.query.filter(Teacher.city.ilike('%a%')).all()
#     return jsonify([t.__dict__ for t in teachers])
#
#
#
#
# ✅ This returns all teacher records with all columns
# teachers = Teacher.query.all()
# SELECT * FROM teachers;
#
# b) Retrieve any two columns of Teacher table (e.g., t_fname, email)
# teachers = db.session.query(Teacher.t_fname, Teacher.email).all()
# SELECT t_fname, email FROM teachers;
#
# c) Retrieve more than three columns (e.g., t_fname, email, age, subject)
# SELECT t_fname, email, age, subject FROM teachers;
# teachers = db.session.query(
#     Teacher.t_fname,
#     Teacher.email,
#     Teacher.age,
#     Teacher.subject
# ).all()
#
# d) Show teacher data with student age in encrypted form
# SELECT t_fname, (age * 3 - 5) / 4 AS encrypted_age FROM teachers;
# from sqlalchemy import func
#
# teachers = db.session.query(
#     Teacher.t_fname,
#     ((Teacher.age * 3 - 5) / 4).label("encrypted_age")
# ).all()
#
# e) Retrieve t_fname as Teacher Name
# SELECT t_fname AS "Teacher Name" FROM teachers;
# teachers = db.session.query(
#     Teacher.t_fname.label("Teacher Name")
# ).all()
#
#
#
# 1.	Show student data with age + 5
# from sqlalchemy import literal_column
#
# students = db.session.query(
#     Student.fname,
#     Student.age,
#     (Student.age + 5).label("encrypted_age")
# ).all()
#
# 2.	Show sid and CGPA with CGPA - 1.0
# students = db.session.query(
#     Student.id,
#     (Student.cgpa - 1.0).label("encrypted_cgpa")
# ).all()
#
# 3.	Show age (×2), degree, section
# students = db.session.query(
#     (Student.age * 2).label("encrypted_age"),
#     Student.degree,
#     Student.section
# ).all()
#
# 4.	Show fname, city, and cgpa ÷ 2.0
# students = db.session.query(
#     Student.fname,
#     Student.city,
#     (Student.cgpa / 2.0).label("encrypted_cgpa")
# ).all()
#
# Show name, and age in 4 ways: +10, -5, ×2, ÷2
# students = db.session.query(
#     Student.fname.label("name"),
#     (Student.age + 10).label("age_plus_10"),
#     (Student.age - 5).label("age_minus_5"),
#     (Student.age * 2).label("age_times_2"),
#     (Student.age / 2).label("age_div_2")
# ).all()
#
#
# Show city as Student_City and age as Student_Age
# students = db.session.query(
#     Student.city.label("Student_City"),
#     Student.age.label("Student_Age")
# ).all()
#
#
#
#
