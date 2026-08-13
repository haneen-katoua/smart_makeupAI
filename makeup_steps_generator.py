"""
makeup_steps_generator.py
=========================

Converts the output of the Expert Makeup System into an ordered
step-by-step makeup application workflow.

This module does NOT draw anything.
It only generates structured makeup steps that can later be used
by OpenCV or any frontend.

Author:
Smart Makeup AI
"""

from __future__ import annotations

from dataclasses import dataclass, field, asdict
from enum import Enum
from typing import Dict, List, Any, Optional


# ==========================================================
# Face Areas
# ==========================================================

class FaceArea(Enum):
    """
    Atomic drawable regions.
    Every region corresponds to one drawable area.
    """

    FULL_FACE = "full_face"

    UNDER_LEFT_EYE = "under_left_eye"
    UNDER_RIGHT_EYE = "under_right_eye"

    LEFT_FACE_CONTOUR = "left_face_contour"
    RIGHT_FACE_CONTOUR = "right_face_contour"

    LEFT_CHEEK = "left_cheek"
    RIGHT_CHEEK = "right_cheek"

    FOREHEAD = "forehead"

    CHIN = "chin"

    NOSE_CONTOUR_LEFT = "nose_contour_left"
    NOSE_CONTOUR_RIGHT = "nose_contour_right"

    NOSE_BRIDGE = "nose_bridge"

    NOSE_TIP = "nose_tip"

    LEFT_EYEBROW = "left_eyebrow"
    RIGHT_EYEBROW = "right_eyebrow"

    LEFT_UPPER_EYELID = "left_upper_eyelid"
    RIGHT_UPPER_EYELID = "right_upper_eyelid"

    LEFT_EYELINER = "left_eyeliner"
    RIGHT_EYELINER = "right_eyeliner"

    LEFT_LASHES = "left_lashes"
    RIGHT_LASHES = "right_lashes"

    UPPER_LIP = "upper_lip"
    LOWER_LIP = "lower_lip"

    LIP_BORDER = "lip_border"


# ==========================================================
# Categories
# ==========================================================

class MakeupCategory(Enum):

    BASE = "Base"

    FACE = "Face"

    EYES = "Eyes"

    BROWS = "Brows"

    LIPS = "Lips"

    FINISHING = "Finishing"


# ==========================================================
# Makeup Step
# ==========================================================

@dataclass(slots=True)
class MakeupStep:
    """
    Represents one makeup step.
    """

    step_number: int

    category: MakeupCategory

    title: str

    product: str

    instruction: str

    targets: List[FaceArea]

    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self):

        data = asdict(self)

        data["category"] = self.category.value

        data["targets"] = [
            t.value
            for t in self.targets
        ]

        return data

# ==========================================================
# Generator
# ==========================================================

class MakeupStepsGenerator:

    def __init__(self, expert_output: Dict):

        self.data = expert_output

        self.steps: List[MakeupStep] = []

    # ------------------------------------------------------

    def generate(self) -> List[Dict]:
        """
        Main API.

        Returns
        -------
        List[dict]
        """

        self.steps.clear()

        self._generate_base()

        self._generate_face()

        self._generate_brows()

        self._generate_eyes()

        self._generate_lips()

        self._generate_finishing()

        return [step.to_dict() for step in self.steps]

    # ------------------------------------------------------

    def _next_step(self) -> int:

        return len(self.steps) + 1

    # ------------------------------------------------------

    def _add_step(
            self,
            *,
            category: MakeupCategory,
            title: str,
            product: str,
            instruction: str,
            targets: List[FaceArea],
            metadata: Optional[Dict] = None
    ) -> None:

        self.steps.append(

            MakeupStep(

                step_number=self._next_step(),

                category=category,

                title=title,

                product=product,

                instruction=instruction,

                targets=targets,

                metadata=metadata or {}
            )
        )

