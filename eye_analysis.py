import cv2
import mediapipe as mp
import math


# =====================================================
# Distance
# =====================================================

def distance(p1, p2):

    return math.sqrt(
        (p1[0]-p2[0])**2 +
        (p1[1]-p2[1])**2
    )



# =====================================================
# Landmarks
# =====================================================


EYE_POINTS = {

    "left_corner": 33,
    "right_corner": 133,

    "upper_lid": 159,
    "lower_lid": 145,

    "iris_top": 474,
    "iris_bottom": 477,

}



BROW_POINTS = [

    70,
    63,
    105,
    66,
    107

]



FACE_POINTS = {

    "face_left":234,
    "face_right":454

}



# =====================================================
# Load Image
# =====================================================


image = cv2.imread(
    "pictures2/photo_2026-06-04_11-19-15.jpg"
)


if image is None:

    print("Image not found")
    exit()



rgb = cv2.cvtColor(
    image,
    cv2.COLOR_BGR2RGB
)



# =====================================================
# MediaPipe
# =====================================================


mp_face_mesh = mp.solutions.face_mesh



with mp_face_mesh.FaceMesh(

    static_image_mode=True,
    max_num_faces=1,
    refine_landmarks=True

) as mesh:



    result = mesh.process(rgb)



    if not result.multi_face_landmarks:

        print("No face detected")
        exit()



    face = result.multi_face_landmarks[0]


    h,w,_ = image.shape



    points = {}



    # -------------------------
    # Eye + Face points
    # -------------------------

    needed = {}

    needed.update(EYE_POINTS)
    needed.update(FACE_POINTS)



    for name,idx in needed.items():

        lm = face.landmark[idx]


        points[name] = (

            int(lm.x*w),
            int(lm.y*h)

        )



    # -------------------------
    # Brow
    # -------------------------

    brow_points=[]


    for idx in BROW_POINTS:

        lm = face.landmark[idx]

        brow_points.append(
            (
            int(lm.x*w),
            int(lm.y*h)
            )
        )



    brow_top = min(
        brow_points,
        key=lambda p:p[1]
    )



    # Drawing

    for p in points.values():

        cv2.circle(
            image,
            p,
            4,
            (0,255,0),
            -1
        )



# =====================================================
# Feature Extraction
# =====================================================


face_width = distance(
    points["face_left"],
    points["face_right"]
)



eye_width = distance(
    points["left_corner"],
    points["right_corner"]
)



eye_height = distance(
    points["upper_lid"],
    points["lower_lid"]
)



# طول العين

eye_length_ratio = (
    eye_width / eye_height
)



# نسبة العين للوجه

eye_height_ratio = (
    eye_height / face_width
)



eye_width_ratio = (
    eye_width / face_width
)



# اتجاه العين

corner_tilt = (

    points["right_corner"][1]
    -
    points["left_corner"][1]

) / face_width



# الحاجب

brow_distance = distance(
    points["upper_lid"],
    brow_top
)



brow_eye_ratio = (

    brow_distance / eye_height

)



# =====================================================
# New Hooded Features
# =====================================================


upper_lid_gap = distance(

    points["upper_lid"],
    points["iris_top"]

)


lower_lid_gap = distance(

    points["iris_bottom"],
    points["lower_lid"]

)



upper_visibility = (

    upper_lid_gap / eye_height

)



lower_visibility = (

    lower_lid_gap / eye_height

)



# =====================================================
# Classification
# =====================================================


# -------------------------
# Eye Shape
# -------------------------


if eye_length_ratio >= 2.4:

    eye_shape = "Almond"


elif eye_length_ratio <= 1.9:

    eye_shape = "Round"


else:

    eye_shape = "Average"



# -------------------------
# Eye Size
# -------------------------


if eye_height_ratio >= 0.095:

    eye_size="Large"


elif eye_height_ratio <= 0.065:

    eye_size="Small"


else:

    eye_size="Normal"



# -------------------------
# Corner
# -------------------------


if corner_tilt > 0.02:

    eye_corner="Downturned"


elif corner_tilt < -0.02:

    eye_corner="Upturned"


else:

    eye_corner="Neutral"



# -------------------------
# Eyelid
# -------------------------


if (

    upper_visibility < 0.20

    or brow_eye_ratio < 2.5

):

    eyelid_type="Hooded"


else:

    eyelid_type="Open"



# =====================================================
# Output
# =====================================================


print("\n========== FEATURES ==========")


print(
"Eye length ratio:",
round(eye_length_ratio,3)
)


print(
"Eye height ratio:",
round(eye_height_ratio,3)
)


print(
"Eye width ratio:",
round(eye_width_ratio,3)
)


print(
"Corner tilt:",
round(corner_tilt,3)
)


print(
"Brow/Eye:",
round(brow_eye_ratio,3)
)


print(
"Upper lid visibility:",
round(upper_visibility,3)
)



print("\n========== RESULT ==========")


print(
"Shape:",
eye_shape
)


print(
"Size:",
eye_size
)


print(
"Corner:",
eye_corner
)


print(
"Lid:",
eyelid_type
)



cv2.imwrite(
    "eye_final_analysis.jpg",
    image
)


print("\nSaved")