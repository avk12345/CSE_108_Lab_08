import os
from flask import Flask, render_template, jsonify, request
from flask_sqlalchemy import SQLAlchemy
# from flask_cors import CORS

app = Flask(__name__)
# CORS(app)

# =========================================================================
# 1. DATABASE CONFIGURATION
# =========================================================================
# 3 slashes (///) means "create this file right here in my project folder".
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///university.sqlite'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Links the database tool (SQLAlchemy) to the specific Flask app.
db = SQLAlchemy(app)

# =========================================================================
# 2. DATABASE MODELS AREA (Lecture 14, Pages 8 & 14)
# =========================================================================

class Class(db.Model):
    __tablename__ = 'classes'
    id = db.Column(db.Integer, primary_key=True)       # Standard Auto-Increment ID
    class_name = db.Column(db.String(100), unique=True, nullable=False)
    teacher_name = db.Column(db.String(100), nullable=False)
    class_time = db.Column(db.String(100), nullable=False)
    capacity = db.Column(db.Integer, nullable=False)

class Student(db.Model):
    __tablename__ = 'students'
    id = db.Column(db.Integer, primary_key=True)       # Standard Auto-Increment ID / Surrogate key
    student_name = db.Column(db.String(100), unique=True, nullable=False)

class Enrollment(db.Model):
    """The Junction Table treated as a standard, simple database table."""
    __tablename__ = 'enrollments'
    id = db.Column(db.Integer, primary_key=True)       # Standard Auto-Increment ID
    
    # Simple Foreign Keys pointing back to the core tables
    class_id = db.Column(db.Integer, db.ForeignKey('classes.id'), nullable=False)
    student_id = db.Column(db.Integer, db.ForeignKey('students.id'), nullable=False)
    
    # Float grade attribute entry tracking cell matching assignment logs
    grade = db.Column(db.Float, nullable=True)  


# =========================================================================
# 3. THE DATABASE BUILDER & INITIAL SEEDER (Flask Context Layer)
# =========================================================================
# Wakes up Flask's background settings openly so it executes safely during 'flask run'.
with app.app_context():
    db.create_all()  # Build table schemas inside university.sqlite automatically
    
    # Check if the database table is completely fresh and empty before seeding entries
    if Class.query.first() is None and Student.query.first() is None:
        math = Class(class_name="Math 101", teacher_name="Ralph Jenkins", class_time="MWF 10:00-10:50 AM", capacity=2)
        physics = Class(class_name="Physics 121", teacher_name="Susan Walker", class_time="TR 11:00-11:50 AM", capacity=10)
        cs = Class(class_name="CS 106", teacher_name="Dr Hepworth", class_time="MWF 2:00-2:50 PM", capacity=10)
        
        jose = Student(student_name="Jose Santos")
        betty = Student(student_name="Betty Brown")
        justin = Student(student_name="Justin Jeffrys")
        
        db.session.add_all([math, physics, cs, jose, betty, justin])
        db.session.commit()

        # Pre-seed sample enrollment links so that the GET routes have data to display
        link_1 = Enrollment(class_id=math.id, student_id=jose.id, grade=92.5)
        link_2 = Enrollment(class_id=physics.id, student_id=betty.id, grade=88.0)
        link_3 = Enrollment(class_id=physics.id, student_id=justin.id, grade=75.0)
        link_4 = Enrollment(class_id=cs.id, student_id=jose.id, grade=95.0)
        db.session.add_all([link_1, link_2, link_3, link_4])
        db.session.commit()


# =========================================================================
# 4. CORE APP ROUTES (FETCH & PARSE CONTRACT)
# =========================================================================

@app.route('/')
def home():
    """Serves the test faceplate HTML layout document from the Flask templates folder."""
    return render_template('index.html')


