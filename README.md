# The Absolute Final Database Blueprint

The entire backend application communicates with a single SQLite database file containing three tables:

```text
                     +----------------------------------------+

                     |           university.sqlite            |
                     +----------------------------------------+
+---------------+         +-----------------+              +---------------+

|    CLASSES    |         |   ENROLLMENTS   |              |   STUDENTS    |
+---------------+         +-----------------+              +---------------+

| id (PK)       |----+--->| id (PK)         |              | id (PK)       |
| class_name    |         | class_id (FK)   |              | student_name  |
| teacher_name  |         | student_id (FK) |<-------------+               |
| class_time    |         | grade           |              +---------------+
| capacity      |         +-----------------+                         
+---------------+
```

---

# ACME University Enrollment System - Backend API Specification

> **IMPORTANT TEAM DISCLAIMER (CORS & Standalone HTML/CSS vs. React Setup):**
> By default, `from flask_cors import CORS` and `CORS(app)` at the top of `app.py` are **commented out** so teammates testing standalone HTML/CSS templates served directly by Flask (`http://localhost:5000`) can run the server immediately without extra packages.
> * **If testing via Flask's `templates/` folder (HTML/CSS/Vanilla JS on port 5000):** Leave both CORS lines commented out. Only `pip install flask flask-sqlalchemy` is needed.
> * **If connecting an external React dev server (e.g., `localhost:3000` or `localhost:5173`):** Run `pip install flask-cors` and uncomment `# from flask_cors import CORS` (Line 4) and `# CORS(app)` (Line 7) in `app.py` so the browser allows cross-port `fetch()` requests.

## Overview & Server Setup
This stateless Flask backend serves as the REST API and SQLite persistence layer for the ACME University Enrollment Web App. Every endpoint, including invalid or malformed URL routes, returns a structured JSON payload so frontend response.json() calls never fail on HTML error pages.

* **Base URL:** `http://localhost:5000`
* **Core Dependencies:** `pip install flask flask-sqlalchemy` *(plus `flask-cors` only if running a separate React port)*
* **Launch Command:** `python app.py`
* **Required Headers for JSON Payloads:** `Content-Type: application/json`

> **Stateless Architecture & Global Safety Contracts:**
> * **Built-In Live Test Bench (`/`):** Visit `http://localhost:5000/` in a browser to open `templates/index.html` (the CSE 108 Data Tier Test Bench) and verify all 12 endpoints independently of React.
> * **Frontend Owns Session State:** Store the object returned by `POST /login` (`role`, `display_name`, and `student_id` for students) in frontend state or `localStorage`. All API routes operate statelessly using the parameters passed in each request.
> * **URL Paths ALWAYS use Positive Integer IDs** (`student_id`, `class_id`), never names (e.g., `/enroll/1/2`, **not** `/enroll/Math%20101/Jose%20Santos`). No `encodeURIComponent` is needed.
> * **Names (`username`, `student_name`, `class_name`) ONLY go inside JSON bodies** (`POST`) or get displayed as UI text.
> * **Global Missing/Malformed JSON Body Guard (`400 Bad Request`):** All `POST` endpoints expecting a JSON body (`login`, `update-grade`, `create-class`, `update-class`, `update-student`) return `{ "error": "Invalid or missing JSON object" }` (`400`) if the `Content-Type: application/json` header is missing or the payload is not a JSON object.
> * **Global Invalid URL / Non-Positive ID Fallback (`404 Not Found`):** Passing negative integers (e.g., `-5000`), non-numeric strings (e.g., `abc`), or unknown paths to any `<int:...>` route automatically returns `{ "error": "Invalid ID or resource not found" }` (`404`).

---

## 1. Authentication & Session Initialization

### `POST /login`
Authenticates users across `student`, `teacher`, and `admin` roles. If a student username does not yet exist in the database, the backend automatically registers a new student record and returns their assigned `student_id`.

* **Request Body (JSON):**

    {
      "username": "Jose Santos",
      "password": "password123"
    }

* **Responses:**
  * **`200 OK` (Student):**

      {
        "role": "student",
        "student_id": 1,
        "display_name": "Jose Santos",
        "is_new_student": false,
        "message": "Existing student login successful"
      }

    *(Note: When `is_new_student` is `true`, `message` returns `"New student registered and logged in"`.)*
  * **`200 OK` (Teacher - `username: "ahepworth"`):**

      {
        "role": "teacher",
        "display_name": "Dr Hepworth"
      }

    *(Note: Initial database seeding pre-populates "CS 106" under "teacher_name": "Dr Hepworth" with Jose Santos enrolled at 95.0, so the Teacher dashboard works immediately upon filtering GET /courses by display_name.)*

  * **`200 OK` (Admin - `username: "admin"`):**

      {
        "role": "admin",
        "display_name": "System Administrator"
      }

  * **`400 Bad Request`:** `{ "error": "Username must contain at least one letter" }`
  * **`401 Unauthorized`:** `{ "error": "Invalid password credentials" }`

