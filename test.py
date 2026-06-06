# import cv2
# import mediapipe as mp

# # قراءة الصورة
# image = cv2.imread("face.jpg")

# # تحويل الألوان
# rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

# # تشغيل Face Mesh
# mp_face_mesh = mp.solutions.face_mesh

# with mp_face_mesh.FaceMesh(static_image_mode=True) as face_mesh:

#     results = face_mesh.process(rgb_image)

#     # إذا اكتشف وجه
#     if results.multi_face_landmarks:

#         for face_landmarks in results.multi_face_landmarks:

#             # رسم النقاط
#             for landmark in face_landmarks.landmark:

#                 h, w, c = image.shape

#                 x = int(landmark.x * w)
#                 y = int(landmark.y * h)

#                 cv2.circle(image, (x, y), 1, (0,255,0), -1)

# # عرض الصورة
# cv2.imwrite("output.jpg", image)

# print("photo saved")



import cv2
import mediapipe as mp
import plotly.graph_objects as go

# قراءة الصورة
image = cv2.imread("face.jpg")

rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

# FaceMesh
mp_face_mesh = mp.solutions.face_mesh

face_mesh = mp_face_mesh.FaceMesh(static_image_mode=True)

results = face_mesh.process(rgb_image)

# استخراج النقاط
if results.multi_face_landmarks:

    face_landmarks = results.multi_face_landmarks[0]

    x_list = []
    y_list = []
    z_list = []

    for landmark in face_landmarks.landmark:

        x_list.append(landmark.x)
        y_list.append(-landmark.y)
        z_list.append(-landmark.z)

    # رسم ثلاثي الأبعاد
    fig = go.Figure(data=[go.Scatter3d(
        x=x_list,
        y=y_list,
        z=z_list,
        mode='markers'
    )])

    fig.show()