@app.route('/login', methods=['POST'])
def mock_login():
    """Validates parameters from json payloads to identify user roles."""
    # Extract the incoming JSON string from the request and convert it into a Python dictionary
    data = request.get_json(silent=True)
    if not isinstance(data, dict):
        return jsonify({"error": "Invalid or missing JSON object"}), 400
    
    username = data.get('username')
    password = data.get('password')
    
    # Reject the request if the password does not match the hardcoded test password
    if password != "password123":
        # jsonify converts the Python dictionary into a JSON string with a 401 Unauthorized status
        return jsonify({"error": "Invalid password credentials"}), 401

    # 1. isinstance(username, str) checks that the input is actually text (not a raw number or None).
    # 2. any(c.isalpha() for c in username) loops through each character to make sure there is at least one letter, blocking empty strings, spaces, and number-only inputs.
    if not isinstance(username, str) or not any(c.isalpha() for c in username):
        # Return a 400 Bad Request status because the input format itself is invalid.
        return jsonify({"error": "Username must contain at least one letter"}), 400

    # .strip() removes any accidental spaces at the very beginning or end of the valid name.
    username = username.strip()
        
    # Check the username against the provided three seeded teacher credentials and return their role as JSON
    teachers = {
        "ahepworth": "Dr Hepworth",
        "rjenkins": "Ralph Jenkins",
        "swalker": "Susan Walker"
    }
    if username in teachers:
        return jsonify({"role": "teacher", "display_name": teachers[username]}), 200

        
    # Check for hardcoded admin credentials and return their role as JSON
    if username == "admin":
        return jsonify({"role": "admin", "display_name": "System Administrator"}), 200
        
    # Query database using non-primary key column; requires explicit execution method (.first())
    student = Student.query.filter_by(student_name=username).first()

    is_new = False
    
    # If the student does not exist in the database yet, create and save a new record
    if student is None:
        student = Student(student_name=username)
        db.session.add(student)
        db.session.commit()
        is_new = True
        
    # Convert the student's details into a JSON string and send it back to the frontend with a 200 OK status
    return jsonify({
        "role": "student",
        "student_id": student.id,
        "display_name": student.student_name,
        "is_new_student": is_new,
        "message": "New student registered and logged in" if is_new else "Existing student login successful"
    }), 200

@app.route('/students', methods=['GET'])
def get_all_students():
    """SAMPLE BASELINE: Pulls students out of the SQL Student table and converts them to a readable JSON array."""
    
    response_list = []
    for s in Student.query.all():
        response_list.append({
            "student_id": s.id,
            "student_name": s.student_name
        })
    # 3. Flatten the data and send it to the frontend interface browser window.
    return jsonify(response_list), 200


@app.route('/courses', methods=['GET'])
def get_all_courses():
    """SAMPLE BASELINE: Pulls courses out of SQL tables and converts them to JSON text."""
    # 1. Pull down all of the row record objects from the SQL database file
    # Note: .order_by() sorts in ascending order (A-Z) by default when .asc() or .desc() is omitted
    all_classes = Class.query.order_by(Class.class_name).all()
    
    response_list = []
    # 2. Use a standard loop to extract fields back into standard cells (maintaining the A-Z order from above)
    for c in all_classes:
        # Simply count total linkage rows in the enrollment table where class_id matches
        live_count = Enrollment.query.filter_by(class_id=c.id).count()
        response_list.append({
            "class_id": c.id,
            "class_name": c.class_name,
            "teacher_name": c.teacher_name,
            "time": c.class_time,
            "enrolled": live_count,
            "capacity": c.capacity
        })

    # 3. Flatten the data and send it to the frontend interface browser window.
    return jsonify(response_list), 200


@app.route('/enrollments', methods=['GET'])
def get_all_enrollments():
    response_list = []

    all_enrollments = Enrollment.query.all()
    if all_enrollments is None:
            return jsonify({"error": "No enrollments found"}), 404

    for e in all_enrollments:
        curr_course = db.session.get(Class, e.class_id)
        current_student = db.session.get(Student, e.student_id)
        response_list.append({
            "enrollment_id": e.id,
            "class_id": e.class_id,
            "class_name": curr_course.class_name,
            "student_id": e.student_id,
            "student_name": current_student.student_name,
            "grade": e.grade
        })
    return jsonify(response_list), 200


