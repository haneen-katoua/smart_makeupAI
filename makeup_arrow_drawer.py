import cv2
import numpy as np


class ArrowMapper:

    def __init__(self, expert_output):
        self.data = expert_output
        
    
    def primer(self):

        return "full_face" 
    
    def foundation(self):

        return "full_face" \
    
    def concealer(self):

        return [
            "under_eye_left",
            "under_eye_right"
        ]
    
    def face_contour(self):

        placement = self.data["face"]["sculpt"]["placement"]

        if "مركز الخد" in placement:
            return [
                "cheek_center_left",
                "cheek_center_right"
            ]

        if "الأذن" in placement:
            return [
                "cheek_outer_left",
                "cheek_outer_right"
            ]

        return [
            "cheek_center_left",
            "cheek_center_right"
        ]