# django 
from django.db import models
from django.core.validators import FileExtensionValidator
from django.core.exceptions import ValidationError

# Users
from users.models import User

# Create your models here.
class post(models.Model):
    posted_by = models.ForeignKey(User, on_delete=models.CASCADE)
    caption = models.CharField(max_length=500)
    song = models.JSONField(null=True, blank= True)
    likes = models.PositiveBigIntegerField(default=0)
    comments = models.PositiveBigIntegerField(default=0)
    reposts = models.PositiveBigIntegerField(default=0)
    saves = models.PositiveBigIntegerField(default=0)

    video = models.FileField(upload_to='videos_uploaded',null=True, blank=True,
    validators=[FileExtensionValidator(allowed_extensions=['MOV','avi','mp4','webm','mkv'])])

    Picture = models.FileField(upload_to='Images_uploaded',null=True, blank=True,
    validators=[FileExtensionValidator(allowed_extensions=['png','jpg'])])

    def clean(self):
        """
        Custom validation method to check that at least either 'video' or 'Picture' has been uploaded.
        """
        has_video = bool(self.video)
        has_picture = bool(self.Picture)

        if not has_video and not has_picture:
            raise ValidationError("At least either 'video' or 'Picture' must be uploaded.")

    def save(self, *args, **kwargs):
        """
        Override the save method to perform custom validation before saving the instance.
        """
        self.clean() 
        super().save(*args, **kwargs)  

