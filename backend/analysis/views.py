from django.shortcuts import render

# Create your views here.
from rest_framework.response import Response
from rest_framework.generics import CreateAPIView
from rest_framework.permissions import IsAuthenticated
from .services.makeup_pipeline import run_makeup_pipeline
from .models import MakeupRequest , MakeupStepImage
from .serializers import MakeupRequestSerializer , AdminAnalysisDetailSerializer , AdminAnalysisListSerializer , UserAnalysisHistorySerializer , UserAnalysisDetailSerializer , MakeupStepImageSerializer
from rest_framework.generics import (
    ListAPIView,
    RetrieveAPIView
)
from rest_framework.permissions import IsAdminUser
from rest_framework.generics import DestroyAPIView
from rest_framework import status
from rest_framework.filters import SearchFilter
from django_filters.rest_framework import DjangoFilterBackend
from django_filters import rest_framework as filters
from django.utils import timezone
from django.shortcuts import get_object_or_404
from django.db.models import Count
from django.contrib.auth.models import User
from rest_framework.views import APIView
from generate_final_steps import (
    create_final_steps_from_analysis
)

from .services.makeup_steps_service import (
    load_makeup_steps,
    generate_makeup_step_images
)

from complete_makeup_pipline import analyze_image
import os
import json
from pathlib import Path
from django.conf import settings
import cv2
import numpy as np
from makeup_steps_generator import (
    MakeupStepsGenerator
)