@app.route('/student/my-courses/<int:student_id>', methods=['GET'])
def get_student_courses(student_id):
    """Gathers an isolated schedule roster for a specific student ID (Page 3)."""
    
    # 1. Replaced deprecated Student.query.get()
    current_student = db.session.get(Student, student_id)

    # 2. Safeguard check for invalid/non-existent student IDs
    if current_student is None:
        return jsonify({"error": "Student not found"}), 404

    # Look up all rows matching the foreign key student_id from the junction table
    my_enrollments = Enrollment.query.filter_by(student_id=student_id).all()
    personal_schedule = []
    
    # Iterate through each isolated enrollment record to bridge back to class details
    for record in my_enrollments:
        # Direct lookup shortcut targeted purely at finding a single row by its unique primary key
        # Syntax on session object: session.query(EntityClass).get(primary_key_value)
        course_details = db.session.get(Class, record.class_id)
        
        # Verify row exists in target table before attempting to extract specific cell values
        if course_details is not None:
            personal_schedule.append({
                "student_name": current_student.student_name,
                "class_id": course_details.id,
                "class_name": course_details.class_name,
                "teacher_name": course_details.teacher_name,
                "time": course_details.class_time,
                "grade": record.grade
            })
    return jsonify(personal_schedule), 200 # By default, Flask's jsonify() engine automatically rearranges all keys inside a dictionary into alphabetical order before sending it out.


@app.route('/enroll/<int:chosen_class_id>/<int:chosen_student_id>', methods=['POST'])
def enroll_student(chosen_class_id, chosen_student_id):
    """Handles course addition with dynamic parameter paths."""
    # Direct lookup shortcut targeted purely at finding a single row by its unique primary key
    target_class = db.session.get(Class, chosen_class_id)

    # Ensures the given course ID exists before performing any subsequent checks
    if target_class is None:
        return jsonify({"error": "Class not found"}), 404

    # Ensures the student exists before checking capacity or duplicates
    target_student = db.session.get(Student, chosen_student_id)
    if target_student is None:
        return jsonify({"error": "Student not found"}), 404

    live_count = Enrollment.query.filter_by(class_id=chosen_class_id).count()

    # Use .count() to block enrollment if the class is full.
    if live_count >= target_class.capacity:
        return jsonify({"error": "Class is full"}), 400
    
    # Check BOTH class_id and student_id together so a student can take multiple different classes
    if Enrollment.query.filter_by(class_id=chosen_class_id, student_id=chosen_student_id).first() is not None:
        return jsonify({"error": "Student already enrolled in this class"}), 409
        
    new_signup = Enrollment(class_id=chosen_class_id, student_id=chosen_student_id, grade=None)
    db.session.add(new_signup)
    db.session.commit()
    return jsonify({"success": "Student successfully enrolled"}), 201


@app.route('/drop/<int:chosen_class_id>/<int:chosen_student_id>', methods=['POST'])
def drop_student(chosen_class_id, chosen_student_id):
    """Handles course deletion via dynamic parameters."""
    # Goal: Locate matching rows via .filter_by() and clear the link via db.session.delete().
    
    curr_enrollment = Enrollment.query.filter_by(student_id=chosen_student_id, class_id=chosen_class_id).first()
    if curr_enrollment is None:
        return jsonify({"error": "Enrollment record not found"}), 404

    db.session.delete(curr_enrollment)
    db.session.commit()
    
    return jsonify({"success": "Course dropped successfully"}), 200


@app.route('/teacher/update-grade/', methods=['POST'])
@app.route('/teacher/update-grade/<int:class_id>/<int:student_id>', methods=['POST'])
def update_grade(class_id=None, student_id=None, subpath=None):
    """Allows instructors to privately modify a unique grade attribute (Page 7)."""
    if class_id is None or student_id is None:
        return jsonify({"error": "Class ID, Student ID, and Grade must all be provided"}), 400

    data = request.get_json(silent=True)
    if not isinstance(data, dict):
        return jsonify({"error": "Invalid or missing JSON object"}), 400
        
    new_grade = data.get('grade')

    if not isinstance(new_grade, (int, float)) or not (0 <= new_grade <= 100):
        return jsonify({"error": "Invalid or missing new grade provided"}), 400

    curr_enrollment = Enrollment.query.filter_by(student_id=student_id, class_id=class_id).first()
    if curr_enrollment is None:
        return jsonify({"error": "Enrollment record not found"}), 404

    curr_enrollment.grade = new_grade
    db.session.commit()

    return jsonify({"success": "Grade sheet updated successfully"}), 200


