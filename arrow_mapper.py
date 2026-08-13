# -*- coding: utf-8 -*-

import cv2
import mediapipe as mp


class ArrowMapper:

    def __init__(self, image):

        self.image = image

        self.height, self.width = image.shape[:2]

        self.landmarks = self._get_landmarks()

    # =====================================================
    # MediaPipe
    # =====================================================

    def _get_landmarks(self):

        mp_face_mesh = mp.solutions.face_mesh

        rgb = cv2.cvtColor(
            self.image,
            cv2.COLOR_BGR2RGB
        )

        with mp_face_mesh.FaceMesh(
            static_image_mode=True,
            max_num_faces=1,
            refine_landmarks=True,
            min_detection_confidence=0.5
        ) as face_mesh:

            result = face_mesh.process(rgb)

            if not result.multi_face_landmarks:
                print("[WARNING] No face detected")
                return None

            return result.multi_face_landmarks[0].landmark

    # =====================================================
    # Target aliases
    # =====================================================

    def normalize_target(self, target):

        aliases = {

            # -------------------------------------------------
            # Base
            # -------------------------------------------------

            "primer": "full_face",
            "foundation": "full_face",

            # -------------------------------------------------
            # Face contour
            # -------------------------------------------------

            "face_contour": "cheeks",
            "left_face_contour": "left_cheek",
            "right_face_contour": "right_cheek",

            "left_cheek": "left_cheek",
            "right_cheek": "right_cheek",

            "cheek": "cheeks",

            # -------------------------------------------------
            # Face highlight
            # -------------------------------------------------

            "face_highlight": "highlight_cheeks",

            # -------------------------------------------------
            # Concealer
            # -------------------------------------------------

            "under_eye": "concealer",

            "concealer_left": "concealer_left",
            "concealer_right": "concealer_right",

            # -------------------------------------------------
            # Eyeshadow
            # -------------------------------------------------

            "eyeshadow": "eyeshadow",
            "eyelid": "eyeshadow",

            "left_upper_eyelid": "left_eyeshadow",
            "right_upper_eyelid": "right_eyeshadow",

            # -------------------------------------------------
            # Eyeliner
            # -------------------------------------------------

            "eyeliner": "eyeliner",

            "left_eyeliner": "left_eyeliner",
            "right_eyeliner": "right_eyeliner",

            # -------------------------------------------------
            # Mascara
            # -------------------------------------------------

            "lashes": "lashes",

            "left_lashes": "left_lashes",
            "right_lashes": "right_lashes",

            "mascara": "lashes",

            # -------------------------------------------------
            # Brows
            # -------------------------------------------------

            "eyebrows": "brows",
            "left_eyebrow": "left_brow",
            "right_eyebrow": "right_brow",
            "brows": "brows",

            # -------------------------------------------------
            # Nose
            # -------------------------------------------------

            "nose": "nose_bridge",
            "nose_highlight": "nose_bridge",

            # -------------------------------------------------
            # Lips
            # -------------------------------------------------

            "lip_border": "lip_border",

            "upper_lip": "upper_lip",
            "lower_lip": "lower_lip",

            "lipstick": "lips",
            "lips": "lips",

            # -------------------------------------------------
            # Full face
            # -------------------------------------------------

            "full_face": "full_face",
        }

        return aliases.get(
            target,
            target
        )

    # =====================================================
    # Point Groups
    #
    # MediaPipe Face Mesh landmarks
    # =====================================================

    POINT_GROUPS = {

        # =================================================
        # FULL FACE
        # =================================================

        "forehead": [
            10,
            151,
            9
        ],

        "left_cheek": [
            50,
            101,
            116,
            123,
            147,
            205
        ],

        "right_cheek": [
            280,
            330,
            346,
            352,
            376,
            425
        ],

        "cheeks": [
            50,
            101,
            116,
            123,
            147,
            205,
            280,
            330,
            346,
            352,
            376,
            425
        ],

        "full_face": [
            10,
            152
        ],

        # =================================================
        # FACE HIGHLIGHT
        # =================================================

        "highlight_left_cheek": [
            116,
            117,
            118,
            119
        ],

        "highlight_right_cheek": [
            345,
            346,
            347,
            348
        ],

        "highlight_cheeks": [
            116,
            117,
            118,
            119,
            345,
            346,
            347,
            348
        ],

        # =================================================
        # CONCEALER
        #
        # Points are intentionally BELOW the eye.
        # =================================================

        "concealer_left": [
            145,
            153,
            154,
            155
        ],

        "concealer_right": [
            374,
            380,
            381,
            382
        ],

        "concealer": [
            145,
            153,
            154,
            155,
            374,
            380,
            381,
            382
        ],

        # =================================================
        # EYESHADOW
        # =================================================

        "left_eyeshadow": [
            157,
            158,
            159,
            160,
            161
        ],

        "right_eyeshadow": [
            384,
            385,
            386,
            387,
            388
        ],

        "eyeshadow": [
            157,
            158,
            159,
            160,
            161,
            384,
            385,
            386,
            387,
            388
        ],

        # =================================================
        # EYELINER
        #
        # We use the actual upper eye contour.
        # =================================================

        "left_eyeliner": [
            33,
            133,
            159
        ],

        "right_eyeliner": [
            362,
            263,
            386
        ],

        "eyeliner": [
            33,
            133,
            159,
            362,
            263,
            386
        ],

        # =================================================
        # LASHES
        # =================================================

        "left_lashes": [
            33,
            133,
            145,
            159
        ],

        "right_lashes": [
            362,
            263,
            374,
            386
        ],

        "lashes": [
            33,
            133,
            145,
            159,
            362,
            263,
            374,
            386
        ],

        # =================================================
        # BROWS
        # =================================================

        "left_brow": [
            46,
            52,
            55,
            65,
            105
        ],

        "right_brow": [
            276,
            282,
            285,
            295,
            334
        ],

        "brows": [
            46,
            52,
            55,
            65,
            105,
            276,
            282,
            285,
            295,
            334
        ],

        # =================================================
        # NOSE
        # =================================================

        "nose_bridge": [
            6,
            197,
            195
        ],

        "nose_tip": [
            1,
            2,
            4
        ],

        "nose_contour_left": [
            217,
            218,
            219
        ],

        "nose_contour_right": [
            437,
            438,
            439
        ],

        # =================================================
        # LIPS
        # =================================================

        "lips": [
            0,
            13,
            14,
            17
        ],

        "upper_lip": [
            0,
            13,
            82,
            312
        ],

        "lower_lip": [
            14,
            17,
            87,
            317
        ],

        # Actual lip border areas
        "left_lip_border": [
            61,
            146,
            91,
            181
        ],

        "right_lip_border": [
            291,
            375,
            321,
            405
        ],

        "lip_border": [
            61,
            146,
            91,
            181,
            291,
            375,
            321,
            405
        ]
    }

    # =====================================================
    # Average point
    # =====================================================

    def average_point(self, indexes):

        if self.landmarks is None:
            return None

        if not indexes:
            return None

        xs = []
        ys = []

        for idx in indexes:

            if idx >= len(self.landmarks):
                continue

            point = self.landmarks[idx]

            xs.append(point.x)
            ys.append(point.y)

        if not xs:
            return None

        x = int(
            sum(xs) / len(xs) * self.width
        )

        y = int(
            sum(ys) / len(ys) * self.height
        )

        return (
            x,
            y
        )

    # =====================================================
    # Move point vertically
    # =====================================================

    def move_y(self, point, ratio):

        if point is None:
            return None

        x, y = point

        y += int(
            self.height * ratio
        )

        y = max(
            0,
            min(
                self.height - 1,
                y
            )
        )

        return (
            x,
            y
        )

    # =====================================================
    # Get point
    # =====================================================

    def get_point(self, target):

        target = self.normalize_target(
            target
        )

        if target not in self.POINT_GROUPS:
            return None

        point = self.average_point(
            self.POINT_GROUPS[target]
        )

        # -------------------------------------------------
        # Concealer must be BELOW the eye.
        # -------------------------------------------------

        if target in [
            "concealer_left",
            "concealer_right"
        ]:

            point = self.move_y(
                point,
                0.035
            )

        return point

    # =====================================================
    # Start point
    # =====================================================

    def _get_start_point(
        self,
        end,
        distance_ratio=0.20
    ):

        x, y = end

        distance = int(
            self.width * distance_ratio
        )

        if x < self.width / 2:

            start = (
                max(
                    20,
                    x - distance
                ),
                y
            )

        else:

            start = (
                min(
                    self.width - 20,
                    x + distance
                ),
                y
            )

        return start

    # =====================================================
    # Eye arrow
    # =====================================================

    def _get_eye_arrow(self, target):

        target = self.normalize_target(target)

        # =================================================
        # LEFT EYE
        # =================================================

        if target == "left_eyeliner":

            # الزاوية الخارجية للعين
            end = self.average_point([
                33
            ])

            if end is None:
                return None

            # السهم يأتي من خارج الوجه باتجاه
            # الزاوية الخارجية للعين
            start = (
                max(
                    20,
                    end[0] - int(self.width * 0.12)
                ),
                end[1]
            )

            return {
                "start": start,
                "end": end
            }

        # =================================================
        # RIGHT EYE
        # =================================================

        if target == "right_eyeliner":

            # الزاوية الخارجية للعين
            end = self.average_point([
                263
            ])

            if end is None:
                return None

            # السهم يأتي من خارج الوجه باتجاه
            # الزاوية الخارجية للعين
            start = (
                min(
                    self.width - 20,
                    end[0] + int(self.width * 0.12)
                ),
                end[1]
            )

            return {
                "start": start,
                "end": end
            }

        # =================================================
        # LEFT LASHES
        # =================================================

        if target == "left_lashes":

            end = self.average_point([
                33
            ])

            if end is None:
                return None

            start = (
                max(
                    20,
                    end[0] - int(self.width * 0.10)
                ),
                end[1]
            )

            return {
                "start": start,
                "end": end
            }

        # =================================================
        # RIGHT LASHES
        # =================================================

        if target == "right_lashes":

            end = self.average_point([
                263
            ])

            if end is None:
                return None

            start = (
                min(
                    self.width - 20,
                    end[0] + int(self.width * 0.10)
                ),
                end[1]
            )

            return {
                "start": start,
                "end": end
            }

        return None

    # =====================================================
    # Lip border arrow
    # =====================================================

    def _get_lip_border_arrows(self):

        left_end = self.average_point(
            self.POINT_GROUPS[
                "left_lip_border"
            ]
        )

        right_end = self.average_point(
            self.POINT_GROUPS[
                "right_lip_border"
            ]
        )

        arrows = []

        # -------------------------------------------------
        # LEFT BORDER
        # -------------------------------------------------

        if left_end is not None:

            start = (
                max(
                    20,
                    left_end[0] - int(
                        self.width * 0.12
                    )
                ),
                left_end[1]
            )

            arrows.append({
                "start": start,
                "end": left_end
            })

        # -------------------------------------------------
        # RIGHT BORDER
        # -------------------------------------------------

        if right_end is not None:

            start = (
                min(
                    self.width - 20,
                    right_end[0] + int(
                        self.width * 0.12
                    )
                ),
                right_end[1]
            )

            arrows.append({
                "start": start,
                "end": right_end
            })

        return arrows

    # =====================================================
    # Cheek arrows
    # =====================================================

    def _get_cheek_arrows(self):

        arrows = []

        left_end = self.average_point(
            self.POINT_GROUPS[
                "left_cheek"
            ]
        )

        right_end = self.average_point(
            self.POINT_GROUPS[
                "right_cheek"
            ]
        )

        # -------------------------------------------------
        # LEFT CHEEK
        # -------------------------------------------------

        if left_end is not None:

            start = (
                max(
                    20,
                    left_end[0] - int(
                        self.width * 0.18
                    )
                ),
                left_end[1]
            )

            arrows.append({
                "start": start,
                "end": left_end
            })

        # -------------------------------------------------
        # RIGHT CHEEK
        # -------------------------------------------------

        if right_end is not None:

            start = (
                min(
                    self.width - 20,
                    right_end[0] + int(
                        self.width * 0.18
                    )
                ),
                right_end[1]
            )

            arrows.append({
                "start": start,
                "end": right_end
            })

        return arrows

    # =====================================================
    # Full face arrows
    #
    # Primer / Foundation / Set Makeup
    # =====================================================

    def _get_full_face_arrows(self):

        arrows = []

        # -------------------------------------------------
        # Forehead
        # -------------------------------------------------

        forehead = self.average_point(
            self.POINT_GROUPS[
                "forehead"
            ]
        )

        if forehead is not None:

            start = (
                forehead[0],
                max(
                    20,
                    forehead[1] - int(
                        self.height * 0.15
                    )
                )
            )

            arrows.append({
                "start": start,
                "end": forehead
            })

        # -------------------------------------------------
        # Left cheek
        # -------------------------------------------------

        left = self.average_point(
            self.POINT_GROUPS[
                "left_cheek"
            ]
        )

        if left is not None:

            start = (
                max(
                    20,
                    left[0] - int(
                        self.width * 0.18
                    )
                ),
                left[1]
            )

            arrows.append({
                "start": start,
                "end": left
            })

        # -------------------------------------------------
        # Right cheek
        # -------------------------------------------------

        right = self.average_point(
            self.POINT_GROUPS[
                "right_cheek"
            ]
        )

        if right is not None:

            start = (
                min(
                    self.width - 20,
                    right[0] + int(
                        self.width * 0.18
                    )
                ),
                right[1]
            )

            arrows.append({
                "start": start,
                "end": right
            })

        return arrows
    
    # =====================================================
    # Brow arrows
    # =====================================================

    def _get_brow_arrows(self):

        arrows = []

        # -------------------------------------------------
        # Left eyebrow
        # -------------------------------------------------

        left_end = self.average_point(
            self.POINT_GROUPS["left_brow"]
        )

        if left_end is not None:

            start = (
                max(
                    20,
                    left_end[0] - int(
                        self.width * 0.12
                    )
                ),
                left_end[1]
            )

            arrows.append({
                "start": start,
                "end": left_end
            })

        # -------------------------------------------------
        # Right eyebrow
        # -------------------------------------------------

        right_end = self.average_point(
            self.POINT_GROUPS["right_brow"]
        )

        if right_end is not None:

            start = (
                min(
                    self.width - 20,
                    right_end[0] + int(
                        self.width * 0.12
                    )
                ),
                right_end[1]
            )

            arrows.append({
                "start": start,
                "end": right_end
            })

        return arrows

    # =====================================================
    # Generic multiple arrows
    # =====================================================

    def get_arrows(self, target):

        target = self.normalize_target(
            target
        )

        # -------------------------------------------------
        # Full face
        # -------------------------------------------------

        if target == "full_face":

            return self._get_full_face_arrows()

        # -------------------------------------------------
        # Cheeks
        # -------------------------------------------------

        if target in [
            "cheeks"
        ]:

            return self._get_cheek_arrows()
        
        
        # -------------------------------------------------
        # Brows
        # -------------------------------------------------

        if target == "brows":

            arrows = []

            left = self._get_single_arrow(
                "left_brow"
            )

            right = self._get_single_arrow(
                "right_brow"
            )

            if left:
                arrows.append(left)

            if right:
                arrows.append(right)

            return arrows

        # -------------------------------------------------
        # Concealer
        # -------------------------------------------------

        if target == "concealer":

            arrows = []

            left = self._get_single_arrow(
                "concealer_left"
            )

            right = self._get_single_arrow(
                "concealer_right"
            )

            if left:
                arrows.append(left)

            if right:
                arrows.append(right)

            return arrows

        # -------------------------------------------------
        # Eyeshadow
        # -------------------------------------------------

        if target == "eyeshadow":

            arrows = []

            left = self._get_single_arrow(
                "left_eyeshadow"
            )

            right = self._get_single_arrow(
                "right_eyeshadow"
            )

            if left:
                arrows.append(left)

            if right:
                arrows.append(right)

            return arrows

        # -------------------------------------------------
        # Eyeliner
        # -------------------------------------------------

        if target == "eyeliner":

            arrows = []

            left = self._get_eye_arrow(
                "left_eyeliner"
            )

            right = self._get_eye_arrow(
                "right_eyeliner"
            )

            if left:
                arrows.append(left)

            if right:
                arrows.append(right)

            return arrows

        # -------------------------------------------------
        # Lashes
        # -------------------------------------------------

        if target == "lashes":

            arrows = []

            left = self._get_eye_arrow(
                "left_lashes"
            )

            right = self._get_eye_arrow(
                "right_lashes"
            )

            if left:
                arrows.append(left)

            if right:
                arrows.append(right)

            return arrows

        # -------------------------------------------------
        # Lip border
        # -------------------------------------------------

        if target == "lip_border":

            return self._get_lip_border_arrows()

        return []

    # =====================================================
    # Single arrow helper
    # =====================================================

    def _get_single_arrow(self, target):

        end = self.get_point(
            target
        )

        if end is None:
            return None

        start = self._get_start_point(
            end
        )

        return {
            "start": start,
            "end": end
        }

    # =====================================================
    # MAIN
    # =====================================================

    def get_arrow(self, target):

        if target is None:
            return None

        # -------------------------------------------------
        # If target is a list
        # -------------------------------------------------

        if isinstance(target, list):

            arrows = []

            for item in target:

                result = self.get_arrow(
                    item
                )

                if result is None:
                    continue

                if isinstance(result, list):
                    arrows.extend(result)
                else:
                    arrows.append(result)

            return arrows

        target = self.normalize_target(
            target
        )

        # -------------------------------------------------
        # Multiple arrow targets
        # -------------------------------------------------

        if target in [
            "full_face",
            "cheeks",
            "concealer",
            "eyeshadow",
            "eyeliner",
            "lashes",
            "lip_border",
            "brows"
        ]:

            return self.get_arrows(
                target
            )

        # -------------------------------------------------
        # Eye arrows
        # -------------------------------------------------

        if target in [
            "left_eyeliner",
            "right_eyeliner",
            "left_lashes",
            "right_lashes"
        ]:

            return self._get_eye_arrow(
                target
            )

        # -------------------------------------------------
        # Lip border
        # -------------------------------------------------

        if target == "lip_border":

            return self._get_lip_border_arrows()

        # -------------------------------------------------
        # Normal target
        # -------------------------------------------------

        end = self.get_point(
            target
        )

        if end is None:
            return None

        start = self._get_start_point(
            end
        )

        return {
            "start": start,
            "end": end
        }