# ==========================================================
# BASE
# ==========================================================

    def _generate_base(self):

        foundation = self.data.get("foundation")

        if not foundation:
            return

        self._primer_step(foundation)

        self._foundation_step(foundation)

        self._concealer_step(foundation)

    # ------------------------------------------------------

    def _primer_step(self, foundation):

        primer = foundation.get("primer")

        if not primer:
            return

        self._add_step(

            category=MakeupCategory.BASE,

            title="Prepare Skin",

            product="Primer",

            instruction=primer["type"],

            targets=[
                FaceArea.FULL_FACE
            ],

            metadata=primer
        )

    # ------------------------------------------------------

    def _foundation_step(self, foundation):

        formula = foundation.get("formula")

        shade = foundation.get("shade")

        if not formula:
            return

        text = (
            f"{formula['primary']} | "
            f"التغطية: {formula['coverage']}"
        )

        self._add_step(

            category=MakeupCategory.BASE,

            title="Apply Foundation",

            product="Foundation",

            instruction=text,

            targets=[
                FaceArea.FULL_FACE
            ],

            metadata={
                "formula": formula,
                "shade": shade
            }
        )

    # ------------------------------------------------------

    def _concealer_step(self, foundation):

        concealer = foundation.get("concealer")

        if not concealer:
            return

        self._add_step(

            category=MakeupCategory.BASE,

            title="Apply Concealer",

            product="Concealer",

            instruction=concealer["descriptor"],

            targets=[
                FaceArea.UNDER_LEFT_EYE,
                FaceArea.UNDER_RIGHT_EYE
            ],

            metadata=concealer
        )
    
    # ==========================================================
# FACE
# ==========================================================

    def _generate_face(self) -> None:
        """
        Generate all face-related makeup steps.
        """

        face = self.data.get("face")
        nose = self.data.get("nose")

        if face:
            self._face_contour_step(face)
            self._blush_step(face)
            self._face_highlight_step(face)

        if nose:
            self._nose_contour_step(nose)
            self._nose_highlight_step(nose)

    # ------------------------------------------------------

    def _face_contour_step(self, face: Dict) -> None:

        sculpt = face.get("sculpt")

        if not sculpt:
            return

        instruction = sculpt.get(
            "placement",
            "Apply contour according to face shape."
        )

        self._add_step(

            category=MakeupCategory.FACE,

            title="Face Contour",

            product="Contour",

            instruction=instruction,

            targets=[
                FaceArea.LEFT_FACE_CONTOUR,
                FaceArea.RIGHT_FACE_CONTOUR
            ],

            metadata={
                "purpose": sculpt.get("purpose"),
                "shape": face.get("shape"),
                "recommendation": face.get("recommendation"),
                "adjustment": face.get("adjustment"),
                "texture": face.get("texture")
            }
        )

    # ------------------------------------------------------

    def _nose_contour_step(self, nose: Dict) -> None:

        shape = nose.get("shape")
        contour = nose.get("contour")

        if not shape:
            return

        instruction = shape.get(
            "technique",
            "Apply nose contour."
        )

        self._add_step(

            category=MakeupCategory.FACE,

            title="Nose Contour",

            product="Contour",

            instruction=instruction,

            targets=[
                FaceArea.NOSE_CONTOUR_LEFT,
                FaceArea.NOSE_CONTOUR_RIGHT
            ],

            metadata={
                "shape": shape,
                "contour": contour,
                "map": nose.get("map")
            }
        )

    # ------------------------------------------------------

    def _blush_step(self, face: Dict) -> None:

        blush = face.get("blush")

        if not blush:
            return

        placement = blush.get(
            "placement",
            "Apply blush."
        )

        color = face.get("color", {}).get(
            "base_color",
            ""
        )

        if color:
            instruction = f"{placement} | اللون: {color}"
        else:
            instruction = placement

        self._add_step(

            category=MakeupCategory.FACE,

            title="Blush",

            product="Blush",

            instruction=instruction,

            targets=[
                FaceArea.LEFT_CHEEK,
                FaceArea.RIGHT_CHEEK
            ],

            metadata={
                "blush": blush,
                "color": face.get("color"),
                "recommendation": face.get("recommendation")
            }
        )

    # ------------------------------------------------------

    def _face_highlight_step(self, face: Dict) -> None:

        highlight = face.get("highlight")

        if not highlight:
            return

        self._add_step(

            category=MakeupCategory.FACE,

            title="Face Highlight",

            product="Highlighter",

            instruction=highlight.get(
                "placement",
                "Apply face highlighter."
            ),

            targets=[
                FaceArea.NOSE_BRIDGE
            ],

            metadata={
                "highlight": highlight,
                "texture": face.get("texture")
            }
        )

    # ------------------------------------------------------

    def _nose_highlight_step(self, nose: Dict) -> None:

        highlight = nose.get("highlight")

        mapping = nose.get("map")

        if not highlight:
            return

        instruction = mapping.get(
            "highlight",
            highlight.get(
                "method",
                "Apply nose highlight."
            )
        )

        self._add_step(

            category=MakeupCategory.FACE,

            title="Nose Highlight",

            product="Highlighter",

            instruction=instruction,

            targets=[
                FaceArea.NOSE_TIP
            ],

            metadata={
                "highlight": highlight,
                "map": mapping
            }
        )
        


