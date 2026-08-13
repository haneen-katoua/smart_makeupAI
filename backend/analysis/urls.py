from django.urls import path
from .views import MakeupRequestCreateView , AdminAnalysisDetailAPIView , AdminAnalysisListAPIView , AdminAnalysisDeleteAPIView , AdminDashboardAPIView, AdminDashboardOccasionAPIView , AdminDashboardRecentAPIView , UserAnalysisHistoryAPIView , UserAnalysisDetailAPIView , MakeupStepsView , GenerateMakeupStepsAPIView


urlpatterns = [

    path(
        'request/',
        MakeupRequestCreateView.as_view()
    ),
    path(
        "admin/analyses/",
        AdminAnalysisListAPIView.as_view()
    ),


    path(
        "admin/analyses/<int:pk>/",
        AdminAnalysisDetailAPIView.as_view()
    ),
    path(
        "admin/analyses/<int:pk>/delete/",
        AdminAnalysisDeleteAPIView.as_view()
    ),
    
    path(
        "admin/dashboard/",
        AdminDashboardAPIView.as_view()
    ),


    path(
        "admin/dashboard/occasions/",
        AdminDashboardOccasionAPIView.as_view()
    ),


    path(
        "admin/dashboard/recent/",
        AdminDashboardRecentAPIView.as_view()
    ),
    
    path(
        "my-analyses/",
        UserAnalysisHistoryAPIView.as_view()
    ),
    
    path(
    "my-analyses/<int:pk>/",
    UserAnalysisDetailAPIView.as_view()
),
     path(
        "makeup-steps/<int:request_id>/",
        MakeupStepsView.as_view(),
        name="makeup-steps"
    ),
     
    path(
        "makeup/requests/<int:request_id>/generate-steps/",
        GenerateMakeupStepsAPIView.as_view(),
        name="generate-makeup-steps"
    ),



]