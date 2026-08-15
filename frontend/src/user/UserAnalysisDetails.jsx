import { useEffect, useState } from "react";
import { useNavigate, useParams } from "react-router-dom";

import api from "../services/api";
import UserNavbar from "./UserNavbar";

import "../styles/UserAnalysisDetails.css";


const BASE_URL = "http://127.0.0.1:8000";


function UserAnalysisDetails() {

    const { id } = useParams();

    const navigate = useNavigate();


    const [analysis, setAnalysis] = useState(null);

    const [loading, setLoading] = useState(true);

    const [error, setError] = useState("");


    // =====================================================
    // IMAGE URL
    // =====================================================

    const getImageUrl = (path) => {

        if (!path) {
            return null;
        }


        if (
            path.startsWith("http://") ||
            path.startsWith("https://")
        ) {
            return path;
        }


        const normalizedPath =
            path.replaceAll("\\", "/");


        return `${BASE_URL}/${normalizedPath.replace(/^\/+/, "")}`;

    };


    // =====================================================
    // LOAD ANALYSIS
    // =====================================================

    useEffect(() => {

        loadAnalysis();

    }, [id]);


    const loadAnalysis = async () => {

        try {

            setLoading(true);

            setError("");


            const response = await api.get(
                `/api/analysis/my-analyses/${id}/`
            );


            console.log(
                "USER ANALYSIS DETAILS:",
                response.data
            );


            setAnalysis(
                response.data
            );


        } catch (error) {

            console.error(
                "USER ANALYSIS DETAILS ERROR:",
                error
            );


            setError(
                error.response?.data?.detail ||
                "Could not load this analysis."
            );


        } finally {

            setLoading(false);

        }

    };


    // =====================================================
    // LOADING
    // =====================================================

    if (loading) {

        return (

            <>

                <UserNavbar />

                <div className="user-analysis-loading">

                    <div className="loading-spinner">
                    </div>

                    <h2>
                        Loading your analysis...
                    </h2>

                    <p>
                        Please wait while we load your analysis details.
                    </p>

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

                <div className="user-analysis-error">

                    <h2>
                        Something went wrong
                    </h2>

                    <p>
                        {error}
                    </p>


                    <div className="analysis-error-buttons">

                        <button
                            onClick={loadAnalysis}
                        >
                            Try Again
                        </button>


                        <button
                            className="secondary-button"
                            onClick={() =>
                                navigate("/profile")
                            }
                        >
                            ← Back to Profile
                        </button>

                    </div>

                </div>

            </>

        );

    }


    // =====================================================
    // NO DATA
    // =====================================================

    if (!analysis) {

        return (

            <>

                <UserNavbar />

                <div className="user-analysis-error">

                    <h2>
                        Analysis not found
                    </h2>

                    <p>
                        We could not find this analysis.
                    </p>


                    <button
                        onClick={() =>
                            navigate("/profile")
                        }
                    >
                        ← Back to Profile
                    </button>

                </div>

            </>

        );

    }


    // =====================================================
    // ANALYSIS RESULT
    // =====================================================

    const result =
        analysis.analysis_result || {};


    const faceAnalysis =
        result.face_analysis || {};


    const skinAnalysis =
        result.skin_analysis || {};


    const expert =
        result.expert_output || {};


    const eyes =
        faceAnalysis.eyes || {};


    const brows =
        faceAnalysis.brows || {};


    const lips =
        faceAnalysis.lips || {};


    const nose =
        faceAnalysis.nose || {};


    const face =
        expert.face || {};


    const foundation =
        expert.foundation || {};


    const lipRecommendation =
        expert.lips || {};


    const noseRecommendation =
        expert.nose || {};


    const clothingAnalysis =
        result.clothing_analysis || {};


    const shadowPalette =
        result.shadow_palette || {};


    const paletteImage =
        getImageUrl(
            shadowPalette.palette_image
        );


    const faceImage =
        getImageUrl(
            analysis.face_image
        );


    const clothesImage =
        getImageUrl(
            analysis.clothes_image
        );


    // =====================================================
    // PAGE
    // =====================================================

    return (

        <div className="user-analysis-details-page">


            {/* =================================================
                NAVBAR
            ================================================= */}

            <UserNavbar />


            {/* =================================================
                HEADER
            ================================================= */}

            <div className="user-analysis-header">


                <button
                    className="back-profile-button"
                    onClick={() =>
                        navigate("/profile")
                    }
                >
                    ← Back to Profile
                </button>


                <div className="analysis-header-content">

                    <div>

                        <h1>
                            Your Makeup Analysis
                        </h1>

                        <p>
                            Personalized analysis and recommendations
                            generated for you.
                        </p>

                    </div>


                    <div className="analysis-id">

                        Analysis #{analysis.id}

                    </div>

                </div>

            </div>


            {/* =================================================
                CONTENT
            ================================================= */}

            <div className="user-analysis-content">


                {/* =================================================
                    BASIC INFORMATION
                ================================================= */}

                <section className="user-analysis-card">


                    <div className="section-title">

                        <span className="section-icon">
                            📋
                        </span>

                        <div>

                            <h2>
                                Analysis Information
                            </h2>

                            <p>
                                Basic information about this analysis
                            </p>

                        </div>

                    </div>


                    <div className="basic-info-grid">


                        <div>

                            <span>
                                Occasion
                            </span>

                            <strong>
                                {analysis.occasion || "-"}
                            </strong>

                        </div>


                        <div>

                            <span>
                                Created
                            </span>

                            <strong>
                                {
                                    analysis.created_at
                                        ? new Date(
                                            analysis.created_at
                                        ).toLocaleString()
                                        : "-"
                                }
                            </strong>

                        </div>


                    </div>


                </section>



                {/* =================================================
                    IMAGES
                ================================================= */}

                <section className="user-analysis-card">


                    <div className="section-title">

                        <span className="section-icon">
                            🖼️
                        </span>

                        <div>

                            <h2>
                                Uploaded Images
                            </h2>

                            <p>
                                Images used for your analysis
                            </p>

                        </div>

                    </div>


                    <div className="uploaded-images">


                        {faceImage && (

                            <div className="uploaded-image-card">

                                <h3>
                                    Face Image
                                </h3>

                                <img
                                    src={faceImage}
                                    alt="Your face"
                                />

                            </div>

                        )}


                        {clothesImage && (

                            <div className="uploaded-image-card">

                                <h3>
                                    Clothes Image
                                </h3>

                                <img
                                    src={clothesImage}
                                    alt="Your clothes"
                                />

                            </div>

                        )}


                    </div>


                </section>



                {/* =================================================
                    FACE ANALYSIS
                ================================================= */}

                <section className="user-analysis-card">


                    <div className="section-title">

                        <span className="section-icon">
                            ✨
                        </span>

                        <div>

                            <h2>
                                Face Analysis
                            </h2>

                            <p>
                                Your detected facial characteristics
                            </p>

                        </div>

                    </div>


                    <div className="analysis-grid">


                        <div className="analysis-box">

                            <h3>
                                Face Shape
                            </h3>

                            <div className="big-value">

                                {
                                    faceAnalysis.face_shape?.shape
                                    || "-"
                                }

                            </div>

                            <p>

                                Confidence:

                                {" "}

                                {
                                    faceAnalysis.face_shape?.confidence
                                        ? `${(
                                            faceAnalysis.face_shape.confidence * 100
                                        ).toFixed(0)}%`
                                        : "-"
                                }

                            </p>

                        </div>


                        <div className="analysis-box">

                            <h3>
                                Left Eye
                            </h3>

                            <p>
                                <span>
                                    Shape
                                </span>

                                {
                                    eyes.left_eye?.geo_shape
                                    || "-"
                                }
                            </p>

                            <p>
                                <span>
                                    Type
                                </span>

                                {
                                    eyes.left_eye?.eye_type
                                    || "-"
                                }
                            </p>

                            <p>
                                <span>
                                    Size
                                </span>

                                {
                                    eyes.left_eye?.size
                                    || "-"
                                }
                            </p>

                        </div>


                        <div className="analysis-box">

                            <h3>
                                Right Eye
                            </h3>

                            <p>
                                <span>
                                    Shape
                                </span>

                                {
                                    eyes.right_eye?.geo_shape
                                    || "-"
                                }
                            </p>

                            <p>
                                <span>
                                    Type
                                </span>

                                {
                                    eyes.right_eye?.eye_type
                                    || "-"
                                }
                            </p>

                            <p>
                                <span>
                                    Size
                                </span>

                                {
                                    eyes.right_eye?.size
                                    || "-"
                                }
                            </p>

                        </div>


                        <div className="analysis-box">

                            <h3>
                                Brows
                            </h3>

                            <p>
                                <span>
                                    Thickness
                                </span>

                                {
                                    brows.thickness || "-"
                                }
                            </p>

                            <p>
                                <span>
                                    Shape
                                </span>

                                {
                                    brows.shape || "-"
                                }
                            </p>

                            <p>
                                <span>
                                    Position
                                </span>

                                {
                                    brows.position || "-"
                                }
                            </p>

                        </div>


                        <div className="analysis-box">

                            <h3>
                                Lips
                            </h3>

                            <p>
                                <span>
                                    Volume
                                </span>

                                {
                                    lips.volume || "-"
                                }
                            </p>

                            <p>
                                <span>
                                    Balance
                                </span>

                                {
                                    lips.balance || "-"
                                }
                            </p>

                            <p>
                                <span>
                                    Width
                                </span>

                                {
                                    lips.width || "-"
                                }
                            </p>

                        </div>


                        <div className="analysis-box">

                            <h3>
                                Nose
                            </h3>

                            <p>
                                <span>
                                    Shape
                                </span>

                                {
                                    nose.shape || "-"
                                }
                            </p>

                            <p>
                                <span>
                                    Width
                                </span>

                                {
                                    nose.width || "-"
                                }
                            </p>

                            <p>
                                <span>
                                    Bridge
                                </span>

                                {
                                    nose.bridge || "-"
                                }
                            </p>

                        </div>


                    </div>


                </section>



                {/* =================================================
                    SKIN ANALYSIS
                ================================================= */}

                <section className="user-analysis-card">


                    <div className="section-title">

                        <span className="section-icon">
                            🌸
                        </span>

                        <div>

                            <h2>
                                Skin Analysis
                            </h2>

                            <p>
                                Your detected skin characteristics
                            </p>

                        </div>

                    </div>


                    <div className="skin-grid">


                        <div className="skin-value">

                            <span>
                                Skin Depth
                            </span>

                            <strong>
                                {
                                    skinAnalysis.skin_depth
                                    || "-"
                                }
                            </strong>

                        </div>


                        <div className="skin-value">

                            <span>
                                Undertone
                            </span>

                            <strong>
                                {
                                    skinAnalysis.undertone
                                    || "-"
                                }
                            </strong>

                        </div>


                        <div className="skin-value">

                            <span>
                                Skin Type
                            </span>

                            <strong>
                                {
                                    skinAnalysis.skin_type
                                    || "-"
                                }
                            </strong>

                        </div>


                        <div className="skin-value">

                            <span>
                                Confidence
                            </span>

                            <strong>

                                {
                                    skinAnalysis.confidence
                                        ? `${(
                                            skinAnalysis.confidence * 100
                                        ).toFixed(0)}%`
                                        : "-"
                                }

                            </strong>

                        </div>


                        <div className="skin-color">

                            <span>
                                Detected Skin Color
                            </span>


                            <div
                                className="color-preview"
                                style={{
                                    backgroundColor:
                                        skinAnalysis.color_hex ||
                                        "#ddd"
                                }}
                            >
                            </div>


                            <strong>
                                {
                                    skinAnalysis.color_hex
                                    || "-"
                                }
                            </strong>

                        </div>


                    </div>


                </section>



                {/* =================================================
                    MAKEUP RECOMMENDATIONS
                ================================================= */}

                <section className="user-analysis-card">


                    <div className="section-title">

                        <span className="section-icon">
                            💄
                        </span>

                        <div>

                            <h2>
                                Makeup Recommendations
                            </h2>

                            <p>
                                Personalized recommendations generated for you
                            </p>

                        </div>

                    </div>


                    {/* FACE */}

                    <div className="recommendation-section">

                        <h3>
                            Face
                        </h3>


                        <div className="recommendation-content">


                            <div>

                                <span>
                                    Face Shape
                                </span>

                                <strong>
                                    {
                                        face.shape?.shape
                                        || "-"
                                    }
                                </strong>

                            </div>


                            <div>

                                <span>
                                    Contour
                                </span>

                                <strong>
                                    {
                                        face.sculpt?.placement
                                        || "-"
                                    }
                                </strong>

                            </div>


                            <div>

                                <span>
                                    Blush
                                </span>

                                <strong>
                                    {
                                        face.blush?.placement
                                        || "-"
                                    }
                                </strong>

                            </div>


                            <div>

                                <span>
                                    Highlight
                                </span>

                                <strong>
                                    {
                                        face.highlight?.placement
                                        || "-"
                                    }
                                </strong>

                            </div>


                        </div>

                    </div>



                    {/* EYES */}

                    <div className="recommendation-section">

                        <h3>
                            Eyes
                        </h3>


                        <div className="recommendation-content">


                            <div>

                                <span>
                                    Style
                                </span>

                                <strong>
                                    {
                                        expert.eyes?.left?.plan?.style
                                        || "-"
                                    }
                                </strong>

                            </div>


                            <div>

                                <span>
                                    Texture
                                </span>

                                <strong>
                                    {
                                        expert.eyes?.left?.plan?.texture
                                        || "-"
                                    }
                                </strong>

                            </div>


                            <div>

                                <span>
                                    Eyeliner
                                </span>

                                <strong>
                                    {
                                        expert.eyes?.left?.plan?.eyeliner
                                        || "-"
                                    }
                                </strong>

                            </div>


                            <div>

                                <span>
                                    Lashes
                                </span>

                                <strong>
                                    {
                                        expert.eyes?.left?.plan?.lashes
                                        || "-"
                                    }
                                </strong>

                            </div>


                        </div>

                    </div>



                    {/* BROWS */}

                    <div className="recommendation-section">

                        <h3>
                            Brows
                        </h3>


                        <div className="recommendation-content">


                            <div>

                                <span>
                                    Style
                                </span>

                                <strong>
                                    {
                                        expert.brows?.style?.style
                                        || "-"
                                    }
                                </strong>

                            </div>


                            <div>

                                <span>
                                    Technique
                                </span>

                                <strong>
                                    {
                                        expert.brows?.style?.technique
                                        || "-"
                                    }
                                </strong>

                            </div>


                            <div>

                                <span>
                                    Product
                                </span>

                                <strong>
                                    {
                                        expert.brows?.style?.product
                                        || "-"
                                    }
                                </strong>

                            </div>


                        </div>

                    </div>



                    {/* FOUNDATION */}

                    <div className="recommendation-section">

                        <h3>
                            Foundation
                        </h3>


                        <div className="recommendation-content">


                            <div>

                                <span>
                                    Shade
                                </span>

                                <strong>
                                    {
                                        foundation.shade?.descriptor
                                        || "-"
                                    }
                                </strong>

                            </div>


                            <div>

                                <span>
                                    Formula
                                </span>

                                <strong>
                                    {
                                        foundation.formula?.primary
                                        || "-"
                                    }
                                </strong>

                            </div>


                            <div>

                                <span>
                                    Coverage
                                </span>

                                <strong>
                                    {
                                        foundation.formula?.coverage
                                        || "-"
                                    }
                                </strong>

                            </div>


                            <div>

                                <span>
                                    Primer
                                </span>

                                <strong>
                                    {
                                        foundation.primer?.type
                                        || "-"
                                    }
                                </strong>

                            </div>


                        </div>

                    </div>



                    {/* LIPS */}

                    <div className="recommendation-section">

                        <h3>
                            Lips
                        </h3>


                        <div className="recommendation-content">


                            <div>

                                <span>
                                    Shape
                                </span>

                                <strong>
                                    {
                                        lipRecommendation.shape?.category
                                        || "-"
                                    }
                                </strong>

                            </div>


                            <div>

                                <span>
                                    Technique
                                </span>

                                <strong>
                                    {
                                        lipRecommendation.shape?.technique
                                        || "-"
                                    }
                                </strong>

                            </div>


                            <div>

                                <span>
                                    Palette
                                </span>

                                <strong>
                                    {
                                        lipRecommendation.color?.colors_summary
                                        || "-"
                                    }
                                </strong>

                            </div>


                        </div>


                        {
                            lipRecommendation.color?.lipstick_shades?.length > 0 && (

                                <div className="color-list">

                                    <h4>
                                        Recommended Lipstick Shades
                                    </h4>


                                    <div className="color-cards">

                                        {
                                            lipRecommendation.color.lipstick_shades.map(
                                                (color, index) => (

                                                    <div
                                                        className="makeup-color-card"
                                                        key={index}
                                                    >

                                                        <div
                                                            className="makeup-color-circle"
                                                            style={{
                                                                backgroundColor:
                                                                    color.hex
                                                            }}
                                                        >
                                                        </div>


                                                        <strong>
                                                            {color.name}
                                                        </strong>


                                                        <span>
                                                            {color.hex}
                                                        </span>

                                                    </div>

                                                )
                                            )
                                        }

                                    </div>

                                </div>

                            )
                        }


                    </div>



                    {/* NOSE */}

                    <div className="recommendation-section">

                        <h3>
                            Nose
                        </h3>


                        <div className="recommendation-content">


                            <div>

                                <span>
                                    Shape
                                </span>

                                <strong>
                                    {
                                        noseRecommendation.shape?.name_ar
                                        || "-"
                                    }
                                </strong>

                            </div>


                            <div>

                                <span>
                                    Technique
                                </span>

                                <strong>
                                    {
                                        noseRecommendation.shape?.technique
                                        || "-"
                                    }
                                </strong>

                            </div>


                            <div>

                                <span>
                                    Contour Product
                                </span>

                                <strong>
                                    {
                                        noseRecommendation.contour?.product
                                        || "-"
                                    }
                                </strong>

                            </div>


                            <div>

                                <span>
                                    Highlight
                                </span>

                                <strong>
                                    {
                                        noseRecommendation.highlight?.tone
                                        || "-"
                                    }
                                </strong>

                            </div>


                        </div>

                    </div>


                </section>



                {/* =================================================
                    CLOTHING
                ================================================= */}

                <section className="user-analysis-card">


                    <div className="section-title">

                        <span className="section-icon">
                            👗
                        </span>

                        <div>

                            <h2>
                                Clothing Analysis
                            </h2>

                            <p>
                                Analysis of your outfit color
                            </p>

                        </div>

                    </div>


                    <div className="clothing-info">


                        <div>

                            <span>
                                Status
                            </span>

                            <strong>
                                {
                                    clothingAnalysis.status
                                    || "-"
                                }
                            </strong>

                        </div>


                        <div>

                            <span>
                                Hue
                            </span>

                            <strong>
                                {
                                    clothingAnalysis.Input_Hue
                                    ?? "-"
                                }
                            </strong>

                        </div>


                        <div>

                            <span>
                                Color
                            </span>


                            <div className="clothing-color">

                                <div
                                    style={{
                                        backgroundColor:
                                            clothingAnalysis.hex ||
                                            "#ddd"
                                    }}
                                >
                                </div>


                                <strong>
                                    {
                                        clothingAnalysis.hex
                                        || "-"
                                    }
                                </strong>

                            </div>

                        </div>


                    </div>


                </section>



                {/* =================================================
                    PALETTE
                ================================================= */}

                <section className="user-analysis-card palette-section">


                    <div className="section-title">

                        <span className="section-icon">
                            🎨
                        </span>

                        <div>

                            <h2>
                                Recommended Eyeshadow Palette
                            </h2>

                            <p>
                                Palette generated according to your
                                skin undertone and clothing color
                            </p>

                        </div>

                    </div>


                    {
                        paletteImage ? (

                            <div className="palette-container">


                                <img
                                    src={paletteImage}
                                    alt="Recommended eyeshadow palette"
                                    className="palette-image"
                                />


                                <div className="palette-info">


                                    <div>

                                        <span>
                                            Skin Undertone
                                        </span>

                                        <strong>
                                            {
                                                shadowPalette.skin_undertone
                                                || "-"
                                            }
                                        </strong>

                                    </div>


                                    <div>

                                        <span>
                                            Clothing Hue
                                        </span>

                                        <strong>
                                            {
                                                shadowPalette.clothing_hue
                                                ?? "-"
                                            }
                                        </strong>

                                    </div>


                                    <div>

                                        <span>
                                            Palette Type
                                        </span>

                                        <strong>
                                            {
                                                shadowPalette.path_type
                                                || "-"
                                            }
                                        </strong>

                                    </div>


                                </div>


                            </div>

                        ) : (

                            <div className="no-palette">

                                No palette image available.

                            </div>

                        )
                    }


                </section>



                {/* =================================================
                    MAKEUP STEPS
                ================================================= */}

                <section className="makeup-steps-action">


                    <h2>
                        Ready to apply your makeup?
                    </h2>


                    <p>
                        Follow your personalized step-by-step makeup
                        instructions with visual guides.
                    </p>


                    <button
                        type="button"
                        className="makeup-steps-button"
                        onClick={() =>
                            navigate(
                                `/makeup-steps/${analysis.id}`
                            )
                        }
                    >
                        💄 View Makeup Steps
                    </button>


                </section>


            </div>


            {/* =================================================
                FOOTER
            ================================================= */}

            <div className="user-analysis-footer">

                <button
                    onClick={() =>
                        navigate("/profile")
                    }
                >
                    ← Back to Profile
                </button>

            </div>


        </div>

    );

}


export default UserAnalysisDetails;