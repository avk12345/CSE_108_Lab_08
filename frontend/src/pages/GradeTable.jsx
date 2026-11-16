import { useEffect, useState } from "react";
import { getEnrollments, updateGrade } from "../api";

export default function GradeTable({ course, onBack }) {
    const [rows, setRows] = useState([]);
    const [error, setError] = useState("");

    useEffect(() => {
        getEnrollments()
            .then((all) => setRows(all.filter((e) => e.class_id === course.class_id)))
            .catch((e) => setError(e.message));
    }, [course.class_id]);

    return (
        <section className="grade-page">
            <div className="tabs">
                <button type="button" className="back-link" aria-label="Back to your courses" onClick={onBack}>
                    ←
                </button>
                <div className="tab active">{course.class_name}</div>
            </div>

            <div className="tab-panel">
                {error && (
                    <p className="error" role="alert">
                        {error}
                    </p>
                )}
                <table className="grade-table">
                    <thead>
                        <tr>
                            <th>Student Name</th>
                            <th>Grade</th>
                        </tr>
                    </thead>
                    <tbody>
                        {rows.map((r) => (
                            <GradeRow key={r.enrollment_id} row={r} onError={setError} />
                        ))}
                    </tbody>
                </table>
            </div>
        </section>
    );
}

function GradeRow({ row, onError }) {
    const [grade, setGrade] = useState(row.grade ?? ""); 
    const [saved, setSaved] = useState(row.grade ?? ""); 

    async function save() {
        const text = String(grade).trim();
        if (text === String(saved)) return; 
        if (text === "" || Number.isNaN(Number(text))) {
            onError("Enter a number for the grade.");
            setGrade(saved);
            return;
        }
        try {
            await updateGrade(row.class_id, row.student_id, text);
            setSaved(text);
            setGrade(text);
            onError("");
        } catch (e) {
            onError(e.message); 
            setGrade(saved); 
        }
    }

    return (
        <tr>
            <td>{row.student_name}</td>
            <td>
                <input
                    className="grade-input"
                    aria-label={`Grade for ${row.student_name}`}
                    value={grade}
                    onChange={(e) => setGrade(e.target.value)}
                    onBlur={save}
                    onKeyDown={(e) => e.key === "Enter" && e.currentTarget.blur()}
                />
            </td>
        </tr>
    );
}