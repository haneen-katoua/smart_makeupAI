# -*- coding: utf-8 -*-

"""
Generate final makeup steps.

This module combines:
    1. Static makeup steps
    2. Expert analysis
    3. Arrow targets

The final steps are generated in memory and are NOT saved
into a shared final_makeup_steps.json file.
"""

from copy import deepcopy


# ==========================================================
# Extract Arrow Targets From Expert
# ==========================================================

def extract_arrow_targets(analysis):
    """
    Extract arrow targets from expert_output.

    Args:
        analysis:
            Makeup analysis dictionary.

    Returns:
        dict:
            {
                "Face Contour": "contour_cheeks",
                "Blush": "blush",
                ...
            }
    """

    if not isinstance(analysis, dict):
        return {}

    targets = {}

    expert = analysis.get(
        "expert_output",
        {}
    )

    if not isinstance(expert, dict):
        return targets

    # ======================================================
    # FACE
    # ======================================================

    face = expert.get(
        "face",
        {}
    )

    if isinstance(face, dict):

        # --------------------------------------------------
        # Face Contour
        # --------------------------------------------------

        sculpt = face.get(
            "sculpt",
            {}
        )

        if isinstance(sculpt, dict):

            target = sculpt.get(
                "arrow_target"
            )

            if target is not None:

                targets["Face Contour"] = target

        # --------------------------------------------------
        # Blush
        # --------------------------------------------------

        blush = face.get(
            "blush",
            {}
        )

        if isinstance(blush, dict):

            target = blush.get(
                "arrow_target"
            )

            if target is not None:

                targets["Blush"] = target

        # --------------------------------------------------
        # Face Highlight
        # --------------------------------------------------

        highlight = face.get(
            "highlight",
            {}
        )

        if isinstance(highlight, dict):

            target = highlight.get(
                "arrow_target"
            )

            if target is not None:

                targets["Face Highlight"] = target

    # ======================================================
    # BROWS
    # ======================================================

    brows = expert.get(
        "brows",
        {}
    )

    if isinstance(brows, dict):

        style = brows.get(
            "style",
            {}
        )

        if isinstance(style, dict):

            target = style.get(
                "arrow_target"
            )

            if target is not None:

                targets["Eyebrows"] = target

    # ======================================================
    # EYES
    # ======================================================

    eyes = expert.get(
        "eyes",
        {}
    )

    if isinstance(eyes, dict):

        # --------------------------------------------------
        # Left eye
        # --------------------------------------------------

        left = eyes.get(
            "left",
            {}
        )

        if not isinstance(left, dict):
            left = {}

        left_plan = left.get(
            "plan",
            {}
        )

        if not isinstance(left_plan, dict):
            left_plan = {}

        # --------------------------------------------------
        # Right eye
        # --------------------------------------------------

        right = eyes.get(
            "right",
            {}
        )

        if not isinstance(right, dict):
            right = {}

        right_plan = right.get(
            "plan",
            {}
        )

        if not isinstance(right_plan, dict):
            right_plan = {}

        # ==================================================
        # Eyeshadow
        # ==================================================

        left_target = left_plan.get(
            "eyeshadow_arrow_target"
        )

        right_target = right_plan.get(
            "eyeshadow_arrow_target"
        )

        if left_target is not None:

            targets["Eyeshadow"] = left_target

        elif right_target is not None:

            targets["Eyeshadow"] = right_target

        # ==================================================
        # Eyeliner
        # ==================================================

        left_target = left_plan.get(
            "eyeliner_arrow_target"
        )

        right_target = right_plan.get(
            "eyeliner_arrow_target"
        )

        if left_target is not None:

            targets["Eyeliner"] = left_target

        elif right_target is not None:

            targets["Eyeliner"] = right_target

        # ==================================================
        # Mascara
        # ==================================================

        left_target = left_plan.get(
            "mascara_arrow_target"
        )

        right_target = right_plan.get(
            "mascara_arrow_target"
        )

        if left_target is not None:

            targets["Mascara"] = left_target

        elif right_target is not None:

            targets["Mascara"] = right_target

    # ======================================================
    # NOSE
    # ======================================================

    nose = expert.get(
        "nose",
        {}
    )

    if isinstance(nose, dict):

        nose_map = nose.get(
            "map",
            {}
        )

        if not isinstance(nose_map, dict):
            nose_map = {}

        # --------------------------------------------------
        # Nose Contour
        # --------------------------------------------------

        contour_target = nose_map.get(
            "contour_arrow_target"
        )

        if contour_target is not None:

            targets["Nose Contour"] = contour_target

        # --------------------------------------------------
        # Nose Highlight
        # --------------------------------------------------

        highlight_target = nose_map.get(
            "highlight_arrow_target"
        )

        if highlight_target is not None:

            targets["Nose Highlight"] = highlight_target

    # ======================================================
    # LIPS
    # ======================================================

    lips = expert.get(
        "lips",
        {}
    )

    if isinstance(lips, dict):

        # --------------------------------------------------
        # Lip Liner
        # --------------------------------------------------

        shape = lips.get(
            "shape",
            {}
        )

        if isinstance(shape, dict):

            target = shape.get(
                "arrow_target"
            )

            if target is not None:

                targets["Lip Liner"] = target

        # --------------------------------------------------
        # Lipstick
        # --------------------------------------------------

        color = lips.get(
            "color",
            {}
        )

        if isinstance(color, dict):

            target = color.get(
                "arrow_target"
            )

            if target is not None:

                targets["Lipstick"] = target

    return targets


# ==========================================================
# Default Targets
# ==========================================================

DEFAULT_TARGETS = {

    "Prepare Skin": "full_face",

    "Apply Foundation": "full_face",

    "Apply Concealer": "under_eye",

    "Set Makeup": "full_face",
}


# ==========================================================
# Create Final Steps
# ==========================================================

def create_final_steps_from_analysis(
    steps,
    analysis
):
    """
    Create final makeup steps for ONE user/request.

    Expert arrow targets have the highest priority.

    Priority:

        1. Expert arrow_target
        2. Default target
        3. Existing step targets
        4. None

    Args:
        steps:
            Base makeup steps loaded from makeup_steps.json.

        analysis:
            Analysis result belonging to one MakeupRequest.

    Returns:
        list:
            User-specific final makeup steps.
    """

    arrow_targets = extract_arrow_targets(
        analysis
    )

    final_steps = []

    for original_step in steps:

        # Avoid modifying original steps
        step = deepcopy(
            original_step
        )

        title = step.get(
            "title",
            ""
        )

        # ==================================================
        # 1. Expert target
        # ==================================================

        if title in arrow_targets:

            target = arrow_targets[
                title
            ]

            if target is not None:

                step["arrow_target"] = target

                final_steps.append(
                    step
                )

                continue

        # ==================================================
        # 2. Default target
        # ==================================================

        if title in DEFAULT_TARGETS:

            step["arrow_target"] = (
                DEFAULT_TARGETS[title]
            )

            final_steps.append(
                step
            )

            continue

        # ==================================================
        # 3. Existing target
        # ==================================================

        existing_targets = step.get(
            "targets"
        )

        if existing_targets:

            step["arrow_target"] = (
                existing_targets
            )

        else:

            step["arrow_target"] = None

        final_steps.append(
            step
        )

    return final_steps