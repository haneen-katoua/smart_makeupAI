# -*- coding: utf-8 -*-

import cv2

from django.core.files.base import ContentFile

from ..models import MakeupStepImage

from arrow_mapper import ArrowMapper

import json
import os

from django.conf import settings


# ==========================================================
# Draw Arrow
# ==========================================================

def draw_arrow(
    image,
    arrow
):
    """
    Draw one arrow on image.
    """

    if not arrow:
        return

    start = arrow.get(
        "start"
    )

    end = arrow.get(
        "end"
    )

    if start is None or end is None:
        return

    cv2.arrowedLine(
        image,
        tuple(start),
        tuple(end),
        (0, 0, 0),
        4,
        tipLength=0.15
    )


# ==========================================================
# Generate Makeup Step Images
# ==========================================================

def generate_makeup_step_images(
    makeup_request,
    image,
    final_steps
):
    """
    Generate images for one MakeupRequest.

    Each step gets its own image.

    Args:
        makeup_request:
            MakeupRequest instance.

        image:
            OpenCV BGR image.

        final_steps:
            User-specific final makeup steps.

    Returns:
        list[MakeupStepImage]
    """

    if image is None:
        raise ValueError(
            "Image is empty."
        )

    # ======================================================
    # Delete previously generated steps
    # ======================================================

    MakeupStepImage.objects.filter(
        makeup_request=makeup_request
    ).delete()

    # ======================================================
    # Create ArrowMapper
    # ======================================================

    mapper = ArrowMapper(
        image
    )

    results = []

    # ======================================================
    # Generate every step
    # ======================================================

    for step in final_steps:

        step_number = step.get(
            "step_number"
        )

        title = step.get(
            "title",
            ""
        )

        category = step.get(
            "category",
            ""
        )

        product = step.get(
            "product",
            ""
        )

        instruction = step.get(
            "instruction",
            ""
        )

        metadata = step.get(
            "metadata"
        )

        arrow_target = step.get(
            "arrow_target"
        )

        print(
            f"Processing step {step_number}: {title}"
        )

        # ==================================================
        # Start from original user image
        # ==================================================

        output = image.copy()

        # ==================================================
        # Get arrows
        # ==================================================

        if arrow_target:

            arrows = mapper.get_arrow(
                arrow_target
            )

            if arrows is None:

                print(
                    f"[WARNING] "
                    f"No arrow for target: "
                    f"{arrow_target}"
                )

                arrows = []

            elif not isinstance(
                arrows,
                list
            ):

                arrows = [
                    arrows
                ]

            # ==============================================
            # Draw arrows
            # ==============================================

            for arrow in arrows:

                draw_arrow(
                    output,
                    arrow
                )

        else:

            print(
                f"[WARNING] "
                f"No arrow_target for step "
                f"{step_number}"
            )

        # ==================================================
        # Encode PNG
        # ==================================================

        success, encoded = cv2.imencode(
            ".png",
            output
        )

        if not success:

            raise ValueError(
                f"Could not encode image "
                f"for step {step_number}"
            )

        # ==================================================
        # Create database object
        # ==================================================

        result = MakeupStepImage(
            makeup_request=makeup_request,

            step_number=step_number,

            category=category,

            title=title,

            product=product,

            instruction=instruction,

            arrow_target=arrow_target,

            metadata=metadata
        )

        # ==================================================
        # Filename
        # ==================================================

        safe_title = (
            title
            .replace(" ", "_")
            .replace("/", "_")
            .replace("\\", "_")
        )

        filename = (
            f"step{step_number:02d}_"
            f"{safe_title}.png"
        )

        # ==================================================
        # Save image
        # ==================================================

        result.image.save(
            filename,
            ContentFile(
                encoded.tobytes()
            ),
            save=False
        )

        result.save()

        results.append(
            result
        )

    return results


def load_makeup_steps():
    path = os.path.join(
        settings.BASE_DIR,
        "makeup_steps.json"
    )

    if not os.path.exists(path):

        raise FileNotFoundError(
            f"makeup_steps.json not found: {path}"
        )

    with open(
        path,
        "r",
        encoding="utf-8"
    ) as f:

        steps = json.load(f)

    if not isinstance(steps, list):

        raise ValueError(
            "makeup_steps.json must contain a list."
        )

    return steps