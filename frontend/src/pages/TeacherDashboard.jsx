import { useEffect, useState } from "react";
import { getCourses } from "../api";
import CourseTable from "../components/CourseTable";
import GradeTable from "./GradeTable";

export default function TeacherDashboard({ user }) {
    const [courses, setCourses] = useState([]);
    const [selected, setSelected] = useState(null); 
    const [error, setError] = useState("");

    useEffect(() => {
        // There is no classes for this teacher, so filter all courses by teacher name.
        getCourses()
            .then((all) => setCourses(all.filter((c) => c.teacher_name === user.display_name)))
            .catch((e) => setError(e.message));
    }, [user.display_name]);

    if (selected) return <GradeTable course={selected} onBack={() => setSelected(null)} />;

    return (
        <section className="teacher-dashboard">
            <div className="tabs">
                <div className="tab active">Your Courses</div>
            </div>

            <div className="tab-panel">
                {error && (
                    <p className="error" role="alert">
                        {error}
                    </p>
                )}
                <CourseTable
                    courses={courses}
                    renderName={(c) => (
                        <a
                            href="#"
                            className="course-link"
                            onClick={(e) => {
                                e.preventDefault();
                                setSelected(c);
                            }}
                        >
                            {c.class_name}
                        </a>
                    )}
                />
            </div>
        </section>
    );
}