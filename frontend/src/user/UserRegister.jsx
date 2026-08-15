import { useState } from "react";
import { useNavigate, Link } from "react-router-dom";

import api from "../services/api";
import "../styles/UserRegister.css";


function UserRegister() {

    const navigate = useNavigate();

    const [username, setUsername] = useState("");
    const [email, setEmail] = useState("");
    const [password, setPassword] = useState("");

    const [error, setError] = useState("");
    const [success, setSuccess] = useState("");

    const [loading, setLoading] = useState(false);


    const handleSubmit = async (event) => {

        event.preventDefault();

        setError("");
        setSuccess("");
        setLoading(true);


        try {

            const response = await api.post(
                "/api/accounts/register/",
                {
                    username: username.trim(),
                    email: email.trim(),
                    password: password
                }
            );


            console.log(
                "Registration successful:",
                response.data
            );


            setSuccess(
                "Account created successfully!"
            );


            setTimeout(() => {

                navigate("/login");

            }, 1200);


        } catch (error) {

            console.error(
                "Registration error:",
                error
            );


            if (error.response) {

                const data =
                    error.response.data;


                if (data.username) {

                    setError(
                        Array.isArray(data.username)
                            ? data.username[0]
                            : data.username
                    );

                } else if (data.email) {

                    setError(
                        Array.isArray(data.email)
                            ? data.email[0]
                            : data.email
                    );

                } else if (data.password) {

                    setError(
                        Array.isArray(data.password)
                            ? data.password[0]
                            : data.password
                    );

                } else if (data.detail) {

                    setError(
                        data.detail
                    );

                } else {

                    setError(
                        "Registration failed. Please check your information."
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

        <main className="user-register-page">

            <div className="user-register-card">


                <div className="user-register-brand">

                    <div className="user-register-logo">
                        SM
                    </div>

                    <h1>
                        Smart Makeup AI
                    </h1>

                    <p>
                        Create Your Account
                    </p>

                </div>


                <form
                    className="user-register-form"
                    onSubmit={handleSubmit}
                >


                    <div className="user-register-group">

                        <label htmlFor="register-username">
                            Username
                        </label>

                        <input
                            id="register-username"
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


                    <div className="user-register-group">

                        <label htmlFor="register-email">
                            Email
                        </label>

                        <input
                            id="register-email"
                            type="email"
                            value={email}
                            onChange={(event) =>
                                setEmail(
                                    event.target.value
                                )
                            }
                            placeholder="Enter your email"
                            autoComplete="email"
                            required
                        />

                    </div>


                    <div className="user-register-group">

                        <label htmlFor="register-password">
                            Password
                        </label>

                        <input
                            id="register-password"
                            type="password"
                            value={password}
                            onChange={(event) =>
                                setPassword(
                                    event.target.value
                                )
                            }
                            placeholder="Create a password"
                            autoComplete="new-password"
                            required
                        />

                    </div>


                    {error && (

                        <div className="user-register-error">
                            {error}
                        </div>

                    )}


                    {success && (

                        <div className="user-register-success">
                            {success}
                        </div>

                    )}


                    <button
                        type="submit"
                        className="user-register-button"
                        disabled={loading}
                    >

                        {loading
                            ? "Creating Account..."
                            : "Create Account"
                        }

                    </button>


                </form>


                <div className="user-register-login">

                    <span>
                        Already have an account?
                    </span>

                    <Link to="/login">
                        Login
                    </Link>

                </div>


            </div>

        </main>

    );

}


export default UserRegister;