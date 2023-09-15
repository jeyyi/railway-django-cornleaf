from django.db import models

from users.models import MyUser

# Create your models here.
class Post(models.Model):
    author = models.ForeignKey(MyUser, on_delete=models.CASCADE)
    content = models.TextField(null=True, blank=True)
    image = models.ImageField(upload_to='post_pictures/')
    is_classification = models.BooleanField(default=False)
    is_multiple_classification = models.BooleanField(default=False)
    total_blight = models.IntegerField(default=0)
    total_rust = models.IntegerField(default=0)
    total_gray_leaf_spot = models.IntegerField(default=0)
    total_healthy = models.IntegerField(default=0)
    total_other = models.IntegerField(default=0)
    blight = models.BooleanField(default=False)
    rust = models.BooleanField(default=False)
    gray_leaf_spot = models.BooleanField(default=False)
    healthy = models.BooleanField(default=False)
    other = models.BooleanField(default=False)
    date_posted = models.DateField(auto_now_add=True, null=True)
    
    def __str__(self):
        return f'{self.content} - by {self.author}'


class Picture(models.Model):
    image = models.ImageField(upload_to='post_pictures/')
    uploaded_at = models.DateTimeField(auto_now_add=True)