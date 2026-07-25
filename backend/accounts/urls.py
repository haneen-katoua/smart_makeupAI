from django.urls import path
from .views import RegisterView , AdminUsersAPIView , UserProfileAPIView


urlpatterns = [

    path(
        'register/',
        RegisterView.as_view(),
        name='register'
    ),
     path(
        "admin/users/",
        AdminUsersAPIView.as_view()
    ),


    path(
        "admin/users/<int:user_id>/",
        AdminUsersAPIView.as_view()
    ),
    
    path(
        "profile/",
        UserProfileAPIView.as_view()
    ),

]