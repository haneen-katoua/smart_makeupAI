from rest_framework import serializers
from .models import MakeupRequest


class MakeupRequestSerializer(serializers.ModelSerializer):
    

    class Meta:

        model = MakeupRequest

        fields = [
            'face_image',
            'clothes_image',
            'occasion'
        ]


class AdminAnalysisListSerializer(serializers.ModelSerializer):

    username = serializers.CharField(
        source="user.username",
        read_only=True
    )


    class Meta:
        model = MakeupRequest

        fields = [
            "id",
            "username",
            "occasion",
            "created_at",
            "face_image",
            "clothes_image"
        ]
        

class AdminAnalysisDetailSerializer(serializers.ModelSerializer):

    username = serializers.CharField(
        source="user.username",
        read_only=True
    )

    email = serializers.EmailField(
        source="user.email",
        read_only=True
    )


    class Meta:
        model = MakeupRequest

        fields = [
            "id",
            "username",
            "email",
            "face_image",
            "clothes_image",
            "occasion",
            "analysis_result",
            "created_at"
        ]

class UserAnalysisHistorySerializer(serializers.ModelSerializer):

    class Meta:
        model = MakeupRequest

        fields = [
            "id",
            "face_image",
            "occasion",
            "created_at"
        ]                        

class UserAnalysisDetailSerializer(serializers.ModelSerializer):

    class Meta:
        model = MakeupRequest

        fields = [
            "id",
            "face_image",
            "clothes_image",
            "occasion",
            "analysis_result",
            "created_at"
        ]        