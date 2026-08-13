# -*- coding: utf-8 -*-

"""
face_template.py

Face template coordinates for makeup arrows and overlays.

Compatible arrow_target values:

face_contour
cheeks
face_highlight

nose_contour_left
nose_contour_right
nose_bridge
nose_tip

eyelid
eyeliner
lashes

brows

lip_border
lips

full_face
"""


from dataclasses import dataclass
import numpy as np



@dataclass
class FaceTemplate:

    # Face
    face_polygon: np.ndarray


    # Face makeup
    face_contour_left: np.ndarray
    face_contour_right: np.ndarray

    cheeks_left: np.ndarray
    cheeks_right: np.ndarray

    face_highlight_left: np.ndarray
    face_highlight_right: np.ndarray


    # Nose

    nose_contour_left: np.ndarray
    nose_contour_right: np.ndarray

    nose_bridge: np.ndarray
    nose_tip: np.ndarray


    # Eyes

    eyelid_left: np.ndarray
    eyelid_right: np.ndarray

    eyeliner_left: np.ndarray
    eyeliner_right: np.ndarray

    lashes_left: np.ndarray
    lashes_right: np.ndarray


    # Brows

    brows_left: np.ndarray
    brows_right: np.ndarray


    # Lips

    lip_border: np.ndarray
    lips: np.ndarray




def scale_points(points, width, height):

    points = points.copy()

    points[:,0] *= width
    points[:,1] *= height

    return points.astype(np.int32)




def load_template(width, height):


    # ==========================
    # Face outline
    # ==========================

    face_polygon = np.array([
        (0.17,0.18),
        (0.24,0.08),
        (0.50,0.03),
        (0.76,0.08),
        (0.83,0.18),

        (0.86,0.38),
        (0.84,0.63),

        (0.72,0.86),
        (0.50,0.97),
        (0.28,0.86),

        (0.16,0.63),
        (0.14,0.38)

    ])



    # ==========================
    # Face contour
    # ==========================

    face_contour_left = np.array([
        (0.20,0.42),
        (0.34,0.45),
        (0.28,0.62),
        (0.17,0.65)
    ])


    face_contour_right = np.array([
        (0.66,0.45),
        (0.80,0.42),
        (0.83,0.65),
        (0.72,0.62)
    ])



    # ==========================
    # Cheeks
    # ==========================

    cheeks_left = np.array([
        (0.25,0.50),
        (0.40,0.50),
        (0.40,0.60),
        (0.25,0.60)
    ])


    cheeks_right = np.array([
        (0.60,0.50),
        (0.75,0.50),
        (0.75,0.60),
        (0.60,0.60)
    ])




    # ==========================
    # Highlight
    # ==========================


    face_highlight_left = np.array([
        (0.32,0.43),
        (0.45,0.43),
        (0.45,0.48),
        (0.33,0.48)
    ])


    face_highlight_right = np.array([
        (0.55,0.43),
        (0.68,0.43),
        (0.67,0.48),
        (0.55,0.48)
    ])




    # ==========================
    # Nose
    # ==========================


    nose_contour_left = np.array([
        (0.455,0.35),
        (0.465,0.35),
        (0.465,0.63),
        (0.450,0.63)
    ])


    nose_contour_right = np.array([
        (0.535,0.35),
        (0.545,0.35),
        (0.550,0.63),
        (0.535,0.63)
    ])



    nose_bridge = np.array([
        (0.485,0.35),
        (0.515,0.35),
        (0.515,0.62),
        (0.485,0.62)
    ])



    nose_tip = np.array([
        (0.46,0.62),
        (0.54,0.62),
        (0.54,0.70),
        (0.46,0.70)
    ])




    # ==========================
    # Eyes
    # ==========================


    eyelid_left = np.array([
        (0.28,0.32),
        (0.42,0.32),
        (0.42,0.40),
        (0.28,0.40)
    ])


    eyelid_right = np.array([
        (0.58,0.32),
        (0.72,0.32),
        (0.72,0.40),
        (0.58,0.40)
    ])




    eyeliner_left = np.array([
        (0.28,0.38),
        (0.42,0.38),
        (0.42,0.40),
        (0.28,0.40)
    ])


    eyeliner_right = np.array([
        (0.58,0.38),
        (0.72,0.38),
        (0.72,0.40),
        (0.58,0.40)
    ])




    lashes_left = np.array([
        (0.30,0.40),
        (0.42,0.40),
        (0.42,0.42),
        (0.30,0.42)
    ])


    lashes_right = np.array([
        (0.58,0.40),
        (0.70,0.40),
        (0.70,0.42),
        (0.58,0.42)
    ])




    # ==========================
    # Brows
    # ==========================


    brows_left = np.array([
        (0.24,0.25),
        (0.42,0.25),
        (0.42,0.31),
        (0.24,0.31)
    ])


    brows_right = np.array([
        (0.58,0.25),
        (0.76,0.25),
        (0.76,0.31),
        (0.58,0.31)
    ])




    # ==========================
    # Lips
    # ==========================


    lip_border = np.array([
        (0.39,0.67),
        (0.61,0.67),
        (0.61,0.74),
        (0.39,0.74)
    ])


    lips = np.array([
        (0.41,0.68),
        (0.59,0.68),
        (0.58,0.73),
        (0.42,0.73)
    ])




    return FaceTemplate(

        face_polygon=scale_points(face_polygon,width,height),

        face_contour_left=scale_points(face_contour_left,width,height),
        face_contour_right=scale_points(face_contour_right,width,height),

        cheeks_left=scale_points(cheeks_left,width,height),
        cheeks_right=scale_points(cheeks_right,width,height),

        face_highlight_left=scale_points(face_highlight_left,width,height),
        face_highlight_right=scale_points(face_highlight_right,width,height),


        nose_contour_left=scale_points(nose_contour_left,width,height),
        nose_contour_right=scale_points(nose_contour_right,width,height),

        nose_bridge=scale_points(nose_bridge,width,height),
        nose_tip=scale_points(nose_tip,width,height),


        eyelid_left=scale_points(eyelid_left,width,height),
        eyelid_right=scale_points(eyelid_right,width,height),

        eyeliner_left=scale_points(eyeliner_left,width,height),
        eyeliner_right=scale_points(eyeliner_right,width,height),

        lashes_left=scale_points(lashes_left,width,height),
        lashes_right=scale_points(lashes_right,width,height),


        brows_left=scale_points(brows_left,width,height),
        brows_right=scale_points(brows_right,width,height),


        lip_border=scale_points(lip_border,width,height),
        lips=scale_points(lips,width,height)

    )





# ===============================
# Arrow Mapping
# ===============================


ARROW_POINTS = {


    "full_face": (368,520),



    "face_contour": {

        "left": (230,610),
        "right": (505,610)

    },


    "cheeks": {

        "left": (280,570),
        "right": (455,570)

    },


    "face_highlight": {

        "left": (330,520),
        "right": (405,520)

    },



    "nose_contour_left": (345,520),

    "nose_contour_right": (390,520),

    "nose_bridge": (368,470),

    "nose_tip": (368,650),



    "eyelid": {

        "left": (315,350),
        "right": (420,350)

    },


    "eyeliner": {

        "left": (315,370),
        "right": (420,370)

    },


    "lashes": {

        "left": (315,390),
        "right": (420,390)

    },



    "brows": {

        "left": (315,285),
        "right": (420,285)

    },



    "lip_border": (368,730),

    "lips": (368,780)

}