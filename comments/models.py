from django.db import models
from post.models import Post

from users.models import MyUser

# Create your models here.
class Comment(models.Model):
    content = models.TextField()
    author = models.ForeignKey(MyUser, on_delete=models.CASCADE)
    post = models.ForeignKey(Post, on_delete=models.CASCADE)

    def __str__(self):
        return f'{self.post.pk} - {self.author} - {self.content}'

