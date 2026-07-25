from django.db import models
from django.contrib.auth.models import User


class MakeupRequest(models.Model):

    OCCASION_CHOICES = [

        ('work', 'Work'),
        ('party', 'Party'),
        ('wedding', 'Wedding'),
        ('photo', 'Photography')
        
    ]


    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE
    )


    face_image = models.ImageField(
        upload_to='faces/'
    )


    clothes_image = models.ImageField(
    upload_to='clothes/',
    null=True,
    blank=True
    )

    occasion = models.CharField(
        max_length=50,
        choices=OCCASION_CHOICES
    )
    
    analysis_result = models.JSONField(
        null=True,
        blank=True
    )


    created_at = models.DateTimeField(
        auto_now_add=True
    )


    def __str__(self):
        return self.user.username

    
