// Every call to the Flask backend lives in this file; components never call fetch() directly
// Each function matches one route in app.py. 

const BASE = import.meta.env.DEV ? "/api" : "";

async function request(path, method = "GET", body) {
    let res;
    try {
    res = await fetch(BASE + path, {
        method,
        headers: { "Content-Type": "application/json" },
        body: body === undefined ? undefined : JSON.stringify(body),
    });
  } 
  catch {
    throw new Error("Cannot reach the server. Is Flask running on port 5000?");
  }
  const data = await res.json();
  
  if (!res.ok) throw new Error(data.error || "Request failed");
  return data;
}

export const login = (username, password) => request("/login", "POST", { username, password });

// Reads
export const getCourses = () => request("/courses"); // class_id, class_name, teacher_name, time, enrolled, capacity
export const getStudents = () => request("/students"); // student_id, student_name
export const getEnrollments = () => request("/enrollments"); // enrollment_id, class_id, student_id, student_name, grade
export const getMyCourses = (studentId) => request(`/student/my-courses/${studentId}`);

// Student
export const enroll = (classId, studentId) => request(`/enroll/${classId}/${studentId}`, "POST");
export const drop = (classId, studentId) => request(`/drop/${classId}/${studentId}`, "POST");

// Teacher (grade must be sent as a number)
export const updateGrade = (classId, studentId, grade) =>
    request(`/teacher/update-grade/${classId}/${studentId}`, "POST", { grade: Number(grade) });

// Admin (fields = { class_name, teacher_name, class_time, capacity })
export const createClass = (fields) => request("/admin/create-class", "POST", fields);
export const updateClass = (classId, fields) => request(`/admin/update-class/${classId}`, "POST", fields);
export const deleteClass = (classId) => request(`/admin/delete-class/${classId}`, "DELETE");
export const updateStudent = (studentId, name) =>
    request(`/admin/update-student/${studentId}`, "POST", { student_name: name });
export const deleteStudent = (studentId) => request(`/admin/delete-student/${studentId}`, "DELETE");