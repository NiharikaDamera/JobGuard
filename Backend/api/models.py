from django.db import models
from django.conf import settings


class JobAnalysis(models.Model):

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='job_analyses',
        null=True,
        blank=True
    )

    job_title = models.CharField(max_length=200)

    company_name = models.CharField(max_length=200)

    job_description = models.TextField()

    risk_score = models.IntegerField(default=0)

    risk_level = models.CharField(
        max_length=50,
        default="Low"
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):
        return self.job_title