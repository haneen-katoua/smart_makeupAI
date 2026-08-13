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

    

class MakeupStepImage(models.Model):

    makeup_request = models.ForeignKey(
        MakeupRequest,
        on_delete=models.CASCADE,
        related_name="step_images"
    )

    step_number = models.PositiveIntegerField()

    category = models.CharField(
        max_length=100,
        blank=True
    )

    title = models.CharField(
        max_length=255
    )

    product = models.CharField(
        max_length=255,
        blank=True
    )

    instruction = models.TextField(
        blank=True
    )

    image = models.ImageField(
        upload_to="makeup_steps/"
    )

    arrow_target = models.JSONField(
        null=True,
        blank=True
    )

    metadata = models.JSONField(
        null=True,
        blank=True
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    class Meta:

        ordering = [
            "step_number"
        ]

    def __str__(self):

        return (
            f"{self.makeup_request_id} - "
            f"Step {self.step_number}: "
            f"{self.title}"
        )