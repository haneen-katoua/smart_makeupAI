# -*- coding: utf-8 -*-

import cv2
import os
import json

from arrow_mapper import ArrowMapper


def generate_makeup_chart(
    image_path,
    steps,
    output_dir
):
    """
    Generate one image for every makeup step.

    Args:
        image_path: path of user's face image
        steps_file: path to final_makeup_steps.json
        output_dir: directory where generated images are saved

    Returns:
        list of generated step information
    """

    # =====================================================
    # Load image
    # =====================================================

    image = cv2.imread(image_path)

    if image is None:
        raise ValueError(
            f"Image not found: {image_path}"
        )

    # =====================================================
    # Create output directory
    # =====================================================

    os.makedirs(
        output_dir,
        exist_ok=True
    )
    
    print(
    f"Loaded {len(steps)} makeup steps"
    )



    # =====================================================
    # Create ArrowMapper
    # =====================================================

    mapper = ArrowMapper(
        image
    )

    generated_steps = []

    # =====================================================
    # Generate images
    # =====================================================

    for step in steps:

        number = step["step_number"]

        title = step["title"]

        target = step.get(
            "arrow_target"
        )

        if target is None:

            target = step.get(
                "targets"
            )

        print(
            f"Processing step {number}: {title}"
        )

        output = image.copy()

        # =================================================
        # Draw arrows
        # =================================================

        if target:

            arrows = mapper.get_arrow(
                target
            )

            if arrows is not None:

                if not isinstance(
                    arrows,
                    list
                ):

                    arrows = [
                        arrows
                    ]

                for arrow in arrows:

                    if not arrow:
                        continue

                    cv2.arrowedLine(
                        output,
                        arrow["start"],
                        arrow["end"],
                        (0, 0, 0),
                        4,
                        tipLength=0.15
                    )

            else:

                print(
                    "[WARNING] No arrow:",
                    target
                )

        else:

            print(
                "[WARNING] No arrow target"
            )

        # =================================================
        # File name
        # =================================================

        safe_title = (
            title
            .replace(" ", "_")
            .replace("/", "_")
            .replace("\\", "_")
        )

        filename = (
            f"step{number:02d}_"
            f"{safe_title}.png"
        )

        output_path = os.path.join(
            output_dir,
            filename
        )

        # =================================================
        # Save image
        # =================================================

        success = cv2.imwrite(
            output_path,
            output
        )

        if not success:

            raise RuntimeError(
                f"Could not save image: {output_path}"
            )

        print(
            "Saved:",
            output_path
        )

        # =================================================
        # Save step information
        # =================================================

        generated_steps.append({

            "step_number": number,

            "category": step.get(
                "category"
            ),

            "title": title,

            "product": step.get(
                "product"
            ),

            "instruction": step.get(
                "instruction"
            ),

            "targets": step.get(
                "targets"
            ),

            "arrow_target": target,

            "metadata": step.get(
                "metadata"
            ),

            "image_path": output_path

        })

    print(
        "Makeup chart completed successfully"
    )

    return generated_steps


def generate_makeup_chart_from_steps(
    image_path,
    steps,
    output_dir
):
    """
    Generate makeup step images directly from a steps list.

    Args:
        image_path: path to user's face image
        steps: list of final makeup steps
        output_dir: directory where images are saved

    Returns:
        list of generated step information
    """

    image = cv2.imread(image_path)

    if image is None:
        raise ValueError(
            f"Image not found: {image_path}"
        )

    os.makedirs(
        output_dir,
        exist_ok=True
    )

    mapper = ArrowMapper(
        image
    )

    generated_steps = []

    for step in steps:

        number = step["step_number"]

        title = step["title"]

        target = step.get(
            "arrow_target"
        )

        if target is None:
            target = step.get(
                "targets"
            )

        print(
            f"Processing step {number}: {title}"
        )

        output = image.copy()

        # ==============================================
        # Draw arrows
        # ==============================================

        if target:

            arrows = mapper.get_arrow(
                target
            )

            if arrows is not None:

                if not isinstance(
                    arrows,
                    list
                ):
                    arrows = [arrows]

                for arrow in arrows:

                    if not arrow:
                        continue

                    cv2.arrowedLine(
                        output,
                        arrow["start"],
                        arrow["end"],
                        (0, 0, 0),
                        4,
                        tipLength=0.15
                    )

        # ==============================================
        # Safe filename
        # ==============================================

        safe_title = (
            title
            .replace(" ", "_")
            .replace("/", "_")
            .replace("\\", "_")
        )

        filename = (
            f"step{number:02d}_"
            f"{safe_title}.png"
        )

        output_path = os.path.join(
            output_dir,
            filename
        )

        success = cv2.imwrite(
            output_path,
            output
        )

        if not success:

            raise RuntimeError(
                f"Could not save image: {output_path}"
            )

        # ==============================================
        # API step information
        # ==============================================

        generated_steps.append({

            "step_number": number,

            "category": step.get(
                "category"
            ),

            "title": title,

            "product": step.get(
                "product"
            ),

            "instruction": step.get(
                "instruction"
            ),

            "targets": step.get(
                "targets"
            ),

            "arrow_target": target,

            "metadata": step.get(
                "metadata"
            ),

            "image_path": output_path
        })

    return generated_steps

# =========================================================
# Manual testing
# =========================================================

if __name__ == "__main__":

    USER_IMAGE = (
        "pictures3/"
        "photo_2026-06-04_11-18-41.jpg"
    )

    STEPS_FILE = (
        "final_makeup_steps.json"
    )

    OUTPUT_DIR = "output"

    generate_makeup_chart(
        image_path=USER_IMAGE,
        steps_file=STEPS_FILE,
        output_dir=OUTPUT_DIR
    )