from django.shortcuts import render

# Create your views here.
from rest_framework.response import Response
from rest_framework.generics import CreateAPIView
from rest_framework.permissions import IsAuthenticated
from .services.makeup_pipeline import run_makeup_pipeline
from .models import MakeupRequest
from .serializers import MakeupRequestSerializer , AdminAnalysisDetailSerializer , AdminAnalysisListSerializer , UserAnalysisHistorySerializer , UserAnalysisDetailSerializer
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
from django.db.models import Count
from django.contrib.auth.models import User
from rest_framework.views import APIView





class MakeupRequestCreateView(CreateAPIView):

    serializer_class = MakeupRequestSerializer

    permission_classes=[
        IsAuthenticated
    ]


    def create(self, request, *args, **kwargs):

        serializer = self.get_serializer(
            data=request.data
        )

        serializer.is_valid(
            raise_exception=True
        )


        makeup_request = serializer.save(
            user=request.user
        )


        result = run_makeup_pipeline(
            makeup_request
        )
        
        makeup_request.analysis_result = result
        makeup_request.save()


        return Response({
            "request_id": makeup_request.id,
            "result": result
        })
        

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