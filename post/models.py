from django.db import models

from users.models import MyUser

# Create your models here.
class Post(models.Model):
    content = models.TextField()
    image = models.ImageField(upload_to='post_pictures/')
    author = models.ForeignKey(MyUser, on_delete=models.CASCADE)
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