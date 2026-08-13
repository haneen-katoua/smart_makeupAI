from all_face_analysis import  analyze_face_from_image_dict
from skin_analysis import analyze_skin_from_image_dict
from clothing_hue_extractor import analyze_clothing_color
from shadow_palette_rules import generate_shadow_palette


def run_makeup_pipeline(request):

    # ==========================
    # 1) تحليل الوجه والمكياج
    # ==========================
    face_result = analyze_face_from_image_dict(
        request.face_image.path
    )
    
    if not face_result.get("success"):

        return {
            "face_makeup": face_result,
            "skin_analysis": None,
            "clothes_analysis": None,
            "shadow_palette": None
        }



    # ==========================
    # 2) تحليل البشرة
    # ==========================

    skin_result = analyze_skin_from_image_dict(
        request.face_image.path
    )


    if not skin_result.get("success"):

        return {
            "face_makeup": face_result,
            "skin_analysis": skin_result,
            "clothes_analysis": None,
            "shadow_palette": None
        }



    # ==========================
    # 2) تحليل الملابس
    # ==========================
    clothes_result = None
    shadow_palette_result = None

    if request.clothes_image:

        # استخراج لون الملابس
        clothes_result = analyze_clothing_color(
            request.clothes_image.path
        )

        skin_undertone = skin_result.get(
            "undertone"
        )


        try:

            shadow_palette_result = generate_shadow_palette(
                clothes_result,
                skin_undertone
            )


        except Exception as e:

            shadow_palette_result = {
                "error": str(e)
            }



    # ==========================
    # النتيجة النهائية
    # ==========================

    return {


        "face_makeup": face_result,


        "skin_analysis": skin_result,


        "clothes_analysis": clothes_result,


        "shadow_palette": shadow_palette_result

    }