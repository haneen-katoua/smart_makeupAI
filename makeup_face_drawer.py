import cv2



import numpy as np

LEFT_EYEBROW = [
    70, 63, 105, 66, 107,
    55, 65, 52, 53, 46
]

RIGHT_EYEBROW = [
    336, 296, 334, 293, 300,
    285, 295, 282, 283, 276
]

LEFT_EYESHADOW = [
    33, 246, 161, 160, 159, 158, 157, 173,
    105, 66, 107, 55, 65, 52, 53, 46, 124, 35
]

RIGHT_EYESHADOW = [
    263, 466, 388, 387, 386, 385, 384, 398,
    334, 293, 300, 285, 295, 282, 283, 276, 353, 265
]

def get_eyebrows(face_landmarks, width, height):

    left = []
    right = []

    for idx in LEFT_EYEBROW:
        p = face_landmarks.landmark[idx]
        left.append((
            int(p.x * width),
            int(p.y * height)
        ))

    for idx in RIGHT_EYEBROW:
        p = face_landmarks.landmark[idx]
        right.append((
            int(p.x * width),
            int(p.y * height)
        ))

    return (
        np.array(left, np.int32),
        np.array(right, np.int32)
    )


def get_eyeshadow_polygons(face_landmarks, w, h):

    left = np.array([
        (
            int(face_landmarks.landmark[i].x * w),
            int(face_landmarks.landmark[i].y * h)
        )
        for i in LEFT_EYESHADOW
    ], dtype=np.int32)

    right = np.array([
        (
            int(face_landmarks.landmark[i].x * w),
            int(face_landmarks.landmark[i].y * h)
        )
        for i in RIGHT_EYESHADOW
    ], dtype=np.int32)

    return left, right


    
