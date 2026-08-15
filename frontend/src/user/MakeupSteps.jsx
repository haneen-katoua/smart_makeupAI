import {
    useEffect,
    useState,
    useRef
} from "react";

import {
    useParams,
    useNavigate
} from "react-router-dom";

import api from "../services/api";

import "../styles/MakeupSteps.css";
import UserNavbar from "./UserNavbar";


// =====================================================
// PREVENT DUPLICATE GENERATION REQUESTS
// =====================================================
//
// هذا الـMap يمنع React من إرسال POST للتوليد
// أكثر من مرة لنفس request أثناء نفس تشغيل التطبيق.
//
// مهم خصوصًا مع React.StrictMode في development.
//

const generationLocks = new Map();


function MakeupSteps() {

    const { id } = useParams();

    const navigate = useNavigate();


    const [steps, setSteps] = useState([]);

    const [loading, setLoading] = useState(true);

    const [error, setError] = useState("");

    const [generating, setGenerating] = useState(false);


    // يمنع تنفيذ loadMakeupSteps أكثر من مرة
    // في نفس دورة الصفحة.
    const loadedRequestId = useRef(null);


    // =====================================================
    // LOAD STEPS ON PAGE LOAD
    // =====================================================

    useEffect(() => {

        if (!id) {
            setError("Invalid makeup request ID.");
            setLoading(false);
            return;
        }


        // إذا تم تحميل نفس الطلب مسبقًا
        // لا نعيد التحميل.
        if (loadedRequestId.current === id) {
            return;
        }


        loadedRequestId.current = id;


        loadMakeupSteps(id);


        // eslint-disable-next-line react-hooks/exhaustive-deps
    }, [id]);


    // =====================================================
    // LOAD EXISTING STEPS
    // =====================================================

    const loadMakeupSteps = async (requestId) => {

        try {

            setLoading(true);

            setError("");


            console.log(
                "================================="
            );

            console.log(
                "LOADING MAKEUP STEPS"
            );

            console.log(
                "REQUEST ID:",
                requestId
            );


            // -------------------------------------------------
            // GET EXISTING STEPS
            // -------------------------------------------------

            const response = await api.get(
                `/api/analysis/makeup-steps/${requestId}/`
            );


            const existingSteps =
                Array.isArray(response.data?.steps)
                    ? response.data.steps
                    : [];


            console.log(
                "EXISTING STEPS FROM API:",
                existingSteps
            );

            console.log(
                "EXISTING STEPS COUNT:",
                existingSteps.length
            );


            // -------------------------------------------------
            // STEPS ALREADY EXIST
            // -------------------------------------------------

            if (existingSteps.length > 0) {

                console.log(
                    "STEPS ALREADY EXIST - NO GENERATION NEEDED"
                );


                // استبدال القائمة بالكامل
                // وليس إضافة خطوات جديدة.
                setSteps(
                    existingSteps
                );


                return;

            }


            // -------------------------------------------------
            // NO STEPS -> GENERATE
            // -------------------------------------------------

            console.log(
                "NO EXISTING STEPS - GENERATING..."
            );


            await generateSteps(requestId);


        } catch (error) {

            console.error(
                "MAKEUP STEPS LOAD ERROR:",
                error
            );


            setError(
                error.response?.data?.detail ||
                error.message ||
                "Could not load makeup steps."
            );

        } finally {

            setLoading(false);

        }

    };


    // =====================================================
    // GENERATE STEPS
    // =====================================================

    const generateSteps = async (requestId) => {

        // -------------------------------------------------
        // CHECK IF GENERATION IS ALREADY RUNNING
        // -------------------------------------------------

        if (generationLocks.has(requestId)) {

            console.log(
                "GENERATION ALREADY RUNNING FOR REQUEST:",
                requestId
            );


            // ننتظر نفس الطلب الموجود بدل إرسال POST جديد.
            await generationLocks.get(requestId);

            return;

        }


        // -------------------------------------------------
        // CREATE GENERATION PROMISE
        // -------------------------------------------------

        const generationPromise = (async () => {

            try {

                setGenerating(true);

                setError("");


                console.log(
                    "================================="
                );

                console.log(
                    "GENERATING MAKEUP STEPS"
                );

                console.log(
                    "REQUEST ID:",
                    requestId
                );


                // -------------------------------------------------
                // POST GENERATE
                // -------------------------------------------------

                const generateResponse =
                    await api.post(
                        `/api/analysis/makeup/requests/${requestId}/generate-steps/`
                    );


                console.log(
                    "GENERATE API RESPONSE:",
                    generateResponse.data
                );


                // -------------------------------------------------
                // GET GENERATED STEPS
                // -------------------------------------------------

                const response =
                    await api.get(
                        `/api/analysis/makeup-steps/${requestId}/`
                    );


                const generatedSteps =
                    Array.isArray(response.data?.steps)
                        ? response.data.steps
                        : [];


                console.log(
                    "GENERATED STEPS:",
                    generatedSteps
                );

                console.log(
                    "GENERATED STEPS COUNT:",
                    generatedSteps.length
                );


                // -------------------------------------------------
                // VALIDATE RESULT
                // -------------------------------------------------

                if (!generatedSteps.length) {

                    throw new Error(
                        "No makeup steps were generated."
                    );

                }


                // -------------------------------------------------
                // IMPORTANT
                // -------------------------------------------------
                //
                // نستبدل الـsteps بالكامل.
                //
                // لا نستخدم:
                //
                // setSteps(prev => [...prev, ...generatedSteps])
                //
                // لأن هذا ممكن يسبب 15 + 15 = 30.
                //

                setSteps(
                    generatedSteps
                );


                console.log(
                    "FINAL STEPS COUNT:",
                    generatedSteps.length
                );


            } catch (error) {

                console.error(
                    "MAKEUP STEPS GENERATION ERROR:",
                    error
                );


                setError(
                    error.response?.data?.detail ||
                    error.message ||
                    "Could not generate makeup steps."
                );


                throw error;


            } finally {

                setGenerating(false);

            }

        })();


        // -------------------------------------------------
        // SAVE LOCK
        // -------------------------------------------------

        generationLocks.set(
            requestId,
            generationPromise
        );


        try {

            await generationPromise;

        } finally {

            // بعد انتهاء التوليد نزيل الـlock.
            generationLocks.delete(
                requestId
            );

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
    // LOADING
    // =====================================================

    if (loading) {

        return (

            <div className="makeup-steps-loading">

                <div className="loading-spinner">
                </div>


                <h2>

                    {
                        generating
                            ? "Creating your personalized makeup steps..."
                            : "Loading your makeup steps..."
                    }

                </h2>


                <p>

                    {
                        generating
                            ? "Please wait while we prepare your personalized makeup guide."
                            : "Please wait..."
                    }

                </p>

            </div>

        );

    }


    // =====================================================
    // ERROR
    // =====================================================

    if (error) {

        return (

            <div className="makeup-steps-error">

                <h2>
                    Something went wrong
                </h2>


                <p>
                    {error}
                </p>


                <div className="makeup-error-buttons">

                    <button
                        onClick={() => {

                            setError("");

                            setLoading(true);

                            loadedRequestId.current = null;

                            loadMakeupSteps(id);

                        }}
                    >
                        Try Again
                    </button>


                    <button
                    className="secondary-button"
                    onClick={() =>
                        navigate(`/my-analyses/${id}`)
                    }
                >
                    Back to Analysis
                </button>

                </div>

            </div>

        );

    }


    // =====================================================
    // PAGE
    // =====================================================

    return (

        <div className="makeup-steps-page">
            <UserNavbar />


            {/* =================================================
                HEADER
            ================================================= */}

            <div className="makeup-steps-header">


                <div>

                    <button
                    className="steps-back-button"
                    onClick={() =>
                        navigate(`/my-analyses/${id}`)
                    }
                >
                    ← Back to Analysis
                </button>


                    <h1>
                        Your Personalized Makeup Steps
                    </h1>


                    <p>
                        Follow these steps to recreate your
                        personalized makeup look.
                    </p>

                </div>


                <div className="steps-count">

                    {steps.length} Steps

                </div>


            </div>


            {/* =================================================
                STEPS
            ================================================= */}

            <div className="makeup-steps-container">


                {
                    steps.map((step, index) => {

                        const imageUrl =
                            getImageUrl(step.image);


                        return (

                            <section
                                className="makeup-step-card"
                                key={
                                    step.id ??
                                    `${step.step_number}-${index}`
                                }
                            >


                                {/* =================================
                                    STEP HEADER
                                ================================= */}

                                <div className="makeup-step-header">


                                    <div className="step-number">

                                        {step.step_number}

                                    </div>


                                    <div className="step-heading">


                                        <span className="step-category">

                                            {
                                                step.category ||
                                                "Makeup"
                                            }

                                        </span>


                                        <h2>

                                            {
                                                step.title ||
                                                `Step ${step.step_number}`
                                            }

                                        </h2>

                                    </div>


                                </div>


                                {/* =================================
                                    IMAGE
                                ================================= */}

                                {
                                    imageUrl && (

                                        <div className="makeup-step-image-wrapper">

                                            <img
                                                src={imageUrl}
                                                alt={
                                                    step.title ||
                                                    `Makeup step ${step.step_number}`
                                                }
                                                className="makeup-step-image"
                                            />

                                        </div>

                                    )
                                }


                                {/* =================================
                                    INFORMATION
                                ================================= */}

                                <div className="makeup-step-information">


                                    {
                                        step.product && (

                                            <div className="step-info-box">

                                                <span>
                                                    Product
                                                </span>

                                                <strong>
                                                    {step.product}
                                                </strong>

                                            </div>

                                        )
                                    }


                                    {
                                        step.instruction && (

                                            <div className="step-instruction">

                                                <h3>
                                                    How to apply
                                                </h3>

                                                <p>
                                                    {step.instruction}
                                                </p>

                                            </div>

                                        )
                                    }


                                    {
                                        step.arrow_target && (

                                            <div className="step-target">

                                                <span>
                                                    Application area
                                                </span>

                                                <strong>

                                                    {
                                                        typeof step.arrow_target === "string"
                                                            ? step.arrow_target
                                                            : JSON.stringify(
                                                                step.arrow_target
                                                            )
                                                    }

                                                </strong>

                                            </div>

                                        )
                                    }


                                </div>


                            </section>

                        );

                    })

                }

            </div>


            {/* =================================================
                FOOTER
            ================================================= */}

            <div className="makeup-steps-footer">

                <button
                onClick={() =>
                    navigate(`/my-analyses/${id}`)
                }
            >
                ← Back to Analysis
            </button>

            </div>


        </div>

    );

}


export default MakeupSteps;