# ==========================================================
# BROWS
# ==========================================================

    def _generate_brows(self) -> None:

        brows = self.data.get("brows")

        if not brows:
            return

        self._brows_step(brows)

    # ------------------------------------------------------

    def _brows_step(self, brows: Dict) -> None:

        style = brows.get("style")

        correction = brows.get("correction")

        if not style:
            return

        style_name = style.get("style", "")

        technique = style.get("technique", "")

        product = style.get(
            "product",
            "Eyebrow Pencil"
        )

        appearance = style.get(
            "appearance",
            ""
        )

        parts = []

        if style_name:
            parts.append(style_name)

        if technique:
            parts.append(technique)

        if appearance:
            parts.append(appearance)

        instruction = " | ".join(parts)

        self._add_step(

            category=MakeupCategory.BROWS,

            title="Eyebrows",

            product=product,

            instruction=instruction,

            targets=[
                FaceArea.LEFT_EYEBROW,
                FaceArea.RIGHT_EYEBROW
            ],

            metadata={
                "style": style,
                "correction": correction,
                "color": brows.get("color"),
                "recommendation": brows.get("recommendation")
            }
        )
        
    
    # ==========================================================
# EYES
# ==========================================================

    def _generate_eyes(self) -> None:
        """
        Generate eye makeup steps.

        Since both eyes receive the same recommendation,
        we generate ONE unified workflow.
        """

        eyes = self.data.get("eyes")

        if not eyes:
            return

        eye = eyes.get("left")

        if not eye:
            return

        plan = eye.get("plan")

        if not plan:
            return

        self._eyeshadow_step(plan)

        self._eyeliner_step(plan)

        self._mascara_step(plan)

    # ------------------------------------------------------

    def _eyeshadow_step(self, plan: Dict) -> None:

        style = plan.get("style")

        texture = plan.get("texture")

        if not style:
            return

        instruction = style

        if texture:
            instruction += f" | {texture}"

        self._add_step(

            category=MakeupCategory.EYES,

            title="Eyeshadow",

            product="Eyeshadow",

            instruction=instruction,

            targets=[
                FaceArea.LEFT_UPPER_EYELID,
                FaceArea.RIGHT_UPPER_EYELID
            ],

            metadata={

                "style": style,

                "texture": texture
            }
        )

    # ------------------------------------------------------

    def _eyeliner_step(self, plan: Dict) -> None:

        eyeliner = plan.get("eyeliner")

        if not eyeliner:
            return

        self._add_step(

            category=MakeupCategory.EYES,

            title="Eyeliner",

            product="Eyeliner",

            instruction=eyeliner,

            targets=[
                FaceArea.LEFT_EYELINER,
                FaceArea.RIGHT_EYELINER
            ],

            metadata={

                "style": eyeliner
            }
        )

    # ------------------------------------------------------

    def _mascara_step(self, plan: Dict) -> None:

        lashes = plan.get("lashes")

        if not lashes:
            return

        self._add_step(

            category=MakeupCategory.EYES,

            title="Mascara",

            product="Mascara",

            instruction=lashes,

            targets=[
                FaceArea.LEFT_LASHES,
                FaceArea.RIGHT_LASHES
            ],

            metadata={

                "lashes": lashes
            }
        )
    
    # ==========================================================
