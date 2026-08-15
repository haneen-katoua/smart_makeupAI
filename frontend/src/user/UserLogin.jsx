import { useState } from "react";
import { useNavigate, Link } from "react-router-dom";

import api from "../services/api";
import "../styles/UserLogin.css";


function UserLogin() {

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
                "/api/login/",
                {
                    username: username.trim(),
                    password: password
                }
            );

            console.log(
                "User login successful:",
                response.data
            );


            const access = response.data.access;
            const refresh = response.data.refresh;


            if (!access || !refresh) {

                throw new Error(
                    "Login response does not contain tokens."
                );

            }


            localStorage.setItem(
                "access_token",
                access
            );

            localStorage.setItem(
                "refresh_token",
                refresh
            );


           navigate("/makeup-request");

        } catch (error) {

            console.error(
                "User login error:",
                error
            );


            if (error.response) {

                if (error.response.status === 401) {

                    setError(
                        "Invalid username or password."
                    );

                } else {

                    setError(
                        error.response.data?.detail ||
                        "Login failed. Please try again."
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

        <main className="user-login-page">

            <div className="user-login-card">


                <div className="user-login-brand">

                    <div className="user-login-logo">
                        SM
                    </div>

                    <h1>
                        Smart Makeup AI
                    </h1>

                    <p>
                        Welcome Back
                    </p>

                </div>


                <form
                    className="user-login-form"
                    onSubmit={handleSubmit}
                >


                    <div className="user-login-group">

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


                    <div className="user-login-group">

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

                        <div className="user-login-error">
                            {error}
                        </div>

                    )}


                    <button
                        type="submit"
                        className="user-login-button"
                        disabled={loading}
                    >

                        {loading
                            ? "Logging in..."
                            : "Login"
                        }

                    </button>


                </form>


                <div className="user-login-register">

                    <span>
                        Don't have an account?
                    </span>

                    <Link to="/register">
                        Create an account
                    </Link>

                </div>


            </div>

        </main>

    );

}


export default UserLogin;