@app.route('/admin/create-class', methods=['POST'])
def admin_create_class():
    """Allows administrators to seed completely new courses into the database (Page 11)."""
    # Goal: Instantiate a new Class model, and commit it to the table.
    
    data = request.get_json(silent=True)
    if not isinstance(data, dict):
        return jsonify({"error": "Invalid or missing JSON object"}), 400
        
    new_class_name = data.get('class_name')
    new_teacher_name = data.get('teacher_name')
    new_class_time = data.get('class_time')
    new_capacity = data.get('capacity')

    if not isinstance(new_class_name, str) or not any(c.isalpha() for c in new_class_name) or not any(c.isdigit() for c in new_class_name) or " " not in new_class_name.strip():
        return jsonify({"error": "Invalid course name, must use format [Course Name Course Num]"}), 400
    if not isinstance(new_teacher_name, str) or not any(c.isalpha() for c in new_teacher_name):
            return jsonify({"error": "Invalid teacher name"}), 400
    if (
        not isinstance(new_class_time, str)
        or not any(c.isalpha() for c in new_class_time)
        or not any(c.isdigit() for c in new_class_time)
        or ":" not in new_class_time
        or "-" not in new_class_time
        or " " not in new_class_time.strip()
        ):
        return jsonify({
            "error": "Invalid format. Use [Days StartTime-EndTime AM/PM], such as [TTh 10:00-11:15 AM]"
        }), 400
    if not isinstance(new_capacity, int) or new_capacity <= 0:
        return jsonify({"error": "Invalid course capacity"}), 400

    new_class = Class(class_name=new_class_name.strip(), teacher_name=new_teacher_name, class_time=new_class_time, capacity=new_capacity)

    if Class.query.filter_by(class_name=new_class_name.strip()).first() is not None:
        return jsonify({"error": "Class name already exists"}), 409
    
    db.session.add(new_class)
    db.session.commit()
    
    return jsonify({"success": "New course successfully created by administrator"}), 201

@app.route('/admin/update-class/', methods=['POST'])
@app.route('/admin/update-class/<int:class_id>', methods=['POST'])
def admin_update_class(class_id = None):
    """Allows administrators to edit existing course details via POST (Page 11)."""
    # Goal 1: Look up the target Class by primary key (db.session.get) and return 404 if None.
    # Goal 2: Update attributes (class_name, teacher_name, class_time, capacity) from 'data'.
    # Goal 3: Save changes via db.session.commit().
    
    if class_id is None:
        return jsonify({"error": "Class ID must be provided"}), 400

    data = request.get_json(silent=True)
    if not isinstance(data, dict):
        return jsonify({"error": "Invalid or missing JSON object"}), 400
    
    current_class = db.session.get(Class, class_id)

    # Ensures the given course ID exists before performing any subsequent checks
    if current_class is None:
        return jsonify({"error": "Class not found"}), 404
    
    new_class_name = data.get('class_name')
    new_teacher_name = data.get('teacher_name')
    new_class_time = data.get('class_time')
    new_capacity = data.get('capacity')

    if new_class_name in (None, "") and new_teacher_name in (None, "") and new_class_time in (None, "") and new_capacity in (None, ""):
        return jsonify({ "error": "At least one field to update must be provided" }), 400

    if new_class_name not in (None, "") and (not isinstance(new_class_name, str) or not any(c.isalpha() for c in new_class_name) or not any(c.isdigit() for c in new_class_name) or " " not in new_class_name.strip()):
        return jsonify({"error": "Invalid course name, must use format [Course Name Course Num]"}), 400
    if new_teacher_name not in (None, "") and (not isinstance(new_teacher_name, str) or not any(c.isalpha() for c in new_teacher_name)):
        return jsonify({"error": "Invalid teacher name"}), 400
    if new_class_time not in (None, "") and (
        not isinstance(new_class_time, str)
        or not any(c.isalpha() for c in new_class_time)
        or not any(c.isdigit() for c in new_class_time)
        or ":" not in new_class_time
        or "-" not in new_class_time
        or " " not in new_class_time.strip()
    ):
        return jsonify({
            "error": "Invalid format. Use [Days StartTime-EndTime AM/PM], such as [TTh 10:00-11:15 AM]"
        }), 400
    if new_capacity not in (None, "") and (not isinstance(new_capacity, int) or new_capacity <= 0):
        return jsonify({"error": "Invalid course capacity"}), 400

    # Only update the columns with values that were provided
    if new_class_name not in (None, ""):
        if new_class_name.strip() != current_class.class_name and Class.query.filter_by(class_name=new_class_name.strip()).first() is not None:
            return jsonify({"error": "Class name already exists"}), 409
        current_class.class_name = new_class_name.strip()
    if new_teacher_name not in (None, ""):
        current_class.teacher_name = new_teacher_name
    if new_class_time not in (None, ""):
        current_class.class_time = new_class_time
    if new_capacity not in (None, ""):
        current_class.capacity = new_capacity

    db.session.commit()
   
    return jsonify({"success": "Course updated successfully by administrator"}), 200

