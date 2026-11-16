import { useState } from "react";
import { login } from "../api";

export default function Login({ onLogin }) {
    const [username, setUsername] = useState("");
    const [password, setPassword] = useState("");
    const [error, setError] = useState("");

    async function handleSubmit(e) {
        e.preventDefault();
        try {
            onLogin(await login(username.trim(), password));
        }
        catch (err) {
            setError(err.message);
        }
    }

    return (
        <div className="login-page">
            <h1 className="site-title">ACME University</h1>
            <form className="login-form" onSubmit={handleSubmit}>
                <label htmlFor="username">Username</label>
                <input id="username" value={username} onChange={(e) => setUsername(e.target.value)} required />

                <label htmlFor="password">Password</label>
                <input
                    id="password"
                    type="password"
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                    required
                />

                <button type="submit" className="signin-btn">
                    Sign in
                </button>

                {error && (
                    <p className="error" role="alert">
                        {error}
                    </p>
                )}
            </form>
        </div>
    );
}