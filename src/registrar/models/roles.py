from django.contrib.auth.models import Permission
from django.db import models

# class CustomPermission(models.Model):
#     name = models.CharField(max_length=100, unique=True)
#     codename = models.CharField(max_length=100, unique=True)

#     def __str__(self):
#         return self.name
    
class Role(models.Model):
    name = models.CharField(max_length=100, unique=True)
    permissions = models.ManyToManyField(Permission)

    def __str__(self):
        return self.name