from all_face_analysis import analyze_face
from clothing_hue_extractor import analyze_clothing_color
from shadow_palette_rules import generate_shadow_palette


def run_makeup_pipeline(request):

    # ==========================
    # 1) تحليل الوجه والمكياج
    # ==========================
    face_result = analyze_face(
        request.face_image.path,
        request.occasion
    )


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

        # أخذ undertone من تحليل البشرة
        skin_undertone = face_result.get("skin", {}).get("undertone")
        
        print("SKIN:", face_result.get("skin_analysis"))
        print("UNDERTONE:", skin_undertone) 


        # توليد باليت ظلال مناسبة
        try:

            shadow_palette_result = generate_shadow_palette(
                clothes_result,
                skin_undertone
            )

        except Exception as e:

            print("SHADOW ERROR:", str(e))

            shadow_palette_result = {
                "error": str(e)
            }


    return {
        "face_makeup": face_result,

        "clothes_analysis": clothes_result,

        "shadow_palette": shadow_palette_result
    }