from django.shortcuts import render
from rest_framework.generics import CreateAPIView
from .serializers import RegisterSerializer
from django.contrib.auth.models import User

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAdminUser
from rest_framework.permissions import IsAuthenticated

from .serializers import AdminUserSerializer , UserProfileSerializer
from rest_framework.generics import RetrieveUpdateAPIView


class RegisterView(CreateAPIView):

    serializer_class = RegisterSerializer
    


class AdminUsersAPIView(APIView):

    permission_classes = [IsAdminUser]


    # عرض كل المستخدمين
    def get(self, request):

        users = User.objects.all()

        serializer = AdminUserSerializer(
            users,
            many=True
        )

        return Response(serializer.data)



    # حذف مستخدم
    def delete(self, request, user_id):

        try:
            user = User.objects.get(id=user_id)

        except User.DoesNotExist:
            return Response(
                {
                    "error": "User not found"
                },
                status=404
            )


        # منع حذف الادمن نفسه
        if user == request.user:
            return Response(
                {
                    "error": "You cannot delete yourself"
                },
                status=400
            )


        user.delete()


        return Response(
            {
                "message": "User deleted successfully"
            }
        ) 


class UserProfileAPIView(RetrieveUpdateAPIView):

    permission_classes = [
        IsAuthenticated
    ]

    serializer_class = UserProfileSerializer


    def get_object(self):

        return self.request.user           
    