---

## 2. Read Endpoints (`GET`)

### `GET /courses`
Retrieves the master course catalog sorted alphabetically (`A-Z`) by `class_name`, including live enrollment counts.

* **URL Parameters:** None
* **Response (`200 OK` - Array of Objects):**

    [
      {
        "class_id": 1,
        "class_name": "Math 101",
        "teacher_name": "Ralph Jenkins",
        "time": "MWF 10:00-10:50 AM",
        "enrolled": 1,
        "capacity": 2
      }
    ]

* **Frontend Usage Notes:**
  * Format seat availability as `${course.enrolled}/${course.capacity}`.
  * Disable enrollment actions when `course.enrolled >= course.capacity`.
  * Filter by `course.teacher_name === user.display_name` to populate the Teacher dashboard.

### `GET /student/my-courses/<int:student_id>`
Retrieves the personal enrolled schedule and current grades for a specific student.

* **URL Parameters:** `student_id` (positive integer)
* **Responses:**
  * **`200 OK` (Array of Objects):**

      [
        {
          "student_name": "Jose Santos",
          "class_id": 1,
          "class_name": "Math 101",
          "teacher_name": "Ralph Jenkins",
          "time": "MWF 10:00-10:50 AM",
          "grade": 92.5
        }
      ]

    *(Note: Returns an empty array `[]` if the student exists but is enrolled in zero classes. `grade` will be `null` until an instructor assigns a score.)*
  * **`404 Not Found`:** `{ "error": "Student not found" }`

### `GET /students`
Retrieves all registered students in the database.

* **URL Parameters:** None
* **Response (`200 OK` - Array of Objects):**

    [
      {
        "student_id": 1,
        "student_name": "Jose Santos"
      }
    ]

### `GET /enrollments`
Retrieves all student-course junction records across the university.

* **URL Parameters:** None
* **Response (`200 OK` - Array of Objects):**

    [
      {
        "enrollment_id": 1,
        "class_id": 1,
        "class_name": "Math 101",
        "student_id": 1,
        "student_name": "Jose Santos",
        "grade": 92.5
      }
    ]

* **Frontend Usage Notes:** Filter this list by `item.class_id` when a teacher selects a specific course to view or edit student grades.

---

## 3. Student Operations (`POST`)

### `POST /enroll/<int:chosen_class_id>/<int:chosen_student_id>`
Enrolls a student in a course after validating course capacity and preventing duplicate sign-ups.

* **URL Parameters:** `chosen_class_id` (integer), `chosen_student_id` (integer)
* **Request Body:** None
* **Responses:**
  * **`201 Created`:** `{ "success": "Student successfully enrolled" }`
  * **`400 Bad Request`:** `{ "error": "Class is full" }`
  * **`404 Not Found`:** `{ "error": "Class not found" }` or `{ "error": "Student not found" }`
  * **`409 Conflict`:** `{ "error": "Student already enrolled in this class" }`

### `POST /drop/<int:chosen_class_id>/<int:chosen_student_id>`
Removes an existing enrollment record for a student in a specific course. The student account and all other enrollments remain intact.

* **URL Parameters:** `chosen_class_id` (integer), `chosen_student_id` (integer)
* **Request Body:** None
* **Responses:**
  * **`200 OK`:** `{ "success": "Course dropped successfully" }`
  * **`404 Not Found`:** `{ "error": "Enrollment record not found" }`

---

## 4. Teacher Operations (`POST`)

### `POST /teacher/update-grade/<int:class_id>/<int:student_id>`
Updates a student's grade for a specific enrolled course.

* **URL Parameters:** `class_id` (integer), `student_id` (integer)
* **Request Body (JSON):**

    {
      "grade": 95.0
    }

  *(Important: Because `grade` is passed inside the `fetch` body rather than a URL path variable, run `parseFloat()` on the input value before `JSON.stringify()` so that it arrives as a real float/int between `0` and `100`, not a string.)*
* **Responses:**
  * **`200 OK`:** `{ "success": "Grade sheet updated successfully" }`
  * **`400 Bad Request` (Missing URL IDs on `/teacher/update-grade/`):** `{ "error": "Class ID, Student ID, and Grade must all be provided" }`
  * **`400 Bad Request` (Missing, string, or out-of-range grade):** `{ "error": "Invalid or missing new grade provided" }`
  * **`404 Not Found`:** `{ "error": "Enrollment record not found" }`

---

## 5. Administrator Operations (`POST` & `DELETE`)

> **Database Integrity Guarantee:** All administrative delete endpoints automatically clean up dependent child records in the `enrollments` table before removing the target parent record from `classes` or `students`.

### `POST /admin/create-class`
Adds a new course to the master catalog.

