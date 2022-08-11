import uuid
from django.db import models


class Forum(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    name = models.CharField(max_length=200)


class Post(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    forum = models.ForeignKey(Forum, on_delete=models.CASCADE, related_name='posts')
    body = models.CharField(max_length=20000)


class Comment(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='comments')
    body = models.CharField(max_length=20000)
