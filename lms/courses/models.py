from django.db import models
from users.models import CustomUser  # Import your CustomUser model

# Create your models here.

class Course(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    course_pic = models.ImageField(upload_to='course_pics/', blank=False, null=True)
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)  #
    instructor = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='courses_taught')
    students = models.ManyToManyField(CustomUser, related_name='enrolled_courses', blank=True)
    
    def is_free(self):
        return self.price == 0.00
    
    def __str__(self):
        return f"{self.title}"

class Payment(models.Model):
    STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('Success', 'Success'),
        ('Failed', 'Failed'),
    ]
    
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    course = models.ForeignKey('Course', on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='Pending')
    payment_id = models.CharField(max_length=100, unique=True, null=True, blank=True)
    order_id = models.CharField(max_length=100, unique=True, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username} - {self.course.title} - {self.status}"