class MakeupDrawer:

    def __init__(self):
        pass

    def create_overlay(self, image):

        h,w = image.shape[:2]

        return np.zeros((h,w,4),dtype=np.uint8)

    def alpha_blend(self, image, overlay):

        result = image.copy()

        alpha = overlay[:,:,3]/255.0

        for c in range(3):

            result[:,:,c] = (
                overlay[:,:,c]*alpha +
                result[:,:,c]*(1-alpha)
            )

        return result

    

    def draw_primer(
            self,
            image,
            template,
            opacity=35
    ):

        overlay = self.create_overlay(image)

        color = (
            255,
            248,
            240,
            opacity
        )

        cv2.fillPoly(
            overlay,
            [template.face_polygon],
            color
        )

        overlay = cv2.GaussianBlur(
            overlay,
            (81,81),
            0
        )

        return self.alpha_blend(image,overlay)
    
    
    def draw_foundation(
            self,
            image,
            template,
            opacity=55
    ):

        overlay = self.create_overlay(image)

        # لون فاونديشن محايد
        foundation_color = (
            228,
            205,
            182,
            opacity
        )

        cv2.fillPoly(
            overlay,
            [template.face_polygon],
            foundation_color
        )

        overlay = cv2.GaussianBlur(
            overlay,
            (91,91),
            0
        )

        return self.alpha_blend(image, overlay)
    
    def draw_concealer(
        self,
        image,
        template,
        opacity=110
    ):

        overlay = self.create_overlay(image)

        color = (
            210,
            235,
            255,
            opacity
        )

        regions = [

            template.concealer_left,
            template.concealer_right,

            template.concealer_forehead,

            template.concealer_nose,

            template.concealer_chin
        ]

        for region in regions:

            cv2.fillPoly(
                overlay,
                [region],
                color
            )

        overlay = cv2.GaussianBlur(
            overlay,
            (21,21),
            0
        )

        return self.alpha_blend(
            image,
            overlay
        )
        
    def draw_contour(
        self,
        image,
        template,
        opacity=90
    ):

        overlay = self.create_overlay(image)

        # لون بني غامق مناسب للكونتور (BGRA)
        color = (
            70,
            95,
            140,
            opacity
        )

        regions = [

            template.contour_left_forehead,
            template.contour_right_forehead,

            template.contour_left_cheek,
            template.contour_right_cheek,

            template.contour_left_jaw,
            template.contour_right_jaw
        ]

        for region in regions:

            cv2.fillPoly(
                overlay,
                [region],
                color
            )

        overlay = cv2.GaussianBlur(
            overlay,
            (41,41),
            0
        )

        return self.alpha_blend(
            image,
            overlay
        )
        
     
    def draw_blush(
        self,
        image,
        template,
        opacity=80
    ):

        overlay = self.create_overlay(image)

        # لون وردي طبيعي (BGRA)
        color = (
            120,
            100,
            220,
            opacity
        )

        cv2.circle(
            overlay,
            template.blush_left_center,
            template.blush_radius,
            color,
            -1,
            lineType=cv2.LINE_AA
        )

        cv2.circle(
            overlay,
            template.blush_right_center,
            template.blush_radius,
            color,
            -1,
            lineType=cv2.LINE_AA
        )

        overlay = cv2.GaussianBlur(
            overlay,
            (21,21),
            0
        )

        return self.alpha_blend(
            image,
            overlay
        )
    
    def draw_highlighter(
        self,
        image,
        template,
        opacity=95
    ):

        overlay = self.create_overlay(image)

        color = (
            220,
            245,
            255,
            opacity
        )

        regions = [

            template.highlight_left_cheek,
            template.highlight_right_cheek,

            template.highlight_nose,

            template.highlight_forehead,

            template.highlight_chin,

            template.highlight_cupid
        ]

        for region in regions:

            cv2.fillPoly(
                overlay,
                [region],
                color
            )

        overlay = cv2.GaussianBlur(
            overlay,
            (31,31),
            0
        )

        return self.alpha_blend(
            image,
            overlay
        )
        
    def apply_png_overlay(
        self,
        image,
        png_path
    ):

        overlay = cv2.imread(
            png_path,
            cv2.IMREAD_UNCHANGED
        )

        overlay = cv2.resize(
            overlay,
            (image.shape[1], image.shape[0])
        )

        return self.alpha_blend(
            image,
            overlay
        ) 
        
    def draw_nose_contour(
        self,
        image,
        template,
        opacity=110
    ):

        overlay = self.create_overlay(image)

        # لون بني للكونتور
        color = (
            70,
            90,
            135,
            opacity
        )

        cv2.fillPoly(
            overlay,
            [template.nose_contour_left],
            color
        )

        cv2.fillPoly(
            overlay,
            [template.nose_contour_right],
            color
        )

        overlay = cv2.GaussianBlur(
            overlay,
            (15,15),
            0
        )

        return self.alpha_blend(
            image,
            overlay
        )
    
    def draw_nose_highlight(
        self,
        image,
        template,
        opacity=140
    ):

        overlay = self.create_overlay(image)

        # أبيض مائل للكريمي حتى لا يبدو حادًا
        color = (
            255,
            255,
            255,
            opacity
        )

        cv2.fillPoly(
            overlay,
            [template.nose_highlight],
            color
        )

        overlay = cv2.GaussianBlur(
            overlay,
            (5,5),
            0
        )

        return self.alpha_blend(
            image,
            overlay
        )
    

    
    def draw_eyebrows(
        self,
        image,
        face_landmarks,
        strength=0.40
    ):

        h, w = image.shape[:2]

        left, right = get_eyebrows(
            face_landmarks,
            w,
            h
        )

        result = image.copy()

        mask = np.zeros((h, w), dtype=np.uint8)

        cv2.fillPoly(mask, [left], 255)
        cv2.fillPoly(mask, [right], 255)

        mask = cv2.GaussianBlur(
            mask,
            (5,5),
            0
        )

        alpha = (mask.astype(np.float32) / 255.0) * strength

        for c in range(3):

            result[:,:,c] = (
                result[:,:,c] * (1 - alpha)
            ).astype(np.uint8)

        return result
    
    
    def apply_png_overlay(
            self,
            image,
            png_path
        ):
    
            overlay = cv2.imread(
                png_path,
                cv2.IMREAD_UNCHANGED
            )
    
            overlay = cv2.resize(
                overlay,
                (image.shape[1], image.shape[0])
            )
    
            return self.alpha_blend(
                image,
                overlay
            ) 
            
    def apply_png_overlay(
            self,
            image,
            png_path
    ):

        overlay = cv2.imread(
            png_path,
            cv2.IMREAD_UNCHANGED
        )

        if overlay is None:
            raise FileNotFoundError(
                f"Cannot load {png_path}"
            )

        overlay = cv2.resize(
            overlay,
            (image.shape[1], image.shape[0])
        )

        return self.alpha_blend(
            image,
            overlay
        )