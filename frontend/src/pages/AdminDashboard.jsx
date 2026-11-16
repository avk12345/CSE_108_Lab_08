import { useEffect, useState } from "react";
import {
    createClass,
    deleteClass,
    deleteStudent,
    getCourses,
    getStudents,
    updateClass,
    updateStudent,
} from "../api";

export default function AdminDashboard() {
    const [tab, setTab] = useState("courses"); 

    return (
        <section className="admin-dashboard">
            <div className="tabs">
                <button
                    type="button"
                    className={`tab ${tab === "courses" ? "active" : ""}`}
                    onClick={() => setTab("courses")}
                >
                    Courses
                </button>
                <button
                    type="button"
                    className={`tab ${tab === "students" ? "active" : ""}`}
                    onClick={() => setTab("students")}
                >
                    Students
                </button>
            </div>
            <div className="tab-panel">{tab === "courses" ? <CoursesPanel /> : <StudentsPanel />}</div>
        </section>
    );
}


const bind = (state, setState, key) => ({
    value: state[key],
    onChange: (e) => setState({ ...state, [key]: e.target.value }),
});


const EMPTY_COURSE = { class_name: "", teacher_name: "", class_time: "", capacity: "" };
const toBody = (f) => ({ ...f, capacity: parseInt(f.capacity, 10) }); 

function CoursesPanel() {
    const [courses, setCourses] = useState([]);
    const [form, setForm] = useState(EMPTY_COURSE); 
    const [editingId, setEditingId] = useState(null);
    const [draft, setDraft] = useState(EMPTY_COURSE); 
    const [error, setError] = useState("");

    const load = () => getCourses().then(setCourses).catch((e) => setError(e.message));
    useEffect(() => {
        load();
    }, []);

    async function run(action) {
        setError("");
        try {
            await action();
            await load();
            return true;
        } catch (e) {
            setError(e.message);
            return false;
        }
    }

    async function create(e) {
        e.preventDefault();
        if (await run(() => createClass(toBody(form)))) setForm(EMPTY_COURSE);
    }

    function startEdit(c) {
        setEditingId(c.class_id);
        setDraft({
            class_name: c.class_name,
            teacher_name: c.teacher_name,
            class_time: c.time,
            capacity: String(c.capacity),
        });
    }

    async function save(id) {
        if (await run(() => updateClass(id, toBody(draft)))) setEditingId(null);
    }

    function remove(c) {
        if (window.confirm(`Delete ${c.class_name}?`)) run(() => deleteClass(c.class_id));
    }

    return (
        <div className="admin-panel">
            <form className="admin-form" onSubmit={create}>
                <h2>Add a course</h2>
                <input aria-label="Course name" placeholder="Course name (e.g. CS 106)" {...bind(form, setForm, "class_name")} />
                <input aria-label="Teacher name" placeholder="Teacher name" {...bind(form, setForm, "teacher_name")} />
                <input aria-label="Class time" placeholder="Time (e.g. MWF 2:00-2:50 PM)" {...bind(form, setForm, "class_time")} />
                <input aria-label="Capacity" type="number" min="1" placeholder="Capacity" {...bind(form, setForm, "capacity")} />
                <button type="submit" className="create-btn">
                    Create course
                </button>
            </form>

            {error && (
                <p className="error" role="alert">
                    {error}
                </p>
            )}

            <div className="table-scroll" role="region" aria-label="Manage courses" tabIndex={0}>
                <table className="admin-table">
                    <thead>
                        <tr>
                            <th>Course Name</th>
                            <th>Teacher</th>
                            <th>Time</th>
                            <th>Enrolled</th>
                            <th>Capacity</th>
                            <th>Actions</th>
                        </tr>
                    </thead>
                    <tbody>
                        {courses.map((c) =>
                            editingId === c.class_id ? (
                                <tr key={c.class_id}>
                                    <td>
                                        <input aria-label="Edit course name" {...bind(draft, setDraft, "class_name")} />
                                    </td>
                                    <td>
                                        <input aria-label="Edit teacher name" {...bind(draft, setDraft, "teacher_name")} />
                                    </td>
                                    <td>
                                        <input aria-label="Edit class time" {...bind(draft, setDraft, "class_time")} />
                                    </td>
                                    <td>{c.enrolled}</td>
                                    <td>
                                        <input aria-label="Edit capacity" type="number" min="1" {...bind(draft, setDraft, "capacity")} />
                                    </td>
                                    <td className="action-cell">
                                        <button type="button" className="save-btn" onClick={() => save(c.class_id)}>
                                            Save
                                        </button>
                                        <button type="button" className="cancel-btn" onClick={() => setEditingId(null)}>
                                            Cancel
                                        </button>
                                    </td>
                                </tr>
                            ) : (
                                <tr key={c.class_id}>
                                    <td>{c.class_name}</td>
                                    <td>{c.teacher_name}</td>
                                    <td>{c.time}</td>
                                    <td>{c.enrolled}</td>
                                    <td>{c.capacity}</td>
                                    <td className="action-cell">
                                        <button type="button" className="edit-btn" aria-label={`Edit ${c.class_name}`} onClick={() => startEdit(c)}>
                                            Edit
                                        </button>
                                        <button type="button" className="delete-btn" aria-label={`Delete ${c.class_name}`} onClick={() => remove(c)}>
                                            Delete
                                        </button>
                                    </td>
                                </tr>
                            )
                        )}
                    </tbody>
                </table>
            </div>
        </div>
    );
}

