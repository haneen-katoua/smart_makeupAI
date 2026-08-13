import cv2

from face_template import load_template
from arrow_mapper import generate_arrow_actions
from makeup_arrow_drawer import MakeupArrowDrawer



# =========================
# تحميل الصورة
# =========================

image = cv2.imread(
    "assets/face1.png"
)


if image is None:
    raise FileNotFoundError(
        "Image not found"
    )



h, w = image.shape[:2]



# =========================
# تحميل Face Template
# =========================

template = load_template(
    w,
    h
)



# =========================
# تجربة expert output
# =========================

expert_output = {


    "face": {

        "blush": {

            "placement":
            "في مركز الخد باتجاه الأذن"

        },

        "sculpt": {

            "placement":
            "برونز دافئ خفيف في مركز الخد"

        }

    },


    "nose": {

        "map": {

            "contour":
            "كونتور جانبي الأنف",

            "highlight":
            "هايلايت على الأنف"

        }

    },


    "eyes": {

        "left": {

            "plan": {

                "style":
                "سموكي درامي",

                "eyeliner":
                "آيلاينر سائل"

            }

        }

    },


    "brows": {

        "style": {

            "style":
            "تحديد بقوس واضح"

        }

    },


    "lips": {

        "shape": {

            "technique":
            "تحديد الشفاه"

        }

    }

}



# =========================
# تحويل الاقتراحات
# =========================

actions = generate_arrow_actions(
    expert_output
)



print(actions)



# =========================
# رسم الأسهم
# =========================


drawer = MakeupArrowDrawer()


result = drawer.apply(
    image,
    template,
    actions
)



cv2.imwrite(
    "output_arrow_test.png",
    result
)


print(
    "DONE"
)