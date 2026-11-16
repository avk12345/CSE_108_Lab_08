import { useEffect, useState } from "react";
import { drop, enroll, getCourses, getMyCourses } from "../api";
import CourseTable from "../components/CourseTable";

export default function StudentDashboard({ user }) {
    const [tab, setTab] = useState("mine"); 
    const [courses, setCourses] = useState([]); 
    const [myIds, setMyIds] = useState([]); 
    const [error, setError] = useState("");

    async function load() {
        try {
            const [all, mine] = await Promise.all([getCourses(), getMyCourses(user.student_id)]);
            setCourses(all);
            setMyIds(mine.map((c) => c.class_id));
        } 
        catch (e) {
            setError(e.message);
        }
    }

    useEffect(() => {
        load();
    }, []);

    // Add or drop a class, show the backend's error if it refuses, then reload.
    async function change(action, classId) {
        setError("");
        try {
            await action(classId, user.student_id);
        } 
        catch (e) {
            setError(e.message);
        }
        load();
    }

    function renderAction(c) {
        if (myIds.includes(c.class_id)) {
            return (
                <button
                    type="button"
                    className="drop-btn"
                    aria-label={`Drop ${c.class_name}`}
                    onClick={() => change(drop, c.class_id)}
                >
                    −
                </button>
            );
        }
        if (c.enrolled < c.capacity) {
            return (
                <button
                    type="button"
                    className="add-btn"
                    aria-label={`Add ${c.class_name}`}
                    onClick={() => change(enroll, c.class_id)}
                >
                    +
                </button>
            );
        }
        return null; // class is full: no button
    }

    return (
        <section className="student-dashboard">
            <div className="tabs">
                <button
                    type="button"
                    className={`tab ${tab === "mine" ? "active" : ""}`}
                    onClick={() => setTab("mine")}
                >
                    Your Courses
                </button>
                <button
                    type="button"
                    className={`tab ${tab === "add" ? "active" : ""}`}
                    onClick={() => setTab("add")}
                >
                    Add Courses
                </button>
            </div>

            <div className="tab-panel">
                {error && (
                    <p className="error" role="alert">
                        {error}
                    </p>
                )}
                {tab === "mine" ? (
                    <CourseTable courses={courses.filter((c) => myIds.includes(c.class_id))} />
                ) : (
                    <CourseTable courses={courses} actionHeader="Add class" renderAction={renderAction} />
                )}
            </div>
        </section>
    );
}