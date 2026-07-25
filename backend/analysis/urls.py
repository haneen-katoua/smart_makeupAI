from django.urls import path
from .views import MakeupRequestCreateView , AdminAnalysisDetailAPIView , AdminAnalysisListAPIView , AdminAnalysisDeleteAPIView , AdminDashboardAPIView, AdminDashboardOccasionAPIView , AdminDashboardRecentAPIView , UserAnalysisHistoryAPIView , UserAnalysisDetailAPIView


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


]