class MakeupRequestCreateView(CreateAPIView):

    serializer_class = MakeupRequestSerializer

    permission_classes = [
        IsAuthenticated
    ]

    def create(self, request, *args, **kwargs):

        # ==================================================
        # Validate request
        # ==================================================

        serializer = self.get_serializer(
            data=request.data
        )

        serializer.is_valid(
            raise_exception=True
        )

        # ==================================================
        # Create MakeupRequest
        # ==================================================

        makeup_request = serializer.save(
            user=request.user
        )

        # ==================================================
        # Get face image path
        # ==================================================

        face_image_path = (
            makeup_request.face_image.path
        )
        
        clothes_image_path = None

        if makeup_request.clothes_image:
            clothes_image_path = (
                makeup_request.clothes_image.path
            )

        # ==================================================
        # Run complete makeup pipeline
        # ==================================================

        try:

            result = analyze_image(
                face_image_path=face_image_path,
                occasion=makeup_request.occasion,
                eye_strategy="Monochromatic",
                print_report=False
            )
            clothing_result = None
            palette_result = None

            if clothes_image_path:

                from clothing_hue_extractor import (
                    analyze_clothing_color
                )

                from shadow_palette_rules import (
                    generate_shadow_palette
                )

                clothing_result = analyze_clothing_color(
                    clothes_image_path
                )

                if "error" not in clothing_result:

                    skin_undertone = result.get(
                        "skin_analysis",
                        {}
                    ).get(
                        "undertone"
                    )

                    if skin_undertone:

                        palette_result = generate_shadow_palette(
                            clothing_result=clothing_result,
                            skin_undertone=skin_undertone
                        )

        except Exception as exc:

            makeup_request.delete()

            return Response(
                {
                    "detail": "Makeup analysis failed.",
                    "error": str(exc)
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

        # ==================================================
        # Check result
        # ==================================================

        if result is None:

            makeup_request.delete()

            return Response(
                {
                    "detail": (
                        "Could not analyze "
                        "the uploaded face image."
                    )
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        # ==================================================
        # Save complete analysis
        # ==================================================
        
        result["clothing_analysis"] = clothing_result

        result["shadow_palette"] = palette_result

        makeup_request.analysis_result = result

        makeup_request.save(
            update_fields=[
                "analysis_result"
            ]
        )

        # ==================================================
        # Response
        # ==================================================

        return Response(
            {
                "request_id": makeup_request.id,
                "result": result
            },
            status=status.HTTP_201_CREATED
        )

class AdminAnalysisFilter(filters.FilterSet):

    date = filters.DateFilter(
        field_name="created_at",
        lookup_expr="date"
    )

    class Meta:
        model = MakeupRequest
        fields = [
            "occasion",
            "date"
        ]
        
class AdminAnalysisListAPIView(ListAPIView):

    permission_classes = [
        IsAdminUser
    ]

    serializer_class = AdminAnalysisListSerializer

    queryset = MakeupRequest.objects.select_related(
        "user"
    ).order_by(
        "-created_at"
    )

    filter_backends = [
        DjangoFilterBackend,
        SearchFilter
    ]

    filterset_class = AdminAnalysisFilter

    search_fields = [
        "user__username",
        "user__email"
    ]


class AdminAnalysisDetailAPIView(RetrieveAPIView):

    permission_classes = [
        IsAdminUser
    ]

    serializer_class = AdminAnalysisDetailSerializer

    queryset = MakeupRequest.objects.select_related(
        "user"
    )

class AdminAnalysisDeleteAPIView(DestroyAPIView):

    permission_classes = [
        IsAdminUser
    ]

    def delete(self, request, pk):

        try:
            analysis = MakeupRequest.objects.get(
                id=pk
            )

            analysis.delete()


            return Response(
                {
                    "message": "Analysis deleted successfully"
                },
                status=status.HTTP_200_OK
            )


        except MakeupRequest.DoesNotExist:

            return Response(
                {
                    "message": "Analysis not found"
                },
                status=status.HTTP_404_NOT_FOUND
            )         

class AdminDashboardAPIView(APIView):

    permission_classes = [
        IsAdminUser
    ]


    def get(self, request):

        today = timezone.now().date()

        total_users = User.objects.count()

        total_analyses = MakeupRequest.objects.count()

        today_analyses = MakeupRequest.objects.filter(
            created_at__date=today
        ).count()


        return Response({
            "total_users": total_users,
            "total_analyses": total_analyses,
            "today_analyses": today_analyses
        }) 


class AdminDashboardOccasionAPIView(APIView):

    permission_classes = [
        IsAdminUser
    ]


    def get(self, request):

        occasions = MakeupRequest.objects.values(
            "occasion"
        ).annotate(
            count=Count("id")
        )


        result = {}

        for item in occasions:
            result[item["occasion"]] = item["count"]


        return Response(result)


class AdminDashboardRecentAPIView(APIView):

    permission_classes = [
        IsAdminUser
    ]


    def get(self, request):

        analyses = MakeupRequest.objects.select_related(
            "user"
        ).order_by(
            "-created_at"
        )[:5]


        data = []

        for analysis in analyses:

            data.append({
                "id": analysis.id,
                "username": analysis.user.username,
                "occasion": analysis.occasion,
                "created_at": analysis.created_at
            })


        return Response(data)
    

class UserAnalysisHistoryAPIView(ListAPIView):

    permission_classes = [
        IsAuthenticated
    ]

    serializer_class = UserAnalysisHistorySerializer


    def get_queryset(self):

        return MakeupRequest.objects.filter(
            user=self.request.user
        ).order_by(
            "-created_at"
        )


class UserAnalysisDetailAPIView(RetrieveAPIView):

    permission_classes = [
        IsAuthenticated
    ]

    serializer_class = UserAnalysisDetailSerializer


    def get_queryset(self):

        return MakeupRequest.objects.filter(
            user=self.request.user
        )
        


class GenerateMakeupStepsAPIView(APIView):

    permission_classes = [
        IsAuthenticated
    ]

    def post(
        self,
        request,
        request_id
    ):

        # ==================================================
        # 1. Get user's MakeupRequest
        # ==================================================

        makeup_request = get_object_or_404(
            MakeupRequest,
            id=request_id,
            user=request.user
        )

        # ==================================================
        # 2. Check face image
        # ==================================================

        if not makeup_request.face_image:

            return Response(
                {
                    "detail": (
                        "No face image found "
                        "for this makeup request."
                    )
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        # ==================================================
        # 3. Check analysis
        # ==================================================

        analysis = makeup_request.analysis_result

        if not analysis:

            return Response(
                {
                    "detail": (
                        "Makeup analysis is not "
                        "available yet."
                    )
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        # ==================================================
        # 4. Get expert_output from analysis
        # ==================================================

        expert_output = analysis.get(
            "expert_output"
        )

        if not isinstance(
            expert_output,
            dict
        ):

            return Response(
                {
                    "detail": (
                        "expert_output is missing "
                        "from analysis result."
                    )
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        # ==================================================
        # 5. Generate makeup steps
        # ==================================================
        #
        # IMPORTANT:
        #
        # We DO NOT load a static makeup_steps.json.
        #
        # The steps are generated directly from
        # this user's expert makeup recommendation.
        #
        # ==================================================

        try:

            generator = MakeupStepsGenerator(
                expert_output
            )

            steps = generator.generate()

        except Exception as exc:

            return Response(
                {
                    "detail": (
                        "Could not generate "
                        "makeup steps from "
                        "expert recommendation."
                    ),
                    "error": str(exc)
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

        # ==================================================
        # 6. Check generated steps
        # ==================================================

        if not steps:

            return Response(
                {
                    "detail": (
                        "No makeup steps were generated "
                        "from the expert recommendation."
                    )
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        # ==================================================
        # 7. Add arrow targets
        # ==================================================
        #
        # Priority:
        #
        # 1. Expert arrow_target
        # 2. Default target
        # 3. Generator targets
        #
        # ==================================================

        try:

            final_steps = (
                create_final_steps_from_analysis(
                    steps,
                    analysis
                )
            )

        except Exception as exc:

            return Response(
                {
                    "detail": (
                        "Could not create final "
                        "makeup steps."
                    ),
                    "error": str(exc)
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

        # ==================================================
        # 8. Validate final steps
        # ==================================================

        if not final_steps:

            return Response(
                {
                    "detail": (
                        "Final makeup steps are empty."
                    )
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        # ==================================================
        # 9. Read user's face image
        # ==================================================

        try:

            makeup_request.face_image.open(
                "rb"
            )

            image_bytes = (
                makeup_request.face_image.read()
            )

            makeup_request.face_image.close()

        except Exception as exc:

            return Response(
                {
                    "detail": (
                        "Could not read face image."
                    ),
                    "error": str(exc)
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

        # ==================================================
        # 10. Convert image bytes -> OpenCV
        # ==================================================

        image_array = np.frombuffer(
            image_bytes,
            dtype=np.uint8
        )

        image = cv2.imdecode(
            image_array,
            cv2.IMREAD_COLOR
        )

        if image is None:

            return Response(
                {
                    "detail": (
                        "Could not decode face image."
                    )
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        # ==================================================
        # 11. Generate cumulative makeup images
        # ==================================================
        #
        # final_steps contains:
        #
        # - personalized instruction
        # - product
        # - targets
        # - arrow_target
        #
        # The image generator uses these steps
        # to create the step images.
        #
        # ==================================================

        try:
            
            # ==================================================
            # Remove previously generated makeup steps
            # ==================================================

            makeup_request.step_images.all().delete()

            results = generate_makeup_step_images(
                makeup_request=makeup_request,
                image=image,
                final_steps=final_steps
            )

        except Exception as exc:

            return Response(
                {
                    "detail": (
                        "Could not generate "
                        "makeup step images."
                    ),
                    "error": str(exc)
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

        # ==================================================
        # 12. Serialize results
        # ==================================================

        serializer = MakeupStepImageSerializer(
            results,
            many=True,
            context={
                "request": request
            }
        )

        # ==================================================
        # 13. Response
        # ==================================================

        return Response(
            {
                "makeup_request_id": (
                    makeup_request.id
                ),

                "count": len(results),

                "steps": serializer.data
            },
            status=status.HTTP_201_CREATED
        )
            
class MakeupStepsView(APIView):

    permission_classes = [
        IsAuthenticated
    ]

    def get(
        self,
        request,
        request_id
    ):

        # ==================================================
        # Get user's MakeupRequest
        # ==================================================

        makeup_request = get_object_or_404(
            MakeupRequest,
            id=request_id,
            user=request.user
        )

        # ==================================================
        # Get generated makeup steps
        # ==================================================

        steps = makeup_request.step_images.all().order_by(
            "step_number"
        )

        # ==================================================
        # Serialize
        # ==================================================

        serializer = MakeupStepImageSerializer(
            steps,
            many=True,
            context={
                "request": request
            }
        )

        # ==================================================
        # Response
        # ==================================================

        return Response(
            {
                "request_id": makeup_request.id,
                "count": steps.count(),
                "steps": serializer.data
            },
            status=status.HTTP_200_OK
        )