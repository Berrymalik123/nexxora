from django.conf import settings
from django.db import models


class Profile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='profile')
    bio = models.TextField(blank=True, max_length=500)
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True)
    last_seen = models.DateTimeField(null=True, blank=True)
    followers = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='following_profiles', blank=True)

    def __str__(self):
        return f"{self.user.username}'s profile"

    @property
    def follower_count(self):
        return self.followers.count()

    @property
    def following_count(self):
        return Profile.objects.filter(followers=self.user).count()
