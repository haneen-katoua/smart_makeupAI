import {
    useEffect,
    useState
} from "react";

import {
    useNavigate
} from "react-router-dom";

import api from "../services/api";

import UserNavbar from "./UserNavbar";

import "../styles/UserProfile.css";


function UserProfile() {

    const navigate = useNavigate();


    const [profile, setProfile] = useState(null);

    const [analyses, setAnalyses] = useState([]);


    const [loading, setLoading] = useState(true);

    const [error, setError] = useState("");

    const [editing, setEditing] = useState(false);

    const [editData, setEditData] = useState({
        first_name: "",
        last_name: ""
    });

    const [saving, setSaving] = useState(false);

    const handleEditChange = (event) => {

    const { name, value } = event.target;

    setEditData((prev) => ({
        ...prev,
        [name]: value
    }));

    };

    const handleSaveProfile = async () => {

    try {

        setSaving(true);
        setError("");

        const response = await api.patch(
            "/api/accounts/profile/",
            {
                first_name: editData.first_name,
                last_name: editData.last_name
            }
        );

        setProfile(response.data);

        setEditData({
            first_name: response.data.first_name || "",
            last_name: response.data.last_name || ""
        });

        setEditing(false);

    } catch (error) {

        console.error(
            "UPDATE PROFILE ERROR:",
            error
        );

        setError(
            error.response?.data?.detail ||
            "Could not update your profile."
        );

    } finally {

        setSaving(false);

    }

    };


    // =====================================================
    // LOAD PROFILE + ANALYSES
    // =====================================================

    useEffect(() => {

        loadProfileData();

    }, []);


    const loadProfileData = async () => {

        try {

            setLoading(true);

            setError("");


            // -------------------------------------------------
            // USER PROFILE
            // -------------------------------------------------

            const profileResponse =
                await api.get(
                    "/api/accounts/profile/"
                );


            console.log(
                "USER PROFILE:",
                profileResponse.data
            );


            setProfile(
                profileResponse.data
            );

            setEditData({
            first_name: profileResponse.data.first_name || "",
            last_name: profileResponse.data.last_name || ""
        });


            // -------------------------------------------------
            // USER ANALYSES
            // -------------------------------------------------

            const analysesResponse =
                await api.get(
                    "/api/analysis/my-analyses/"
                );


            console.log(
                "USER ANALYSES:",
                analysesResponse.data
            );


            /*
             * ListAPIView normally returns:
             *
             * {
             *     count: ...,
             *     next: ...,
             *     previous: ...,
             *     results: [...]
             * }
             *
             * But if pagination is disabled,
             * it may directly return an array.
             */


            const analysisData =
                Array.isArray(
                    analysesResponse.data
                )
                    ? analysesResponse.data
                    : analysesResponse.data?.results || [];


            setAnalyses(
                analysisData
            );


        } catch (error) {

            console.error(
                "USER PROFILE ERROR:",
                error
            );


            setError(
                error.response?.data?.detail ||
                "Could not load your profile."
            );

        } finally {

            setLoading(false);

        }

    };


    // =====================================================
    // IMAGE URL
    // =====================================================

    const getImageUrl = (image) => {

        if (!image) {
            return null;
        }


        if (
            image.startsWith("http://") ||
            image.startsWith("https://")
        ) {

            return image;

        }


        return `http://127.0.0.1:8000/${image.replace(/^\/+/, "")}`;

    };


    // =====================================================
    // FORMAT DATE
    // =====================================================

    const formatDate = (date) => {

        if (!date) {
            return "-";
        }


        return new Date(date).toLocaleDateString(
            undefined,
            {
                year: "numeric",
                month: "long",
                day: "numeric"
            }
        );

    };


    // =====================================================
    // LOADING
    // =====================================================

    if (loading) {

        return (

            <>

                <UserNavbar />


                <div className="user-profile-loading">

                    <div className="profile-loading-spinner">
                    </div>

                    <h2>
                        Loading your profile...
                    </h2>

                </div>

            </>

        );

    }


    // =====================================================
    // ERROR
    // =====================================================

    if (error) {

        return (

            <>

                <UserNavbar />


                <div className="user-profile-error">

                    <h2>
                        Something went wrong
                    </h2>

                    <p>
                        {error}
                    </p>


                    <button
                        onClick={loadProfileData}
                    >
                        Try Again
                    </button>

                </div>

            </>

        );

    }


    // =====================================================
    // PAGE
    // =====================================================

    return (

        <div className="user-profile-page">


            <UserNavbar />


            <main className="user-profile-container">


                {/* =================================================
                    PROFILE HEADER
                ================================================= */}

                <section className="profile-card">


                    <div className="profile-avatar">

                        👤

                    </div>


                    <div className="profile-main-info">

                        <h1>

                            {
                                profile?.first_name ||
                                profile?.last_name
                                    ? `${profile?.first_name || ""} ${profile?.last_name || ""}`.trim()
                                    : profile?.username || "User"
                            }

                        </h1>


                        <p className="profile-username">

                            @{profile?.username || "-"}

                        </p>


                        <p className="profile-email">

                            {profile?.email || "-"}

                        </p>

                    </div>

                </section>



                {/* =================================================
                    PROFILE INFORMATION
                ================================================= */}

                <section className="profile-information-card">


                    <div className="profile-section-title">

                        <h2>
                            Personal Information
                        </h2>

                        <p>
                            Your account information
                        </p>

                    </div>

                    {!editing && (
                    <button
                        className="edit-profile-button"
                        onClick={() => setEditing(true)}
                    >
                        ✏️ Edit Profile
                    </button>
                )}


                    <div className="profile-information-grid">


                        <div className="profile-information-item">

                            <span>
                                Username
                            </span>

                            <strong>
                                {profile?.username || "-"}
                            </strong>

                        </div>


                        <div className="profile-information-item">

                            <span>
                                Email
                            </span>

                            <strong>
                                {profile?.email || "-"}
                            </strong>

                        </div>


                        <div className="profile-information-item">

                            <span>
                                First Name
                            </span>

                            {editing ? (

                                <input
                                    type="text"
                                    name="first_name"
                                    value={editData.first_name}
                                    onChange={handleEditChange}
                                />

                            ) : (

                                <strong>
                                    {profile.first_name || "-"}
                                </strong>

                            )}

                        </div>


                        <div className="profile-information-item">

                            <span>
                                Last Name
                            </span>

                            {editing ? (

                                <input
                                    type="text"
                                    name="last_name"
                                    value={editData.last_name}
                                    onChange={handleEditChange}
                                />

                            ) : (

                                <strong>
                                    {profile.last_name || "-"}
                                </strong>

                            )}

                        </div>

                        {editing && (

                            <div className="profile-edit-actions">

                                <button
                                    className="save-profile-button"
                                    onClick={handleSaveProfile}
                                    disabled={saving}
                                >
                                    {saving ? "Saving..." : "Save Changes"}
                                </button>

                                <button
                                    className="cancel-profile-button"
                                    onClick={() => {

                                        setEditData({
                                            first_name: profile.first_name || "",
                                            last_name: profile.last_name || ""
                                        });

                                        setEditing(false);

                                    }}
                                    disabled={saving}
                                >
                                    Cancel
                                </button>

                            </div>

                        )}


                        <div className="profile-information-item">

                            <span>
                                Member Since
                            </span>

                            <strong>
                                {formatDate(profile?.date_joined)}
                            </strong>

                        </div>


                    </div>

                </section>



                {/* =================================================
                    ANALYSIS HISTORY
                ================================================= */}

                <section className="profile-analyses-section">


                    <div className="profile-section-title">

                        <div>

                            <h2>
                                My Makeup Analyses
                            </h2>

                            <p>
                                View your previous personalized makeup analyses.
                            </p>

                        </div>


                        <div className="analysis-total">

                            {analyses.length}

                        </div>

                    </div>



                    {/* =================================================
                        NO ANALYSES
                    ================================================= */}

                    {analyses.length === 0 ? (

                        <div className="no-analyses">

                            <div className="no-analyses-icon">
                                💄
                            </div>


                            <h3>
                                No makeup analyses yet
                            </h3>


                            <p>
                                Start your first makeup analysis
                                to see it here.
                            </p>


                            <button
                                onClick={() =>
                                    navigate("/makeup-request")
                                }
                            >
                                Start Makeup Analysis
                            </button>

                        </div>

                    ) : (


                        /* =================================================
                            ANALYSIS LIST
                        ================================================= */

                        <div className="analyses-list">


                            {
                                analyses.map((analysis) => {

                                    const imageUrl =
                                        getImageUrl(
                                            analysis.face_image
                                        );


                                    return (

                                        <article
                                            className="analysis-history-card"
                                            key={analysis.id}
                                            onClick={() =>
                                                navigate(
                                                    `/my-analyses/${analysis.id}`
                                                )
                                            }
                                        >


                                            {/* IMAGE */}

                                            <div className="analysis-history-image">

                                                {imageUrl ? (

                                                    <img
                                                        src={imageUrl}
                                                        alt="Analysis face"
                                                    />

                                                ) : (

                                                    <div className="analysis-no-image">
                                                        👤
                                                    </div>

                                                )}

                                            </div>


                                            {/* CONTENT */}

                                            <div className="analysis-history-content">


                                                <div className="analysis-history-top">


                                                    <span className="analysis-history-id">

                                                        Analysis #{analysis.id}

                                                    </span>


                                                    <span className="analysis-history-date">

                                                        {
                                                            formatDate(
                                                                analysis.created_at
                                                            )
                                                        }

                                                    </span>

                                                </div>


                                                <h3>

                                                    Makeup Analysis

                                                </h3>


                                                <p>

                                                    Occasion:
                                                    {" "}

                                                    <strong>
                                                        {
                                                            analysis.occasion ||
                                                            "-"
                                                        }
                                                    </strong>

                                                </p>


                                            </div>


                                            {/* ARROW */}

                                            <div className="analysis-history-arrow">

                                                →

                                            </div>


                                        </article>

                                    );

                                })

                            }


                        </div>

                    )}

                </section>


            </main>

        </div>

    );

}


export default UserProfile;