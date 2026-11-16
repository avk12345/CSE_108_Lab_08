// Used by the student dashboard and the teacher dashboard.

export default function CourseTable({ courses, renderName, renderAction, actionHeader = "" }) {
    return (
        <div className="table-scroll" role="region" aria-label="Courses" tabIndex={0}>
            <table className="course-table">
                <thead>
                    <tr>
                        <th>Course Name</th>
                        <th>Teacher</th>
                        <th>Time</th>
                        <th>Students Enrolled</th>
                        {renderAction && <th>{actionHeader}</th>}
                    </tr>
                </thead>
                <tbody>
                    {courses.map((c) => (
                        <tr key={c.class_id}>
                            <td>{renderName ? renderName(c) : c.class_name}</td>
                            <td>{c.teacher_name}</td>
                            <td>{c.time}</td>
                            <td>
                                {c.enrolled}/{c.capacity}
                            </td>
                            {renderAction && <td className="action-cell">{renderAction(c)}</td>}
                        </tr>
                    ))}
                </tbody>
            </table>
        </div>
    );
}