from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core import validators

# Create your models here.
class Users(AbstractUser):

    user_id = models.CharField('user_id',max_length=18,blank=False)

    # class Meta:
    #     db_table = 'db_users'
    #     verbose_name = '用户'
    #     verbose_name_plural = verbose_name