import { useState } from "react";
import Login from "./pages/Login";
import StudentDashboard from "./pages/StudentDashboard";
import TeacherDashboard from "./pages/TeacherDashboard";
import AdminDashboard from "./pages/AdminDashboard";

export default function App() {
    const [user, setUser] = useState(null);

    if (!user) return <Login onLogin={setUser} />;

    return (
        <div className="app">
            <header className="navbar">
                <span className="welcome">Welcome {user.display_name}!</span>
                <h1 className="site-title">ACME University</h1>
                <button type="button" className="signout-link" onClick={() => setUser(null)}>
                    Sign out
                </button>
            </header>

            <main className="content">
                {user.role === "student" && <StudentDashboard user={user} />}
                {user.role === "teacher" && <TeacherDashboard user={user} />}
                {user.role === "admin" && <AdminDashboard />}
            </main>
        </div>
    );
}