function StudentsPanel() {
    const [students, setStudents] = useState([]);
    const [editingId, setEditingId] = useState(null);
    const [nameDraft, setNameDraft] = useState("");
    const [error, setError] = useState("");

    const load = () => getStudents().then(setStudents).catch((e) => setError(e.message));
    useEffect(() => {
        load();
    }, []);

    async function run(action) {
        setError("");
        try {
            await action();
            await load();
            return true;
        } catch (e) {
            setError(e.message);
            return false;
        }
    }

    function startEdit(s) {
        setEditingId(s.student_id);
        setNameDraft(s.student_name);
    }

    async function save(id) {
        if (await run(() => updateStudent(id, nameDraft))) setEditingId(null);
    }

    function remove(s) {
        if (window.confirm(`Delete ${s.student_name}?`)) run(() => deleteStudent(s.student_id));
    }

    return (
        <div className="admin-panel">
            {error && (
                <p className="error" role="alert">
                    {error}
                </p>
            )}

            <div className="table-scroll" role="region" aria-label="Manage students" tabIndex={0}>
                <table className="admin-table">
                    <thead>
                        <tr>
                            <th>ID</th>
                            <th>Student Name</th>
                            <th>Actions</th>
                        </tr>
                    </thead>
                    <tbody>
                        {students.map((s) =>
                            editingId === s.student_id ? (
                                <tr key={s.student_id}>
                                    <td>{s.student_id}</td>
                                    <td>
                                        <input aria-label="Edit student name" value={nameDraft} onChange={(e) => setNameDraft(e.target.value)} />
                                    </td>
                                    <td className="action-cell">
                                        <button type="button" className="save-btn" onClick={() => save(s.student_id)}>
                                            Save
                                        </button>
                                        <button type="button" className="cancel-btn" onClick={() => setEditingId(null)}>
                                            Cancel
                                        </button>
                                    </td>
                                </tr>
                            ) : (
                                <tr key={s.student_id}>
                                    <td>{s.student_id}</td>
                                    <td>{s.student_name}</td>
                                    <td className="action-cell">
                                        <button type="button" className="edit-btn" aria-label={`Rename ${s.student_name}`} onClick={() => startEdit(s)}>
                                            Rename
                                        </button>
                                        <button type="button" className="delete-btn" aria-label={`Delete ${s.student_name}`} onClick={() => remove(s)}>
                                            Delete
                                        </button>
                                    </td>
                                </tr>
                            )
                        )}
                    </tbody>
                </table>
            </div>
        </div>
    );
}