@app.route('/admin/update-student/', methods=['POST'])
@app.route('/admin/update-student/<int:student_id>', methods=['POST'])
def admin_update_student(student_id = None):
    """Allows administrators to rename or update an existing student via POST (Page 11)."""
    # Goal 1: Look up the target Student by primary key (db.session.get) and return 404 if None.
    # Goal 2: Validate and update student_name from 'data', then run db.session.commit().
    
    if student_id is None:
        return jsonify({"error": "No student ID provided"}), 400

    data = request.get_json(silent=True)
    if not isinstance(data, dict):
        return jsonify({"error": "Invalid or missing JSON object"}), 400
        
    current_student = db.session.get(Student, student_id)
    new_student_name = data.get('student_name')

    if student_id in (None, ""):
        return jsonify({ "error": "No student ID provided" }), 400
    if new_student_name in (None, ""):
        return jsonify({"error": "No student name provided"}), 400
    if current_student is None:
        return jsonify({"error": "Student not found"}), 404
    if Student.query.filter_by(student_name=new_student_name.strip()).first() is not None:
        return jsonify({"error": "Student name already exists"}), 409
    if not isinstance(new_student_name, str) or not any(c.isalpha() for c in new_student_name):
        return jsonify({"error": "Invalid student name provided"}), 400

    current_student.student_name = new_student_name.strip()
    db.session.commit()

    return jsonify({"success": "Student updated successfully by administrator"}), 200

@app.route('/admin/delete-class/', methods=['DELETE'])
@app.route('/admin/delete-class/<int:class_id>', methods=['DELETE'])
def admin_delete_class(class_id = None):
    """Allows administrators to remove an existing course from the database (Page 11)."""
    # Goal 1: Look up the target Class by primary key (db.session.get) and return 404 if None.
    # Goal 2 (Order Matters): Query and delete all child Enrollment rows matching class_id FIRST
    #         so foreign key links are cleared without deleting the Student accounts themselves.
    # Goal 3: Delete the parent Class row from the classes table and run db.session.commit().
    
    if class_id is None:
        return jsonify({"error": "Class ID must be provided"}), 400

    target_class = db.session.get(Class, class_id)

    if target_class is None:
        return jsonify({"error": "Class not found"}), 404

    # Gather all rows matching the foreign key class_id from the junction table to prepare for deletion
    all_enrollments = Enrollment.query.filter_by(class_id=class_id).all()

    for e in all_enrollments:
        db.session.delete(e)
    db.session.delete(target_class)

    db.session.commit()

    return jsonify({"success": "Course successfully deleted by administrator"}), 200


@app.route('/admin/delete-student/', methods=['DELETE'])
@app.route('/admin/delete-student/<int:student_id>', methods=['DELETE'])
def admin_delete_student(student_id = None):
    """Allows administrators to permanently remove a student from the university database (Page 11)."""
    # Goal 1: Look up the target Student by primary key (db.session.get) and return 404 if None.
    # Goal 2 (Order Matters): Query and delete all child Enrollment rows matching student_id FIRST
    #         so foreign key links to the student are cleared (do NOT delete the Class rows themselves).
    # Goal 3: Delete the parent Student row from the students table and run db.session.commit().

    if student_id is None:
        return jsonify({"error": "Student ID must be provided"}), 400

    target_student = db.session.get(Student, student_id)

    if target_student is None:
            return jsonify({"error": "Student ID not found"}), 404
    
    # Gather all rows matching the foreign key student_id from the junction table to prepare for deletion
    all_enrollments = Enrollment.query.filter_by(student_id=student_id).all()

    for e in all_enrollments:
        db.session.delete(e)
    db.session.delete(target_student)

    db.session.commit()
    
    return jsonify({"success": "Student successfully removed from database"}), 200

@app.errorhandler(404)
def handle_404(e):
    return jsonify({"error": "Invalid ID or resource not found"}), 404

if __name__ == '__main__':
    # Launches the execution engine server on localhost port 5000.
    app.run(debug=True, port=5000)
