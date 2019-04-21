from django.db import models
from django.contrib.auth.models import User
from django.utils.html import mark_safe
from markdown import markdown
import math
# Create your models here.

class Board(models.Model):
    objects =models.Manager()
    name = models.CharField(max_length=30, unique=True)
    description = models.CharField(max_length=100)

    def __str__(self):
        return self.name

    def get_posts_count(self):
        return Post.objects.filter(topic__board=self).count()

    def get_last_post(self):
        return Post.objects.filter(topic__board=self).order_by('created_at').last()

        # return Post.objects.filter(topic__board=self).order_by('created_at').last().message

class Topic(models.Model):
    objects = models.Manager()
    subject = models.CharField(max_length=255)
    last_updated = models.DateTimeField(auto_now_add=True)
    board = models.ForeignKey(Board, related_name='topics',on_delete=models.DO_NOTHING)
    starter = models.ForeignKey(User, related_name='topics', on_delete=models.DO_NOTHING)
    views = models.PositiveIntegerField(default=0)

    def get_posts_count(self):
        return Post.objects.filter(topic=self).count()
        # return self_posts.count()

    def get_page_count(self):
        count = self.posts.count()
        pages = count/10
        return math.ceil(pages)

    def has_many_pages(self, count=None):
        if count is None:
            count = self.get_page_count()
        return count>6

    def get_page_range(self):
        count = self.get_page_count()
        if self.has_many_pages(count):
            return range(1,5)
        return range(1,count+1)

    def get_last_ten_posts(self):
        return self.posts.order_by('-created_at')[:10]

    def __str__(self):

        if len(self.subject)>50:
            return self.subject[:50]+"..."
        else:
            return self.subject


class Post(models.Model):
    objects = models.Manager()
    message = models.TextField(max_length=4000)
    topic = models.ForeignKey(Topic, related_name='posts', on_delete=models.DO_NOTHING)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(null=True)
    created_by = models.ForeignKey(User, related_name='posts', on_delete=models.DO_NOTHING)
    updated_by = models.ForeignKey(User, null=True, related_name='+', on_delete=models.DO_NOTHING)

    def __str__(self):
        if len(self.message)>50:
            return self.message[:50]+"..."
        else:
            return self.message

    def get_message_as_markdown(self):
        return mark_safe(markdown(self.message, safe_mode='escape'))


