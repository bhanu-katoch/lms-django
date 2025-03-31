from django.db import models
from users.models import CustomUser  # Import your CustomUser model

# Create your models here.

class Course(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    course_pic = models.ImageField(upload_to='course_pics/', blank=True, null=True)
    instructor = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='courses_taught')
    students = models.ManyToManyField(CustomUser, related_name='enrolled_courses', blank=True)

    def __str__(self):
        return f"{self.title}"