* **URL Parameters:** None
* **Request Body (JSON):**

    {
      "class_name": "CS 106",
      "teacher_name": "Dr Hepworth",
      "class_time": "MWF 2:00-2:50 PM",
      "capacity": 10
    }

* **Validation Rules:**
  * `class_name`: String containing at least one letter, one digit, and an internal space (e.g., `"CS 106"`).
  * `teacher_name`: String containing at least one letter.
  * `class_time`: String containing letters, digits, `:`, `-`, and an internal space (e.g., `"MWF 2:00-2:50 PM"`).
  * `capacity`: Run `parseInt()` before `JSON.stringify()` so it arrives as a positive integer `> 0`, not a string.
* **Responses:**
  * **`201 Created`:** `{ "success": "New course successfully created by administrator" }`
  * **`400 Bad Request` (Specific field validation errors):**
    * `{ "error": "Invalid course name, must use format [Course Name Course Num]" }`
    * `{ "error": "Invalid teacher name" }`
    * `{ "error": "Invalid format. Use [Days StartTime-EndTime AM/PM], such as [TTh 10:00-11:15 AM]" }`
    * `{ "error": "Invalid course capacity" }`
  * **`409 Conflict`:** `{ "error": "Class name already exists" }`

### `POST /admin/update-class/<int:class_id>`
Updates an existing course's details (name, teacher, time, and capacity).

* **URL Parameters:** `class_id` (integer)
* **Request Body (JSON):**

    {
      "class_name": "CS 106",
      "teacher_name": "Dr Hepworth",
      "class_time": "MWF 2:00-2:50 PM",
      "capacity": 15
    }

  *(Important: All fields are optional for partial updates. Omitted keys, `null`, or empty strings `""` are skipped so current values stay intact. Provided fields enforce the same validation rules as `POST /admin/create-class`. Run `parseInt()` on `capacity` in the frontend before `JSON.stringify()` to send a true integer `> 0`.)*
* **Responses:**
  * **`200 OK`:** `{ "success": "Course updated successfully by administrator" }`
  * **`400 Bad Request` (Missing `class_id` on `/admin/update-class/`):** `{ "error": "Class ID must be provided" }`
  * **`400 Bad Request` (All fields empty/omitted):** `{ "error": "At least one field to update must be provided" }`
  * **`400 Bad Request` (Specific field validation errors):**
    * `{ "error": "Invalid course name, must use format [Course Name Course Num]" }`
    * `{ "error": "Invalid teacher name" }`
    * `{ "error": "Invalid format. Use [Days StartTime-EndTime AM/PM], such as [TTh 10:00-11:15 AM]" }`
    * `{ "error": "Invalid course capacity" }`
  * **`404 Not Found`:** `{ "error": "Class not found" }`
  * **`409 Conflict`:** `{ "error": "Class name already exists" }`

---

### `POST /admin/update-student/<int:student_id>`
Updates an existing student's name in the database.

* **URL Parameters:** `student_id` (integer)
* **Request Body (JSON):**

    {
      "student_name": "Jose A. Santos"
    }

  *(Important: `student_name` must be a unique string containing at least one letter, matching the username rule in `POST /login`.)*
* **Responses:**
  * **`200 OK`:** `{ "success": "Student updated successfully by administrator" }`
  * **`400 Bad Request` (Missing `student_id` on `/admin/update-student/`):** `{ "error": "No student ID provided" }`
  * **`400 Bad Request` (Empty/missing `student_name`):** `{ "error": "No student name provided" }`
  * **`400 Bad Request` (Non-string or no letters):** `{ "error": "Invalid student name provided" }`
  * **`404 Not Found`:** `{ "error": "Student not found" }`
  * **`409 Conflict`:** `{ "error": "Student name already exists" }`

### `DELETE /admin/delete-class/<int:class_id>`
Permanently deletes a course from the catalog and clears all associated enrollment links first. Student accounts remain untouched.

* **URL Parameters:** `class_id` (integer)
* **Request Body:** None
* **Responses:**
  * **`200 OK`:** `{ "success": "Course successfully deleted by administrator" }`
  * **`400 Bad Request` (Missing `class_id` on `/admin/delete-class/`):** `{ "error": "Class ID must be provided" }`
  * **`404 Not Found`:** `{ "error": "Class not found" }`

### `DELETE /admin/delete-student/<int:student_id>`
Permanently removes a student account and clears all associated enrollment links first. Course records remain untouched.

* **URL Parameters:** `student_id` (integer)
* **Request Body:** None
* **Responses:**
  * **`200 OK`:** `{ "success": "Student successfully removed from database" }`
  * **`400 Bad Request` (Missing `student_id` on `/admin/delete-student/`):** `{ "error": "Student ID must be provided" }`
  * **`404 Not Found`:** `{ "error": "Student ID not found" }`

---