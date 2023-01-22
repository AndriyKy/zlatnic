import os
import uuid

from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.text import slugify
from phonenumber_field.modelfields import PhoneNumberField


def user_image_file_path(instance, filename):
    _, extension = os.path.splitext(filename)
    filename = f"{slugify(instance.username)}-{uuid.uuid4()}{extension}"

    return os.path.join("profile_picture/", filename)


class User(AbstractUser):
    email = models.EmailField(null=False, blank=False)
    phone_number = PhoneNumberField(blank=True)
    image = models.ImageField(null=True, blank=True, upload_to=user_image_file_path)
