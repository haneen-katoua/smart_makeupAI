import { useState } from "react";
import api from "../services/api";
import "../styles/MakeupRequest.css";
import { useNavigate } from "react-router-dom";
import UserNavbar from "./UserNavbar";

const BASE_URL = "http://127.0.0.1:8000";

function MakeupRequest() {
  const navigate = useNavigate();
  const [faceImage, setFaceImage] = useState(null);
  const [clothesImage, setClothesImage] = useState(null);
  const [facePreview, setFacePreview] = useState("");
  const [clothesPreview, setClothesPreview] = useState("");
  const [occasion, setOccasion] = useState("");
  const [analysis, setAnalysis] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  // ----- حالة إظهار استوديو التجربة الافتراضية المباشر (Gradio 1) -----
  const [showGradio, setShowGradio] = useState(false);
  // ----- حالة إظهار استوديو محاكاة درجات الفاونديشن (Gradio 2) -----
  const [showFoundationGradio, setShowFoundationGradio] = useState(false);

  // =====================================================
  // IMAGE URL
  // =====================================================
  const getImageUrl = (path) => {
    if (!path) {
      return null;
    }
    if (path.startsWith("http")) {
      return path;
    }
    const normalizedPath = path.replaceAll("\\", "/");
    return `${BASE_URL}/${normalizedPath.replace(/^\/+/, "")}`;
  };

  // =====================================================
  // FACE IMAGE
  // =====================================================
  const handleFaceImageChange = (event) => {
    const file = event.target.files?.[0];
    if (!file) {
      return;
    }
    setFaceImage(file);
    setFacePreview(URL.createObjectURL(file));
    setError("");
  };

  // =====================================================
  // CLOTHES IMAGE
  // =====================================================
  const handleClothesImageChange = (event) => {
    const file = event.target.files?.[0];
    if (!file) {
      return;
    }
    setClothesImage(file);
    setClothesPreview(URL.createObjectURL(file));
    setError("");
  };

  // =====================================================
  // START ANALYSIS
  // =====================================================
  const handleSubmit = async (event) => {
    event.preventDefault();
    setError("");
    setAnalysis(null);
    setShowGradio(false);
    setShowFoundationGradio(false);

    if (!faceImage) {
      setError("Please upload your face image.");
      return;
    }

    if (!occasion) {
      setError("Please select an occasion.");
      return;
    }

    const formData = new FormData();
    formData.append("face_image", faceImage);
    if (clothesImage) {
      formData.append("clothes_image", clothesImage);
    }
    formData.append("occasion", occasion);

    try {
      setLoading(true);
      const response = await api.post("/api/analysis/request/", formData, {
        headers: {
          "Content-Type": "multipart/form-data",
        },
      });
      console.log("MAKEUP ANALYSIS RESULT:", response.data);
      setAnalysis(response.data);
    } catch (error) {
      console.error("MAKEUP ANALYSIS ERROR:", error);
      if (error.response?.status === 500) {
        setError(
          "Makeup analysis failed. Please check that your face and clothing images are clear and try again."
        );
      } else {
        setError("Makeup analysis failed. Please try again.");
      }
    } finally {
      setLoading(false);
    }
  };

  // =====================================================
  // ANALYSIS DATA
  // =====================================================
  const result = analysis?.result || {};
  const faceAnalysis = result.face_analysis || {};
  const skinAnalysis = result.skin_analysis || {};
  const expert = result.expert_output || {};

  const eyes = faceAnalysis.eyes || {};
  const brows = faceAnalysis.brows || {};
  const lips = faceAnalysis.lips || {};
  const nose = faceAnalysis.nose || {};

  const face = expert.face || {};
  const foundation = expert.foundation || {};
  const lipRecommendation = expert.lips || {};
  const noseRecommendation = expert.nose || {};

  const clothingAnalysis = result.clothing_analysis || {};
  const shadowPalette = result.shadow_palette || {};
  const paletteImage = getImageUrl(shadowPalette.palette_image);

  // =====================================================
  // RENDER
  // =====================================================
  return (
    <div className="user-makeup-page">
      <UserNavbar />

      {/* =================================================
          REQUEST FORM
      ================================================= */}
      <section className="makeup-request-card">
        <div className="request-header">
          <div>
            <h1> Smart Makeup Analysis </h1>
            <p>
              Upload your photo, outfit and choose your occasion to get your
              personalized makeup recommendations.
            </p>
          </div>
        </div>

        <form onSubmit={handleSubmit} className="makeup-request-form">
          {/* =============================== FACE IMAGE ================================ */}
          <div className="upload-section">
            <h2> Your Face </h2>
            <p> Upload a clear photo of your face. </p>

            <label className="upload-box">
              {facePreview ? (
                <div className="preview-container">
                  <img
                    src={facePreview}
                    alt="Face preview"
                    className="upload-preview"
                  />
                  <span> Change image </span>
                </div>
              ) : (
                <div className="upload-placeholder">
                  <span className="upload-icon"> 📷 </span>
                  <strong> Upload your face image </strong>
                  <span> Click to choose an image </span>
                </div>
              )}

              <input
                type="file"
                accept="image/*"
                onChange={handleFaceImageChange}
              />
            </label>
          </div>

          {/* =============================== CLOTHES IMAGE ================================ */}
          <div className="upload-section">
            <h2> Your Outfit </h2>
            <p> Upload your clothes or outfit image. </p>

            <label className="upload-box">
              {clothesPreview ? (
                <div className="preview-container">
                  <img
                    src={clothesPreview}
                    alt="Clothes preview"
                    className="upload-preview"
                  />
                  <span> Change image </span>
                </div>
              ) : (
                <div className="upload-placeholder">
                  <span className="upload-icon"> 👗 </span>
                  <strong> Upload your clothes image </strong>
                  <span> Optional </span>
                </div>
              )}

              <input
                type="file"
                accept="image/*"
                onChange={handleClothesImageChange}
              />
            </label>
          </div>

          {/* =============================== OCCASION ================================ */}
          <div className="occasion-section">
            <label htmlFor="occasion"> Occasion </label>
            <select
              id="occasion"
              value={occasion}
              onChange={(event) => setOccasion(event.target.value)}
            >
              <option value=""> Select an occasion </option>
              <option value="work"> Work </option>
              <option value="party"> Party </option>
              <option value="wedding"> Wedding </option>
              <option value="photo"> Photography </option>
            </select>
          </div>

          {/* =============================== ERROR ================================ */}
          {error && <div className="makeup-request-error">{error}</div>}

          {/* =============================== BUTTON ================================ */}
          <button
            type="submit"
            className="start-analysis-button"
            disabled={loading}
          >
            {loading ? (
              <>
                <span className="button-spinner"> </span> Analyzing your
                features...
              </>
            ) : (
              <> ✨ Start Makeup Analysis </>
            )}
          </button>
        </form>
      </section>

      {/* =================================================
          LOADING
      ================================================= */}
      {loading && (
        <section className="analysis-loading">
          <div className="loading-spinner"> </div>
          <h2> Your makeup analysis is in progress... </h2>
          <p> We are analyzing your face, skin, outfit and makeup preferences. </p>
        </section>
      )}

      {/* =================================================
          RESULT
      ================================================= */}
      {!loading && analysis && (
        <div className="analysis-result">
          {/* =============================== RESULT HEADER ================================ */}
          <div className="details-header">
            <div>
              <h1> Your Makeup Analysis </h1>
              <p> Personalized analysis and recommendations generated for you. </p>
            </div>
            <div className="analysis-id"> Analysis #{analysis.request_id} </div>
          </div>

          {/* =============================== UPLOADED IMAGES ================================ */}
          <section className="details-card">
            <div className="section-title">
              <span className="section-icon"> 🖼️ </span>
              <div>
                <h2> Uploaded Images </h2>
                <p> Images used for your analysis </p>
              </div>
            </div>

            <div className="uploaded-images">
              {facePreview && (
                <div className="uploaded-image-card">
                  <h3> Face Image </h3>
                  <img src={facePreview} alt="Your face" />
                </div>
              )}

              {clothesPreview && (
                <div className="uploaded-image-card">
                  <h3> Clothes Image </h3>
                  <img src={clothesPreview} alt="Your clothes" />
                </div>
              )}
            </div>
          </section>

          {/* =============================== FACE ANALYSIS ================================ */}
          <section className="details-card">
            <div className="section-title">
              <span className="section-icon"> ✨ </span>
              <div>
                <h2> Face Analysis </h2>
                <p> Your detected facial characteristics </p>
              </div>
            </div>

            <div className="analysis-grid">
              <div className="analysis-box">
                <h3> Face Shape </h3>
                <div className="big-value">
                  {faceAnalysis.face_shape?.shape || "-"}
                </div>
                <p>
                  Confidence:{" "}
                  {faceAnalysis.face_shape?.confidence
                    ? `${(faceAnalysis.face_shape.confidence * 100).toFixed(0)}%`
                    : "-"}
                </p>
              </div>

              <div className="analysis-box">
                <h3> Left Eye </h3>
                <p>
                  <span> Shape </span> {eyes.left_eye?.geo_shape || "-"}
                </p>
                <p>
                  <span> Type </span> {eyes.left_eye?.eye_type || "-"}
                </p>
                <p>
                  <span> Size </span> {eyes.left_eye?.size || "-"}
                </p>
              </div>

              <div className="analysis-box">
                <h3> Right Eye </h3>
                <p>
                  <span> Shape </span> {eyes.right_eye?.geo_shape || "-"}
                </p>
                <p>
                  <span> Type </span> {eyes.right_eye?.eye_type || "-"}
                </p>
                <p>
                  <span> Size </span> {eyes.right_eye?.size || "-"}
                </p>
              </div>

              <div className="analysis-box">
                <h3> Brows </h3>
                <p>
                  <span> Thickness </span> {brows.thickness || "-"}
                </p>
                <p>
                  <span> Shape </span> {brows.shape || "-"}
                </p>
                <p>
                  <span> Position </span> {brows.position || "-"}
                </p>
              </div>

              <div className="analysis-box">
                <h3> Lips </h3>
                <p>
                  <span> Volume </span> {lips.volume || "-"}
                </p>
                <p>
                  <span> Balance </span> {lips.balance || "-"}
                </p>
                <p>
                  <span> Width </span> {lips.width || "-"}
                </p>
              </div>

              <div className="analysis-box">
                <h3> Nose </h3>
                <p>
                  <span> Shape </span> {nose.shape || "-"}
                </p>
                <p>
                  <span> Width </span> {nose.width || "-"}
                </p>
                <p>
                  <span> Bridge </span> {nose.bridge || "-"}
                </p>
              </div>
            </div>
          </section>

          {/* =============================== SKIN ANALYSIS ================================ */}
          <section className="details-card">
            <div className="section-title">
              <span className="section-icon"> 🌸 </span>
              <div>
                <h2> Skin Analysis </h2>
                <p> Your detected skin characteristics </p>
              </div>
            </div>

            <div className="skin-grid">
              <div className="skin-value">
                <span> Skin Depth </span>
                <strong> {skinAnalysis.skin_depth || "-"} </strong>
              </div>

              <div className="skin-value">
                <span> Undertone </span>
                <strong> {skinAnalysis.undertone || "-"} </strong>
              </div>

              <div className="skin-value">
                <span> Skin Type </span>
                <strong> {skinAnalysis.skin_type || "-"} </strong>
              </div>

              <div className="skin-value">
                <span> Confidence </span>
                <strong>
                  {" "}
                  {skinAnalysis.confidence
                    ? `${(skinAnalysis.confidence * 100).toFixed(0)}%`
                    : "-"}{" "}
                </strong>
              </div>

              <div className="skin-color">
                <span> Detected Skin Color </span>
                <div
                  className="color-preview"
                  style={{
                    backgroundColor: skinAnalysis.color_hex || "#ddd",
                  }}
                ></div>
                <strong> {skinAnalysis.color_hex || "-"} </strong>
              </div>
            </div>
          </section>

          {/* =============================== MAKEUP RECOMMENDATIONS ================================ */}
          <section className="details-card">
            <div className="section-title">
              <span className="section-icon"> 💄 </span>
              <div>
                <h2> Makeup Recommendations </h2>
                <p> Personalized recommendations generated for you </p>
              </div>
            </div>

            {/* FACE */}
            <div className="recommendation-section">
              <h3> Face </h3>
              <div className="recommendation-content">
                <div>
                  <span> Face Shape </span>
                  <strong> {face.shape?.shape || "-"} </strong>
                </div>
                <div>
                  <span> Contour </span>
                  <strong> {face.sculpt?.placement || "-"} </strong>
                </div>
                <div>
                  <span> Blush </span>
                  <strong> {face.blush?.placement || "-"} </strong>
                </div>
                <div>
                  <span> Highlight </span>
                  <strong> {face.highlight?.placement || "-"} </strong>
                </div>
              </div>
            </div>

            {/* EYES */}
            <div className="recommendation-section">
              <h3> Eyes </h3>
              <div className="recommendation-content">
                <div>
                  <span> Style </span>
                  <strong> {expert.eyes?.left?.plan?.style || "-"} </strong>
                </div>
                <div>
                  <span> Texture </span>
                  <strong> {expert.eyes?.left?.plan?.texture || "-"} </strong>
                </div>
                <div>
                  <span> Eyeliner </span>
                  <strong> {expert.eyes?.left?.plan?.eyeliner || "-"} </strong>
                </div>
                <div>
                  <span> Lashes </span>
                  <strong> {expert.eyes?.left?.plan?.lashes || "-"} </strong>
                </div>
              </div>
            </div>

            {/* BROWS */}
            <div className="recommendation-section">
              <h3> Brows </h3>
              <div className="recommendation-content">
                <div>
                  <span> Style </span>
                  <strong> {expert.brows?.style?.style || "-"} </strong>
                </div>
                <div>
                  <span> Technique </span>
                  <strong> {expert.brows?.style?.technique || "-"} </strong>
                </div>
                <div>
                  <span> Product </span>
                  <strong> {expert.brows?.style?.product || "-"} </strong>
                </div>
              </div>
            </div>

            {/* FOUNDATION */}
            <div className="recommendation-section">
              <h3> Foundation </h3>
              <div className="recommendation-content">
                <div>
                  <span> Shade </span>
                  <strong> {foundation.shade?.descriptor || "-"} </strong>
                </div>
                <div>
                  <span> Formula </span>
                  <strong> {foundation.formula?.primary || "-"} </strong>
                </div>
                <div>
                  <span> Coverage </span>
                  <strong> {foundation.formula?.coverage || "-"} </strong>
                </div>
                <div>
                  <span> Primer </span>
                  <strong> {foundation.primer?.type || "-"} </strong>
                </div>
              </div>
            </div>

            {/* LIPS */}
            <div className="recommendation-section">
              <h3> Lips </h3>
              <div className="recommendation-content">
                <div>
                  <span> Shape </span>
                  <strong> {lipRecommendation.shape?.category || "-"} </strong>
                </div>
                <div>
                  <span> Technique </span>
                  <strong> {lipRecommendation.shape?.technique || "-"} </strong>
                </div>
                <div>
                  <span> Palette </span>
                  <strong>
                    {" "}
                    {lipRecommendation.color?.colors_summary || "-"}{" "}
                  </strong>
                </div>
              </div>

              {lipRecommendation.color?.lipstick_shades?.length > 0 && (
                <div className="color-list">
                  <h4> Recommended Lipstick Shades </h4>
                  <div className="color-cards">
                    {lipRecommendation.color.lipstick_shades.map(
                      (color, index) => (
                        <div className="makeup-color-card" key={index}>
                          <div
                            className="makeup-color-circle"
                            style={{ backgroundColor: color.hex }}
                          ></div>
                          <strong> {color.name} </strong>
                          <span> {color.hex} </span>
                        </div>
                      )
                    )}
                  </div>
                </div>
              )}
            </div>

            {/* NOSE */}
            <div className="recommendation-section">
              <h3> Nose </h3>
              <div className="recommendation-content">
                <div>
                  <span> Shape </span>
                  <strong> {noseRecommendation.shape?.name_ar || "-"} </strong>
                </div>
                <div>
                  <span> Technique </span>
                  <strong> {noseRecommendation.shape?.technique || "-"} </strong>
                </div>
                <div>
                  <span> Contour Product </span>
                  <strong>
                    {" "}
                    {noseRecommendation.contour?.product || "-"}{" "}
                  </strong>
                </div>
                <div>
                  <span> Highlight </span>
                  <strong>
                    {" "}
                    {noseRecommendation.highlight?.tone || "-"}{" "}
                  </strong>
                </div>
              </div>
            </div>
          </section>

          {/* =============================== CLOTHES ================================ */}
          <section className="details-card">
            <div className="section-title">
              <span className="section-icon"> 👗 </span>
              <div>
                <h2> Clothing Analysis </h2>
                <p> Analysis of your outfit color </p>
              </div>
            </div>

            <div className="clothing-info">
              <div>
                <span> Status </span>
                <strong> {clothingAnalysis.status || "-"} </strong>
              </div>
              <div>
                <span> Hue </span>
                <strong> {clothingAnalysis.Input_Hue ?? "-"} </strong>
              </div>
              <div>
                <span> Color </span>
                <div className="clothing-color">
                  <div
                    style={{ backgroundColor: clothingAnalysis.hex || "#ddd" }}
                  ></div>
                  <strong> {clothingAnalysis.hex || "-"} </strong>
                </div>
              </div>
            </div>
          </section>

          {/* =============================== PALETTE ================================ */}
          <section className="details-card palette-section">
            <div className="section-title">
              <span className="section-icon"> 🎨 </span>
              <div>
                <h2> Recommended Eyeshadow Palette </h2>
                <p>
                  Palette generated according to your skin undertone and clothing
                  color
                </p>
              </div>
            </div>

            {paletteImage ? (
              <div className="palette-container">
                <img
                  src={paletteImage}
                  alt="Recommended eyeshadow palette"
                  className="palette-image"
                />
                <div className="palette-info">
                  <div>
                    <span> Skin Undertone </span>
                    <strong> {shadowPalette.skin_undertone || "-"} </strong>
                  </div>
                  <div>
                    <span> Clothing Hue </span>
                    <strong> {shadowPalette.clothing_hue ?? "-"} </strong>
                  </div>
                  <div>
                    <span> Palette Type </span>
                    <strong> {shadowPalette.path_type || "-"} </strong>
                  </div>
                </div>
              </div>
            ) : (
              <div className="no-palette"> No palette image available. </div>
            )}
          </section>

          {/* =================================================
              ACTION BUTTONS (FORMAL TITLES)
          ================================================= */}
          <div className="makeup-steps-action">
            <h2>Ready to Experience Your Makeup Application?</h2>
            <p>
              Review your comprehensive step-by-step application guide, launch the interactive virtual studio, or simulate foundation matching.
            </p>

            <div
              style={{
                display: "flex",
                gap: "15px",
                justify: "center",
                flexWrap: "wrap",
                marginTop: "18px",
              }}
            >
              {/* زر عرض الخطوات المخصصة */}
              <button
                type="button"
                className="makeup-steps-button"
                onClick={() =>
                  navigate(`/makeup-steps/${analysis.request_id}`)
                }
              >
                📋 View Detailed Application Steps
              </button>

              {/* زر فتح استوديو المحاكاة التفاعلي (Gradio 1 - Port 7860) */}
              <button
                type="button"
                className="makeup-steps-button"
                style={{
                  background: showGradio
                    ? "#2c3e50"
                    : "linear-gradient(135deg, #d87093 0%, #b85271 100%)",
                  border: "none",
                  boxShadow: "0 4px 14px rgba(216, 112, 147, 0.35)",
                  transition: "all 0.3s ease",
                }}
                onClick={() => {
                  setShowGradio(!showGradio);
                  if (!showGradio) setShowFoundationGradio(false);
                }}
              >
                {showGradio
                  ? "✕ Close Virtual Studio"
                  : "✨ Interactive Virtual Try-On"}
              </button>

              {/* زر فتح استوديو مطابقة الفاونديشن (Gradio 2 - Port 7861) */}
              <button
                type="button"
                className="makeup-steps-button"
                style={{
                  background: showFoundationGradio
                    ? "#2c3e50"
                    : "linear-gradient(135deg, #e06691 0%, #993355 100%)",
                  border: "none",
                  boxShadow: "0 4px 14px rgba(224, 102, 145, 0.35)",
                  transition: "all 0.3s ease",
                }}
                onClick={() => {
                  setShowFoundationGradio(!showFoundationGradio);
                  if (!showFoundationGradio) setShowGradio(false);
                }}
              >
                {showFoundationGradio
                  ? "✕ Close Foundation Swatches"
                  : "🌸 Foundation Swatches Engine"}
              </button>
            </div>
          </div>

          {/* =================================================
              EMBEDDED GRADIO 1 SECTION (VIRTUAL TRY-ON - PORT 7860)
          ================================================= */}
          {showGradio && (
            <section
              className="details-card"
              style={{
                marginTop: "30px",
                padding: "24px 16px",
                borderRadius: "20px",
                border: "1px solid #e8b4c8",
                boxShadow: "0 12px 35px rgba(216, 112, 147, 0.12)",
                backgroundColor: "#ffffff",
                overflow: "hidden",
              }}
            >
              <div
                className="section-title"
                style={{
                  marginBottom: "20px",
                  paddingBottom: "12px",
                  borderBottom: "1px solid #f3d5e0",
                }}
              >
                <span className="section-icon"> 🎨 </span>
                <div>
                  <h2
                    style={{
                      fontSize: "1.4rem",
                      color: "#333",
                      fontWeight: "700",
                    }}
                  >
                    Virtual Try-On & Makeup Studio
                  </h2>
                  <p style={{ color: "#666", fontSize: "0.95rem" }}>
                    Explore personalized virtual product applications, custom color palettes, and makeup strategies in real-time.
                  </p>
                </div>
              </div>

              <div
                style={{
                  width: "100%",
                  height: "950px",
                  borderRadius: "14px",
                  overflow: "hidden",
                  backgroundColor: "#fafafa",
                  boxShadow: "inset 0 0 10px rgba(0,0,0,0.03)",
                  border: "1px solid #eee",
                }}
              >
                <iframe
                  src="http://127.0.0.1:7860"
                  title="Virtual Try-On Engine"
                  style={{
                    width: "100%",
                    height: "100%",
                    border: "none",
                  }}
                />
              </div>
            </section>
          )}

          {/* =================================================
              EMBEDDED GRADIO 2 SECTION (FOUNDATION SWATCHES - PORT 7861)
          ================================================= */}
          {showFoundationGradio && (
            <section
              className="details-card"
              style={{
                marginTop: "30px",
                padding: "24px 16px",
                borderRadius: "20px",
                border: "1px solid #e8b4c8",
                boxShadow: "0 12px 35px rgba(216, 112, 147, 0.12)",
                backgroundColor: "#ffffff",
                overflow: "hidden",
              }}
            >
              <div
                className="section-title"
                style={{
                  marginBottom: "20px",
                  paddingBottom: "12px",
                  borderBottom: "1px solid #f3d5e0",
                }}
              >
                <span className="section-icon"> 🌸 </span>
                <div>
                  <h2
                    style={{
                      fontSize: "1.4rem",
                      color: "#333",
                      fontWeight: "700",
                    }}
                  >
                    Real Foundation Swatches Engine
                  </h2>
                  <p style={{ color: "#666", fontSize: "0.95rem" }}>
                    Select Dior palette shades and simulate customized foundation swatches and strategies directly on your face.
                  </p>
                </div>
              </div>

              <div
                style={{
                  width: "100%",
                  height: "950px",
                  borderRadius: "14px",
                  overflow: "hidden",
                  backgroundColor: "#fafafa",
                  boxShadow: "inset 0 0 10px rgba(0,0,0,0.03)",
                  border: "1px solid #eee",
                }}
              >
                <iframe
                  src="http://127.0.0.1:7861"
                  title="Real Foundation Swatches Engine"
                  style={{
                    width: "100%",
                    height: "100%",
                    border: "none",
                  }}
                />
              </div>
            </section>
          )}
        </div>
      )}
    </div>
  );
}

export default MakeupRequest;