# from django.db import models
# from django.conf import settings
# from cars.models import Car


# class Report(models.Model):

#     user = models.ForeignKey(
#         settings.AUTH_USER_MODEL,
#         on_delete=models.CASCADE,
#         related_name='reports'
#     )
#     car = models.ForeignKey(
#         Car,
#         on_delete=models.CASCADE,
#         related_name='reports'
#     )
#     reason = models.CharField(max_length=50)
#     description = models.TextField(blank=True, null=True)
#     created_at = models.DateTimeField(auto_now_add=True)

#     class Meta:
#         ordering = ['-created_at']

#     def __str__(self):
#         return f"Скарга від {self.user.email} на {self.car.brand} {self.car.model} — {self.get_reason_display()}"