# LIPS
# ==========================================================

    def _generate_lips(self) -> None:
        """
        Generate all lip makeup steps.
        """

        lips = self.data.get("lips")

        if not lips:
            return

        self._lipliner_step(lips)

        self._lipstick_step(lips)

    # ------------------------------------------------------

    def _lipliner_step(self, lips: Dict) -> None:

        shape = lips.get("shape")

        if not shape:
            return

        technique = shape.get("technique")

        if not technique:
            return

        correction = shape.get("correction", "")

        instruction = technique

        if correction:
            instruction += f" | {correction}"

        self._add_step(

            category=MakeupCategory.LIPS,

            title="Lip Liner",

            product="Lip Liner",

            instruction=instruction,

            targets=[
                FaceArea.LIP_BORDER
            ],

            metadata={
                "shape": shape
            }
        )

    # ------------------------------------------------------

    def _lipstick_step(self, lips: Dict) -> None:

        occasion = lips.get("occasion")

        color = lips.get("color")

        if not occasion:
            return

        parts = []

        if occasion.get("product"):
            parts.append(occasion["product"])

        if occasion.get("texture"):
            parts.append(occasion["texture"])

        if color and color.get("colors"):
            parts.append(f"اللون: {color['colors']}")

        instruction = " | ".join(parts)

        self._add_step(

            category=MakeupCategory.LIPS,

            title="Lipstick",

            product="Lipstick",

            instruction=instruction,

            targets=[
                FaceArea.UPPER_LIP,
                FaceArea.LOWER_LIP
            ],

            metadata={
                "occasion": occasion,
                "color": color,
                "recommendation": lips.get("recommendation")
            }
        )


# ==========================================================
# FINISHING
# ==========================================================

    def _generate_finishing(self) -> None:

        foundation = self.data.get("foundation")

        if not foundation:
            return

        self._setting_step(foundation)

    # ------------------------------------------------------

    def _setting_step(self, foundation: Dict) -> None:

        setting = foundation.get("setting")

        if not setting:
            return

        instruction = setting.get(
            "method",
            "Set the makeup."
        )

        technique = setting.get("technique")

        if technique:
            instruction += f" | {technique}"

        self._add_step(

            category=MakeupCategory.FINISHING,

            title="Set Makeup",

            product="Setting Powder & Spray",

            instruction=instruction,

            targets=[
                FaceArea.FULL_FACE
            ],

            metadata=setting
        )


# ==========================================================
# EXPORT
# ==========================================================

    def export_to_json(
            self,
            output_path: str
    ) -> None:
        """
        Export generated steps to JSON.
        """

        import json

        data = self.generate()

        with open(
                output_path,
                "w",
                encoding="utf-8"
        ) as f:

            json.dump(
                data,
                f,
                ensure_ascii=False,
                indent=4
            )


# ==========================================================
# HELPERS
# ==========================================================

    def get_steps(self) -> List[MakeupStep]:
        """
        Return MakeupStep objects.
        """

        return self.steps

    # ------------------------------------------------------

    def print_steps(self) -> None:
        """
        Pretty console output.
        """

        print("\n")
        print("=" * 70)
        print("MAKEUP APPLICATION ROADMAP")
        print("=" * 70)

        for step in self.steps:

            print(
                f"[{step.step_number:02}] "
                f"{step.title}"
            )

            print(
                f"     Product : {step.product}"
            )

            print(
                f"     Area    : {step.targets}"
            )

            print(
                f"     Action  : {step.instruction}"
            )

            print()


# ==========================================================
# EXAMPLE
# ==========================================================

if __name__ == "__main__":

    import json

    with open(
            "makeup_analysis.json",
            "r",
            encoding="utf-8"
    ) as f:

        analysis = json.load(f)

    generator = MakeupStepsGenerator(

        analysis["expert_output"]

    )

    steps = generator.generate()

    generator.print_steps()

    generator.export_to_json(

        "makeup_steps.json"

    )

    print()

    print("✓ Makeup roadmap generated.")

    print("✓ Saved to makeup_steps.json")    
        
    
                