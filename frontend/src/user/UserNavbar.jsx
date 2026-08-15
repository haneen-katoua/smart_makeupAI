import { useLocation } from "react-router-dom";
import "../styles/UserNavbar.css";
import { useNavigate } from "react-router-dom";

function UserNavbar() {

    const navigate = useNavigate();

    const handleLogout = () => {
    localStorage.removeItem("access_token");
    localStorage.removeItem("refresh_token");

    navigate("/login", { replace: true });
    };

    const location = useLocation();


    return (

        <nav className="user-navbar">

            <div className="user-navbar-container">


                {/* =================================================
                    LOGO
                ================================================= */}

                <button
                    className="user-navbar-logo"
                    onClick={() =>
                        navigate("/makeup-request")
                    }
                >
                    ✨ Smart Makeup AI
                </button>


                {/* =================================================
                    NAVIGATION
                ================================================= */}

                <div className="user-navbar-actions">


                    {/* MAKEUP ANALYSIS */}

                    <button
                        className={
                            `user-navbar-link ${
                                location.pathname === "/makeup-request"
                                    ? "active"
                                    : ""
                            }`
                        }
                        onClick={() =>
                            navigate("/makeup-request")
                        }
                    >
                        💄 Makeup Analysis
                    </button>


                    {/* PROFILE */}

                    <button
                        className={
                            `user-profile-button ${
                                location.pathname.startsWith("/profile")
                                    ? "active"
                                    : ""
                            }`
                        }
                        onClick={() =>
                            navigate("/profile")
                        }
                        title="My Profile"
                    >

                        <span className="user-profile-icon">
                            👤
                        </span>

                        <span>
                            Profile
                        </span>

                    </button>

                    <button
                className="logout-button"
                onClick={handleLogout}
                    >
                        Logout
                    </button>


                </div>

            </div>

        </nav>

    );

}


export default UserNavbar;