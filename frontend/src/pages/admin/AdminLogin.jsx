import { useState } from "react";
import api from "../../services/api";
import "../../styles/AdminLogin.css";
import { useNavigate } from "react-router-dom";

function AdminLogin() {
    const navigate = useNavigate();
    const [username, setUsername] = useState("");
    const [password, setPassword] = useState("");

    const [error, setError] = useState("");
    const [loading, setLoading] = useState(false);

    const handleSubmit = async (event) => {
        event.preventDefault();

        setError("");
        setLoading(true);

        try {
            const response = await api.post(
                "/api/accounts/admin/login/",
                {
                    username,
                    password,
                }
            );

            console.log("Login successful:", response.data);

            const { access, refresh } = response.data;

            localStorage.setItem("access_token", access);
            localStorage.setItem("refresh_token", refresh);

            navigate("/admin/dashboard");

        } catch (error) {
            console.error("Login error:", error);

            if (error.response) {
                if (error.response.status === 401) {
                    setError(
                        "Invalid username or password."
                    );
                } else if (error.response.status === 400) {
                    setError(
                        "You do not have admin access."
                    );
                } else {
                    setError(
                        "Something went wrong. Please try again."
                    );
                }
            } else {
                setError(
                    "Cannot connect to the server."
                );
            }
        } finally {
            setLoading(false);
        }
    };

    return (
        <main className="admin-login-page">

            <section className="admin-login-card">

                <div className="admin-login-brand">

                    <div className="admin-logo">
                        SM
                    </div>

                    <h1>
                        Smart Makeup AI
                    </h1>

                    <p>
                        Admin Panel
                    </p>

                </div>

                <form
                    className="admin-login-form"
                    onSubmit={handleSubmit}
                >

                    <div className="admin-form-group">

                        <label htmlFor="username">
                            Username
                        </label>

                        <input
                            id="username"
                            type="text"
                            value={username}
                            onChange={(event) =>
                                setUsername(
                                    event.target.value
                                )
                            }
                            placeholder="Enter your username"
                            autoComplete="username"
                            required
                        />

                    </div>

                    <div className="admin-form-group">

                        <label htmlFor="password">
                            Password
                        </label>

                        <input
                            id="password"
                            type="password"
                            value={password}
                            onChange={(event) =>
                                setPassword(
                                    event.target.value
                                )
                            }
                            placeholder="Enter your password"
                            autoComplete="current-password"
                            required
                        />

                    </div>

                    {error && (
                        <div className="admin-login-error">
                            {error}
                        </div>
                    )}

                    <button
                        type="submit"
                        className="admin-login-button"
                        disabled={loading}
                    >
                        {loading
                            ? "Logging in..."
                            : "Login"}
                    </button>

                </form>

            </section>

        </main>
    );
}

export default AdminLogin;