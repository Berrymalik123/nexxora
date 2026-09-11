from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    """Application user. Uses Django's standard username/password fields."""
    pass
