from django.db import models

# Create your models here.
class Video(models.Model):
    video_url = models.URLField()
    transcript = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.video_url

    class Meta:
        ordering = ['-created_at']